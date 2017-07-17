"""
    This is the entry point to searching / downloading the virus files from Virus total using private api's.
    This will take the query as a parameter & the max number of samples to download.
"""
__author__ = 'Rohan Khale'
try:
    import os
    import sys
    import optparse
    import datetime
    import time
    import shutil
    import logging.config
    from multiprocessing.dummy import Pool as ThreadPool
    import tokens as tokens
    from virustotal import VIRUSTOTAL
except ImportError as error:
    print (error)
    sys.exit(-1)

logging.config.fileConfig(tokens.LOG_CONFIG_FILE)
logger = logging.getLogger(__name__)

logger.debug("Current System path is : %s",sys.path)
logger.info("Current Python version is %s.%s.%s"%sys.version_info[:3])

virusCount = 0
DWNLDDIR=None
num_files=0

#clean_files=True

def buildQuery(OPTIONS,ARGUMENTS):
    """
        This function will build the required query from the options & the arguments that are passed to it
    """
    try:        
        logger.debug("Inside function %s",sys._getframe().f_code.co_name)
        if not OPTIONS or not ARGUMENTS:
            logger.error("OPTIONS or ARGUMENTS cannot be blank")
        else:
            logger.debug ("Options Passed : %s",OPTIONS)
            logger.debug("Arguments Passed : %s",ARGUMENTS)
            global virusCount 
            virusCount = int(OPTIONS.numfiles)
			clean_files= OPTIONS.cleanfiles
            logger.debug ("Max number of files to download (virusCount) :-- %s",virusCount)
            query = OPTIONS.query
            #TODO ... add a regular expression here to check if the fs given is in the format expected.
            greaterthan=False
            found = False        
            for queryElements in ARGUMENTS:
                queryElements=queryElements.strip()
                if "fs:today" in queryElements.lower():                
                    found = True
                    mydate = datetime.datetime.today().strftime('%Y-%m-%d')
                    logger.debug("Found today in Arguments. Will be changed to %s",mydate)
                elif "fs:tomorrow" in queryElements.lower():
                    found = True
                    mydate = (datetime.datetime.today()+ datetime.timedelta(days=1)).strftime('%Y-%m-%d')
                    logger.debug("Found tomorrow in Arguments. Will be changed to %s",mydate)
                elif "fs:yesterday" in queryElements.lower():
                    found = True
                    mydate = (datetime.datetime.today()- datetime.timedelta(days=1)).strftime('%Y-%m-%d')
                    logger.debug("Found yesterday in Arguments. Will be changed to %s",mydate)
                
                if not greaterthan and found:
                    logger.debug("Updating %s to %s",queryElements,'fs:'+str(mydate)+'+')                    
                    queryElements = "fs:"+str(mydate)+"+"
                    found = False
                    greaterthan = True
                elif greaterthan and found:
                    logger.debug("Updating %s to %s",queryElements,'fs:'+str(mydate)+'-')                    
                    queryElements = "fs:"+str(mydate)+"-"
                    found = False
                
                query = query.strip()
                query = query + " " + queryElements
                
            if query and len(query) > 0:
                return query
            else:
                return False
    except Exception as error:
        logger.error("Exception",exc_info=True)            
        raise (error)
    

def deleteDirectory (DIR_TO_BE_DELETED,RECURSIVE=False):
    # This function will Clean the directory that is  on disk directory. If Recursive is set to true then it will remove any Sub-directories too
    try:
        logger.debug("Inside function %s",sys._getframe().f_code.co_name)                        
        if os.path.isdir(DIR_TO_BE_DELETED):
            for del_file in os.listdir(DIR_TO_BE_DELETED):
                file_path = os.path.join(DIR_TO_BE_DELETED,del_file)                    
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif (os.path.isdir(file_path) & RECURSIVE == True):
                    shutil.rmtree(file_path, True)                
            return False
        else:
            return True
    except Exception as error:
        logger.error("Exception",exc_info=True)
        raise error
        
        
def createLocalDest(ON_DISK_PATH):
    """
        This will read the base location for download from a file & then will create a new nested directory to work with
    """
    try:
        logger.debug("Inside function %s",sys._getframe().f_code.co_name)
        if not os.path.isdir(ON_DISK_PATH):
            logger.info(ON_DISK_PATH + " doesn't exist. Creating it.")                
            os.makedirs(ON_DISK_PATH)
        else:
            logger.debug("Found " + ON_DISK_PATH + "\nDeleting it's contents.")                
            if not deleteDirectory(ON_DISK_PATH):
                logger.error("Unable to clear contents from "+ ON_DISK_PATH)
                return False
            logger.debug("All contents from "+ ON_DISK_PATH + " cleared")
        if os.path.isdir(ON_DISK_PATH) and not os.listdir(ON_DISK_PATH):
            logger.debug("%s exists and is empty",ON_DISK_PATH)
            return True
        else:
            logger.error("%s does not exists or is not Empty",ON_DISK_PATH)
            return False
    except Exception as error:
        logger.error("Exception",exc_info=True)
        raise (error)
    return False
        
usage = 'usage: %prog [options] <virustotal query>\nTry %prog -h / --help for more information'
parser = optparse.OptionParser(usage=usage, description='Allows you to download the top-n files returned by a given VirusTotal Intelligence search. Example: python %prog -n 10 type:"peexe" positives:5+')
parser.add_option('-n', '--numfiles', dest='numfiles', default=100,help='Max umber of files to download. Default is 100.')
parser.add_option('-c', '--cleanfiles', dest='cleanfiles', default=True,help='Download only Clean Files.')
parser.add_option('-q', '--query', dest='query', default="",help='Virus Total intellegient Query that is needed to be executed.')
(options, args) = parser.parse_args()

if not args:    
    parser.error('No search query provided')
else:
    try :
        virusCount = int(options.numfiles)
    except Exception as error:
        logger.error("%s is not an integer. Please specify an integer value for --numfiles or leave it blank for a default value of 100",options.numfiles)                
        sys.exit(-1)
    
    query = buildQuery(options, args)
    
    """
	if clean_files:
        query = 'type:peexe size:2mb- positives:0+ fs:2017-07-01+ fs:2017-07-14- not tag:corrupt'
        #query = 'type:peexe size:2mb- positives:0+ positives:7- fs:2017-07-01+ fs:2017-07-14- not tag:corrupt'
        #query = 'type:peexe size:2mb- positives:0+ fs:2017-07-01+ fs:2017-07-14- not tag:corrupt and (not cylance:infected or cylance:infected or not mcafee:infected or mcafee:infected not microsoft:infected or microsoft:infected not symantec:infected or symantec:infected not bitdefender:infected or bitdefender:infected not mcafee_gw_edition:infected or mcafee_gw_edition:infected)'
    else:
        query = 'type:peexe size:2mb- positives:10+ positives:11- fs:yesterday+ fs:today- not tag:corrupt'
    """
    logger.info("Max files to download is %s",virusCount)
    logger.info("Query is :-- %s",query)    
    next_page=None
    try:
        logger.debug("Creating object for class virustotal")
        vt=VIRUSTOTAL(query,virusCount)
        logger.info("Searching Virustotal with Query %s",query)        
        
                
        next_page,file_hashs = vt.file_search_IntelAPI()
        #next_page,file_hashs = vt.file_search_privateAPI(page=next_page)
        
        total_file_hash = []
        total_file_hash.extend(file_hashs)
        while next_page:            
            
            next_page,file_hashs = vt.file_search_IntelAPI(page=next_page)
            #next_page,file_hashs = vt.file_search_privateAPI(page=next_page)
                        
            if file_hashs :
                total_file_hash.extend(file_hashs)        
        
        if total_file_hash:
            logger.info("Found %s File Hashs with the query %s",len(total_file_hash),query)
            logger.debug("File Hash's are %s",total_file_hash)
            
            #__DEBUG__
            if clean_files:
                file_name = time.strftime('%Y%m%dT%H%M%S') + "_IntelAPI.txt"
            else:
                file_name = time.strftime('%Y%m%dT%H%M%S') + "_PrivateAPI.txt"
                
            file_name =  "C:/Python_Projects/git/virusTotal/" + file_name
            file_object = open(file_name,"w")
            file_object.write(str(total_file_hash))
            file_object.close()
            #__END__
            
            if clean_files:
                DWNLDDIR = vt.BASELOCALDIR + "/" + time.strftime('%Y%m%dT%H%M%S') + "_cleanfiles"
            else:
                DWNLDDIR = vt.BASELOCALDIR + "/" + time.strftime('%Y%m%dT%H%M%S')        
            
            logger.debug("Current download folder is %s",DWNLDDIR)
            
            if not os.path.isdir(DWNLDDIR):
                if createLocalDest(DWNLDDIR):
                    logger.info("%s successfully created",DWNLDDIR)
                else:
                    logger.error("Unable to create %s",DWNLDDIR)
                    sys.exit(-1)
            else:
                if deleteDirectory(DWNLDDIR, True):
                    logger.debug("Found %s . All Contents from %s successfully deleted.",DWNLDDIR,DWNLDDIR)
                else:
                    logger.error("Found %s . Unable to clear contents from %s.",DWNLDDIR,DWNLDDIR)
                    sys.exit(-1)
            
            if clean_files:
                logger.info("Filter the file Hash's since we wish to download only Clean Files.")
                file_hash_to_download = vt.getscanReport_PrivateAPI(total_file_hash)
                
                logger.info("Found %s File hash's that can be downloaded.",len(file_hash_to_download))
                logger.debug("File hash's are :",file_hash_to_download)
                total_file_hash = []
                total_file_hash.extend(file_hash_to_download)
                file_hash_to_download=[]
            
            logger.info("Downloading the Virus Files to %s",DWNLDDIR)
            hash_Iteratable = []
            
            #__DEBUG__
            if clean_files:
                file_name = time.strftime('%Y%m%dT%H%M%S') + "_IntelAPI_CLEAN.txt"
            else:
                file_name = time.strftime('%Y%m%dT%H%M%S') + "_PrivateAPI_CLEAN.txt"                
            file_name =  "C:/Python_Projects/git/virusTotal/" + file_name
            file_object = open(file_name,"w")
            file_object.write(str(total_file_hash))
            file_object.close()
            #__END__
            
            logger.info("Preventing downloads ... exit now")
            sys.exit(0)
            
            for file_hash in total_file_hash:
                hash_Iteratable.append((file_hash,DWNLDDIR))
            logger.debug("Creating a Threadpool of %s Threads for faster download.",vt.THREADCNT)
            pool = ThreadPool(vt.THREADCNT)
            
            #pool.map(lambda args :vt.downloadFile_privateAPI(*args), hash_Iteratable)
            pool.map(lambda args :vt.downloadFile_IntelAPI(*args), hash_Iteratable)
            
            pool.close()
            pool.join()        
            num_files = len ([f for f in os.listdir (DWNLDDIR) if os.path.isfile(os.path.join(DWNLDDIR,f))])
            logger.info("Downloaded %s files to %s",num_files,DWNLDDIR)            
        else:
            logger.error("Query did not return any file Hash's. Exiting now.")
            sys.exit(-1)
    except Exception as err:
        logger.error("Exception %s",err)
        logger.error("Exception",exc_info=True)        
        sys.exit(1)
    
#byconventions
sys.exit(0)