import serial,time,os
ser = serial.Serial('com33',115200,timeout=5)
if ser.inWaiting():
    print(ser.read(ser.inWaiting()).decode())

def create_writefile():
    writefile = [
                'def wf(filename):\\r\\n',
                '    if filename == "":\\r\\n',
                '        filename = input("Filename?: ")\\r\\n',
                '    file = open(filename,"w")\\r\\n',
                '    inp = ""\\r\\n',
                '    while inp != "*":\\r\\n',
                '        inp = input(".")\\r\\n',
                '        if inp != "*":\\r\\n',
                '            file.write(inp+"\\\\r\\\\n")\\r\\n',
                '    file.close()\\r\\n']

    print(sendToRepl(ser,"f = open('writefile.py','w')\r\n"))
    for codeline in writefile:
        print(sendToRepl(ser,"f.write('"+codeline+"')\r\n"))
    print(sendToRepl(ser,"f.close()\r\n"))

def sendToRepl(ser,replCmd):
    ser.write(replCmd.encode())
    time.sleep(.2)
    if ser.inWaiting():
        return ser.read(ser.inWaiting()).decode()
    return None

def copyToRemote(hostfilename,microfilename):
    if microfilename == "" or microfilename == "*":
        microfilename = hostfilename
    file = open(hostfilename)
    sendToRepl(ser,"writefile.wf('"+microfilename+"')\r\n")
    for line in file:
        print(sendToRepl(ser,line.replace('\n','')+'\r\n'))
    print(sendToRepl(ser,"*\r\n"))
    file.close()

def print_directory(path, remote=False, tabs=0):
    if remote:
        dirlisttxt = sendToRepl(ser,"os.listdir()\r\n")
        dirlist = (dirlisttxt.split('\r\n')[1:-1][0])[1:-1].replace("'","").replace(" ","").split(",")
    else:
        dirlist = os.listdir(path)

    for file in dirlist:
        if remote:
            stattxt = sendToRepl(ser,"os.stat('"+file+"')\r\n")
            stats = list(map(int,(stattxt.split('\r\n')[1:-1][0]).replace('(','').replace(')','').split(',')))
        else:
            stats = os.stat(path + "/" + file)
        filesize = stats[6]
        isdir = stats[0] & 0x4000

        if filesize < 1000:
            sizestr = str(filesize) + " bytes"
        elif filesize < 1000000:
            sizestr = "%0.1f KB" % (filesize / 1000)
        else:
            sizestr = "%0.1f MB" % (filesize / 1000000)

        prettyprintname = ""
        for _ in range(tabs):
            prettyprintname += "   "
        prettyprintname += file
        if isdir:
            prettyprintname += "/"
        print("{0:<40} Size: {1:>10}".format(prettyprintname, sizestr))

        # recursively print directory contents
        #if isdir:
            #print_directory(path + "/" + file, tabs + 1)

print(sendToRepl(ser,"\x04"))
print(sendToRepl(ser,"\r\n"))
print(sendToRepl(ser,"\x03"))
print(sendToRepl(ser,"\r\n"))

print(sendToRepl(ser,"import os\r\n"))
print(sendToRepl(ser,"os.chdir('/')\r\n"))
microfiles = sendToRepl(ser,"os.listdir()\r\n")
if microfiles.find('writefile.py') == -1:
    create_writefile()
print(sendToRepl(ser,"import writefile\r\n"))

inp = "*"
hostfilename = ""
microfilename = ""
while inp[0].upper() != "Q":
    localdir = os.getcwd()
    sendToRepl(ser,"\r\n")
    remotedir = sendToRepl(ser,"os.getcwd()\r\n").split("\r\n")[1][1:-1]
    print()
    print("Local Dir: ",localdir," Remote Dir: ",remotedir)
    print("Host: ",hostfilename," Micro: ",microfilename)
    inp = input("Enter Command (? - Help, q - Quit): ")

    if inp.upper() == "HFILE":
        hostfilename = input("Enter the name of the file on the Host computer: ")
    elif inp.upper() == "MFILE":
        microfilename = input("Enter the name of the file to be created on the Microcontroller: ")
    elif inp.upper() == "NDIR":
        ndir = input("Enter new folder to create on Microcontroller in "+remotedir+" ($ to abort): ")
        if ndir != "$":
            print(sendToRepl(ser,"os.mkdir('"+ndir+"')\r\n"))
            sendToRepl(ser,"os.chdir('"+ndir+"')\r\n")
    elif inp.upper() == "LDIR":
        print_directory(localdir)
    elif inp.upper() == "RDIR":
        print_directory(localdir, remote=True)
    elif inp.upper() == "RDIR":
        pass
    elif inp.upper() == "LCD":
        try:
            os.chdir(input("Enter source directory: "))
        except:
            print("Error setting requested default directory")
    elif inp.upper() == "RCD":
        sendToRepl(ser,"os.chdir('"+input("Enter destination directory: ")+"')\r\n")
    elif inp.upper() == "RDEL":
        fndel = input("Enter filename/directory to delete ($ to abort): ")
        if fndel != "$":
            if fndel == "*":
                ans = "X"
                while ans.upper() not in ["Y","N"]:
                    ans = input("Delete all files in folder - Are you sure? (Y/N): ")
                if ans.upper() == "Y":
                    dirlisttxt = sendToRepl(ser,"os.listdir()\r\n")
                    dirlist = (dirlisttxt.split('\r\n')[1:-1][0])[1:-1].replace("'","").replace(" ","").split(",")
                    for file in dirlist:
                        stattxt = sendToRepl(ser,"os.stat('"+file+"')\r\n")
                        stats = list(map(int,(stattxt.split('\r\n')[1:-1][0]).replace('(','').replace(')','').split(',')))
                        isdir = stats[0] & 0x4000
                        if not isdir:
                            print(sendToRepl(ser,"os.remove('"+file+"')\r\n"))
            else:
                stattxt = sendToRepl(ser,"os.stat('"+fndel+"')\r\n")
                stats = list(map(int,(stattxt.split('\r\n')[1:-1][0]).replace('(','').replace(')','').split(',')))
                isdir = stats[0] & 0x4000
                if isdir:
                    print(sendToRepl(ser,"os.rmdir('"+fndel+"')\r\n"))
                else:
                    print(sendToRepl(ser,"os.remove('"+fndel+"')\r\n"))
    elif inp.upper() == "COPY":
        os.chdir(localdir)
        sendToRepl(ser,"os.chdir('"+remotedir+"')\r\n")
        if hostfilename[0] == "*":
            if hostfilename[1] == "." and len(hostfilename) > 2:
                filterExt = hostfilename[1:]
                for filename in os.listdir():
                    if filename[-(len(filterExt)):] == filterExt:
                        copyToRemote(filename,filename)
            else:
                print("*ERROR* Wildcard by file extension only (ie *.py)")
        else:
            copyToRemote(hostfilename,microfilename)

    elif inp[0] == "?":
        print("HFILE = Name of the file on the Host computer")
        print("        limited wildcards can be used as source")
        print("        wildcards must have a defined file extension")
        print("        i.e. *.py, *.txt, ...")
        print("MFILE = Name of the file to be created on the Microcontroller")
        print("        Leave blank or '*' to use Host filename (no rename)")
        print("LCD = Set the local (source) directory on the Host computer")
        print("RCD = Set the remote (destination) directory on the Microcontroller")
        print("      When changing directories, relative directory paths work")
        print("      i.e. '..' up one, '../..' up 2")
        print("      paths that don't start with a '/','\' will be from the current path")
        print("NDIR = Create a new directory on the Microcontroller")
        print("LDIR = Display files in local source directory")
        print("RDIR = Display files in remote (Microcontroller) destination directory")
        print("RDEL = Delete a file/directory from Microcontroller")
        print("COPY = Copy the current file from the local directory to the remote directory")


