"""
    This file will host all the variables that we need.
"""
__author__ = 'Rohan Khale'
try:    
    import sys
    import datetime
except ImportError as error:
    print (error)
    raise (error)

def getRoot():
    try :        
        root = sys.executable
        if root.lower().startswith("c:"):
            root = "C:/"            
        elif root.lower().startswith("/"):
            root = "/"
        else:
            print("Unable to determine the root")
            root = None            
        return root
    except Exception as err:
        print(err)
        raise (err)
    return None

BASEDIR = "vtsamples"
KEY="your Virus Total private api Key"
VT_BASEURI = "https://www.virustotal.com/vtapi/v2/"
VT_SEARCHURI = VT_BASEURI + "file/search"
VT_DOWNLOADURI = VT_BASEURI + "file/download"
QUERY_DT_START = datetime.datetime.today().strftime('%Y-%m-%d')
QUERY_DT_END = (datetime.datetime.today()+ datetime.timedelta(days=1)).strftime('%Y-%m-%d')
LOG_CONFIG_FILE = "logging.conf"
THREAD_POOL=10
if getRoot():
    ROOT = getRoot()
else:
    raise Exception ("Unable to determine OS Type")
    sys.exit (1)