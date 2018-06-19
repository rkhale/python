"""
    Sort an array of 1's & 0 
"""
__author__ = 'Rohan Khale'
try:
    import sys
    import os
    import time
    import logging.config
    import random
except ImportError as error:
    print (error)
    sys.exit(-1)


if os.path.exists(os.path.basename(__file__)+ ".log") and os.path.isfile(os.path.basename(__file__)+ ".log"):
    os.unlink(os.path.basename(__file__)+ ".log")
    
#logging.config.fileConfig("logging.conf",defaults={'logfilename': os.path.basename(__file__)+ ".log"})
logging.config.fileConfig(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),"resources","logging.conf"),defaults={'logfilename': os.path.basename(__file__)+ ".log"})
logger = logging.getLogger(__name__)


def sort_While (a_to_be_Sorted):
    i = 0
    i_len_arry = len(a_to_be_Sorted)
    startTime = time.time()       
    while i < i_len_arry:
        if a_to_be_Sorted[i] == 0 and i > 0:
            a_to_be_Sorted.pop(i)
            a_to_be_Sorted.insert(0,0)
        i = i + 1
    time_taken = time.time() - startTime
    logger.debug("Sorted Array :-- %s",a_to_be_Sorted)
    logger.info("Time taken to sort %s length Array with While loop is :-- %s sec.",len(a_to_be_Sorted),time_taken)    


def sort_For (a_to_be_Sorted):
    startTime = time.time()
    for i in range (len(a_to_be_Sorted)):
        if a_to_be_Sorted[i] == 0 and i > 0:
            a_to_be_Sorted.pop(i)
            a_to_be_Sorted.insert(0,0)        
    time_taken = time.time() - startTime
    logger.debug("Sorted Array :-- %s",a_to_be_Sorted)
    logger.info("Time taken to sort %s length Array with For loop is :-- %s sec.",len(a_to_be_Sorted),time_taken)
    
    
def sort_default(a_to_be_Sorted):    
    startTime = time.time()
    for i in range (len(a_to_be_Sorted)-1):
        for j in range(i+1 , len(a_to_be_Sorted)):
            if a_to_be_Sorted[i] > a_to_be_Sorted[j] : 
                a_to_be_Sorted[j] = a_to_be_Sorted[i] + a_to_be_Sorted[j]
                a_to_be_Sorted[i] = a_to_be_Sorted[j] - a_to_be_Sorted[i]
    time_taken = time.time() - startTime
    logger.debug("Sorted Array :-- %s",a_to_be_Sorted)
    logger.info("Time taken to sort %s length Array with n^2 loop is :-- %s sec.",len(a_to_be_Sorted),time_taken)
    
    
if __name__ == "__main__":    
    try:
        a_org = [random.randint(0,1) for _ in range(10000)]
        
        a_to_be_Sorted = []
        a_to_be_Sorted.extend(a_org)
        logger.debug("The Array to be sorted :-- %s",a_to_be_Sorted)        
        sort_While(a_to_be_Sorted)        
        
        a_to_be_Sorted = []
        a_to_be_Sorted.extend(a_org)
        logger.debug("The Array to be sorted :-- %s",a_to_be_Sorted)
        sort_For(a_to_be_Sorted)
        
        a_to_be_Sorted = []
        a_to_be_Sorted.extend(a_org)
        logger.debug("The Array to be sorted :-- %s",a_to_be_Sorted)
        sort_default(a_to_be_Sorted)
        
    except Exception as e:
        print (e)
        raise Exception