"""
There are n people standing in line to buy show tickets.Due to high demand, the venue sells tickets according to the following rules:

The person at the head of the line can buy exactly one ticket and must then exit the line.
if a person needs to purchase additional tickets,they must re-enter the end of the line and wait to be sold their next ticket(assume exit and re-entry takes zero seconds).
Each ticket sale takes exactly one second.
We express initial line of n people as an array, tickets = [tickets0, tickets1 ... ticketsN-1], where ticketsi denotes the number of tickets person i wishes to buy. 
If Jesse is standing at a position p in this line, find out how much time it would take for him to buy all tickets. Complete the waiting time function in the editor below. It has two parameters:

An array, tickets, of n positive integers describing initial sequence of people standing in line. Each ticketsi describes number of tickets that a person waiting at initial place.
An integer p, denoting Jesse's position in tickets.
"""
__author__ = 'Rohan Khale'
try:
    import sys
    import os
    import time
    import logging.config    
except ImportError as error:
    print (error)
    sys.exit(-1)

#a_ticket = [1,5,8,3,4]
a_ticket = [1,0,2,0,3,5,4,7]
p = 6

if os.path.exists(os.path.basename(__file__)+ ".log") and os.path.isfile(os.path.basename(__file__)+ ".log"):
    os.unlink(os.path.basename(__file__)+ ".log")
    
#logging.config.fileConfig("logging.conf",defaults={'logfilename': os.path.basename(__file__)+ ".log"})
logging.config.fileConfig(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),"resources","logging.conf"),defaults={'logfilename': os.path.basename(__file__)+ ".log"})
logger = logging.getLogger(__name__)

def gettime(a_array,p):
    a_result= []
    p_val = a_array[p-1]
    i_untiTime = 0
    while p_val >0:
        i_currVal = a_array[0]      
        a_array.pop(0)
        if (p - 1) == 0 :
            p_val = p_val - 1
            p = len(a_array)+1            
        else:
            p = p - 1
        a_result.append([p_val,p]) 
        if i_currVal >0:
            i_untiTime = i_untiTime + 1
            if i_currVal >1:
                a_array.append(i_currVal-1)            
    return (i_untiTime)

def gettime1(array, p):
    result = p
    for i in range(len(array)):        
        if i <= p-1:
            if array[i] > array[p-1]:
                result += array[p-1]-1
            else:
                result += array[i] - 1
        else:
            if array[i] > array[p-1]:
                result += array[p-1]-1
            else:
                result += array[i]
    return result
    

if __name__ == "__main__":    
    i_element = 0
    i_usr_loc = p
    i_usr_tick = a_ticket[p-1]
    logger.debug("Need to find the time required for Persion at location %s who wants to buy %s tickets",i_usr_loc,i_usr_tick)
    
    a_new_array = []
    a_new_array.extend(a_ticket)
    
    start_time = time.time()
    unitTime = gettime(a_new_array, p)
    time_req = time.time() - start_time
    logger.info("Time taken for Person who was %s in the Queue to buy %s tickets is %s",i_usr_loc,i_usr_tick,unitTime)
    logger.info("Time take to calculate with gettime :-- %s",time_req)
    
    a_new_array = []
    a_new_array.extend(a_ticket)
    start_time = time.time()
    unitTime = gettime1(a_new_array, p)
    time_req = time.time() - start_time
    logger.info("Time taken for Person who was %s in the Queue to buy %s tickets is %s",i_usr_loc,i_usr_tick,unitTime)
    logger.info("Time take to calculate with gettime1 :-- %s",time_req)