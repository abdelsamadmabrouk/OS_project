import sys
from PyQt5.QtWidgets import QApplication
from Scheduler_Ui import CPUSchedulerUI
from GUI_Controller import SchedulerController


def main():
    app = QApplication(sys.argv)
    window = CPUSchedulerUI()
    controller = SchedulerController(window)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
