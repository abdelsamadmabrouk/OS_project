import sys
from PyQt5.QtWidgets import ( QApplication, QMainWindow, QWidget,
                             QVBoxLayout, QHBoxLayout, QFormLayout,
                             QComboBox, QSpinBox, QLineEdit,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QLabel, QHeaderView, QFrame )
from PyQt5.QtCore import Qt

class CPUSchedulerUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CPU Scheduling Simulator")
        self.setGeometry(100, 100, 1050, 700)

        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QVBoxLayout(self.main_widget)

        self.selection_ui()
        self.input_ui()
        self.tables_ui()
        self.gantt_ui()
        self.control_buttons()


    def selection_ui(self):
        group = QFrame()
        layout = QHBoxLayout(group)

        layout.addWidget(QLabel("Select Scheduler Type:"))

        self.algo_combo = QComboBox()
        self.algo_combo.addItems([ "FCFS", 
                                   "SJF (Non-Preemptive)","SJF (Preemptive)",
                                   "Priority (Non-Preemptive)","Priority (Preemptive)",
                                   "Round Robin" ])
        self.algo_combo.currentIndexChanged.connect(self.toggle_fields)
        layout.addWidget(self.algo_combo)
        self.main_layout.addWidget(group)


    def input_ui(self):
        self.input_frame = QFrame()
        layout = QFormLayout(self.input_frame)

        self.p_name = QLineEdit()
        self.p_arrival = QSpinBox()
        self.p_arrival.setMaximum(9999)
        self.p_burst = QSpinBox()
        self.p_burst.setMinimum(1)
        self.p_burst.setMaximum(9999)
        layout.addRow("Process Name:", self.p_name)
        layout.addRow("Arrival Time:", self.p_arrival)
        layout.addRow("Burst Time:",   self.p_burst)

        self.priority_label = QLabel("Priority:")
        self.p_priority = QSpinBox()
        self.p_priority.setMaximum(9999)
        layout.addRow(self.priority_label, self.p_priority)

        self.quantum_label = QLabel("Time Quantum:")
        self.p_quantum = QSpinBox()
        self.p_quantum.setMinimum(1)
        self.p_quantum.setMaximum(9999)
        self.p_quantum.setValue(2)
        layout.addRow(self.quantum_label, self.p_quantum)

        self.add_btn = QPushButton("Add Process")
        self.add_btn.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold;")
        layout.addRow(self.add_btn)

        self.add_now_btn = QPushButton("Add Process Now (at current time)")
        self.add_now_btn.setStyleSheet("background-color: #8e44ad; color: white; font-weight: bold;")
        self.add_now_btn.setVisible(False)
        layout.addRow(self.add_now_btn)

        self.main_layout.addWidget(self.input_frame)
        self.toggle_fields()   


    def toggle_fields(self):
        algo = self.algo_combo.currentText()

        is_priority = "Priority" in algo
        self.p_priority.setVisible(is_priority)
        self.priority_label.setVisible(is_priority)

        is_rr = "Round Robin" in algo
        self.p_quantum.setVisible(is_rr)
        self.quantum_label.setVisible(is_rr)


    def tables_ui(self):
        tables_layout = QHBoxLayout()

        # Main process table — 6 columns including Remaining and Status
        self.process_table = QTableWidget(0, 6)
        self.process_table.setHorizontalHeaderLabels(
            ["Name", "Arrival", "Burst", "Priority", "Remaining", "Status"])
        self.process_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)

        # Live ready-queue table
        self.live_table = QTableWidget(0, 2)
        self.live_table.setHorizontalHeaderLabels(["Process", "Remaining Burst"])
        self.live_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)

        tables_layout.addWidget(self.process_table)
        tables_layout.addWidget(self.live_table)
        self.main_layout.addLayout(tables_layout)


    def gantt_ui(self):
        self.gantt_frame = QFrame()
        self.gantt_frame.setFrameShape(QFrame.StyledPanel)
        self.gantt_frame.setMinimumHeight(200)
        self.gantt_layout = QVBoxLayout(self.gantt_frame)
        self.gantt_layout.addWidget(
            QLabel("Gantt Chart"), 0, Qt.AlignCenter)
        self.main_layout.addWidget(self.gantt_frame)


    def control_buttons(self):
        btn_layout = QHBoxLayout()

        self.start_live_btn = QPushButton("Start Live Simulation")
        self.start_live_btn.setFixedHeight(40)
        self.start_live_btn.setStyleSheet(
            "background-color: #2ecc71; color: white; font-weight: bold;")
  
        self.run_existing_btn = QPushButton("Run Currently Existing Processes")
        self.run_existing_btn.setFixedHeight(40)
        self.run_existing_btn.setStyleSheet(
            "background-color: #3498db; color: white; font-weight: bold;") 

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setFixedHeight(40)
        self.stop_btn.setStyleSheet(
            "background-color: #e67e22; color: white; font-weight: bold;")

        self.reset_btn = QPushButton("Reset")
        self.reset_btn.setFixedHeight(40)
        self.reset_btn.setStyleSheet(
            "background-color: #95a5a6; color: white; font-weight: bold;")

        btn_layout.addWidget(self.start_live_btn)
        btn_layout.addWidget(self.run_existing_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addWidget(self.reset_btn)
        self.main_layout.addLayout(btn_layout)

        results_frame = QFrame()
        results_frame.setStyleSheet(
            "background-color: #2c3e50; border-radius: 5px; padding: 10px;")
        results_layout = QHBoxLayout(results_frame)

        result_style = "color: #ecf0f1; font-size: 15px; font-weight: bold;"
        
        self.avg_waiting_label = QLabel("Avg Waiting Time: --")
        self.avg_waiting_label.setStyleSheet(result_style)

        self.avg_turnaround_label = QLabel("Avg Turnaround Time: --")
        self.avg_turnaround_label.setStyleSheet(result_style)

        results_layout.addWidget(self.avg_waiting_label)
        results_layout.addStretch()
        results_layout.addWidget(self.avg_turnaround_label)
        self.main_layout.addWidget(results_frame)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CPUSchedulerUI()
    window.show()
    sys.exit(app.exec_())