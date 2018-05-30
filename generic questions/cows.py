"""
    A man as 16 cows each gives milk [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16] lts each. The man has 4 sons.
    1. The man wants to give each of his sons 4 cows each such that each son has equal lts of milk.
    2. The man wants to give his sons cow(s) such that they have equal lts of milk , irrespective of the number of cows they have.
"""

__author__ = 'Rohan Khale'
try:
    import sys
    import os
    import itertools
    import pprint
    import logging.config
except ImportError as error:
    print (error)
    sys.exit(-1)

a_cow = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]

if os.path.exists(os.path.basename(__file__)+ ".log") and os.path.isfile(os.path.basename(__file__)+ ".log"):
    os.unlink(os.path.basename(__file__)+ ".log")
    
#logging.config.fileConfig("logging.conf",defaults={'logfilename': os.path.basename(__file__)+ ".log"})
logging.config.fileConfig(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),"resources","logging.conf"),defaults={'logfilename': os.path.basename(__file__)+ ".log"})
logger = logging.getLogger(__name__)
    
def getCombinations (SET,OF_LENGTH=0):
    try:
        if OF_LENGTH == 0:            
            return itertools.chain(*map(lambda x: itertools.combinations(SET, x), range(0, len(SET)+1)))
        else:
            return (itertools.combinations(SET,OF_LENGTH))
    except Exception:
        print (Exception)
        raise Exception


def eliminateIncorrect(aa_array):
    try:                
        for a_array in aa_array:
            # This will get the sum of each array within the aa_array
            for a_array1 in aa_array:
                if a_array != a_array1:
                    b_isCommon = isCommon(a_array,a_array1)
                    if b_isCommon:
                        return None
        return (aa_array)
    except Exception:
        print (Exception)
        raise Exception    

def isCommon(a,b):
    a_set = set(a)
    b_set = set(b)
    if len(a_set.intersection(b_set)) > 0:
        return(True) 
    return(False) 


if __name__ == "__main__":
    try:
        logger.info("#"*100)
        a_all_subset = []
        a_final_subset = []
        a_result = []
        best_sol = sum(a_cow)/4
        for subset in getCombinations(a_cow,4):
            if sum(subset) == best_sol:              
                a_all_subset.append(subset)
        logger.debug("="*100)
        logger.debug("Length of a_all_subset : %s",len(a_all_subset))
        logger.debug("-"*100)
        
        for subset in getCombinations(a_all_subset,4):       
            correct_obj = eliminateIncorrect(subset)            
            if correct_obj:                
                a_final_subset.append(subset)
        
        logger.info("Equal Number of cows + Equal ltrs of Milk.")
        logger.info("-"*100)
        logger.info("Result :\n%s",pprint.pformat(a_final_subset))
        logger.info("-"*100)
        logger.info("Total Number of correct solutions are: %s" ,len(a_final_subset))
        logger.info("="*100)
        logger.info("#"*100)        
                
        a_all_subset = []
        a_final_subset = []
        a_result = []
        best_sol = sum(a_cow)/4
        for subset in getCombinations(a_cow):
            if sum(subset) == best_sol:     
                a_all_subset.append(subset)        
        logger.debug("="*100)
        logger.debug("Length of a_all_subset : %s",len(a_all_subset))
        logger.debug("-"*100)
        
        for subset in getCombinations(a_all_subset,4):            
            correct_obj = eliminateIncorrect(subset)
            if correct_obj:                
                a_final_subset.append(subset)
        
        logger.info("Equal Milk only" ,len(a_final_subset))
        logger.info("-"*100)
        logger.info("Result :\n%s",pprint.pformat(a_final_subset))
        logger.info("-"*100)
        logger.info("Total Number of correct solutions are: %s" ,len(a_final_subset))
        logger.info("="*100)
        logger.info("#"*100)        
    except Exception:
        print (Exception)
        exit (1)