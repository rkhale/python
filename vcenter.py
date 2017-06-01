"""    
    This class has implemented the fuctions for VCenter & creates an object VCenter , which is essentially a VM.
"""
__author__ = 'Rohan Khale'

try:
    from pyVmomi import vim, vmodl
    from pyVim.task import WaitForTask
    from pyVim import connect
    import atexit
    from pyVim.connect import Disconnect, SmartConnect, GetSi
    import os
    from subprocess import TimeoutExpired
except Exception as e:
    print(str(e))
    sys.exit(-1)

class VCENTER ():
    def __init__(self,VMName,IPADDR=None):
        
		self.base_fldr = os.path.dirname(os.path.realpath(__file__))        
        self.esxi_details = os.path.abspath(os.path.join(self.base_fldr, os.pardir)) + "/esx_details.json"
        self.esxi_json = self.get_VCENTER_Details (self.esxi_details)        
        self.vm_details = os.path.abspath(os.path.join(self.base_fldr, os.pardir)) + "/vm_details.json"

        self.vm_ip =[]
        self.vm_internal_ip=None
        
        try:
            if VMName is None:
                raise BLANK_VMNAME
            else:
                self.vm_name = VMName
        except BLANK_VMNAME:
            print ("Name of the Virtual Machine cannot be blank.\nExit NOW")                         
            sys.exit(-1)
        
        try:
            self.vm_object = self.get_vmObject()
            if self.vm_object is None:
                raise BLANK_VMOBJECT
            
        except BLANK_VMOBJECT:
            print ("Unable to find Virtual Machine "+self.vm_name+" on any VCenters.\n" )
            sys.exit(-1)
        
        if IPADDR is None:    
            self.vm_ip=self.getIP()
        else:
            self.vm_ip.append(IPADDR)
        
        self.vm_ostype=self.getOSType()       
        
        
    def get_VCENTER_Details(self,ESX_DET_FILE):
        """
        This will return a JSON Object which has the following details
            1. IP of the ESX server
            2. Username of the ESX Server
            3. Password of the ESX Server
        """
        import json
        try:
            objFile = open(ESX_DET_FILE,"r")        
            ESXi = json.load(objFile)
        
        except Exception as error:
            raise error
        
        return ESXi
    
    def get_vmObject (self):
        """
            This will return the ESX Object which hosts the VM who's name is VMName.
            If not found the ESX Object will be None.
        """
        import ssl
        try:
            vm_object = None
            for key,value in self.esxi_json.items():
                ESX_IP=str(value["ip"])
                ESX_UNAME=str(value["user_name"])
                ESX_PASSWORD=str(value["password"])
                try :                    
                    default_context = ssl._create_default_https_context
                    ssl._create_default_https_context = ssl._create_unverified_context
                    si = SmartConnect(host=ESX_IP, user=ESX_UNAME, pwd=ESX_PASSWORD, port=443)        
                    atexit.register(Disconnect, si)
                    content = si.RetrieveContent()
                    
                    for datacenter in content.rootFolder.childEntity:
                        if hasattr(datacenter.vmFolder, 'childEntity'):
                            vmFolder = datacenter.vmFolder
                            vmList = vmFolder.childEntity
                            #vmList.sort()
                            for vm in vmList:                    
                                summary = vm.summary                    
                                try:                        
                                    if summary.config.name == self.vm_name :
                                        print ("Found Virtual Machine " + self.vm_name + " on ESX " + ESX_IP)                                    
                                        vm_object = vm
                                        return vm_object
                                except Exception as error:
                                    print ("Unable to access summary for VM: ", summary.config.name)
                                    print (error)    
                except Exception as error:
                    print ("Unable to connect to:",ESX_IP)
                    print (error)
        except Exception as error:
            print(error)
            raise (error)
        if not vm_object:
            print("Virtual Machine " + self.vm_name + " does not exist.")
        
        return None       
        
    def get_power_state (self):
        if self.vm_object.runtime.powerState == "poweredOn":
            #print ("Virtual Machine "+ self.vm_name +" is powered on.")
            return True
        else :
            #print ("Virtual Machine "+ self.vm_name +" is powered Off.")
            return False
        
    def getIPfromFile (self):
        # This function will be called only if the getIP function fails to get the IP of the machine from VCenter.
        # This will look into the file VM_DETAILS_JSON file & get the IP's from there.
        import json
        return_array = []
        
        try:
            objFile = open(self.vm_details,"r")        
            VMDetails = json.load(objFile)
            for key,value in VMDetails.iteritems():
                for data in value["VM"]:
                    if data["VMNAME"] == self.vm_name:
                        data_found = True
                        return_array=(data["IP"])
                        break
                               
        except Exception as error:
            raise error
                
        return return_array
    
    def getIP(self):
        # This will return the IP of the VM from the ESX server using VM Name.    
        return_array=[]        
        try:
            summary = self.vm_object.summary            
            if summary.guest.ipAddress != None and summary.guest.ipAddress != "":
                try:
                    for nic in self.vm_object.guest.net:                                        
                        for ip in nic.ipConfig.ipAddress :                        
                            if ip.state == "preferred":
                                return_array.append(ip.ipAddress)
                except Exception as error:
                    print ("Unable to get nic object for: ", VMObject.guest.net)
                    print (error)                                    
        except Exception as error:
            print ("Unable to get Summary for VM object: " + self.vm_name)
            print (error)
        
        if len(return_array) == 0:
            return_array = self.getIPfromFile()
        
        try:
            if return_array is not None:       
                return return_array
        except Exception as error:
            raise error
        
    
    def shutdown(self,TimeOut=int(120),FORCE_SHUTDOWN=False):
        # This function will give a call to the OS via VMTools to shutdown.
        # This function has a default timeout of 60 Sec
        """
            Is there any value to sending a command like shutdown -h now here ? 
        """
        from time import sleep
        currenttry = 0
        try:
            if self.vm_object :
                if self.get_power_state():
                    if self.vm_object.summary.guest.toolsStatus == "toolsNotInstalled":
                        print ("Cannot complete operation because VMware Tools is not running in this virtual machine. Soft Shutdown Not possible")
                        if FORCE_SHUTDOWN :
                            print("Force Power off "+ self.vm_name)
                            if self.powerOff()():
                                 print(self.vm_name + " is now powered off.")
                                 return True
                        else:
                            print("Unable to Shutdown "+ self.vm_name + ".")
                            return False
                    else:
                        #print ("Shutting down " +self.vm_name)                
                        self.vm_object.ShutdownGuest()
                        while (self.get_power_state() and currenttry < TimeOut):                    
                            sleep(10)
                            currenttry = currenttry + 10
                        if self.get_power_state():
                            print ("[ERROR]"+self.vm_name+" is still running.")
                            if FORCE_SHUTDOWN :
                                print("Force Power off "+ self.vm_name)
                                if self.powerOff()():
                                    #print(self.vm_name + " is now powered off.")
                                    return True
                            else:
                                print("Unable to Shutdown "+ self.vm_name + ".")
                                return False
                        else:
                            #print (self.vm_name +" has been Shutdown")
                            return True
                else:                
                    #print (self.vm_name +" has been Shutdown")
                    return True
        except Exception as error:
            print ("Unable to get VM object for: "+self.vm_name)
            print (error)
            
        return False
            
    def powerOff(self):
        # This function will do a hard power-off of the vm.
        # This is big Hammer ..
        try:            
            if self.vm_object :
                if (self.get_power_state()):
                    print ("Powering off "+self.vm_name)                
                    WaitForTask(self.vm_object.PowerOff())
                if (self.get_power_state()):
                    print ("[ERROR] "+ self.vm_name +" is still running.")
                    return False
                else :
                    print (self.vm_name+" has been Powered-off")
                    return True
        except Exception as error:
            print ("Unable to get VM object for: ", vm_name)
            print (error)
        
        return False 
    
    def powerOn(self):
        #This will poweron the VM. This will return True / False
        try:            
            if self.vm_object :            
                if not self.get_power_state():
                    print ("Powering on "+ self.vm_name)                    
                    Power_ON_task=self.vm_object.PowerOn()
                    WaitForTask(Power_ON_task)
                    if (self.get_power_state() and self.waitForOS()):
                        print("Virtual Machine "+ self.vm_name + " is powered on.")
                        return True
                    else:
                        print("Virtual Machine "+ self.vm_name + " cannot be started.")
                        return False
                else:
                    print (self.vm_name + " already powered on.")            
        except Exception as error:
            print ("Unable to get VM object for: ", self.vm_name)
            print (error)
        return False
    
    def waitForOS(self,TIMEOUT=int(180)):
        # This will wait for 3 mins for the OS to Boot up
        from time import sleep
        import subprocess
        mytime=0
        print ("Checking if machine "+ self.vm_name + " is booted.\nTrying to connect "+ self.vm_internal_ip + ":22")
        try:
            p = subprocess.Popen(["/usr/bin/nc","-z",self.vm_internal_ip,"22"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            print ("Checking....")            
            out,err = p.communicate()
            pstatus = p.wait(30)
			#__DEBUG__
            #print("Mytime : " + str(mytime) + "\n\t out :" + out.decode("utf-8") + "\n\t err:" + err.decode("utf-8") + "\n\t process status :" + str(pstatus))
            sleep (30)
            mytime = mytime + 30
            while mytime <= TIMEOUT and (self.vm_internal_ip not in out.decode("utf-8") and "succeeded!" not in out.decode("utf-8") and pstatus !=0):                
                p = subprocess.Popen(["/usr/bin/nc","-z",self.vm_internal_ip,"22"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                print ("Checking....")
                out,err = p.communicate()
                pstatus = p.wait(5)
                sleep(5)
                mytime = mytime + 5
                #__DEBUG__
                #print("Mytime : " + str(mytime) + "\n\t out :" + out.decode("utf-8") + "\n\t err:" + err.decode("utf-8") + "\n\t process status :" + str(pstatus))
            
            if mytime <=TIMEOUT and (self.vm_internal_ip in out.decode("utf-8") and "succeeded!" in out.decode("utf-8") and pstatus ==0):
                print ("Virtual Machine "+ self.vm_name + " is now online.")
                return True
            else:
                print ("Unable to check if "+ self.vm_name + " is running.")
                return False
                        
        except Exception as error:
            print ("Unable to execute command.")
            print (error)
        return False
    
    def revert_VM_Snapshot(self):
        # This will revert the VM Snapshot. This will return True / False
        # This function will revert the machine to its last snapshot.
        try:            
            if self.vm_object :
                if (self.get_power_state()):
                    print ("\n" + self.vm_name+" is in running & needs to be Powered-off before any snapshot can be reverted.")
                    return False
                else:
                    print ("\n" + self.vm_name," is powered off & can be reverted to it's earlier snapshot.")
                    if not self.vm_object.snapshot:
                        print ("Virtual Machine "+self.vm_name+ " doesn't have a Snapshot.")
                        return None
                    else:
                        vm_snapshots = self.vm_object.snapshot.rootSnapshotList                
                        while vm_snapshots[0].childSnapshotList is not None:
                            # Recursively go to the latest Snapshot                    
                            if len(vm_snapshots[0].childSnapshotList) < 1:
                                break
                            vm_snapshots = vm_snapshots[0].childSnapshotList                    
                        print ("Reverting "+self.vm_name+" to Snapshot =>\nName\t\t: "+str(vm_snapshots[0].name)+"\nDescription\t: "+str(vm_snapshots[0].description)+"\n")
                        snapshot = vm_snapshots[0].snapshot
                        WaitForTask(snapshot.RevertToSnapshot_Task())
                        print ("Snapshot Revert Completed.\n")
                        return True
        except Exception as error:
            print ("Unable to get VM object for: ", self.vm_name)
            print (error)
        return None
    
    def reboot(self):
        # This will reboot the VM. This will return True / False

        from time import sleep
        try:
            if self.vm_object :
                if self.get_power_state():
                    if self.vm_object.summary.guest.toolsStatus == "toolsNotInstalled":
                        print ("VMware Tools is not running / Installed on "+ self.vm_name + " . Soft Reboot not possible.")
                        return False
                    else:
                        print ("Rebooting " +self.vm_name)
                        self.vm_object.RebootGuest()
                        sleep(30)
                        if (self.get_power_state() and self.waitForOS()):
                            print(self.vm_name + " is successfuly rebooted.")
                            return True                                            
                else:
                    print (self.vm_name +" is powered-Off.\nRestarting "+ self.vm_name)
                    if (self.get_power_state() and self.waitForOS()):
                        print("Virtual Machine "+ self.vm_name + " is now powered on.")
                        return True
                    else:
                        print("Unable to start "+ self.vm_name)
                        return False
        
        except Exception as error:            
            print (error)
            raise error
            
        return False
        
    
    def isAddressIPV4 (self):
        # This will return True if Address is IPV4 , False if its IPV6
        # Will validate a string & return true if its a valid IP address & false if its not.
        a = self.ip.split('.')
        if len(a) != 4:
            return False
        for x in a:
            if not x.isdigit():
                return False
            i = int(x)
            if i < 0 or i > 255:
                return False
        return True 
    
    def getOSType(self):
         # This will return OS Type for the VM
        try:
            if self.vm_object :
                if len(self.vm_object.summary.config.guestFullName) > 0:
                    return self.vm_object.summary.config.guestFullName
                else:
                    print ("Unable to get os Type for "+self.vm_name+"\n") 
                
        except Exception as error:
            print ("Unable to get VM object for: ", self.vm_name)
            print (error)
        return None
    
"""
    def __del__(self):
        #Destructor
        self.shutdown(FORCE_SHUTDOWN=True)
        self.base_fldr=None
        self.esxi_details=None
        self.esxi_json=None
        self.vm_name=None
        self.vm_details=None
        self.vm_object=None
        self.vm_ip=[]
        self.vm_internal_ip=None
        self.vm_ostype=None
        return None                                   
"""    

"""
if __name__ == "__main__":
    my_windowsVM = VCENTER("W2K8-Console","192.168.1.12")    
    my_windowsVM.powerOn()
    my_windowsVM.reboot()
    my_windowsVM.shutdown(120, True)
    my_windowsVM=None
"""