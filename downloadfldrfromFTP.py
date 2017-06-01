def downloadFldrfromFTP (SERVER_IP,SERVER_UNAME,SERVER_PSSWD,SERVER_DWNLD_PATH,ON_DISK_PATH):
    # This function will download the file / folder recursive to on local disk
    
    import os.path
    import ftplib
    print ("Downloading contents from "+SERVER_DWNLD_PATH + " to " + ON_DISK_PATH+".")
    
    if os.path.isdir(ON_DISK_PATH):
        # Directory exists , now clean it
        print ("Found "+ ON_DISK_PATH + " on local disk.\nDeleting its contents so that the build can be copied here." )
        deleteDirectory (ON_DISK_PATH,True)
    else:
        # Directory does not exist , create it
        print (ON_DISK_PATH + " doesn't exist on local disk. Creating it.")
        os.makedirs(ON_DISK_PATH)    
    
    try:
        ftp = ftplib.FTP(SERVER_IP) 
        ftp.login(SERVER_UNAME, SERVER_PSSWD)
        ftp.cwd(SERVER_DWNLD_PATH)
    except ftplib.error_perm:        
        print ("error: could not change to "+SERVER_DWNLD_PATH+"\n"+error_perm)
        return False

    #list children:
    filelist=ftp.nlst()    

    for ftp_files in filelist:        
        try:
            #this will check if file is folder:                        
            ftp.cwd(SERVER_DWNLD_PATH+ftp_files+"/")
            #if so, explore it:
            downloadFldrfromFTP (SERVER_IP,SERVER_UNAME,SERVER_PSSWD,SERVER_DWNLD_PATH+ftp_files+"/",ON_DISK_PATH+ftp_files + "/")            
        except ftplib.error_perm:
            #not a folder with accessible content
            #download & return
            ftp.cwd(SERVER_DWNLD_PATH)            
            ftp.retrbinary("RETR "+ftp_files, open(os.path.join(ON_DISK_PATH,ftp_files),"wb").write)            
    
    ftp.close()
    print ("All files from "+ SERVER_DWNLD_PATH + " have been successfully downloaded at " + ON_DISK_PATH + ".")
    return True