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
            self.vtfileReport = tokens.VT_FILE_REPORT            
            self.intelsearchURI = tokens.VT_INTELSEARCHURI
            self.inteldownloadURI = tokens.VT_INTELDOWNLOADURI
            
            self.maxtry=tokens.MAXTRY
            
            self.ignored_vendors = tokens.VENDOR_CONVIT            
            
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
            self.logger.error("Exception",exc_info=True)
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
                download_url = self.inteldownloadURI % (FILEHASH,self.api_key)
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
        i_current_Attempt=0        
        headers = {"Accept-Encoding": "gzip, deflate","User-Agent" : "gzip,  My Python requests library example client or username"}        
        if self.files_found >= self.maxFile:
            self.logger.debug("Max Files already found")
            return (None,None)              
        params = dict(apikey=self.api_key, query=self.query,offset=page)
        if page:
            self.logger.debug("Length of Params is : %s", len(self.api_key)+ len(self.query)+ len(page))
        else:
            self.logger.debug("Length of Params is : %s", len(self.api_key)+ len(self.query))
        myhashes = []
        while i_current_Attempt < self.maxtry:
            try:            
                self.logger.info("Sending Query to : %s with Params : %s" , self.searchURI ,params)
                response = requests.post(self.searchURI, data=params, headers=headers, timeout=self.timeout)
                i_current_Attempt=i_current_Attempt+1
            except requests.RequestException as e:
                self.logger.error("Request exception",exc_info=True)
                raise e
                    
            if response.status_code == 200 and json.loads(response.text)["response_code"] == 1:
                i_current_Attempt=0
                self.logger.info("Found %s files for the Search Criteria : %s." ,len(json.loads(response.content.decode("utf-8"))["hashes"]),self.query)
                page = None        
                if self.files_found + len(json.loads(response.content.decode("utf-8"))["hashes"]) > self.maxFile:                
                    self.logger.info("The number of already found + files returned by query is %s > than the max number of files that are expected %s. Selecting only the top %s Files from the Query",self.files_found + len(json.loads(response.content.decode("utf-8"))["hashes"]),self.maxFile,self.maxFile-self.files_found)                
                    myhashes = json.loads(response.content.decode("utf-8"))["hashes"][:self.maxFile-self.files_found]                
                else:
                    myhashes = json.loads(response.content.decode("utf-8"))["hashes"]            
                    if "offset" in response.content.decode("utf-8"):            
                        page = json.loads(response.content.decode("utf-8"))["offset"]                                          
                
                self.files_found = self.files_found+ len(myhashes)      
                self.logger.info("Total number of files found till now is %s",self.files_found)
                self.logger.debug("The Files found by the Query are : %s",myhashes)            
                self.logger.debug("Found offset. Length of offset : %s",len(page))
                break
            else:
                self.logger.debug ("Response Status Code : %s",response.status_code)                            
                self.logger.debug("Response Reason : %s", response.reason)          
                self.logger.debug ("Response Text %s", response.text)  
                self.logger.debug("Trying again [%s] Try",i_current_Attempt)
                time.sleep(10)
        return (page,myhashes)
    
    
    def file_search_IntelAPI(self,page=None):
        """
            This uses the https://www.virustotal.com/intelligence/search/programmatic/ which is the privateAPI equivalent of https://www.virustotal.com/vtapi/v2/file/search.
            This returns page,filehash [].
            If there is a next page to the query then page exits or else its None.
            The query will limit itself to self.maxFile hash's to return
        """
        self.logger.debug("Inside function %s",sys._getframe().f_code.co_name)        
        if self.files_found >= self.maxFile:
            self.logger.debug("Max Number of files found. No more searching")
            return (None,None)        
        i_currentAttempt=0        
        headers = {"Accept-Encoding": "gzip, deflate","User-Agent" : "gzip,  My Python requests library example client or username"}
        params = dict(apikey=self.api_key, query=self.query,page=page)
        if page:
            self.logger.debug("Length of Params is : %s", len(self.api_key)+ len(self.query)+ len(page))
        else:
            self.logger.debug("Length of Params is : %s", len(self.api_key)+ len(self.query))
        myhashes = []
        while i_currentAttempt < self.maxtry:            
            try:            
                self.logger.info("Sending Query to : %s with Params : %s" , self.searchURI ,params)
                response = requests.post(self.intelsearchURI, params=params, headers=headers, timeout=self.timeout)
                i_currentAttempt = i_currentAttempt + 1                            
            except requests.RequestException as e:
                self.logger.error("Request exception",exc_info=True)
                raise e        
            
            if response.status_code == 200 and json.loads(response.text)["result"] == 1 and len(json.loads(response.content.decode("utf-8"))["hashes"]) > 0 :
                i_currentAttempt=0
                self.logger.info("Found %s files for the Search Criteria : %s." ,len(json.loads(response.content.decode("utf-8"))["hashes"]),self.query)
                page = None        
                if self.files_found + len(json.loads(response.content.decode("utf-8"))["hashes"]) > self.maxFile:                
                    self.logger.info("The number of already found + files returned by query is %s > than the max number of files that are expected %s. Selecting only the top %s Files from the Query",self.files_found + len(json.loads(response.content.decode("utf-8"))["hashes"]),self.maxFile,self.maxFile-self.files_found)                
                    myhashes = json.loads(response.content.decode("utf-8"))["hashes"][:self.maxFile-self.files_found]                
                else:
                    myhashes = json.loads(response.content.decode("utf-8"))["hashes"]            
                    if "next_page" in response.content.decode("utf-8"):            
                        page = json.loads(response.content.decode("utf-8"))["next_page"]                                          
                
                self.files_found = self.files_found+ len(myhashes)      
                self.logger.info("Total number of files found till now is %s",self.files_found)
                self.logger.debug("The Files found by the Query are : %s",myhashes)
                self.logger.debug("Found offset. Length of offset : %s",len(page))
                break                
            else:
                self.logger.debug ("Response Status Code : %s",response.status_code)                            
                self.logger.debug("Response Reason : %s", response.reason)          
                self.logger.debug ("Response Text %s", response.text)  
                self.logger.debug("Trying again [%s] Try",i_currentAttempt)
                time.sleep(10)
                        
        return (page,myhashes)            
    
    
    def getscanReport_PrivateAPI(self,RESOURCE):
        """
            GET /vtapi/v2/file/report
            Retrieves a concluded file scan report for a given file. Unlike the public API, this call allows you to also access all the information we have on a particular file
            (VirusTotal metadata, signature information, structural information, etc.) by using the allinfo parameter described later on. 
            You may use either HTTP GET or POST with this API call.
            Parameters
            apikey    Your API key.
            resource    An md5/sha1/sha256 hash of a file for which you want to retrieve the most recent antivirus report. 
                        You may also specify a scan_id (sha256-timestamp as returned by the scan API) to access a specific report. 
                        You can also specify a CSV list made up of a combination of hashes and scan_ids (up to 25 items), this allows you to perform a batch request with just one single call.
            allinfo (optional)    If specified and set to one, the call will return additional info, other than the antivirus results, on the file being queried. 
                    This additional info includes the output of several tools acting on the file (PDFiD, ExifTool, sigcheck, TrID, etc.), metadata regarding VirusTotal submissions (number of unique sources that have sent the file in the past, first seen date, last seen date, etc.), the output of in-house technologies such as a behavioural sandbox, etc.
            
            The RESOURCES can be of any length .. split it up in sets of 25 & then get the response.
        """
        self.logger.debug("Inside function %s",sys._getframe().f_code.co_name)
        self.logger.debug("RESOURCE passed : %s",RESOURCE)
        a_hash=[] # This is an array of hash's that will be retuned.
        if len(RESOURCE)== 0:
            self.logger.error("RESOURCE is Blank. No report to get.")
            return None
        else:
            aa_hash=[]
            if len(RESOURCE)> 25:                
                self.logger.info("Count of Hash's is greater than 25. Splitting it into chunks of 25")
                for i in range (0,len(RESOURCE),25):
                    aa_hash.append(RESOURCE[i:i+25])
            else:
                aa_hash.append(RESOURCE)
            headers = {"Accept-Encoding": "gzip, deflate","User-Agent" : "gzip,  My Python requests library example client or username"}
            for lHash in aa_hash:                                
                self.logger.info("Trying to retrieve the report with resources : %s",lHash)                
                myresource = ",".join(lHash)            
                self.logger.debug("Converting list to csv so it can be used in params : %s",myresource)
                params = dict(apikey=self.api_key, resource=myresource)
                self.logger.debug("Sending Params : %s",params)
                self.logger.info("Retrieving files report from %s",self.vtfileReport)
                try:
                    response = requests.get(self.vtfileReport,params=params, headers=headers)                    
                except requests.RequestException as e:
                    self.logger.error("Exception : %s",e)
                    self.logger.error("Request exception",exc_info=True)
                except Exception as err:
                    self.logger.error("Exception :%s",err)
                    raise err                                    
                if response.status_code == 200:
                    json_response = response.json()
                    self.logger.debug("Found Report : %s",json_response)                                                            
                    for scan in json_response:
                        # Evaluate if multithreading here will help / hurt us .. How much time does it save.
                        f_hash=self.__filterFile(scan)
                        if f_hash:
                            a_hash.append(f_hash)
                else:
                    self.logger.error ("Response not 200. Error Code : %s : %s", response.status_code,response.reason)            
                    raise Exception ("Response not 200.")
            return a_hash
        return None
    
    
    def __filterFile(self,DICT):
        """
            This will return TRUE / FALSE base on the conditions.
            It will take the file report as input.
            # Currently our filter criteria is :-- None of the vendors should flag the file as infected. If any vendor from the self.ignored_vendors list does flag .. we don't care
        """
        self.logger.debug("Inside function %s",sys._getframe().f_code.co_name)
        try:
            if len(DICT) == 0 :
                self.logger.error("Blank DICT .. Nothing to test")
                return None
            else:
                for key , value in DICT.items():
                    if "scans" in key:
                        to_add=True
                        self.logger.info("Check scan details for File Hash %s : ",DICT["resource"] )
                        for k , v in value.items():
                            self.logger.debug("Anti-Virus Name : %s",k)
                            self.logger.debug("Scan details are : %s",v)
                            if k not in self.ignored_vendors and v["detected"] is True: 
                                self.logger.debug("This file cannot be used since %s has convicted the file",k)
                                to_add=False
                                break
                        if to_add:
                            self.logger.info("%s has passed our filter criteria.",DICT["resource"])
                            return DICT["resource"]
        except Exception as err:
            self.logger.error("Exception :%s",err)
            raise err
        return None