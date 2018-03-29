"""
    Retrieve the infrastructure details for all the Infrastructure owned by the user.
"""
__author__ = 'Rohan Khale'
try:    
    import os
    import sys    
    import logging.config            
    import sys
    import ssl
    import atexit
    import json
    from pyVim.connect import Disconnect, SmartConnect   
except ImportError as error:
    print (error)
    sys.exit(-1)

logging.config.fileConfig("logging.conf",defaults={'logfilename': os.path.basename(__file__)+ ".log"})
logger = logging.getLogger(__name__)
infralog = os.path.join(os.path.dirname(os.path.realpath(__file__)),"infra.csv")
vcenterJson = "vcenter.json"
if not os.path.exists(vcenterJson) or not os.path.isfile(vcenterJson):
    logger.error("Unable to find %s. Please keep the %s at the same location where the %s is",vcenterJson,vcenterJson,os.path.basename(__file__))
    exit (-1)
objFile = open(vcenterJson,"r")        
vcDetails = json.load(objFile)
for key,value in vcDetails.items():
    if key != "TEMPLATE":
        vspherIP = str(value["IP"])
        vspherUname = str(value["user_name"])
        if len(str(value["domain"])) > 0 :
            vspherUname = str(value["domain"]) + "\\" + vspherUname
        vspherPsswd = str(value["password"])

def getVMDetails (SUMMARY):
    try:
        outStr = ""
        if "windows" in SUMMARY.config.guestFullName.lower():
            logger.info("{0:40} :-- {1}".format("Operating System Type [Windows / Linux]","Windows"))
            outStr = outStr + "Windows"                 
        else:
            logger.info("{0:40} :-- {1}".format("Operating System Type [Windows / Linux]","Linux"))
            outStr = outStr + "Linux"
        logger.info("{0:40} :-- {1}".format("Operating System",SUMMARY.config.guestFullName))
        outStr = outStr + "," + SUMMARY.config.guestFullName
        logger.info("{0:40} :-- {1}".format("VM name",SUMMARY.config.name))
        outStr = outStr + "," + SUMMARY.config.name
        if "64Guest" in SUMMARY.config.guestId:
            logger.info("{0:40} :-- {1}".format("Architecture Type [64/32]",64))
            outStr = outStr + "," + "64"                               
        else:
            logger.info("{0:40} :-- {1}".format("Architecture Type",32))
            outStr = outStr + "," + "32"
        logger.info("{0:40} :-- {1}".format("Power State",SUMMARY.runtime.powerState))
        outStr = outStr + "," + SUMMARY.runtime.powerState
        logger.debug ("Trying to retrieve the IP on which %s is running.",SUMMARY.config.name)
        logger.debug ("Trying to retrieve the IP on which of Host %s",SUMMARY.runtime.host)
        logger.info("{0:40} :-- {1}".format("Template",SUMMARY.config.template))
        HOST = getHostIPforVM(SUMMARY.runtime.host)
        if HOST:
            logger.info("{0:40} :-- {1}".format("VM Running on Host",HOST))
            outStr = outStr + "," + HOST
        else:
            logger.debug("Unable to retrieve the Host IP for Host with name %s",SUMMARY.runtime.host)
        write2File(outStr, infralog)
        logger.info("="*100)
    except Exception :
        logger.error("Exception",exc_info=True)
        exit (-1)
        

def getHostIPforVM(HOST):
    try:
        HOSTIP = None
        ssl._create_default_https_context = ssl._create_unverified_context
        si = SmartConnect(host=vspherIP, user=vspherUname, pwd=vspherPsswd, port=443)                
        atexit.register(Disconnect, si)
        if si:
            content = si.RetrieveContent()
            for datacenter in content.rootFolder.childEntity:
                if hasattr(datacenter.hostFolder, 'childEntity'):
                    hostFolder = datacenter.hostFolder
                    computeResourceList = hostFolder.childEntity
                    for computeResource in computeResourceList:
                        if computeResource._wsdlName == "ComputeResource" :
                            if computeResource.host[0] == HOST and computeResource.name:
                                HOSTIP = computeResource.name
                        else:
                            ccomputeResourceList = computeResource.childEntity
                            for ccomputeResource in ccomputeResourceList:
                                if ccomputeResource.host[0] == HOST and ccomputeResource.name:
                                    HOSTIP = ccomputeResource.name                                                            
        else:
            logger.error("Unable to connect to %s",vspherIP)
        return (HOSTIP)
    except Exception :
        logger.error("Exception",exc_info=True)
        exit (-1)


def write2File (STR,FILE):
    logger.debug("")
    logger.debug("Inside function %s",sys._getframe().f_code.co_name)
    passed_args = locals()
    logger.debug("The arguments passed to {} are {}".format(sys._getframe().f_code.co_name,passed_args))
    fh = None        
    try:
        if not os.path.exists(FILE) and not os.path.isfile(FILE):
            STR = "OS Type,Operating System,VM Name,Architecture,Power State,Virtualization Host" + "\n" + STR.strip() + "\n"
        else:
            STR = STR.strip() + "\n"
        fh = open (FILE,"a+")        
        fh.write(STR)
        return True
    except Exception:
        logger.error("Exception",exc_info=True)
        return False
    finally: 
        if fh and fh is not None:
            logger.debug("Closing File Handle")
            fh.close()       
        logger.debug("Exit function : %s",sys._getframe().f_code.co_name)


if __name__ == "__main__":
    try:
        #default_context = ssl._create_default_https_context        
        ssl._create_default_https_context = ssl._create_unverified_context
        logger.info("#"*100)        
        logger.info("Trying to connect to %s using username '%s' & Password '%s'",vspherIP,vspherUname,vspherPsswd)
        si = SmartConnect(host=vspherIP, user=vspherUname, pwd=vspherPsswd, port=443)                
        atexit.register(Disconnect, si)
        if si:
            content = si.RetrieveContent()
            vmCount = 0
            for datacenter in content.rootFolder.childEntity:
                if hasattr(datacenter.vmFolder, 'childEntity'):
                    vmOwner = datacenter.permission[0].principal
                    vmFolder = datacenter.vmFolder                    
                    vmList = vmFolder.childEntity                    
                    logger.info("="*100)                         
                    for vm in vmList:                        
                        if vm._wsdlName != "Folder":
                            if vm.summary:
                                vmCount = vmCount + 1
                                getVMDetails(vm.summary)
                        else:                            
                            cvmList = vm.childEntity
                            for cvm in cvmList:
                                if cvm.summary:
                                    vmCount = vmCount + 1
                                    getVMDetails(cvm.summary)
                        
            logger.info("Found %s vm's",vmCount)
    except Exception :
        logger.error("Exception",exc_info=True)
        exit (-1)