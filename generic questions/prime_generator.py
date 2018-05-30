__author__ = 'Rohan Khale'
try:
    import sys
    import os    
    import logging.config
    
except ImportError as error:
    print (error)
    sys.exit(-1)

if os.path.exists(os.path.basename(__file__)+ ".log") and os.path.isfile(os.path.basename(__file__)+ ".log"):
    os.unlink(os.path.basename(__file__)+ ".log")
    
logging.config.fileConfig(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),"resources","logging.conf"),defaults={'logfilename': os.path.basename(__file__)+ ".log"})
logger = logging.getLogger(__name__)

def prime_generator():
    p = 2
    not_prime = False
    while True:
        if p == 2 :
            yield p            
        else:            
            for i in range (2,p-1):
                if p % i == 0 :
                    not_prime = True
                    break
            if not not_prime:
                yield p
        not_prime = False
        p=p+1
                
        

if __name__ == "__main__":
    try:
        max_num = int(sys.argv[1])    
    except ValueError:        
        logger.error("%s is not an Integer but %s. Please provide an integer till which all prime Numbers needs to be printed.",sys.argv[1],type(sys.argv[1]))
        exit (1)
    for prime in prime_generator():        
        if prime > max_num :
            break
        logger.info(prime)