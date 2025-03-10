import os
import ctypes
from ctypes import wintypes
from . import *

class MODULEINFO(ctypes.Structure):
    _fields_ = [
        ("lpBaseOfDll", ctypes.c_void_p),
        ("SizeOfImage", wintypes.DWORD),
        ("EntryPoint", ctypes.c_void_p),
    ]

def wait_for_module(process: int, module_name: str) -> tuple:
    """Blocking function to wait for a module to load.

    :param process: The process handle.
    :type process: int
    :param module_name: The name of the module file.
    :type module_name: str

    :return: A tuple containing the module handle and module path.
    :rtype: tuple"""
    while True:
        count = 128
        while True:
            modulelist = (wintypes.HMODULE * count)()
            modulelist_size = ctypes.sizeof(modulelist)
            cb_needed = wintypes.DWORD()
            if not psapi.EnumProcessModulesEx(process, ctypes.byref(modulelist),
                    modulelist_size, ctypes.byref(cb_needed), LIST_MODULES_ALL):
                status = wintypes.DWORD()
                if kernel32.GetExitCodeProcess(process, ctypes.byref(status)):
                    if status.value != 259: # STILL_ACTIVE: 259
                        raise ProcessClosedError("process is no longer active, exit code %s" % status.value)
                continue
            if cb_needed.value < modulelist_size:
                break
            else:
                count *= 2

        for module in filter(None, modulelist):
            name = ctypes.create_unicode_buffer(MAX_PATH)
            if not psapi.GetModuleFileNameExW(process,
                    ctypes.c_int64(module), name, MAX_PATH):
                continue
            if os.path.basename(name.value) == module_name:
                return (module, name.value)

def dump_module(process: int, module: int) -> tuple:
    """Dumps a module from process memory.

    :param process: The process handle.
    :type process: int
    :param module: The module handle.
    :type module: int

    :return: A tuple containing the length and data.
    :rtype: tuple"""
    module_info = MODULEINFO()
    if not psapi.GetModuleInformation(process,
            ctypes.c_int64(module), ctypes.byref(module_info)):
        error = kernel32.GetLastError()
        raise QueryError("module info query fail, GetModuleInformation return %s" % error)
    dump = ctypes.create_string_buffer(module_info.SizeOfImage)
    if not kernel32.ReadProcessMemory(process, ctypes.c_int64(module_info.lpBaseOfDll),
            ctypes.byref(dump), module_info.SizeOfImage, 0):
        error = kernel32.GetLastError()
        raise ReadWriteError("read error, ReadProcessMemory return %s" % error)
    return (module_info.SizeOfImage, dump.raw)

def inject_module(process: int, module: int, data: bytes) -> None:
    """Injects a module into the given handle.

    :param process: The process handle.
    :type process: int
    :param module: The module handle.
    :type module: int
    :param data: The bytes for the injected module.
    :type data: bytes

    :return: None
    :raises ProtectBypassError: If protection bypass fails.
    :raises ReadWriteError: If there is a write error."""
    old_security = ctypes.c_int64(PAGE_EXECUTE_READ)
    if not kernel32.VirtualProtectEx(process, ctypes.c_int64(module),
            len(data), PAGE_EXECUTE_READWRITE, ctypes.byref(old_security)):
        error = kernel32.GetLastError()
        raise ProtectBypassError("security error, VirtualProtectEx return %s" % error)
    if not kernel32.WriteProcessMemory(process,
            ctypes.c_int64(module), data, len(data), 0):
        error = kernel32.GetLastError()
        raise ReadWriteError("write error, WriteProcessMemory return %s" % error)
