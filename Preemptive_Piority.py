def preemptive_Priority(ready_queue):
    
    while len(ready_queue) > 0:
      Priority_job = max(ready_queue, key=lambda process: process[2])
      Priority_job[1] -= 1
      yield Priority_job[0]
      
      if Priority_job[1] == 0:
        ready_queue.remove(Priority_job)
        
        
queue = [['P0', 4, 2], ['P1', 3, 1]]

clock = 1
process = preemptive_Priority(queue)
current_process = next(process, None)


while current_process != None:
    print(current_process, clock)
    clock += 1

    if clock == 3:
       queue.append(['P3', 1, 3])

    current_process = next(process, None)