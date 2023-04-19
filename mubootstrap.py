import serial,time,os

def reset_serial(ser):
    print("Resetting Serial Port...")
    try:
        ser.flush()
        ser.close()
    except:
        pass
    return serial.Serial('com52',9600,timeout=10,write_timeout=15)
    #return serial.Serial('com68',115200,timeout=10,write_timeout=15)
    #return serial.Serial('com84',1200,timeout=10,write_timeout=15)

def create_writefile():
    writefile = [
                'def wf(filename,binary=""):\\r\\n',
                '    if filename == "":\\r\\n',
                '        filename = input("Filename?: ")\\r\\n',
                '    file = open(filename,"w"+binary)\\r\\n',
                '    inp = ""\\r\\n',
                '    while inp != "*":\\r\\n',
                '        inp = input(".")\\r\\n',
                '        if binary and inp != "*":\\r\\n',
                '            inch = inp.split(",")\\r\\n',
                '            for ch in inch:\\r\\n',
                '                #file.write(bytes(chr(int(ch)),"utf-8"))\\r\\n',
                '                file.write(int(ch).to_bytes(1,"big"))\\r\\n',
                '        elif inp != "*":\\r\\n',
                '            file.write(inp+"\\\\r\\\\n")\\r\\n',
                '    file.close()\\r\\n']

    print(safeStrToRepl(ser,"f = open('writefile.py','w')\r"),end="")
    for codeline in writefile:
        print(safeStrToRepl(ser,"f.write('"+codeline+"')\r"),end="")
    print(safeStrToRepl(ser,"f.close()\r"),end="")
    time.sleep(.002)

def safeStrToRepl(ser,replCmd,prmpt=">>> "):
    retVal = ""
    for lchar in replCmd:
        retVal += sendCharToRepl(ser,lchar,prmpt)

    return retVal

def sendCharToRepl(ser,replCmd,prmpt=">>> "):
    retVal = sendToRepl(ser,replCmd,.0001)
    wait_time = time.monotonic()
    if replCmd == '\r':
        while retVal != '\r\n'+prmpt and time.monotonic()-wait_time < 5:
            if time.monotonic() < wait_time:
                wait_time = time.monotonic()
            if ser.inWaiting():
                retVal += ser.read(ser.inWaiting()).decode()
            if len(retVal) >= len(prmpt):
                if retVal[-len(prmpt):] == prmpt:
                    break
        if len(retVal) >= len(prmpt)+2:
            if retVal[-(len(prmpt)+2):] == '\r\n'+prmpt:
                retVal = retVal[:-(len(prmpt)+2)]+'\n'+prmpt
    else:
        while retVal != replCmd and time.monotonic()-wait_time < 5:
            if time.monotonic() < wait_time:
                wait_time = time.monotonic()
            if ser.inWaiting():
                retVal = ser.read(ser.inWaiting()).decode()

    return retVal

def sendToRepl(ser,replCmd,delaytime=.01):
    try:
        ser.write(replCmd.encode())
    except:
        print("Error Writing to Serial")
        return -1
        
    wait_time = 5
    if delaytime > .0001:
        time.sleep(delaytime*5)
    waiting = -1
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
        try:
            decodedRead = ser.read(ser.inWaiting()).decode()
        except:
            decodedRead = ""
            
        return decodedRead
    elif ser.inWaiting():
        retVal = ""
        while ser.inWaiting():
            #print("@",end="")
            try:
                retVal += ser.read(ser.inWaiting()).decode()
            except:
                pass
            #time.sleep(delaytime)

        #retVal = ser.read(ser.inWaiting()).decode()
        return retVal
    else:
        return ""
    
def multicpy(srcdir,tardir):
    curDLst = os.listdir(srcdir)
    
    print(safeStrToRepl(ser,"os.mkdir('"+tardir+"')\r"))
    
    for _dir in curDLst:
        if os.stat(srcdir+'\\'+_dir)[0] & (2**15) != 0:
            copyToRemote(srcdir+'\\'+_dir,tardir+'/'+_dir,True,True)
        else:
            multicpy(srcdir+'\\'+_dir,tardir+'/'+_dir)

def copyToRemote(hostfilename,microfilename,careful=False,binary=False):
    transErr = 0
    if microfilename == "" or microfilename == "*":
        microfilename = hostfilename
    if binary:
        file = open(hostfilename,"rb")
    else:
        file = open(hostfilename)
    if binary:
        print(safeStrToRepl(ser,"writefile.wf('"+microfilename+"','b')\r","."),end="")
    elif careful:
        print(safeStrToRepl(ser,"writefile.wf('"+microfilename+"')\r","."),end="")
    else:
        print(sendToRepl(ser,"writefile.wf('"+microfilename+"')\r\n"),end="")
    for line in file:
        #print(line,end="")
        tstline = ""
        cleanLine = ""
        if binary and line != b"":
            for i in line:
                cleanLine += str(i)+","
            cleanLine = cleanLine[:-1]
            tstline = safeStrToRepl(ser,cleanLine)
        elif not binary and line.replace('\r','').replace('\n','') != "":
            cleanLine = line.replace('\r','').replace('\n','').replace('\t','    ')
            if careful:
                tstline = safeStrToRepl(ser,cleanLine)
            else:
                tstline = sendToRepl(ser,cleanLine)

        if (len(tstline) == 0 and len(cleanLine) == 0):
            pass
        elif len(tstline) == 0 or \
            (tstline[0] != "." and tstline != cleanLine) or \
            (tstline[0] == "." and tstline[1:] != cleanLine):

            time.sleep(1)
            tstline += ser.read(ser.inWaiting()).decode()

        if len(tstline) == 0:
            if len(cleanLine) != 0:
                print("****** Transmission Error *******")
                print("><")
                print(">"+cleanLine+"<")
                transErr += 1
        elif tstline != cleanLine:
            if tstline[0] != ".":
                print("****** Transmission Error *******")
                print(">"+tstline+"<")
                print(">"+cleanLine+"<")
                transErr += 1
            else:
                if tstline[1:] != cleanLine:
                    print("****** Transmission Error *******")
                    print(">"+tstline+"<")
                    print(">"+cleanLine+"<")
                    transErr += 1

        #print(tstline,end="")
        print("#",end="")
        if careful:
            tstline = sendCharToRepl(ser,"\r",".")
        else:
            #print(sendToRepl(ser,'\r\n').replace('\r\n','\n'),end="")
            tstline = sendToRepl(ser,'\r\n')
        #print("DEBUG:>"+tstline+"<")
        kount = 50
        padtstline = False
        if tstline == "":
            tstline = " "
            padtstline = True
        while tstline[-1] != "." and kount>0:
            kount -= 1
            #print("@",end="")
            tstline += ser.read(ser.inWaiting()).decode()
        if padtstline:
            tstline = tstline[1:]
        #print(tstline.replace('\r\n','\n'),end="")

    if careful:
        #print(sendCharToRepl(ser,"*"),end="")
        #print(sendCharToRepl(ser,"\r"))
        sendCharToRepl(ser,"*")
        sendCharToRepl(ser,"\r")
    else:
        print(sendToRepl(ser,"*\r\n"),end="")
    file.close()
    return transErr

def print_directory(path, remote=False, tabs=0):
    if remote:
        safeStrToRepl(ser,"os.listdir()")
        dirlisttxt = sendCharToRepl(ser,"\r")
        #dirlisttxt = sendToRepl(ser,"os.listdir()\r\n")
        try:
            dirlist = (dirlisttxt.split('\n')[1:-1][0])[1:-1].replace("'","").replace(" ","").split(",")
        except:
            dirlist = []
    else:
        dirlist = os.listdir(path)

    for file in sorted(dirlist,key=str.lower):
        if remote:
            safeStrToRepl(ser,"os.stat('"+file+"')")
            stattxt = sendCharToRepl(ser,"\r")
            #stattxt = sendToRepl(ser,"os.stat('"+file+"')\r\n")
            try:
                stats = list(map(int,(stattxt.split('\n')[1:-1][0]).replace('(','').replace(')','').split(',')))
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
    print(ser.read(ser.inWaiting()).decode(),end="")

print("Attempting to get board attention")
tmp = sendToRepl(ser,"\r\n")
if ">>>" not in str(tmp):
    print('1 ',tmp,end="")
    if tmp == -1:
        ser = reset_serial(ser)
    elif tmp == "":
        print('^D',sendToRepl(ser,b"\x04"),end="")
    time.sleep(3)
    tmp = sendToRepl(ser," ")
    print('2 ',tmp,end="")
    if tmp == -1:
        ser = reset_serial(ser)
    time.sleep(1)
    tmp = sendToRepl(ser,"\x03")
    print('^C',tmp,end="")
    if ">>>" not in str(tmp):
        if tmp=="":
            print('^?',sendToRepl(ser,"\x02"),end="")
        print('3 ',sendToRepl(ser,"\r\n"),end="")
        time.sleep(3)
        print('4 ',sendToRepl(ser,"\r\n"),end="")
        time.sleep(1)
        tmp = sendToRepl(ser," ")
        print('5b',tmp,end="")
        if tmp == -1:
            ser = reset_serial(ser)
        elif tmp == "":
            print('^D',sendToRepl(ser,"\x04"),end="")

        tmp = sendToRepl(ser,"\r\n")
        print('6 ',tmp,end="")
        if ">>>" not in str(tmp):
            time.sleep(3)
            print('7 ',sendToRepl(ser,"\r\n"),end="")
            time.sleep(1)
            if sendToRepl(ser,"\r\n") == "":
                ser = reset_serial(ser)
            time.sleep(5)
            print('8 ',sendToRepl(ser,"\r\n"),end="")
            if sendToRepl(ser,"\r\n") == "":
                print('^D',sendToRepl(ser,"\x04"),end="")
                time.sleep(5)

            print('^C',sendToRepl(ser,"\x03"),end="")
            time.sleep(1)
            print('9 ',sendToRepl(ser,"\r\n"),end="")
print('10',sendToRepl(ser,"\r\n"),end="")

print(safeStrToRepl(ser,"import os\r"),end="")
print(safeStrToRepl(ser,"os.chdir('/')\r"),end="")
print(safeStrToRepl(ser,"import supervisor\r"),end="")
print(safeStrToRepl(ser,"supervisor.runtime.autoreload=False\r"),end="")
microfiles = safeStrToRepl(ser,"os.listdir()\r")
if microfiles.find('writefile.py') == -1:
    create_writefile()
print(safeStrToRepl(ser,"import writefile\r"),end="")

inp = "*"
hostfilename = ""
microfilename = ""
while inp.upper() != "Q":
    localdir = os.getcwd()
    sendCharToRepl(ser,"\r")
    safeStrToRepl(ser,"os.getcwd()")
    remotedir = sendCharToRepl(ser,"\r")
    try:
        #remotedir = sendToRepl(ser,"os.getcwd()\r\n",.1).split("\r\n")[1][1:-1]
        remotedir = remotedir.split("\n")[1][1:-1]
    except:
        remotedir = '/'

    print()
    print("Local Dir: ",localdir," Remote (micro) Dir: ",remotedir)
    print("Local file: ",hostfilename," Remote (micro) file: ",microfilename)
    inp = input("Enter Command (? - Help, q - Quit): ")

    if inp.upper() == "LFILE":
        hostfilename = input("Enter the name of the file on the Host computer: ")
    elif inp.upper() == "RFILE":
        microfilename = input("Enter the name of the file to be created on the remote microcontroller: ")
    elif inp.upper() == "RMD":
        ndir = input("Enter new folder to create on Microcontroller in "+remotedir+" ($ to abort): ")
        if ndir != "$":
            print(safeStrToRepl(ser,"os.mkdir('"+ndir+"')\r"))
            safeStrToRepl(ser,"os.chdir('"+ndir+"')\r")
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
        safeStrToRepl(ser,"os.chdir('"+input("Enter destination directory: ")+"')\r")
    elif inp.upper() == "RDEL":
        fndel = input("Enter filename/directory to delete ($ to abort): ")
        if fndel != "$":
            if fndel == "*":
                ans = "X"
                while ans.upper() not in ["Y","N"]:
                    ans = input("Delete all files in folder - Are you sure? (Y/N): ")
                if ans.upper() == "Y":
                    dirlisttxt = safeStrToRepl(ser,"os.listdir()\r")
                    try:
                        dirlist = (dirlisttxt.split('\n')[1:-1][0])[1:-1].replace("'","").replace(" ","").split(",")
                    except:
                        print("*** Error processing directory listing ***")
                        dirlist = []
                    for file in dirlist:
                        stattxt = safeStrToRepl(ser,"os.stat('"+file+"')\r")
                        try:
                            stats = list(map(int,(stattxt.split('\n')[1:-1][0]).replace('(','').replace(')','').split(',')))
                            isdir = stats[0] & 0x4000
                            if not isdir:
                                print(safeStrToRepl(ser,"os.remove('"+file+"')\r"))
                        except:
                            print("*** Can't determine file type for "+file+" ***")
            else:
                stattxt = safeStrToRepl(ser,"os.stat('"+fndel+"')\r")
                try:
                    stats = list(map(int,(stattxt.split('\n')[1:-1][0]).replace('(','').replace(')','').split(',')))
                    isdir = stats[0] & 0x4000
                    if isdir:
                        print(safeStrToRepl(ser,"os.rmdir('"+fndel+"')\r"))
                    else:
                        print(safeStrToRepl(ser,"os.remove('"+fndel+"')\r"))
                except:
                    print("*** Can't determine file type for "+fndel+" ***")
    elif inp.upper() == "CFOLDER":
        print("Copy all files from HOST:"+localdir+" and any subfolders to Microcontroller REMOTE:"+remotedir)
        print("This will overwrite any files with the same filename on the Microcontroller")
        if input("Continue? (Y/N): ").upper() == "Y":
            multicpy(localdir,remotedir)
    elif inp.upper() in ["COPY","CCOPY","BCOPY"]:
        if inp.upper() == "BCOPY":
            inp = "CCOPY"
            binflag = True
        else:
            binflag = False
        tErr = 0
        os.chdir(localdir)
        safeStrToRepl(ser,"os.chdir('"+remotedir+"')\r")
        if hostfilename[0] == "*":
            if hostfilename[1] == "." and len(hostfilename) > 2:
                filterExt = hostfilename[1:]
                for filename in os.listdir():
                    if filename[-(len(filterExt)):] == filterExt:
                        if inp.upper() == "CCOPY":
                            tErr += copyToRemote(filename,filename,True,binflag)
                        else:
                            tErr += copyToRemote(filename,filename)
                print("Transmission Errors: ",tErr)
            else:
                print("*ERROR* Wildcard by file extension only (ie *.py)")
        else:
            if inp.upper() == "CCOPY":
                tErr = copyToRemote(hostfilename,microfilename,True,binflag)
            else:
                tErr = copyToRemote(hostfilename,microfilename)
            print("Transmission Errors: ",tErr)


    elif inp == "?":
        print("LFILE = Name of the file on the Host computer")
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
        print("RMD  = Create a new directory on the Microcontroller")
        print("LDIR = Display files in local source directory")
        print("RDIR = Display files in remote (Microcontroller) destination directory")
        print("RDEL = Delete a file/directory from Microcontroller")
        print("COPY = Copy the current file from the local directory to the remote directory")
        print("CCOPY= Character (careful) verion of copy routine")
        print("BCOPY= Binary (careful only) version of copy routine")
        print("CFOLDER=Recursivley copy contents of current local source directory to remote directory")

    elif inp.upper() == "Q":
        ser.flush()
        ser.close()
