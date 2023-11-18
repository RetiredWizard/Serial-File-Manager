# Serial-File-Manager
File manager that bootstraps itself over a serial REPL connection

**The Ninth line of code will need to be edited for the specific com port and parameters**
```
    ser = serial.Serial('com33',115200,timeout=5)
```

This is primarly useful for accessing the Flash on CircuitPython or MicroPython boards that don't mount a virtual USB drive to the host computer. With the new Circuit Python Web workflow features this will become less of an issue.


1. In MU or Thonny make sure you have the configuration set to use the "Standard Python" or "The same interpreter that runs Thonny"
2. Then update the Serial parameters on line 9 to match the serial connection to your microcontroller board
3. Run the mubootstrap.py program


## File Manager Commands ##

**The COPY/CCOPY commands will only work with text files, binary files are NOT supported.**
**Use the BCOPY or CFOLDER command for binary files.**

- LFILE = Name of the file on the Host (Local) computer
          limited wildcards can be used as source
          wildcards must have a defined file extension
          i.e. *.py, *.txt, ...
- RFILE = Name of the file to be created on the (Remote) Microcontroller
          Leave blank or '*' to use Host filename (no rename)
- LCD = Set the local (source) directory on the Host computer
- RCD = Set the remote (destination) directory on the Microcontroller
        When changing directories, relative directory paths work
        i.e. '..' up one, '../..' up 2
        paths that don't start with a '/','\' will be from the current path
- RMD  = Create a new directory on the Microcontroller
- LDIR = Display files in local source directory
- RDIR = Display files in remote (Microcontroller) destination directory
- RDEL = Delete a file/directory on Microcontroller
- COPY = Copy the current file from the local directory to the remote directory
- CCOPY= Character (careful) verion of copy routine
- BCOPY= Binary (careful only) version of copy routine
- CFOLDER=Recursivley (binary) copy contents of current local source directory to remote directory

