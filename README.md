<div align=center>
    <h1>librosewater &#127754; &#127801;</h1>
</div>

-----

## :computer: Support
The library only works on Windows for now, but cross-platform support may be added in the future. ~~Don't look forward to it, though.~~

For all support needed to this library, you can open an [issue](https://github.com/OpenM-Project/librosewater/issues/).

## :inbox_tray: Install
Installation is done through `pip`:
```
pip install git+https://github.com/run4r-ses/librosewater.git
```
:warning: **WARNING**: This will require you to have [`git`](https://git-scm.com/downloads) in your `PATH`.

## :zap: Example
In this small example, we will:
- Wait for a process to start & get a handle
- Wait for the module & get a handle
- Dump the module and patch it
- Inject patched module into memory

```py
import ctypes
import librosewater
import librosewater.module
import librosewater.process

process_PID, process_handle = librosewater.process.wait_for_process("my_app.exe")

# Get module handle and path
module_handle, module_path = librosewater.module.wait_for_module(process_handle, "super_secret_stuff.dll")

# Dump module to variable
data_length, data = librosewater.module.dump_module(process_handle, module_handle)

# Inject new module data
new_data = data.replace(b"\x00", b"\x02")
librosewater.module.inject_module(process_handle, module_handle, new_data)
```

## :page_with_curl: License
All code and assets are licensed under MIT License, read more at the [LICENSE](LICENSE) file.
