
from __future__ import annotations

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QMessageBox
from models import Process
from schedulers import fcfs, sjf, priority_sched, round_robin
from gantt_chart import build_gantt_widget

RR_QUANTUM: int = 2


# ══════════════════════════════════════════════════════════════════════════════
class SchedulerController:
    """
    Wires all event handlers and drives the simulation loop.

    Usage (in your MainWindow.__init__ after setupUi):
        self.controller = SchedulerController(self)
    """
    all_processes: list[Process]
    ready_queue:   list[Process]
    current_process: Process | None
    current_time:  int
    gantt_data:    list[list]      # [[pid, start, end], ...]
    _timer:          QTimer
    _live_mode:      bool          # True  → user may add processes mid-run
    _rr_counter:     dict          # pid → ticks used in current RR slice
    _gantt_widget:   object | None # last widget inserted into gantt_layout

    def __init__(self, window) -> None:
        self.window = window
        self.all_processes    = []
        self.ready_queue      = []
        self.current_process  = None
        self.current_time     = 0
        self.gantt_data       = []
        self._rr_counter      = {}
        self._gantt_widget    = None
        self._live_mode       = False
        self._timer = QTimer()
        self._timer.setInterval(1000) 
        self._timer.timeout.connect(self._tick)

        window.add_btn.clicked.connect(self._on_add_process)#حسب مسميات محمد 
        window.start_live_btn.clicked.connect(self._on_start_live)
        window.run_static_btn.clicked.connect(self._on_run_static) 
        window.stop_btn.clicked.connect(self._on_stop)


    def _on_add_process(self) -> None:
        w = self.window #
        try:
            pid      = w.pid_input.text().strip() # دي محتاجة تتغير لما نشوف كود محمد 
            arrival  = int(w.arrival_input.text().strip())
            burst    = int(w.burst_input.text().strip())
            priority = int(w.priority_input.text().strip())
        except ValueError:
            QMessageBox.warning(w, "Input Error",
                                "Arrival, Burst, and Priority must be integers.")
            return

        if not pid:
            QMessageBox.warning(w, "Input Error", "Process ID cannot be empty.")
            return

        if any(p.pid == pid for p in self.all_processes):
            QMessageBox.warning(w, "Duplicate PID",
                                f"A process with PID '{pid}' already exists.")
            return

        proc = Process(
            pid            = pid,
            arrival_time   = arrival,
            burst_time     = burst,
            priority       = priority,
            remaining_time = burst,
            completion_time= 0,
            waiting_time   = 0,
            turnaround_time= 0,
        )
        self.all_processes.append(proc)

        if self._timer.isActive() and proc.arrival_time <= self.current_time:
            self.ready_queue.append(proc)

        self._update_process_table()
        self._clear_inputs()

    def _on_start_live(self) -> None:
        self._live_mode = True
        self._start_simulation()

    def _on_run_static(self) -> None:
    
        self._live_mode = False
        self._start_simulation()

    def _on_stop(self) -> None:
        self._timer.stop()
        self.window.add_btn.setEnabled(True) # على حسب كود محمد
        self.window.start_live_btn.setEnabled(True)
        self.window.run_static_btn.setEnabled(True)

    # ══════════════════════════════════════════════════════════════════════════
    # SIMULATION CORE
    # ══════════════════════════════════════════════════════════════════════════

    def _start_simulation(self) -> None:
        """Shared setup for both live and static runs."""
        if not self.all_processes:
            QMessageBox.information(self.window, "No Processes", "Please add at least one process first.")
            return

        # Reset state
        self.current_time = 0
        self.current_process = None
        self.gantt_data = []
        self.ready_queue = []

        # Reset processes
        for p in self.all_processes:
            p.remaining_time = p.burst_time
            p.completion_time = 0
            p.waiting_time = 0
       
        
        for p in self.all_processes:
            if p.arrival_time == 0:
                self.ready_queue.append(p)

       
        algo = self.window.algo_combo.currentText()
        
        # على حسب كود محمد
        if algo == "FCFS":
            self.scheduler_gen = FCFS(self.ready_queue)
        elif "SJF (Preemptive)" in algo:
            self.scheduler_gen = preemptive_SJF(self.ready_queue)
        elif "SJF (Non-Preemptive)" in algo:
            self.scheduler_gen = SJF(self.ready_queue)
        elif "Priority (Preemptive)" in algo:
            self.scheduler_gen = preemptive_Priority(self.ready_queue)
        elif "Priority (Non-Preemptive)" in algo:
            self.scheduler_gen = Non_preemptive_Priority(self.ready_queue)
        elif algo == "Round Robin":
            quantum = self.window.p_quantum.value()
            self.scheduler_gen = round_robin(self.ready_queue, quantum)

        self.window.add_btn.setEnabled(self._live_mode)
        self.window.start_live_btn.setEnabled(False)
        self.window.run_existing_btn.setEnabled(False)

        self._timer.start()

    def _tick(self) -> None:
        self.current_time += 1
 
        for p in self.all_processes:
            if p.arrival_time == self.current_time - 1 and p not in self.ready_queue:
                if p.completion_time == 0:
                    self.ready_queue.append(p)

        try:
  
            self.current_process = next(self.scheduler_gen)          
            proc = self.current_process
            start_time = self.current_time - 1

            # 3. تحديث بيانات الـ Gantt
            if (self.gantt_data and 
                self.gantt_data[-1][0] == proc.pid and 
                self.gantt_data[-1][2] == start_time):
                self.gantt_data[-1][2] = self.current_time
            else:
                self.gantt_data.append([proc.pid, start_time, self.current_time])

        
            if proc.remaining_time == 0:
                proc.completion_time = self.current_time
                proc.turnaround_time = proc.completion_time - proc.arrival_time

        except StopIteration:
            # 4. الـ Generator خلص (كل العمليات انتهت)
            self._timer.stop()
            self.window.add_btn.setEnabled(True)
            self.window.start_live_btn.setEnabled(True)
            self.window.run_existing_btn.setEnabled(True)
            self._show_final_results()
            return

        # 5. تحديث الـ UI
        self._update_process_table()
        self._update_ready_queue_table()
        self._update_gantt_chart()
        self._update_averages()

    # ══════════════════════════════════════════════════════════════════════════
    # HELPER – FIND PROCESS BY PID
    # ══════════════════════════════════════════════════════════════════════════

    def _find_process(self, pid: str | None) -> Process | None:
        if pid is None:
            return None
        for p in self.all_processes:
            if p.pid == pid:
                return p
        return None

    # ══════════════════════════════════════════════════════════════════════════
    # GUI UPDATE METHODS
    # ══════════════════════════════════════════════════════════════════════════

    # def _update_process_table(self) -> None:
        """
        Refreshes the main process table.
        Expected columns (0-indexed):
          0:PID | 1:Arrival | 2:Burst | 3:Priority | 4:Remaining | 5:Status
        """
        from PyQt6.QtWidgets import QTableWidgetItem
        
        table = self.window.process_table
        table.setRowCount(len(self.all_processes))

        for row, p in enumerate(self.all_processes):
            if p.completion_time > 0:
                status = "Done"
            elif p in self.ready_queue:
                status = "Ready"
            elif self.current_process and self.current_process.pid == p.pid:
                status = "Running"
            else:
                status = "Waiting"

            cells = [
                p.pid,
                str(p.arrival_time),
                str(p.burst_time),
                str(p.priority),
                str(p.remaining_time),
                status,
            ]
            for col, val in enumerate(cells):
                item = QTableWidgetItem(val)
                table.setItem(row, col, item)

    #def _update_ready_queue_table(self) -> None:
        """
        Refreshes the ready-queue table.
        Expected columns:  0:PID | 1:Remaining Time
        """
        from PyQt6.QtWidgets import QTableWidgetItem

        table = self.window.ready_queue_table
        table.setRowCount(len(self.ready_queue))

        for row, p in enumerate(self.ready_queue):
            table.setItem(row, 0, QTableWidgetItem(p.pid))
            table.setItem(row, 1, QTableWidgetItem(str(p.remaining_time)))

    #def _update_gantt_chart(self) -> None:
        """
        Calls the external gantt_chart module, removes the old widget from
        gantt_layout, and inserts the new one.
        """
        if not self.gantt_data:
            return

        layout = self.window.gantt_layout

        # Remove previous widget
        if self._gantt_widget is not None:
            layout.removeWidget(self._gantt_widget)
            self._gantt_widget.deleteLater()
            self._gantt_widget = None

        widget = build_gantt_widget(self.gantt_data)
        if widget:
            layout.addWidget(widget)
            self._gantt_widget = widget

    def _update_averages(self) -> None:
        """Compute and display running averages (only for completed processes)."""
        completed = [p for p in self.all_processes if p.completion_time > 0]
        if not completed:
            return

        avg_wt  = sum(p.waiting_time     for p in completed) / len(completed)
        avg_tat = sum(p.turnaround_time  for p in completed) / len(completed)

        self.window.avg_waiting_label.setText(f"{avg_wt:.2f}") # على حسب كود محمد
        self.window.avg_turnaround_label.setText(f"{avg_tat:.2f}")

    def _show_final_results(self) -> None:
        """Pop up a summary dialog when all processes have finished."""
        completed = [p for p in self.all_processes if p.completion_time > 0]
        if not completed:
            return

        avg_wt  = sum(p.waiting_time     for p in completed) / len(completed)
        avg_tat = sum(p.turnaround_time  for p in completed) / len(completed)

        lines = [
            "=== Simulation Complete ===",
            f"Total processes  : {len(completed)}",
            f"Finish time      : {self.current_time}",
            f"Avg Waiting Time : {avg_wt:.2f}",
            f"Avg Turnaround   : {avg_tat:.2f}",
            "",
            f"{'PID':<8} {'TAT':>6} {'WT':>6}",
            "-" * 24,
        ]
        for p in completed:
            lines.append(f"{p.pid:<8} {p.turnaround_time:>6} {p.waiting_time:>6}")

        QMessageBox.information(self.window, "Results", "\n".join(lines))

    # ══════════════════════════════════════════════════════════════════════════
    # UTILITIES
    # ══════════════════════════════════════════════════════════════════════════

    def _clear_inputs(self) -> None:
        """Clear all process-input fields after a successful add."""
        w = self.window
        w.pid_input.clear()
        w.arrival_input.clear()
        w.burst_input.clear()
        w.priority_input.clear()
        w.pid_input.setFocus()