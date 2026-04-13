
class Process:
   
  def __init__(self, pid, burst_time, priority=None):
      
    self.pid = pid
    self.burst_time = burst_time
    self.remaining_time = burst_time
    self.priority = priority
    self.waiting_time = 0
  

def _update_waiting_time(current_process, ready_queue):
  for process in ready_queue:
    if not (process is current_process):
      process.waiting_time += 1

# -------------Preemptive Shortest Job First Scheduler -----------------  
def preemptive_SJF(ready_queue):
    
    while len(ready_queue) > 0:
      shortest_job = min(ready_queue, key=lambda process: process.remaining_time)
      shortest_job.remaining_time -= 1
      
      # modifying waiting time
      _update_waiting_time(shortest_job, ready_queue)

      yield shortest_job
      
      if shortest_job.remaining_time == 0:
        ready_queue.remove(shortest_job)
        
# -------------Shortest Job First Scheduler -----------------        
def SJF(ready_queue):
   while len(ready_queue) > 0:
      shortest_job = min(ready_queue, key=lambda process: process.remaining_time)

      while shortest_job.remaining_time > 0: 
        shortest_job.remaining_time -= 1
        _update_waiting_time(shortest_job, ready_queue)

        yield shortest_job
      
      ready_queue.remove(shortest_job)
       
# -------------Preepmtive Priority Scheduler -----------------
def preemptive_Priority(ready_queue):
    
    while len(ready_queue) > 0:
      Priority_job = max(ready_queue, key=lambda process: process.priority)
      Priority_job.remaining_time -= 1

      _update_waiting_time(Priority_job, ready_queue)

      yield Priority_job
      
      if Priority_job.remaining_time == 0:
        ready_queue.remove(Priority_job)

# -------------non-preemptive Priority Scheduler -----------------
def Non_preemptive_Priority(ready_queue):
    
    while len(ready_queue) > 0:
      Priority_job = max(ready_queue, key=lambda process: process.priority)
      
      while(Priority_job.remaining_time > 0):
        Priority_job.remaining_time -= 1

        _update_waiting_time(Priority_job, ready_queue)

        yield Priority_job

        if Priority_job.remaining_time == 0:
          ready_queue.remove(Priority_job)


# ─────────────────────────────────────────────────────────────────────────────
#  FCFS  –  First Come First Served  (Non-Preemptive)
# ─────────────────────────────────────────────────────────────────────────────
#
#  ready_queue : list of Process Objects
#
#  Processes are served strictly in queue order.
#  New processes appended to ready_queue while the generator is running will
#  be picked up automatically once earlier processes finish.

def FCFS(ready_queue):
    while ready_queue:
        p = ready_queue[0]             # oldest arrived = front of list
        while p.remaining_time > 0:
            p.remaining_time -= 1

            _update_waiting_time(p, ready_queue)

            yield p
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
        if current.remaining_time <= 0:
            continue

        time_slice = min(quantum, current.remaining_time)
        for _ in range(time_slice):
            current.remaining_time -= 1
            _update_waiting_time(current, ready_queue)
            yield current
            # Check for mid-slice arrivals
            for p in ready_queue:
                if id(p) not in seen:
                    rr_queue.append(p)
                    seen.add(id(p))

        if current.remaining_time > 0:
            rr_queue.append(current)       # not done → back of queue
        else:
            ready_queue.remove(current)    # done → remove from ready_queue ←

