

import threading
from queue import Queue


def runScenario(scenario):
    # Do a bunch of stuff
    with lock:
        # access global variables
        pass
    pass


def logStudyData():
    # Combine results from all scenarios into a df and write to csv
    pass


def worker():
    global q
    while True:
        next_scenario = q.get()
        if next_scenario is None:
            break
        runScenario(next_scenario)
        q.task_done()



global q, lock
q = Queue()
threads = []
scenario_list = ['s1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9', 's10', 's11', 's12']
num_worker_threads = 6
lock = threading.Lock()

for i in range(num_worker_threads):
    print("Thread number ", i)
    this_thread = threading.Thread(target=worker)
    this_thread.start()
    threads.append(this_thread)
for scenario_name in scenario_list:
    q.put(scenario_name)
q.join()
print("q.join completed")
logStudyData()
print("script complete")