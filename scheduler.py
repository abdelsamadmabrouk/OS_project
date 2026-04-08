


def preemptive_SJF(ready_queue):
    
    while len(ready_queue) > 0:
      shortest_job = min(ready_queue, key=lambda process: process[1])
      shortest_job[1] -= 1
      yield shortest_job[0]
      
      if shortest_job[1] == 0:
        ready_queue.remove(shortest_job)
        
        
def SJF(ready_queue):
   while len(ready_queue) > 0:
      shortest_job = min(ready_queue, key=lambda process: process[1])

      while shortest_job[1] > 0: 
        shortest_job[1] -= 1
        yield shortest_job[0]
      
      ready_queue.remove(shortest_job)
   