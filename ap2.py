#!/usr/bin/python

import sys
import ftplib
import os
import time
import errno

FILE_PATH = '/home/sahupr@ad.uc.edu/pubmed_docs/pubmed/updatefiles/'

def src_config(src, args):
    server = "ftp.ncbi.nlm.nih.gov"
    user = "anonymous"
    password = "anonymous"
    source = src
    destination = "/home/sahupr@ad.uc.edu/pubmed_docs/"
    interval = 0.1

    ftp = ftplib.FTP(server)
    ftp.login(user, password)

    downloadFiles(source, destination, interval, ftp, args)

def downloadFiles(path, destination, interval, ftp, args):
    try:
        ftp.cwd(path)       
        os.chdir(destination)
        mkdir_p(destination[0:len(destination)-1] + path)
        print ("Created: " + destination[0:len(destination)-1] + path)
    except OSError:     
        pass
    except ftplib.error_perm:       
        print ("Error: could not change to " + path)
        sys.exit("Ending Application")
    
    filelist=ftp.nlst()
    files = []
    if len(args)==2:
        files = filelist
    elif len(args)>2 and args[2] == 'range':
        ffile = 'pubmed21n'+str(args[3])+'.xml.gz'
        lfile = 'pubmed21n'+str(args[4])+'.xml.gz'
        print(ffile, lfile)
        for f in filelist:
            if f>=ffile and f<=lfile and f[-3:]=='.gz' and os.path.exists(FILE_PATH+f[0:-3]) == False:
                    print('file not found')
                    files.append(f)
    else:
        for i in range(2, len(args)):
            fid = str(sys.argv[i])
            ffile = 'pubmed21n'+str(fid)+'.xml.gz'
            if os.path.exists(FILE_PATH+ffile[0:-3]) == False:
                print('file not found')
                files.append(ffile)
            else:
                continue

    print(files)
    if len(files) != 0:
        for file in files:
            time.sleep(interval)
            try:            
                ftp.cwd(path + file + "/")          
                downloadFiles(path + file + "/", destination)
            except ftplib.error_perm:
                os.chdir(destination[0:len(destination)-1] + path)
                
                try:
                    ftp.retrbinary("RETR " + file, open(os.path.join(destination + path, file),"wb").write)
                    print ("Downloaded: " + file)
                except:
                    print ("Error: File could not be downloaded " + file)
    
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise