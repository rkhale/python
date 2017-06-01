"""
    This file will take the parameter, which is the location of the SEPM Installer.
    It will expect that the Console Simulator jar exists inside the SEPM installation folder & is under the base folder called consim
"""
__author__ = 'Rohan Khale'

def zipFolder (dirPath=None, zipFilePath=None, includeDirInZip=True):
    import os
    import zipfile
    """Create a zip archive from a directory.
    http://peterlyons.com/problog/2009/04/zip-dir-python    
    Note that this function is designed to put files in the zip archive with
    either no parent directory or just one parent directory, so it will trim any
    leading directories in the filesystem paths and not include them inside the
    zip archive paths. This is generally the case when you want to just take a
    directory and make it into a zip file that can be extracted in different
    locations.     
    
    Keyword arguments:
        
    dirPath -- string path to the directory to archive. This is the only
    required argument. It can be absolute or relative, but only one or zero
    leading directories will be included in the zip archive.

    zipFilePath -- string path to the output zip file. This can be an absolute
    or relative path. If the zip file already exists, it will be updated. If
    not, it will be created. If you want to replace it from scratch, delete it
    prior to calling this function. (default is computed as dirPath + ".zip")

    includeDirInZip -- boolean indicating whether the top level directory should
    be included in the archive or omitted. (default True)
"""        
    if not zipFilePath:
        zipFilePath = dirPath + ".zip"
    if not os.path.isdir(dirPath):
        raise OSError("dirPath argument must point to a directory. "
            "'%s' does not." % dirPath)
    parentDir, dirToZip = os.path.split(dirPath)
    #Little nested function to prepare the proper archive path
    def trimPath(path):
        archivePath = path.replace(parentDir, "", 1)
        if parentDir:
            archivePath = archivePath.replace(os.path.sep, "", 1)
        if not includeDirInZip:
            archivePath = archivePath.replace(dirToZip + os.path.sep, "", 1)
        return os.path.normcase(archivePath)
        
    outFile = zipfile.ZipFile(zipFilePath, "w",
        compression=zipfile.ZIP_DEFLATED)
    for (archiveDirPath, dirNames, fileNames) in os.walk(dirPath):
        for fileName in fileNames:
            filePath = os.path.join(archiveDirPath, fileName)
            outFile.write(filePath, trimPath(filePath))
        #Make sure we get empty directories as well
        if not fileNames and not dirNames:
            zipInfo = zipfile.ZipInfo(trimPath(archiveDirPath) + "/")
            #some web sites suggest doing
            #zipInfo.external_attr = 16
            #or
            #zipInfo.external_attr = 48
            #Here to allow for inserting an empty directory.  Still TBD/TODO.
            outFile.writestr(zipInfo, "")
    outFile.close()
    print("Zip operation completed successfully.")
    
def targzFolder (sourcePath, destPath , TARFILENAME):    
    try:
        import tarfile
        import glob
        import ntpath
        
        if not os.path.isdir(sourcePath):
            print(sourcePath + " does not exist")
            return False
        
        if not os.path.isdir(destPath):
            print(destPath + " does not exit. Creating it")
            os.makedirs(destPath)
        # Delete any tar.gz files that are present in the folder.
        files = []
        for file in glob.glob(destPath + "/SEPFL*.tar.gz"):            
            head,tail = ntpath.split(file)
            files.append(tail)
        try:
            for file in files:
                os.unlink(destPath + "/" + file)                
        except Exception as error:
            print(error)
            raise (error)
        
        with tarfile.open(destPath+"/"+TARFILENAME , "w:gz") as tar:
            tar.add(sourcePath,arcname=os.path.basename(sourcePath))     
        
    except Exception as error:
        print(error)
        sys.exit(-1)
    
    print(TARFILENAME + " successfully created.")


def extractZIP (zip_file,dest_fldr):
    try:
        import zipfile
        print("Extracting " + zip_file + " at "+ dest_fldr)
        ZF = zipfile.ZipFile(zip_file, 'r')        
        if os.path.isdir(dest_fldr):
           deleteDirectory (dest_fldr,True)
        else:           
            os.makedirs(dest_fldr)
            
        ZF.extractall(dest_fldr)
        ZF.close()
    
    except Exception as error:
        print(error)
        sys.exit(-1)