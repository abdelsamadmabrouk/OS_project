


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
       
# -------------Priority Scheduler -----------------
def preemptive_Priority(ready_queue):
    
    while len(ready_queue) > 0:
      Priority_job = max(ready_queue, key=lambda process: process[2])
      Priority_job[1] -= 1
      yield Priority_job[0]
      
      if Priority_job[1] == 0:
        ready_queue.remove(Priority_job)

def Non_preemptive_Priority(ready_queue):
    
    while len(ready_queue) > 0:
      Priority_job = max(ready_queue, key=lambda process: process[2])
      
      while(Priority_job[1] > 0):
        Priority_job[1] -= 1
        yield Priority_job[0]
        if Priority_job[1] == 0:
          ready_queue.remove(Priority_job)


# ─────────────────────────────────────────────────────────────────────────────
#  FCFS  –  First Come First Served  (Non-Preemptive)
# ─────────────────────────────────────────────────────────────────────────────
#
#  ready_queue : list of [process_name, burst_time]
#                e.g.  [["P1", 5], ["P2", 3], ["P3", 8]]
#
#  Processes are served strictly in queue order.
#  New processes appended to ready_queue while the generator is running will
#  be picked up automatically once earlier processes finish.

def FCFS(ready_queue):
    while ready_queue:
        p = ready_queue[0]             # oldest arrived = front of list
        while p['remaining'] > 0:
            p['remaining'] -= 1
            yield p['name']
        ready_queue.remove(p)          # ← remove when done


# ─────────────────────────────────────────────────────────────────────────────
#  Round Robin  (Preemptive with fixed quantum)
# ─────────────────────────────────────────────────────────────────────────────
def round_robin(ready_queue, quantum):
    rr_queue = list(ready_queue)
    seen     = {id(p) for p in rr_queue}

    while rr_queue:
        # Enqueue any newly arrived processes (added to ready_queue by App)
        for p in ready_queue:
            if id(p) not in seen:
                rr_queue.append(p)
                seen.add(id(p))

        current = rr_queue.pop(0)
        if current['remaining'] <= 0:
            continue

        time_slice = min(quantum, current['remaining'])
        for _ in range(time_slice):
            current['remaining'] -= 1
            yield current['name']
            # Check for mid-slice arrivals
            for p in ready_queue:
                if id(p) not in seen:
                    rr_queue.append(p)
                    seen.add(id(p))

        if current['remaining'] > 0:
            rr_queue.append(current)       # not done → back of queue
        else:
            ready_queue.remove(current)    # done → remove from ready_queue ←


   
