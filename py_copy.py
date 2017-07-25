"""
    This is the class for copying the source & Destination    
"""
__author__ = 'Rohan Khale'
try:    
    import os      
    import sys
    import logging    
    import shutil
    import win32wnet
    import paramiko
    import scp    
except ImportError as error:
    print (error)
    raise (error)

class COPY ():
    def __init__(self,SOURCE,DEST_HOST,DEST_PATH,UNAME,PASSWD,IS_SSH_SUPPORTED,logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.logger.debug("Inside function %s",sys._getframe().f_code.co_name)        
        self.logger.debug("Creating COPY object")
        self.source=SOURCE        
        self.ip=DEST_HOST
        self.destination = DEST_PATH
        self.user=UNAME
        self.password=PASSWD
        self.is_ssh_supported=IS_SSH_SUPPORTED or None            
        self.logger.debug("    Copy Destination Host    : %s",self.ip)
        self.logger.debug("    Copy Destination Path    : %s",self.destination)        
        self.logger.debug("    Copy Username            : %s",self.user)
        self.logger.debug("    Copy Password            : %s",self.password)
        self.logger.debug("    Copy Source              : %s",self.source)
        self.logger.debug("    Copy Is SSH Supported    : %s",self.is_ssh_supported)
        
        
    def xcopy (self):
        """
            This is the generic function that we have written. It should be able to invoke any of the other functions mentioned below
        """
        self.logger.debug("Inside function %s",sys._getframe().f_code.co_name)
        
        if self.is_ssh_supported:
            self.__scp_copy()
        else:
            self.__unc_copy()
        
    
    def remotedelete(self):
        self.logger.debug("Inside function %s",sys._getframe().f_code.co_name)
        
        if self.is_ssh_supported:
            self.__sshdelete()
        else:
            self.__UNCdelete()
        
        
    def listRemoteFiles(self):
        """
            List all files in a directory on a remote Machine.
            Return an array with the list of files present on the remote directory
            Will return None if anything fails
        """
        self.logger.debug("Inside function %s",sys._getframe().f_code.co_name)
        raise NotImplementedError
    
    
    def __unc_copy (self):
        """
            http://code.activestate.com/recipes/442521-windows-network-file-transfers/
            Copy files from one machine to other based on UNC Path
        """
        self.logger.debug("Inside function %s",sys._getframe().f_code.co_name)
        try:
            self.__wnet_connect(self.ip, self.user, self.password)
            self.logger.debug("Converting %s to UNC Path",self.destination)
            path = self.__convert_unc(self.ip, self.destination)
            self.logger.debug("UNC converted Path : %s",path)
            
            if not path [len(path ) - 1] == '\\':
                path  = ''.join([path, '\\'])        
            
            self.logger.debug("Check if destination %s dir exists",path )
            
            if not os.path.exists(path):
                self.logger.debug("Destination %s dir does not exists. Creating it",path )                
                os.makedirs(path)
            self.logger.debug("%s dir exists",self.destination)
            self.logger.info("Copying %s [ALL] files from %s to %s",len(os.listdir(self.source)),self.source,path)         
            
            for file in os.listdir(self.source):                            
                shutil.copy(os.path.join(self.source,file), path )
                
        except Exception :
            self.logger.error("Exception",exc_info=True)
            raise Exception
        self.logger.info("All Files from %s successfully copied to %s",self.source,path)
        return True
        
                
    def __wnet_connect(self,host,user,password):
        """
            http://code.activestate.com/recipes/442521-windows-network-file-transfers/
            This function is a part __win_unc_copy            
        """
        self.logger.debug("Inside function %s",sys._getframe().f_code.co_name)
        unc = ''.join(['\\\\', host])
        try:
            win32wnet.WNetAddConnection2(0, None, unc, None, user, self.password)
        except Exception as err:
            if isinstance(err, win32wnet.error):
                # Disconnect previous connections if detected, and reconnect.
                if err[0] == 1219:
                    win32wnet.WNetCancelConnection2(unc, 0, 0)
                    return self.__wnet_connect(host,user,password)
            raise err
    
    def __convert_unc(self,host,path):
        """ 
            http://code.activestate.com/recipes/442521-windows-network-file-transfers/            
            Convert a file path on a host to a UNC path.
        """        
        self.logger.debug("Inside function %s",sys._getframe().f_code.co_name)        
        return ''.join(['\\\\', host, '\\', path.replace(':', '$')])
    
    
    def __UNCdelete(self):
        """ 
            http://code.activestate.com/recipes/442521-windows-network-file-transfers/            
            Deletes all files & directories on a remote computer path via UNC
        """  
        self.logger.debug("Inside function %s",sys._getframe().f_code.co_name)
        self.logger.debug("Check for files in %s on %s. If found, delete them.",self.destination,self.ip)                
        try:
            a_files = self.__UNClistRemoteFiles()
            if a_files and len(a_files) > 0:            
                self.logger.info ("Deleting files in %s on %s",self.destination,self.ip)                
                self.__wnet_connect(self.ip,self.user,self.password)    
                path = self.__convert_unc(self.ip,self.destination)
                for del_file in a_files:
                    file_path = os.path.join(path,del_file)
                    try:
                        if os.path.isfile(file_path):
                            #self.logger.debug("Found file %s. Deleting it.",file_path)
                            os.unlink(file_path)
                        elif (os.path.isdir(path)):
                            #self.logger.debug("Found Directory %s, Deleting it.",file_path)
                            shutil.rmtree(file_path,True)                        
                    except Exception as err:
                        self.logger.error("Exception %s",err)
                        raise err
            self.logger.debug("%s folder on %s Empty or all Files in Folder deleted.",self.destination,self.ip)
        except Exception:
            self.logger.error("Exception",exc_info=True)
            raise Exception
        return True      
            
    
    def __sshdelete(self):
        """
            Deletes all files & directories on a remote computer path via ssh
        """
        self.logger.debug("Inside function %s",sys._getframe().f_code.co_name)
        self.logger.debug("Check for files in %s on %s. If found, delete them.",self.destination,self.ip)                
        py_ssh=None
        py_sftp=None
                
        try:
            a_files = self.__sshlistRemoteFiles()
            if a_files and len(a_files) > 0:
                self.logger.info ("Deleting files in %s on %s",self.destination,self.ip)
                self.logger.debug("Checking if path contains something like 'c:\\virus' 'c:/virus' .. if it does.. it will be converted to '\\virus' '/virus'")
                self.logger.debug("Remote path is : %s",self.destination)
                
                if ":" in self.destination:
                    a_newPath = self.destination.split(sep=":", maxsplit=1)                    
                    self.logger.debug("Path updated to %s",a_newPath[1])
                
                py_ssh = paramiko.SSHClient()
                py_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())            
                self.logger.info("Opening a ssh connection to %s with username %s",self.ip,self.user)
                py_ssh.connect(self.ip,22,self.user,self.password)
                
                self.logger.debug("Creating an SFTP client over SSH")
                py_sftp = py_ssh.open_sftp()
                
                self.logger.debug("Changing directory to %s",a_newPath[1])            
                py_sftp.chdir(path=a_newPath[1])                
                                
                for file in a_files:
                    py_sftp.remove(py_sftp.getcwd()+file)
                
            self.logger.debug("%s folder on %s Empty or all Files in Folder deleted.",self.destination,self.ip)            
        except Exception:
            self.logger.error("Exception",exc_info=True)
            raise Exception
        finally:
            if py_sftp:
                py_sftp.close()
            if py_ssh:
                py_ssh.close()
            return True
        
    def __scp_copy (self):
        """
            Copy files from one machine to a remote machine over scp
            TODO : Uses sftp to check if Folder [py_sftp.stat(path)] exists & create it if it doesn't [py_sftp.mkdir(path)] .. check if this can be done with scp only
        """
        self.logger.debug("Inside function %s",sys._getframe().f_code.co_name)
        py_ssh=None
        py_sftp=None
        try:
            self.logger.debug("Checking if path contains something like 'c:\\virus' 'c:/virus' .. if it does.. it will be converted to '\\virus' '/virus'")
            self.logger.debug("Remote path is : %s",self.destination)
            
            if ":" in self.destination:
                a_newPath = self.destination.split(sep=":", maxsplit=1)
                path = a_newPath[1]
                self.logger.debug("Path updated to %s",a_newPath[1])
            if "\\" in path:
                a_newPath = self.destination.split(sep="\\", maxsplit=1)
                path =a_newPath[1]
                self.logger.debug("Path updated to %s",path)
            
            py_ssh = paramiko.SSHClient()
            py_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())            
            self.logger.info("Opening a ssh connection to %s with username %s",self.ip,self.user)
            py_ssh.connect(self.ip,22,self.user,self.password)
            
            try:
                self.logger.debug("Checking if %s exits on %s",self.destination,self.ip)
                py_sftp = paramiko.SFTPClient.from_transport(py_ssh.get_transport())
                py_sftp.stat(path)        
            except FileNotFoundError:
                # Incase the folder does not exist ... create it.
                self.logger.info("%s not found on %s. Creating it.",path,self.ip)
                py_sftp.mkdir(path)

            self.logger.info("Creating a SCP client over ssh")
            py_scp = scp.SCPClient(py_ssh.get_transport())
            
            self.logger.info("Copying %s [ALL] files from %s to %s",len(os.listdir(self.source)),self.source,"\\\\"+self.ip+"\\"+path)            
            for file in os.listdir(self.source):
                py_scp.put(self.source+"/"+file,path)
            
        except Exception:
            self.logger.error("Exception",exc_info=True)
            raise Exception        
        finally:            
            if py_scp:
                py_scp.close()
            if py_sftp:
                py_sftp.close()
            if py_ssh:
                py_ssh.close()
            self.logger.info("All Files from %s successfully copied to %s",self.source,self.ip+a_newPath[1])
            return True        
    
    
    def __UNClistRemoteFiles(self):
        """
            List all files in a directory on a remote Machine via UNC
            Return an array with the list of files present on the remote directory
            Will return None if anything fails
        """
        self.logger.debug("Inside function %s",sys._getframe().f_code.co_name)
        a_listfiles=[]                
        try:
            self.__wnet_connect(self.ip,self.user,self.password)    
            path = self.__convert_unc(self.ip,self.destination)
            self.logger.debug("Check for files on remote directory %s",path)
            if os.path.isdir(path):                
                self.logger.debug("Found %s files in %s.",len(os.listdir(path)),path)
                a_listfiles = os.listdir(path)                
            return a_listfiles
        except Exception:
            self.logger.error("Exception",exc_info=True)
            raise Exception
        return None
        
    
    
    def __sshlistRemoteFiles(self):
        """
            List all files in a directory on a remote Machine via ssh
            Return an array with the list of files present on the remote directory
            Will return None if anything fails
            TODO : This uses sftp .. check if we can do the same using SCP only
        """        
        self.logger.debug("Inside function %s",sys._getframe().f_code.co_name)
        py_ssh=None
        py_sftp=None
        a_listfiles=[]
        try:
            self.logger.debug("Checking if path contains something like 'c:\\virus' 'c:/virus' .. if it does.. it will be converted to '\\virus' '/virus'")
            self.logger.debug("Remote path is : %s",self.destination)
            
            if ":" in self.destination:
                a_newPath = self.destination.split(sep=":", maxsplit=1)
                path =a_newPath[1]
                self.logger.debug("Path updated to %s",path)
            
            if "\\" in path:
                a_newPath = self.destination.split(sep="\\", maxsplit=1)
                path =a_newPath[1]
                self.logger.debug("Path updated to %s",path)
            
            py_ssh = paramiko.SSHClient()
            py_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())            
            self.logger.info("Opening a ssh connection to %s with username %s",self.ip,self.user)
            py_ssh.connect(self.ip,22,self.user,self.password)
            
            self.logger.debug("Creating an SFTP client over SSH")
            py_sftp = paramiko.SFTPClient.from_transport(py_ssh.get_transport())
            
            try:
                self.logger.debug("Checking if %s exits on %s",self.destination,self.ip)                
                py_sftp.stat(path)        
            except FileNotFoundError:
                # Incase the folder does not exist ... create it.
                self.logger.info("%s not found on %s. Creating it.",path,self.ip)
                py_sftp.mkdir(path)
                return a_listfiles                
                
            py_sftp.chdir(path=path)
            self.logger.debug("Check for files on remote directory %s",self.ip+path)            
            a_listfiles = py_sftp.listdir()
            self.logger.debug("Found %s files in %s.",len(a_listfiles),"\\"+self.ip+"\\"+path)
            return a_listfiles        
        except Exception:
            self.logger.error("Exception",exc_info=True)
            raise Exception
        finally:
            if py_sftp:
                py_sftp.close()
            if py_ssh:
                py_ssh.close()