"""
    A man has infinite number of coins & wants all solutions to the sum of it
    e.g. a_coins[1,2,5,10] & wants to give change for 17
"""
__author__ = 'Rohan Khale'
try:
    import sys
    import os
    import itertools
    import logging.config
    
except ImportError as error:
    print (error)
    sys.exit(-1)

a_coins = [1,2,5,10]
i_expectedSum = 17
if os.path.exists(os.path.basename(__file__)+ ".log") and os.path.isfile(os.path.basename(__file__)+ ".log"):
    os.unlink(os.path.basename(__file__)+ ".log")
    
#logging.config.fileConfig("logging.conf",defaults={'logfilename': os.path.basename(__file__)+ ".log"})
logging.config.fileConfig(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),"resources","logging.conf"),defaults={'logfilename': os.path.basename(__file__)+ ".log"})
logger = logging.getLogger(__name__)

def getCombinations (SET,COUNT):
    try:
        return (itertools.combinations_with_replacement(SET,COUNT))
    except Exception:
        print (Exception)
        raise Exception

def areSame(a,b):
    try:
        a_set = set(a)
        b_set = set(b)
        if a_set == b_set and len(a) == len(b):
            return True
        else:
            return False
    except Exception:
        print (Exception)
        raise Exception
    
def getmincount (SET,SUM,COUNT=0):
    try:
        result = SUM - max(SET)
        if result == 0:
            COUNT = COUNT + 1
            return COUNT
        else:
            if result > max(SET):
                COUNT = COUNT + 1
                return getmincount(SET, result, COUNT)
            else:
                if result < 0:
                    SET.remove(max(SET))                
                    return getmincount(SET, SUM, COUNT)
                else:
                    COUNT = COUNT + 1
                    return getmincount(SET, result, COUNT)
    except Exception:
        print (Exception)
        raise Exception

def getMaxCount (SET,SUM,COUNT=0):
    try:
        result = SUM - min(SET)
        if result == 0:
            COUNT = COUNT + 1
            return COUNT
        elif result > 0:
            COUNT = COUNT + 1
            return getMaxCount(SET, result, COUNT)
        else:
            return COUNT
    except Exception:
        print (Exception)
        raise Exception 

if __name__ == "__main__":
    try:
        logger.info("#"*100)
        a_all_subset = []
        a_final_subset = []
        a_result = []
        a_coins1 = []
        a_coins1.extend(a_coins)
        min_count = getmincount(a_coins1, i_expectedSum, 0)
        logger.info("Coins we have : %s",a_coins)
        logger.info("Min number of coins that can be given is %s",min_count)
        a_coins1 = []
        a_coins1.extend(a_coins)
        max_count = getMaxCount(a_coins1, i_expectedSum, 0)
        logger.info("Max number of coins that can be given is %s",max_count)
            
        for i in range (min_count,max_count+1):
            for subset in getCombinations(a_coins,i):
                if sum(subset) == i_expectedSum:   
                    a_all_subset.append(subset)
        
        logger.info("="*100)
        logger.info("Length of a_all_subset : %s",len(a_all_subset))
        logger.info("-"*100)
                
        for subset in a_all_subset:
            for subset1 in a_all_subset:
                if subset != subset1:
                    if areSame(subset, subset):
                        break
            a_final_subset.append(subset)
        
        logger.info("Result :\n")
        for a in a_final_subset:
            logger.info(a)
        logger.info("="*100)
        logger.info("Total Number of correct solutions are: %s" ,len(a_final_subset))
        logger.info("-"*100)
        logger.info("#"*100)
    except Exception:
        print (Exception)
        exit (1)