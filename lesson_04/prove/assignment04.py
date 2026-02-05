"""
Course    : CSE 351
Assignment: 04
Student   : <your name here>

Instructions:
    - review instructions in the course

In order to retrieve a weather record from the server, Use the URL:

f'{TOP_API_URL}/record/{name}/{recno}

where:

name: name of the city
recno: record number starting from 0

"""

import time
from common import *
import queue
from threading import *
from cse351 import *

THREADS = 10                
WORKERS = 10
RECORDS_TO_RETRIEVE = 5000  # Don't change


# ---------------------------------------------------------------------------
def retrieve_weather_data(command_queue, data_queue):
    while True:
        item = command_queue.get()
        if item is None:
            command_queue.task_done()
            break

        city, record_num = item
        data = get_data_from_server(f'{TOP_API_URL}/record/{city}/{record_num}')
        city_name = data['city']
        date = data['date']
        temp = data['temp']

        data_queue.put((city_name, date, temp))
        command_queue.task_done()
     


# ---------------------------------------------------------------------------
class WORKER(Thread):
    def __init__(self, data_queue, noaa, semaphore, lock):
        Thread.__init__(self)
        self.data_queue = data_queue
        self.noaa = noaa
        self.semaphore = semaphore
        self.lock = lock

    def run(self):
        while True:
            item = self.data_queue.get()
            if item is None:
                self.data_queue.task_done()
                break

            city_name = item[0]
            date = item[1]
            temp = item[2]

            self.semaphore.acquire()
            try:
                with self.lock:
                    if city_name not in self.noaa.city_temps:
                        self.noaa.city_temps[city_name] = []
                    self.noaa.city_temps[city_name].append(temp)
            finally:
                self.semaphore.release()
            self.data_queue.task_done()


# ---------------------------------------------------------------------------
class NOAA:

    def __init__(self):
        self.city_temps = {}

    def get_temp_details(self, city):      
        if city not in self.city_temps or len(self.city_temps[city]) == 0:
            return 0.0
    
        temps = self.city_temps[city]
        avg = sum(temps) / len(temps)
        return avg



# ---------------------------------------------------------------------------
def verify_noaa_results(noaa):

    answers = {
        'sandiego': 14.5004,
        'philadelphia': 14.865,
        'san_antonio': 14.638,
        'san_jose': 14.5756,
        'new_york': 14.6472,
        'houston': 14.591,
        'dallas': 14.835,
        'chicago': 14.6584,
        'los_angeles': 15.2346,
        'phoenix': 12.4404,
    }

    print()
    print('NOAA Results: Verifying Results')
    print('===================================')
    for name in CITIES:
        answer = answers[name]
        avg = noaa.get_temp_details(name)

        if abs(avg - answer) > 0.00001:
            msg = f'FAILED  Expected {answer}'
        else:
            msg = f'PASSED'
        print(f'{name:>15}: {avg:<10} {msg}')
    print('===================================')


# ---------------------------------------------------------------------------
def main():

    log = Log(show_terminal=True, filename_log='assignment.log')
    log.start_timer()

    noaa = NOAA()

    # Start server
    data = get_data_from_server(f'{TOP_API_URL}/start')

    # Get all cities number of records
    print('Retrieving city details')
    city_details = {}
    name = 'City'
    print(f'{name:>15}: Records')
    print('===================================')
    for name in CITIES:
        city_details[name] = get_data_from_server(f'{TOP_API_URL}/city/{name}')
        print(f'{name:>15}: Records = {city_details[name]['records']:,}')
    print('===================================')

    records = RECORDS_TO_RETRIEVE

    # TODO - Create any queues, pipes, locks, barriers you need
    
    
    command_queue = queue.Queue()
    data_queue = queue.Queue()

    semaphore = Semaphore(3)
    lock = Lock()

    worker_threads = []
    for i in range(WORKERS):
        wt = WORKER(data_queue, noaa, semaphore, lock)
        wt.start()
        worker_threads.append(wt)

    threads = []
    for i in range(THREADS):
        t = Thread(target=retrieve_weather_data, args=(command_queue, data_queue))
        t.start()
        threads.append(t)

    records_per_city = RECORDS_TO_RETRIEVE // len(CITIES)
    for city_name in CITIES:
        for record_num in range(records_per_city):
            command_queue.put((city_name, record_num))

    command_queue.join()

    for i in range(THREADS):
        command_queue.put(None)

    for t in threads:
        t.join()

    data_queue.join()

    for i in range(WORKERS):
        data_queue.put(None)

    for wt in worker_threads:
        wt.join()



    # End server - don't change below
    data = get_data_from_server(f'{TOP_API_URL}/end')
    print(data)

    verify_noaa_results(noaa)

    log.stop_timer('Run time: ')


if __name__ == '__main__':
    main()

