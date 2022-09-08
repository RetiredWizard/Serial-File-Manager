import serial,time,os

def reset_serial(ser):
    print("Resetting Serial Port...")
    try:
        ser.close()
    except:
        pass
    #return serial.Serial('com20',9600,timeout=10,write_timeout=15)
    return serial.Serial('com33',115200,timeout=10,write_timeout=15)

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

    #print(sendToRepl(ser,"f = open('writefile.py','w')\r\n"))
    #for codeline in writefile:
    #    print(sendToRepl(ser,"f.write('"+codeline+"')\r\n"))
    #print(sendToRepl(ser,"f.close()\r\n"))

    for lchar in "f = open('writefile.py','w')":
        print(sendCharToRepl(ser,lchar),end="")
    print(sendCharToRepl(ser,"\r"))
    for codeline in writefile:
        for lchar in "f.write('":
            print(sendCharToRepl(ser,lchar),end="")
        for lchar in codeline:
            print(sendCharToRepl(ser,lchar),end="")
        for lchar in "')":
            print(sendCharToRepl(ser,lchar),end="")
        print(sendCharToRepl(ser,"\r"))
    for lchar in "f.close()":
        print(sendCharToRepl(ser,lchar),end="")
    print(sendCharToRepl(ser,"\r"))
    time.sleep(.002)

def sendCharToRepl(ser,replCmd):
    retVal = sendToRepl(ser,replCmd,.0001)
    wait_time = time.monotonic()
    if replCmd == '\r':
        while retVal != '\r\n>>> ' and time.monotonic()-wait_time < 5:
            if time.monotonic() < wait_time:
                wait_time = time.monotonic()
            if ser.inWaiting():
                retVal += ser.read(ser.inWaiting()).decode()
            if len(retVal) >= 4:
                if retVal[-4:] == '>>> ':
                    break
        if len(retVal) >= 6:
            if retVal[-6:] == '\r\n>>> ':
                retVal = retVal[:-6]+'\n>>> '
    else:
        while retVal != replCmd and time.monotonic()-wait_time < 5:
            if time.monotonic() < wait_time:
                wait_time = time.monotonic()
            if ser.inWaiting():
                retVal = ser.read(ser.inWaiting()).decode()

    return retVal

def sendToRepl(ser,replCmd,delaytime=.01):
    ser.write(replCmd.encode())
    wait_time = 5
    if delaytime > .0001:
        time.sleep(delaytime*5)
    waiting = 0
    deltatime = max(delaytime,.001)
    while wait_time > 0:
        #print(waiting)
        wait_time -= deltatime
        if ser.inWaiting() and waiting == ser.inWaiting():
            break
        if delaytime > .0001:
            time.sleep(delaytime)
        waiting = ser.inWaiting()

    if ser.inWaiting() and delaytime < .001:
        return ser.read(ser.inWaiting()).decode()
    elif ser.inWaiting():
        retVal = ""
        while ser.inWaiting():
            #print("@",end="")
            retVal += ser.read(ser.inWaiting()).decode()
            #time.sleep(delaytime)

        #retVal = ser.read(ser.inWaiting()).decode()
        return retVal
    else:
        return ""

def copyToRemote(hostfilename,microfilename,careful=False):
    transErr = 0
    if microfilename == "" or microfilename == "*":
        microfilename = hostfilename
    file = open(hostfilename)
    sendToRepl(ser,"writefile.wf('"+microfilename+"')\r\n")
    for line in file:
        #print(line,end="")
        tstline = ""
        if line.replace('\r','').replace('\n','') != "":
            if careful:
                for lchar in line.replace('\r','').replace('\n',''):
                    tstline += sendCharToRepl(ser,lchar)
            else:
                tstline = sendToRepl(ser,line.replace('\r','').replace('\n',''))

        if (len(tstline) == 0 and len(line.replace('\r','').replace('\n','')) == 0):
            pass
        elif len(tstline) == 0 or \
            (tstline[0] != "." and tstline != line.replace('\r','').replace('\n','')) or \
            (tstline[0] == "." and tstline[1:] != line.replace('\r','').replace('\n','')):

            time.sleep(1)
            tstline += ser.read(ser.inWaiting()).decode()

        if len(tstline) == 0:
            if len(line.replace('\r','').replace('\n','')) != 0:
                print("****** Transmission Error *******")
                print("><")
                print(">"+line.replace('\r','').replace('\n','')+"<")
                transErr += 1
        elif tstline != line.replace('\r','').replace('\n',''):
            if tstline[0] != ".":
                print("****** Transmission Error *******")
                print(">"+tstline+"<")
                print(">"+line.replace('\r','').replace('\n','')+"<")
                transErr += 1
            else:
                if tstline[1:] != line.replace('\r','').replace('\n',''):
                    print("****** Transmission Error *******")
                    print(">"+tstline+"<")
                    print(">"+line.replace('\r','').replace('\n','')+"<")
                    transErr += 1

        print(tstline,end="")
        #print(sendToRepl(ser,'\r\n').replace('\r\n','\n'),end="")
        tstline = sendToRepl(ser,'\r\n')
        #print("DEBUG:>"+tstline+"<")
        kount = 50
        while tstline[-1] != "." and kount>0:
            kount -= 1
            #print("@",end="")
            tstline += ser.read(ser.inWaiting()).decode()
        print(tstline.replace('\r\n','\n'),end="")

    print(sendToRepl(ser,"*\r\n"))
    file.close()
    return transErr

def print_directory(path, remote=False, tabs=0):
    if remote:
        dirlisttxt = sendToRepl(ser,"os.listdir()\r\n")
        try:
            dirlist = (dirlisttxt.split('\r\n')[1:-1][0])[1:-1].replace("'","").replace(" ","").split(",")
        except:
            dirlist = []
    else:
        dirlist = os.listdir(path)

    for file in sorted(dirlist,key=str.lower):
        if remote:
            stattxt = sendToRepl(ser,"os.stat('"+file+"')\r\n")
            try:
                stats = list(map(int,(stattxt.split('\r\n')[1:-1][0]).replace('(','').replace(')','').split(',')))
            except:
                stats = [0,0,0,0,0,0,0]
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

ser = reset_serial(None)
print("Serial port reset")
if ser.inWaiting():
    print(ser.read(ser.inWaiting()).decode())

print("Attempting to get board attention")
print(sendToRepl(ser,"\x02"))
try:
    print(sendToRepl(ser," "))
except:
    print(sendToRepl(ser,"\x04"))
if sendToRepl(ser,"\r\n") == "":
    ser = reset_serial(ser)
time.sleep(5)
print(sendToRepl(ser,"\r\n"))
if sendToRepl(ser,"\r\n") == "":
    print(sendToRepl(ser,"\x04"))
    time.sleep(5)

print(sendToRepl(ser,"\x03"))
print(sendToRepl(ser,"\r\n"))
print(sendToRepl(ser,"\r\n"))

print(sendToRepl(ser,"import os\r\n",.2))
print(sendToRepl(ser,"os.chdir('/')\r\n",.2))
microfiles = sendToRepl(ser,"os.listdir()\r\n",.2)
if microfiles.find('writefile.py') == -1:
    create_writefile()
print(sendToRepl(ser,"import writefile\r\n",.2))

inp = "*"
hostfilename = ""
microfilename = ""
while inp[0].upper() != "Q":
    localdir = os.getcwd()
    sendToRepl(ser,"\r\n")
    try:
        remotedir = sendToRepl(ser,"os.getcwd()\r\n",.1).split("\r\n")[1][1:-1]
    except:
        remotedir = '/'
    print()
    print("Local Dir: ",localdir," Remote (micro) Dir: ",remotedir)
    print("Host file: ",hostfilename," Remote (micro) file: ",microfilename)
    inp = input("Enter Command (? - Help, q - Quit): ")

    if inp.upper() == "HFILE":
        hostfilename = input("Enter the name of the file on the Host computer: ")
    elif inp.upper() == "RFILE":
        microfilename = input("Enter the name of the file to be created on the remote microcontroller: ")
    elif inp.upper() == "NDIR":
        ndir = input("Enter new folder to create on Microcontroller in "+remotedir+" ($ to abort): ")
        if ndir != "$":
            print(sendToRepl(ser,"os.mkdir('"+ndir+"')\r\n"))
            sendToRepl(ser,"os.chdir('"+ndir+"')\r\n")
    elif inp.upper() == "LDIR":
        print_directory(localdir)
    elif inp.upper() == "RDIR":
        print_directory(localdir, remote=True)
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
                    dirlisttxt = sendToRepl(ser,"os.listdir()\r\n",.5)
                    try:
                        dirlist = (dirlisttxt.split('\r\n')[1:-1][0])[1:-1].replace("'","").replace(" ","").split(",")
                    except:
                        dirlist = []
                    for file in dirlist:
                        stattxt = sendToRepl(ser,"os.stat('"+file+"')\r\n",.1)
                        try:
                            stats = list(map(int,(stattxt.split('\r\n')[1:-1][0]).replace('(','').replace(')','').split(',')))
                        except:
                            stats = [0x4000]

                        isdir = stats[0] & 0x4000
                        if not isdir:
                            print(sendToRepl(ser,"os.remove('"+file+"')\r\n"))
            else:
                stattxt = sendToRepl(ser,"os.stat('"+fndel+"')\r\n",.1)
                try:
                    stats = list(map(int,(stattxt.split('\r\n')[1:-1][0]).replace('(','').replace(')','').split(',')))
                except:
                    stats = [0x4000]
                isdir = stats[0] & 0x4000
                if isdir:
                    print(sendToRepl(ser,"os.rmdir('"+fndel+"')\r\n"))
                else:
                    print(sendToRepl(ser,"os.remove('"+fndel+"')\r\n"))
    elif inp.upper() in ["COPY","CCOPY"]:
        tErr = 0
        os.chdir(localdir)
        sendToRepl(ser,"os.chdir('"+remotedir+"')\r\n")
        if hostfilename[0] == "*":
            if hostfilename[1] == "." and len(hostfilename) > 2:
                filterExt = hostfilename[1:]
                for filename in os.listdir():
                    if filename[-(len(filterExt)):] == filterExt:
                        if inp.upper() == "CCOPY":
                            tErr += copyToRemote(filename,filename,True)
                        else:
                            tErr += copyToRemote(filename,filename)
                print("Transmission Errors: ",tErr)
            else:
                print("*ERROR* Wildcard by file extension only (ie *.py)")
        else:
            if inp.upper() == "CCOPY":
                tErr = copyToRemote(hostfilename,microfilename,True)
            else:
                tErr = copyToRemote(hostfilename,microfilename)
            print("Transmission Errors: ",tErr)


    elif inp[0] == "?":
        print("HFILE = Name of the file on the Host computer")
        print("        limited wildcards can be used as source")
        print("        wildcards must have a defined file extension")
        print("        i.e. *.py, *.txt, ...")
        print("RFILE = Name of the file to be created on the remote (Microcontroller)")
        print("        Leave blank or '*' to use Host filename (no rename)")
        print("LCD = Set the local (source) directory on the Host computer")
        print("RCD = Set the remote (destination) directory on the Microcontroller")
        print("      When changing directories, relative directory paths work")
        print("      i.e. '..' up one, '../..' up 2")
        print("      paths that don't start with a '/','\\' will be from the current path")
        print("NDIR = Create a new directory on the Microcontroller")
        print("LDIR = Display files in local source directory")
        print("RDIR = Display files in remote (Microcontroller) destination directory")
        print("RDEL = Delete a file/directory from Microcontroller")
        print("COPY = Copy the current file from the local directory to the remote directory")
        print("CCOPY= Character (careful) verion of copy routine")

    elif inp.upper() == "Q":
        ser.close()


