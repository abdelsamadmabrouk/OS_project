


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
#
def FCFS(ready_queue):
    index = 0                           # points to the currently running process

    while index < len(ready_queue):     # len() is re-evaluated every iteration,
                                        # so dynamically added processes are seen
        current = ready_queue[index]

        while current[1] > 0:          # run until burst time hits 0
            current[1] -= 1
            yield current[0]           # yield the process name for this time unit

        index += 1                     # move to the next process in arrival order


# ─────────────────────────────────────────────────────────────────────────────
#  Round Robin  (Preemptive with fixed quantum)
# ─────────────────────────────────────────────────────────────────────────────
#
#  ready_queue : list of [process_name, burst_time]
#  quantum     : int – number of time units each process gets per turn
#
#  The internal round-robin queue is rebuilt from ready_queue on every new
#  cycle so that processes added dynamically are included in the next round.
#
def round_robin(ready_queue, quantum):
    # rr_queue holds references to the same sublists that are in ready_queue,
    # so external burst-time updates are reflected here automatically.
    rr_queue = list(ready_queue)       # snapshot of arrival order for first round
    seen     = set(id(p) for p in rr_queue)   # track which processes we've queued

    while rr_queue:

        # ── pick up any newly arrived processes ──────────────────────────────
        for process in ready_queue:
            if id(process) not in seen:
                rr_queue.append(process)
                seen.add(id(process))

        current = rr_queue.pop(0)      # take the next process in the rr queue

        if current[1] <= 0:            # already finished (shouldn't normally happen)
            continue

        # ── give the process up to `quantum` time units ──────────────────────
        time_slice = min(quantum, current[1])

        for _ in range(time_slice):
            current[1] -= 1
            yield current[0]

            # ── check for new arrivals even mid-slice ────────────────────────
            for process in ready_queue:
                if id(process) not in seen:
                    rr_queue.append(process)
                    seen.add(id(process))

        # ── if the process still has work left, re-queue it at the back ──────
        if current[1] > 0:
            rr_queue.append(current)

   