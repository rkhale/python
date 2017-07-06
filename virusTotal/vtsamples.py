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

virusCount = 0
DWNLDDIR=None
num_files=0

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
        print(error)
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
    logger.info("Max files to download is %s",virusCount)
    logger.info("Query is :-- %s",query)    
    next_page=None
    try:
        logger.debug("Creating object for class virustotal")
        vt=VIRUSTOTAL(query,virusCount)
        logger.info("Searching Virustotal with Query %s",query)
        
        next_page,file_hashs = vt.file_search_IntelAPI()
        #next_page,file_hashs = vt.file_search_privateAPI()
        
        file_hash_to_dwnld = []
        file_hash_to_dwnld.extend(file_hashs)
        while next_page:            
            
            next_page,file_hashs = vt.file_search_IntelAPI(page=next_page)
            #next_page,file_hashs = vt.file_search_privateAPI(page=next_page)
            
            if file_hashs :
                file_hash_to_dwnld.extend(file_hashs)
        if file_hash_to_dwnld:
            logger.info("Found %s file hashs with the query %s",len(file_hash_to_dwnld),query)
            logger.debug("File Hash's are %s",file_hash_to_dwnld)
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
            logger.info("Downloading the Virus Files to %s",DWNLDDIR)
            hash_Iteratable = []
            
            logger.info("Preventing downloads ... exit now")
            sys.exit(0)
            
            for file_hash in file_hash_to_dwnld:
                hash_Iteratable.append((file_hash,DWNLDDIR))
            logger.debug("Creating a Threadpool of %s Threads for faster download.",vt.THREADCNT)
            pool = ThreadPool(vt.THREADCNT)
            
            #pool.map(lambda args :vt.downloadFile_privateAPI(*args), hash_Iteratable)
            pool.map(lambda args :vt.downloadFile_IntelAPI(*args), hash_Iteratable)
            
            pool.close()
            pool.join()        
            num_files = len ([f for f in os.listdir (DWNLDDIR) if os.path.isfile(os.path.join(DWNLDDIR,f))])
            logger.info("Downloaded %s files to %s",num_files,DWNLDDIR)
            logger.info("All files downloaded to %s",DWNLDDIR)
        else:
            logger.error("Blank File Hash.")
            sys.exit(-1)
    except Exception as err:
        logger.error("Exception %s",err)
        sys.exit(1)
    
#byconventions
sys.exit(0)
    