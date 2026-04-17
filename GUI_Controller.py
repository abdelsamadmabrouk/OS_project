
from __future__ import annotations

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem

from scheduler import (Process, FCFS, SJF, preemptive_SJF,
                       preemptive_Priority, Non_preemptive_Priority,
                       round_robin)
from gantt_chart import GanttWidget


# ══════════════════════════════════════════════════════════════════════════════
class SchedulerController:
    """
    Wires all event handlers and drives the simulation loop.

    Usage (in your MainWindow.__init__ after setupUi):
        self.controller = SchedulerController(self)
    """
    all_processes:   list[Process]
    ready_queue:     list[Process]
    current_process: Process | None
    current_time:    int
    gantt_data:      list[list]      # [[pid, start, end], ...]
    _timer:          QTimer
    _live_mode:      bool            # True  → user may add processes mid-run
    _gantt_widget:   GanttWidget | None

    def __init__(self, window) -> None:
        self.window = window
        self.all_processes = []
        self.ready_queue = []
        self.current_process = None
        self.current_time = 0
        self.gantt_data = []
        self._live_mode = False
        self._paused = False

        # ── Gantt widget — create once and add to the gantt_frame layout ──
        self._gantt_widget = GanttWidget()
        window.gantt_layout.addWidget(self._gantt_widget)

        # ── Timer (1 tick = 1 second) ──
        self._timer = QTimer()
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._tick)

        # ── Connect buttons ──
        window.add_btn.clicked.connect(self._on_add_process)
        window.add_now_btn.clicked.connect(self._on_add_process_now)
        window.start_live_btn.clicked.connect(self._on_start_live)
        window.run_existing_btn.clicked.connect(self._on_run_static)
        window.stop_btn.clicked.connect(self._on_stop)
        window.reset_btn.clicked.connect(self._on_reset)

        # ── Reset everything when the algorithm changes ──
        window.algo_combo.currentIndexChanged.connect(self._on_algo_changed)

    def _on_algo_changed(self) -> None:
        """Clear all processes and reset UI when the scheduler type changes."""
        # Stop any running simulation
        self._timer.stop()

        # Clear all data
        self.all_processes = []
        self.ready_queue = []
        self.current_process = None
        self.current_time = 0
        self.gantt_data = []

        # Reset Gantt chart
        self._gantt_widget.reset()

        # Clear tables
        self.window.process_table.setRowCount(0)
        self.window.live_table.setRowCount(0)

        # Reset labels
        self.window.avg_waiting_label.setText("Avg Waiting Time: --")
        self.window.avg_turnaround_label.setText("Avg Turnaround Time: --")

        # Re-enable buttons
        self.window.add_btn.setEnabled(True)
        self.window.start_live_btn.setEnabled(True)
        self.window.run_existing_btn.setEnabled(True)
        self.window.algo_combo.setEnabled(True)

        # Reset pause state
        self._paused = False
        self.window.stop_btn.setText("Pause")
        self.window.stop_btn.setStyleSheet(
            "background-color: #e67e22; color: white; font-weight: bold;")
        self.window.add_now_btn.setVisible(False)

    def _on_reset(self) -> None:
        """Reset the entire application to its initial state."""
        # Stop any running simulation
        self._timer.stop()

        # Clear all data
        self.all_processes = []
        self.ready_queue = []
        self.current_process = None
        self.current_time = 0
        self.gantt_data = []

        # Reset Gantt chart
        self._gantt_widget.reset()

        # Clear tables
        self.window.process_table.setRowCount(0)
        self.window.live_table.setRowCount(0)

        # Reset labels
        self.window.avg_waiting_label.setText("Avg Waiting Time: --")
        self.window.avg_turnaround_label.setText("Avg Turnaround Time: --")

        # Re-enable buttons
        self.window.add_btn.setEnabled(True)
        self.window.start_live_btn.setEnabled(True)
        self.window.run_existing_btn.setEnabled(True)
        self.window.algo_combo.setEnabled(True)

        # Reset pause state
        self._paused = False
        self.window.stop_btn.setText("Pause")
        self.window.stop_btn.setStyleSheet(
            "background-color: #e67e22; color: white; font-weight: bold;")
        self.window.add_now_btn.setVisible(False)

        # Clear input fields
        self._clear_inputs()

    def _on_add_process(self) -> None:
        w = self.window
        algo = w.algo_combo.currentText()

        pid = w.p_name.text().strip()
        if not pid:
            QMessageBox.warning(
                w, "Input Error", "Process Name cannot be empty.")
            return

        if any(p.pid == pid for p in self.all_processes):
            QMessageBox.warning(w, "Duplicate PID",
                                f"A process with name '{pid}' already exists.")
            return

        arrival = w.p_arrival.value()
        burst = w.p_burst.value()

        # Only read priority when a Priority algorithm is selected
        priority = 0
        if "Priority" in algo:
            priority = w.p_priority.value()

        proc = Process(
            pid=pid,
            arrival_time=arrival,
            burst_time=burst,
            priority=priority,
            remaining_time=burst,
            completion_time=0,
            waiting_time=0,
            turnaround_time=0,
        )
        self.all_processes.append(proc)

        # If the simulation is running (or paused) and the process has
        # already arrived, add it directly to the ready queue.
        sim_active = self._timer.isActive() or self._paused
        if sim_active and proc.arrival_time <= self.current_time:
            self.ready_queue.append(proc)

        self._update_process_table()
        self._clear_inputs()

    def _on_add_process_now(self) -> None:
        """Add a process with arrival_time = current simulation time (instant)."""
        w = self.window
        algo = w.algo_combo.currentText()

        pid = w.p_name.text().strip()
        if not pid:
            QMessageBox.warning(
                w, "Input Error", "Process Name cannot be empty.")
            return

        if any(p.pid == pid for p in self.all_processes):
            QMessageBox.warning(w, "Duplicate PID",
                                f"A process with name '{pid}' already exists.")
            return

        burst = w.p_burst.value()

        priority = 0
        if "Priority" in algo:
            priority = w.p_priority.value()

        proc = Process(
            pid=pid,
            arrival_time=self.current_time,
            burst_time=burst,
            priority=priority,
            remaining_time=burst,
            completion_time=0,
            waiting_time=0,
            turnaround_time=0,
        )
        self.all_processes.append(proc)

        # Directly add to ready queue since it arrives "now"
        self.ready_queue.append(proc)

        self._update_process_table()
        self._clear_inputs()

    def _on_start_live(self) -> None:
        self._live_mode = True
        self._start_simulation()

    def _on_run_static(self) -> None:
        """Run all existing processes to completion instantly (no timer delay)."""
        self._live_mode = False
        self._start_simulation_static()

    def _on_stop(self) -> None:
        """Pause / Resume toggle during live simulation."""
        if not self._paused:
            # ── PAUSE ──
            self._timer.stop()
            self._paused = True
            self.window.stop_btn.setText("Resume")
            self.window.stop_btn.setStyleSheet(
                "background-color: #27ae60; color: white; font-weight: bold;")
            self.window.add_btn.setEnabled(True)
            self.window.add_now_btn.setVisible(True)   # show "Add Now"
            self.window.algo_combo.setEnabled(False)
        else:
            # ── RESUME ──
            self._paused = False
            self.window.stop_btn.setText("Pause")
            self.window.stop_btn.setStyleSheet(
                "background-color: #e67e22; color: white; font-weight: bold;")
            self.window.add_btn.setEnabled(self._live_mode)
            self.window.add_now_btn.setVisible(False)   # hide "Add Now"
            # Re-create generator so it picks up any newly added processes
            self.scheduler_gen = self._create_generator()
            self._timer.start()

    # ══════════════════════════════════════════════════════════════════════════
    # SIMULATION CORE
    # ══════════════════════════════════════════════════════════════════════════

    def _start_simulation(self) -> None:
        """Shared setup for both live and static runs."""
        if not self.all_processes:
            QMessageBox.information(self.window, "No Processes",
                                    "Please add at least one process first.")
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
            p.turnaround_time = 0

        # Enqueue processes that arrive at time 0
        for p in self.all_processes:
            if p.arrival_time == 0:
                self.ready_queue.append(p)

        # Reset Gantt widget
        self._gantt_widget.reset()

        # Create the scheduler generator
        self.scheduler_gen = self._create_generator()

        # Reset pause state and button
        self._paused = False
        self.window.stop_btn.setText("Pause")
        self.window.stop_btn.setStyleSheet(
            "background-color: #e67e22; color: white; font-weight: bold;")

        # Disable / enable buttons
        self.window.add_btn.setEnabled(self._live_mode)
        self.window.start_live_btn.setEnabled(False)
        self.window.run_existing_btn.setEnabled(False)
        self.window.algo_combo.setEnabled(False)

        self._timer.start()

    def _create_generator(self):
        """Create a new scheduler generator based on the selected algorithm."""
        algo = self.window.algo_combo.currentText()

        if algo == "FCFS":
            return FCFS(self.ready_queue)
        elif "SJF (Preemptive)" in algo:
            return preemptive_SJF(self.ready_queue)
        elif "SJF (Non-Preemptive)" in algo:
            return SJF(self.ready_queue)
        elif "Priority (Preemptive)" in algo:
            return preemptive_Priority(self.ready_queue)
        elif "Priority (Non-Preemptive)" in algo:
            return Non_preemptive_Priority(self.ready_queue)
        elif algo == "Round Robin":
            quantum = self.window.p_quantum.value()
            return round_robin(self.ready_queue, quantum)

    def _start_simulation_static(self) -> None:
        """Run all existing processes to completion instantly (no timer)."""
        if not self.all_processes:
            QMessageBox.information(self.window, "No Processes",
                                    "Please add at least one process first.")
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
            p.turnaround_time = 0

        # Enqueue processes that arrive at time 0
        for p in self.all_processes:
            if p.arrival_time == 0:
                self.ready_queue.append(p)

        # Reset Gantt widget
        self._gantt_widget.reset()

        # Create the scheduler generator
        scheduler_gen = self._create_generator()

        # Disable buttons during computation
        self.window.add_btn.setEnabled(False)
        self.window.start_live_btn.setEnabled(False)
        self.window.run_existing_btn.setEnabled(False)

        # Safety limit to prevent infinite loops
        max_time = sum(p.burst_time for p in self.all_processes) + \
            max(p.arrival_time for p in self.all_processes) + 10

        # Run the entire simulation instantly
        while self.current_time < max_time:
            self.current_time += 1

            # Admit newly arrived processes
            for p in self.all_processes:
                if p.arrival_time == self.current_time - 1 and p not in self.ready_queue:
                    if p.completion_time == 0 and p.remaining_time > 0:
                        self.ready_queue.append(p)

            try:
                self.current_process = next(scheduler_gen)
                proc = self.current_process
                start_time = self.current_time - 1

                # Update Gantt data
                if (self.gantt_data and
                    self.gantt_data[-1][0] == proc.pid and
                        self.gantt_data[-1][2] == start_time):
                    self.gantt_data[-1][2] = self.current_time
                else:
                    self.gantt_data.append(
                        [proc.pid, start_time, self.current_time])

                # Mark completion
                if proc.remaining_time == 0:
                    proc.completion_time = self.current_time
                    proc.turnaround_time = proc.completion_time - proc.arrival_time

            except StopIteration:
                # Check if there are still unfinished processes
                unfinished = [
                    p for p in self.all_processes if p.completion_time == 0]
                if unfinished:
                    # CPU is idle — re-create generator for when new processes arrive
                    self.current_process = None
                    if self.ready_queue:
                        scheduler_gen = self._create_generator()
                    continue
                else:
                    break

        # Update UI once with final results
        self.window.add_btn.setEnabled(True)
        self.window.start_live_btn.setEnabled(True)
        self.window.run_existing_btn.setEnabled(True)
        self._update_process_table()
        self._update_ready_queue_table()
        self._update_gantt_chart()
        self._update_averages()
        self._show_final_results()

    def _tick(self) -> None:
        self.current_time += 1

        # Admit newly arrived processes
        for p in self.all_processes:
            if p.arrival_time == self.current_time - 1 and p not in self.ready_queue:
                if p.completion_time == 0 and p.remaining_time > 0:
                    self.ready_queue.append(p)

        try:
            self.current_process = next(self.scheduler_gen)
            proc = self.current_process
            start_time = self.current_time - 1

            # Update Gantt data
            if (self.gantt_data and
                self.gantt_data[-1][0] == proc.pid and
                    self.gantt_data[-1][2] == start_time):
                self.gantt_data[-1][2] = self.current_time
            else:
                self.gantt_data.append(
                    [proc.pid, start_time, self.current_time])

            # Mark completion
            if proc.remaining_time == 0:
                proc.completion_time = self.current_time
                proc.turnaround_time = proc.completion_time - proc.arrival_time

        except StopIteration:
            # Check if there are still unfinished processes
            unfinished = [
                p for p in self.all_processes if p.completion_time == 0]
            if unfinished:
                # CPU is idle — re-create generator for when new processes arrive
                self.current_process = None
                if self.ready_queue:
                    self.scheduler_gen = self._create_generator()
            else:
                # Truly done — all processes completed
                self._timer.stop()
                self._paused = False
                self.window.stop_btn.setText("Pause")
                self.window.stop_btn.setStyleSheet(
                    "background-color: #e67e22; color: white; font-weight: bold;")
                self.window.add_btn.setEnabled(True)
                self.window.add_now_btn.setVisible(False)
                self.window.start_live_btn.setEnabled(True)
                self.window.run_existing_btn.setEnabled(True)
                self.window.algo_combo.setEnabled(True)
                self._update_process_table()
                self._update_ready_queue_table()
                self._update_gantt_chart()
                self._update_averages()
                self._show_final_results()
                return

        # Update all UI elements
        self._update_process_table()
        self._update_ready_queue_table()
        self._update_gantt_chart()
        self._update_averages()

    # ══════════════════════════════════════════════════════════════════════════
    # GUI UPDATE METHODS
    # ══════════════════════════════════════════════════════════════════════════

    def _update_process_table(self) -> None:
        """
        Refreshes the main process table.
        Columns: 0:Name | 1:Arrival | 2:Burst | 3:Priority | 4:Remaining | 5:Status
        """
        table = self.window.process_table
        table.setRowCount(len(self.all_processes))

        for row, p in enumerate(self.all_processes):
            if p.completion_time > 0:
                status = "Done"
            elif self.current_process and self.current_process.pid == p.pid:
                status = "Running"
            elif p in self.ready_queue:
                status = "Ready"
            elif p.arrival_time > self.current_time:
                status = "Not Arrived"
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

    def _update_ready_queue_table(self) -> None:
        """
        Refreshes the ready-queue table (live remaining burst).
        Columns:  0:Process | 1:Remaining Burst
        """
        table = self.window.live_table
        table.setRowCount(len(self.ready_queue))

        for row, p in enumerate(self.ready_queue):
            table.setItem(row, 0, QTableWidgetItem(p.pid))
            table.setItem(row, 1, QTableWidgetItem(str(p.remaining_time)))

    def _update_gantt_chart(self) -> None:
        """Update the Gantt chart widget with current segment data."""
        if not self.gantt_data:
            return
        self._gantt_widget.update_segments(self.gantt_data)

    def _update_averages(self) -> None:
        """Compute and display running averages (only for completed processes)."""
        completed = [p for p in self.all_processes if p.completion_time > 0]
        if not completed:
            return

        avg_wt = sum(p.waiting_time for p in completed) / len(completed)
        avg_tat = sum(p.turnaround_time for p in completed) / len(completed)

        self.window.avg_waiting_label.setText(
            f"Avg Waiting Time: {avg_wt:.2f}")
        self.window.avg_turnaround_label.setText(
            f"Avg Turnaround Time: {avg_tat:.2f}")

    def _show_final_results(self) -> None:
        """Pop up a summary dialog when all processes have finished."""
        completed = [p for p in self.all_processes if p.completion_time > 0]
        if not completed:
            return

        avg_wt = sum(p.waiting_time for p in completed) / len(completed)
        avg_tat = sum(p.turnaround_time for p in completed) / len(completed)

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
            lines.append(
                f"{p.pid:<8} {p.turnaround_time:>6} {p.waiting_time:>6}")

        QMessageBox.information(self.window, "Results", "\n".join(lines))

    # ══════════════════════════════════════════════════════════════════════════
    # UTILITIES
    # ══════════════════════════════════════════════════════════════════════════

    def _clear_inputs(self) -> None:
        """Clear all process-input fields after a successful add."""
        w = self.window
        w.p_name.clear()
        w.p_arrival.setValue(0)
        w.p_burst.setValue(1)
        w.p_priority.setValue(0)
        w.p_name.setFocus()
