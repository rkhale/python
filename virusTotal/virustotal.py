"""
    This is the class for VirusTotal Private api's
    This class currently has the functions to execute a search Query & download the files based on the hash's that are passed.
"""
__author__ = 'Rohan Khale'
try:    
    import os      
    import sys
    import json
    import requests
    import tokens as tokens
except ImportError as error:
    print (error)
    raise (error)

    
class VIRUSTOTAL():
    
    def __init__(self,logger,QUERY,MAX_FILES_DWNLD=100):
        try:
            #initialize the Logger
            self.logger = logger
            self.logger.debug("Inside function %s",sys._getframe().f_code.co_name)
            
            QUERY = QUERY.strip()
            if len(QUERY)==0:
                self.logger.error("Query cannot be blank")
                sys.exit(1)        
            self.query=QUERY
            # Get all the necessary variables from tokens.
            self.api_key = tokens.KEY
            self.baseURI = tokens.VT_BASEURI
            self.searchURI = tokens.VT_SEARCHURI
            self.downloadURI = tokens.VT_DOWNLOADURI
            self.timeout=600
            self.ROOT = tokens.ROOT
            self.BASELOCALDIR = self.ROOT + "/" + tokens.BASEDIR                        
            self.maxFile = MAX_FILES_DWNLD
            self.THREADCNT=tokens.THREAD_POOL
            self.IterableHASHMAP=[]
            
            self.logger.debug("Query :-- %s",self.query)
            self.logger.debug("Search URI : %s",self.searchURI)
            self.logger.debug("Download URI : %s",self.downloadURI)
            self.logger.debug("BaseFolder for Virus Download : %s",self.BASELOCALDIR)            
            self.logger.debug("Max files to be Downloaded : %s",self.maxFile)
            
            self.maxFile = 20
              
            if os.path.isdir(self.BASELOCALDIR):
                self.logger.debug("%s directory exists & is the Base directory where the Virus Total Samples will be Downloaded.",self.BASELOCALDIR)
            else:
                self.logger.debug("%s directory does not exists. Creating it now",self.BASELOCALDIR )
                os.makedirs(self.BASELOCALDIR)
                if os.path.isdir(self.BASELOCALDIR):
                    self.logger.debug("%s directory successfully created. It will be the Base directory where the Virus Total Samples will be Downloaded.",self.BASELOCALDIR)
                else:
                    self.logger.error("Unable to create %s",self.BASELOCALDIR)
                    raise ("Unable to create directory %s",self.BASELOCALDIR)
        except Exception as error:
            print (error)
            raise (error)
    
    def downloadFile_privateAPI(self,FILEHASH,LocalDEST):
        """
            This function will download the file with hash = FILEHASH from self.downloadURI to LocalDEST
        """
        self.logger.debug("Inside function %s",sys._getframe().f_code.co_name)        
        FILEHASH = FILEHASH.strip()
        self.logger.debug("FILEHASH passed : %s",FILEHASH)
        if len(FILEHASH)== 0:
            self.logger.error("File hash is Blank. Cannot donwload file.")
            return False
        else:
            if not os.path.isfile(LocalDEST+"/"+FILEHASH):            
                params = {'apikey': self.api_key, 'hash': FILEHASH}
                self.logger.debug("Downloading File with hash : %s at %s",FILEHASH,LocalDEST)    
                try:
                    self.logger.debug("Sending Query to : %s \nParams : %s" , self.downloadURI ,params)
                    response = requests.get(self.downloadURI, params=params, proxies=None, timeout=self.timeout)
                    if response.status_code == 200:                                
                        self.logger.debug("Opening a File Handle to %s with option 'wb' to write the response.content" , LocalDEST+"/"+FILEHASH)
                        file_obj = open(LocalDEST+"/"+FILEHASH,"wb")                
                        self.logger.debug("Writing response.content to %s" , LocalDEST+"/"+FILEHASH)
                        file_obj.write(response.content)
                        file_obj.close()
                        if os.path.isfile(LocalDEST+"/"+FILEHASH):
                            self.logger.debug("File with hash %s successfully downloaded at %s",FILEHASH,LocalDEST)
                            return True
                        else:
                            self.logger.error("File with hash %s successfully downloaded but unable to write to %s",FILEHASH,LocalDEST)
                            return False                    
                    elif response.status_code == 403:
                        self.logger.error("You tried to perform calls to functions for which you do not have access to.\n%s\n%s",response.status_code,response.reason)
                        return False
                    elif response.status_code == 404:
                        self.logger.error ("File with Hash %s not found.\n%s\n%s",FILEHASH ,response.status_code,response.reason)
                        return False
                    else:
                        self.logger.error ("Error Code %s\n%s", response.status_code,response.reason)
                        return False
                except requests.RequestException :
                    self.logger.error("Request Exception",exc_info=True)
                    return False
                except Exception:
                    self.logger.error("Generic Exception :--",exc_info=True)
                    return False
            else:
                self.logger.error("%s file already exists in %s",FILEHASH,LocalDEST)                
                return False

            
    def file_search_privateAPI (self):
        """
            This will return an array of hashes which match the self.query that was sent while creating the class object
            EXAMPLE:
            search_options = 'type:peexe size:2mb- positives:10+ positives:11- fs:2017-01-12+ fs:2017-01-13- not tag:corrupt'                        
        """        
        self.logger.debug("Inside function %s",sys._getframe().f_code.co_name)        
        params = dict(apikey=self.api_key, query=self.query)        
        myhashes = []
        try:            
            self.logger.info("Sending Query to : %s \nParams : %s" , self.searchURI ,params)
            response = requests.get(self.searchURI, params=params, timeout=self.timeout)                
        except requests.RequestException as e:
            self.logger.error("Request exception",exc_info=True)
            return dict(error=str(e))
        if response.status_code == 200:
            self.logger.info("Found %s files for the Search Criteria\n%s." ,len(json.loads(response.content.decode("utf-8"))["hashes"]),self.query)
            if len(json.loads(response.content.decode("utf-8"))["hashes"]) > self.maxFile:
                #self.logger.info("The number of files got " + str(len(json.loads(response.content.decode("utf-8"))["hashes"])) + " > than " + str(self.maxFile)+"\nPicking only the top "+ str(self.maxFile))
                self.logger.info("The number of files returned by query is %s > than the max number of files that are expected.\nSelecting only the top %s Files from the Query",len(json.loads(response.content.decode("utf-8"))["hashes"]),self.maxFile)                
                myhashes = json.loads(response.content.decode("utf-8"))["hashes"][:self.maxFile]
            else:
                myhashes = json.loads(response.content.decode("utf-8"))["hashes"]
            self.logger.debug("The Files found by the Query are\n %s",myhashes)
            return (myhashes)
        else:
            self.logger.error ("Response not 200.\nError Code %s\n%s", response.status_code,response.reason)            
            raise Exception ("Response not 200.")
        return None