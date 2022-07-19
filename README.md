# Serial-File-Manager
File manager that bootstraps itself over a serial REPL connection

This is primarly useful for accessing the Flash on CircuitPython or MicroPython boards that don't mount a virtual USB drive to the host computer. With the new Circuit Python Web workflow features this will become less of an issue.

The File Copy function will only work with text files, binary files are NOT supported.

- HFILE = Name of the file on the Host computer
          limited wildcards can be used as source
          wildcards must have a defined file extension
          i.e. *.py, *.txt, ...
- MFILE = Name of the file to be created on the Microcontroller
          Leave blank or '*' to use Host filename (no rename)
- LCD = Set the local (source) directory on the Host computer
- RCD = Set the remote (destination) directory on the Microcontroller
        When changing directories, relative directory paths work
        i.e. '..' up one, '../..' up 2
        paths that don't start with a '/','\' will be from the current path
- NDIR = Create a new directory on the Microcontroller
- LDIR = Display files in local source directory
- RDIR = Display files in remote (Microcontroller) destination directory
- RDEL = Delete a file/directory on Microcontroller
- COPY = Copy the current file from the local directory to the remote directory

