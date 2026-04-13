import sys
from PyQt6.QtWidgets import ( QApplication, QMainWindow, QWidget,
                             QVBoxLayout, QHBoxLayout, QFormLayout,
                             QComboBox, QSpinBox, QLineEdit,
                             QPushButton, QTableWidget,
                             QLabel, QHeaderView, QFrame )
from PyQt6.QtCore import Qt

class CPUSchedulerUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CPU Scheduling Simulator")
        self.setGeometry(100, 100, 900, 600)

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
        self.p_burst = QSpinBox()
        layout.addRow("Process Name:", self.p_name)
        layout.addRow("Arrival Time:", self.p_arrival)
        layout.addRow("Burst Time:",   self.p_burst)

        self.priority_label = QLabel("Priority:")
        self.p_priority = QSpinBox()
        layout.addRow(self.priority_label, self.p_priority)

        self.quantum_label = QLabel("Time Quantum:")
        self.p_quantum = QSpinBox()
        layout.addRow(self.quantum_label, self.p_quantum)

        self.add_btn = QPushButton("Add Process")
        self.add_btn.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold;")
        layout.addRow(self.add_btn)

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

        self.process_table = QTableWidget(0, 4)
        self.process_table.setHorizontalHeaderLabels( ["Name", "Arrival", "Burst", "Priority"])
        self.process_table.horizontalHeader().setSectionResizeMode( QHeaderView.ResizeMode.Stretch )

        self.live_table = QTableWidget(0, 2)
        self.live_table.setHorizontalHeaderLabels(["Process", "Remaining Burst"])
        self.live_table.horizontalHeader().setSectionResizeMode( QHeaderView.ResizeMode.Stretch )

        tables_layout.addWidget(self.process_table)
        tables_layout.addWidget(self.live_table)
        self.main_layout.addLayout(tables_layout)


    def gantt_ui(self):
        self.gantt_frame = QFrame()
        self.gantt_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.gantt_frame.setMinimumHeight(200)
        layout = QVBoxLayout(self.gantt_frame)
        layout.addWidget(QLabel("Gantt Chart"),alignment=Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.gantt_frame)


    def control_buttons(self):
        btn_layout = QHBoxLayout()

        self.start_live_btn = QPushButton("Start Live Simulation")
        self.start_live_btn.setFixedHeight(40)
        self.start_live_btn.setStyleSheet( "background-color: #2ecc71; color: white; font-weight: bold;")
  
        self.run_existing_btn = QPushButton("Run Currently Existing Processes")
        self.run_existing_btn.setFixedHeight(40)
        self.run_existing_btn.setStyleSheet("background-color: #3498db; color: white; font-weight: bold;") 

        btn_layout.addWidget(self.start_live_btn)
        btn_layout.addWidget(self.run_existing_btn)
        self.main_layout.addLayout(btn_layout)

        results_frame = QFrame()
        results_frame.setStyleSheet( "background-color: #2c3e50; border-radius: 5px; padding: 10px;")
        results_layout = QHBoxLayout(results_frame)

        result_style = "color: #ecf0f1; font-size: 15px; font-weight: bold;"
        
        self.avg_waiting_label = QLabel("Avg Waiting Time: ")
        self.avg_waiting_label.setStyleSheet(result_style)

        self.avg_turnaround_label = QLabel("Avg Turnaround Time: ")
        self.avg_turnaround_label.setStyleSheet(result_style)

        results_layout.addWidget(self.avg_waiting_label)
        results_layout.addStretch()
        results_layout.addWidget(self.avg_turnaround_label)
        self.main_layout.addWidget(results_frame)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CPUSchedulerUI()
    window.show()
    sys.exit(app.exec())