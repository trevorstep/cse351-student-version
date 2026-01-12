""" 
Course: CSE 351
Lesson: L01 Team Activity
File:   team.py
Author: Trevor Stephenson
Purpose: Find prime numbers

Instructions:

- Don't include any other Python packages or modules
- Review and follow the team activity instructions (team.md)

TODO 1) Get this program running.  Get cse351 package installed -Done
TODO 2) move the following for loop into 1 thread
TODO 3) change the program to divide the for loop into 10 threads
TODO 4) change range_count to 100007.  Does your program still work?  Can you fix it?
Question: if the number of threads and range_count was random, would your program work?
"""

from datetime import datetime, timedelta
import threading
import random

# Include cse 351 common Python files
from cse351 import *

# Global variable for counting the number of primes found
prime_count = 0
numbers_processed = 0

def is_prime(n):

    if n <= 3:
        return n > 1
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i ** 2 <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def prime_worker(start_value, end_value):
    global numbers_processed
    global prime_count
    


    for i in range(start_value, end_value):
        numbers_processed += 1
        if is_prime(i):
            prime_count += 1
            # print(i, end=', ', flush=True)
    # print(flush=True)



def main():
    global prime_count          
    global numbers_processed      
    start = 10000000000
    range_count = 100000
    num_threads = 10
    slice_size = range_count // num_threads

    threads = []

    log = Log(show_terminal=True)
    log.start_timer()
 

    for i in range(10):
        start_i = start + (i * slice_size)
        end_i   = start + ((i+1) * slice_size)
        t = threading.Thread(target=prime_worker, args=(start_i, end_i))
        threads.append(t)

    for i in range(10):
        threads[i].start()
        
    for i in range(10):
        threads[i].join()

    
    # Should find 4306 primes
    log.write(f'Numbers processed = {numbers_processed}')
    log.write(f'Primes found      = {prime_count}')
    log.stop_timer('Total time')


if __name__ == '__main__':
    main()
