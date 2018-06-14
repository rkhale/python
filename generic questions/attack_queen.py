"""
N-Queens Problem: Given a chess board having  cells, we need to place  queens in such a way that no queen is attacked by any other queen. A queen can attack horizontally, vertically and diagonally.

So initially we are having  unattacked cells where we need to place  queens. Let's place the first queen at a cell , so now the number of unattacked cells is reduced, and number of queens to be placed is . Place the next queen at some unattacked cell. This again reduces the number of unattacked cells and number of queens to be placed becomes . Continue doing this, as long as following conditions hold.

The number of unattacked cells is not .
The number of queens to be placed is not .
"""
__author__ = 'Rohan Khale'
try:
    import sys
    import os
    import time
    import logging.config
    import pprint    
except ImportError as error:
    print (error)
    sys.exit(-1)


if os.path.exists(os.path.basename(__file__)+ ".log") and os.path.isfile(os.path.basename(__file__)+ ".log"):
    os.unlink(os.path.basename(__file__)+ ".log")
    
#logging.config.fileConfig("logging.conf",defaults={'logfilename': os.path.basename(__file__)+ ".log"})
logging.config.fileConfig(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),"resources","logging.conf"),defaults={'logfilename': os.path.basename(__file__)+ ".log"})
logger = logging.getLogger(__name__)
start_time = time.time()
def is_attacked (x,y,BOARD):
    try:
        # Check if any value in the xth array is 1 #row        
        if 1 in BOARD[x]:
            return True            
        # check if any value of the yth element in all arrays is 1 # colom
        for i in range(len(BOARD)):
            for j in range(len(BOARD[i])):
                if 1 == BOARD[i][y]:
                    return True        
        # diagonals 
        # if x+y = i+j & the value of BOARD[i][j] == 1 then its attacked
        # if x-y = i-j  & the value of BOARD[i][j] == 1 then its attacked
        for i in range(len(BOARD)):
            for j in range(len(BOARD[i])):
                if x+y == i+j and BOARD[i][j] == 1:
                    return True
                if x-y == i-j and BOARD[i][j] == 1:
                    return True
        return False        
    except Exception:
        print (Exception)
        raise Exception

if __name__ == "__main__":
    try:
        max_num = int(sys.argv[1])    
    except ValueError:        
        logger.error("%s is not an Integer but %s. Please provide an integer till which all prime Numbers needs to be printed.",sys.argv[1],type(sys.argv[1]))
        exit (1)
    logger.info("The size of the board is %sx%s",max_num,max_num)    
    board = [[0 for x in range(max_num)] for y in range(max_num)]
    solutions = []    
    num_queens , total_sol = 0,0
    for a in range(len(board)):
        for b in range(len(board[a])):
            board[a][b] = 1
            num_queens = num_queens + 1
            for i in range(len(board)):
                for j in range(len(board[i])):
                    if not is_attacked(i, j, board):
                        board[i][j] = 1
                        num_queens = num_queens + 1 
            logger.info("#"*100)
            logger.info("Max Number of Queens that can be placed on a %sx%s board are %s",max_num,max_num,num_queens)
            logger.info(pprint.pformat(board))
            logger.info("#"*100)
            if board not in solutions:
                solutions.append(board)
                total_sol = total_sol + 1
            board = [[0 for x in range(max_num)] for y in range(max_num)]            
            num_queens = 0
    logger.info("Max Number of Queens that can be placed on a %sx%s board are %s",max_num,max_num,total_sol)    
    logger.info("Total Solutions is %s",len(solutions))
    logger.info(pprint.pformat(solutions))
    logger.info("Time taken to calculate is %s sec",time.time() - start_time)
    