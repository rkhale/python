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
    import urllib
    import logging
    import time
    import tokens as tokens
except ImportError as error:
    print (error)
    raise (error)

    
class VIRUSTOTAL():
    
    def __init__(self,QUERY,MAX_FILES_DWNLD=100,logger=None):
        try:
            #initialize the Logger
            self.logger = logger or logging.getLogger(__name__)
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
            
            self.publicsearchURI = tokens.VT_PUBLICSEARCHURI
            self.publicdownloadURI = tokens.VT_PUBLICDOWNLOADURI
            self.timeout=600
            self.ROOT = tokens.ROOT
            self.BASELOCALDIR = self.ROOT + "/" + tokens.BASEDIR                        
            self.maxFile = MAX_FILES_DWNLD
            self.THREADCNT=tokens.THREAD_POOL
            self.IterableHASHMAP=[]
            self.files_found=0           
            
            self.logger.debug("BaseFolder for Virus Download : %s",self.BASELOCALDIR)            
            self.logger.debug("Max files to be Downloaded : %s",self.maxFile)
              
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
                            self.logger.info("File with hash %s successfully downloaded at %s",FILEHASH,LocalDEST)
                            return True
                        else:
                            self.logger.error("Error downloading file with Hash %s",FILEHASH)
                            self.logger.error("File with hash %s successfully downloaded but unable to write to %s",FILEHASH,LocalDEST)
                            return False                    
                    else:
                        self.logger.error("Error downloading file with Hash %s",FILEHASH)
                        if response.status_code == 403:                            
                            self.logger.error("You tried to perform calls to functions for which you do not have access to.\n%s\n%s",response.status_code,response.reason)
                            return False
                        elif response.status_code == 404:                            
                            self.logger.error ("File with Hash %s not found.\n%s\n%s",FILEHASH ,response.status_code,response.reason)
                            return False
                        else:                            
                            self.logger.error ("Error Code %s\n%s", response.status_code,response.reason)
                            return False                    
                except requests.RequestException :
                    self.logger.error("Error downloading file with Hash %s",FILEHASH)
                    self.logger.error("Request Exception",exc_info=True)
                    return False
                except Exception:
                    self.logger.error("Error downloading file with Hash %s",FILEHASH)
                    self.logger.error("Generic Exception :--",exc_info=True)
                    return False
            else:
                self.logger.error("Error downloading file with Hash %s",FILEHASH)
                self.logger.error("%s file already exists in %s",FILEHASH,LocalDEST)                
                return False

            
    def downloadFile_IntelAPI (self,FILEHASH,LocalDEST):
        """
            This will download the file from Virustotal using progamatic api call.
            If the download is successful, it will return true, else false.
        """
        self.logger.debug("Inside function %s",sys._getframe().f_code.co_name)        
        FILEHASH = FILEHASH.strip()
        self.logger.debug("FILEHASH passed : %s",FILEHASH)
        if len(FILEHASH)== 0:
            self.logger.error("File hash is Blank. Cannot download file.")
            return False
        else:
            if not os.path.isfile(LocalDEST+"/"+FILEHASH):
                self.logger.info("Downloading File with hash : %s at %s",FILEHASH,LocalDEST)
                download_url = self.publicdownloadURI % (FILEHASH,self.api_key)
                self.logger.debug("Download URI is %s",download_url)
                try:
                    response = urllib.request.urlopen(download_url)
                    if response:                        
                        self.logger.debug("Opening a File Handle to %s with option 'wb' to write the response" , LocalDEST+"/"+FILEHASH)
                        file_obj = open(LocalDEST+"/"+FILEHASH,"wb")                
                        self.logger.debug("Writing response to %s" , LocalDEST+"/"+FILEHASH)
                        file_obj.write(response.read())
                        file_obj.close()
                        if os.path.isfile(LocalDEST+"/"+FILEHASH):
                            self.logger.info("File with hash %s successfully downloaded at %s",FILEHASH,LocalDEST)
                            return True
                        else:
                            self.logger.error("Error downloading file with Hash %s",FILEHASH)
                            self.logger.error("File with hash %s successfully downloaded but unable to write to %s",FILEHASH,LocalDEST)
                            return False
                    else:
                        self.logger.error("Error downloading file with Hash %s",FILEHASH)
                        self.logger.error("Blank or None response for %s",FILEHASH)
                        return False
                except Exception as error:
                    self.logger.error("Error downloading file with Hash %s",FILEHASH)
                    self.logger.error("Error %s",error)
                    self.logger.error("Generic Exception :--",exc_info=True)
                    return False
            else:                
                self.logger.error("Error downloading file with Hash %s",FILEHASH)
                self.logger.error("%s file already exists in %s",FILEHASH,LocalDEST)                
                return False
            
        
    def file_search_privateAPI (self,page=None):
        """
            This will return an array of hashes which match the self.query that was sent while creating the class object
            EXAMPLE:
            search_options = 'type:peexe size:2mb- positives:10+ positives:11- fs:2017-01-12+ fs:2017-01-13- not tag:corrupt'
            This will download only 300 .. we need to use the offset parameter to find out if there is indeed an offset & use it.                        
        """        
        self.logger.debug("Inside function %s",sys._getframe().f_code.co_name)
        #headers = {"Accept-Encoding": "gzip, deflate","User-Agent" : "gzip,  My Python requests library example client or username"}
        if self.files_found >= self.maxFile:
            self.logger.debug("Max Files already found")
            return (None,None)               
        params = dict(apikey=self.api_key, query=self.query,offset=page)
        myhashes = []
        try:            
            self.logger.info("Sending Query to : %s \nParams : %s" , self.searchURI ,params)
            response = requests.get(self.searchURI, params=params, timeout=self.timeout)                
            #response = requests.post(self.searchURI, data=params,headers=headers)
        except requests.RequestException as e:
            self.logger.error("Request exception",exc_info=True)
            return dict(error=str(e))
        if response.status_code == 200:
            self.logger.info("Found %s files for the Search Criteria\n%s." ,len(json.loads(response.content.decode("utf-8"))["hashes"]),self.query)            
            if len(json.loads(response.content.decode("utf-8"))["hashes"]) > self.maxFile:                
                self.logger.info("The number of files returned by query is %s > than the max number of files that are expected.\nSelecting only the top %s Files from the Query",len(json.loads(response.content.decode("utf-8"))["hashes"]),self.maxFile)                
                myhashes = json.loads(response.content.decode("utf-8"))["hashes"][:self.maxFile]                
            else:
                myhashes = json.loads(response.content.decode("utf-8"))["hashes"]
            if response.content.decode("utf-8").has_key("offset"):
                page = json.loads(response.content.decode("utf-8"))["offset"]
            else:
                page = None                          
            
            self.files_found = self.files_found+ len(myhashes)      
            self.logger.info("Found %s files in this query. Total number of files found is %s",len(myhashes),self.files_found)
            self.logger.debug("The Files found by the Query are\n %s",myhashes)            
            self.logger.debug("Offset is \n %s",page)            
            return (page,myhashes)
        else:
            self.logger.error ("Response not 200.\nError Code %s\n%s", response.status_code,response.reason)            
            raise Exception ("Response not 200.")
        return None
    
    def file_search_IntelAPI(self,page=None):
        """
            This uses the https://www.virustotal.com/intelligence/search/programmatic/ which is the privateAPI equivalent of https://www.virustotal.com/vtapi/v2/file/search.
            This returns page,filehash [].
            If there is a next page to the query then page exits or else its None.
            The query will limit itself to self.maxFile hash's to return
        """
        self.logger.debug("Inside function %s",sys._getframe().f_code.co_name)
        self.logger.debug("Number of files already found %s",self.files_found)
        if self.files_found >= self.maxFile:
            self.logger.debug("Max Number of files found. No more searching")
            return (None,None)        
        response = None
        page = page or 'undefined'
        attempts = 0
        params = dict(apikey=self.api_key, query=self.query,page=page)
        data = urllib.parse.urlencode(params).encode(encoding='utf_8', errors='strict')
        request=urllib.request.Request(self.publicsearchURI)
        self.logger.debug("Search URL is :-- %s",self.publicsearchURI)
        self.logger.debug("Parameters used are :-- %s",params)
        self.logger.debug("Data is :-- %s",data)
        self.logger.debug("Page is :-- %s",page)
        
        while attempts < 10:
            try:                                
                response = urllib.request.urlopen(request,data).read()
                self.logger.debug("Response has %s",response)                                                
                break
            except Exception as err:
                self.logger.error("Got exception %s",err)
                attempts += 1
                time.sleep(1)
        
        if not response:
            self.logger.error("Blank or no response.")
            return (None, None)
        else:        
            try:
                response_dict = json.loads(response)
                if not response_dict.get('result'):
                    self.logger.error ("Unable to get result in response_dict. Raising InvalidQueryError")
                    raise Exception (response_dict.get('error'))
                next_page = response_dict.get('next_page')
                hashes = response_dict.get('hashes', [])
                self.files_found = self.files_found +len(hashes)
                self.logger.debug("Found %s Hashes in Response.",len(hashes))
                self.logger.debug("Number of files already found %s\n",self.files_found)       
                return (next_page, hashes)
            except ValueError as err:
                self.logger.error("Exception",exc_info=True)
                self.logger.error("ValueError Exception %s",err)
                return (None, None)