import sys
import serial
import serial.tools.list_ports

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class HydrophoneGUI(QWidget):

    def __init__(self):
        super().__init__()

        self.serial_port = None

        self.setWindowTitle("Hydrophone Recorder Controller")
        self.setGeometry(300, 150, 520, 520)

        self.setStyleSheet("""
        QWidget {
            background-color: #1e1e1e;
            color: white;
            font-size: 14px;
        }

        QPushButton {
            background-color: #3c3f41;
            border-radius: 8px;
            padding: 10px;
        }

        QPushButton:hover {
            background-color: #5a5d60;
        }

        QTextEdit {
            background-color: black;
        }

        QComboBox {
            padding: 5px;
        }
        """)

        main_layout = QVBoxLayout()

        title = QLabel("Hydrophone Recorder Control")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:22px;font-weight:bold")

        main_layout.addWidget(title)

        # -------- PORT CONTROL --------

        port_layout = QHBoxLayout()

        self.port_box = QComboBox()
        self.refresh_ports()

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_ports)

        connect_btn = QPushButton("Connect")
        connect_btn.clicked.connect(self.connect_serial)

        port_layout.addWidget(self.port_box)
        port_layout.addWidget(refresh_btn)
        port_layout.addWidget(connect_btn)

        main_layout.addLayout(port_layout)

        # -------- RECORD CONTROL --------

        control_layout = QGridLayout()

        start_btn = QPushButton("START RECORDING")
        stop_btn = QPushButton("STOP RECORDING")

        start_btn.clicked.connect(lambda: self.send_cmd("START"))
        stop_btn.clicked.connect(lambda: self.send_cmd("STOP"))

        start_btn.setStyleSheet("background:#2ecc71;font-weight:bold")
        stop_btn.setStyleSheet("background:#e74c3c;font-weight:bold")

        control_layout.addWidget(start_btn,0,0)
        control_layout.addWidget(stop_btn,0,1)

        cont_on = QPushButton("CONTINUOUS ON")
        cont_off = QPushButton("CONTINUOUS OFF")

        cont_on.clicked.connect(lambda: self.send_cmd("CONTINUOUS_ON"))
        cont_off.clicked.connect(lambda: self.send_cmd("CONTINUOUS_OFF"))

        control_layout.addWidget(cont_on,1,0)
        control_layout.addWidget(cont_off,1,1)

        main_layout.addLayout(control_layout)

        # -------- RTC CONTROL --------

        rtc_label = QLabel("Set RTC Time")

        self.datetime = QDateTimeEdit(QDateTime.currentDateTime())
        self.datetime.setDisplayFormat("yyyy MM dd HH mm ss")

        rtc_btn = QPushButton("Update RTC")
        rtc_btn.clicked.connect(self.set_time)

        main_layout.addWidget(rtc_label)
        main_layout.addWidget(self.datetime)
        main_layout.addWidget(rtc_btn)

        # -------- STATUS --------

        self.status_label = QLabel("STATUS: DISCONNECTED")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size:16px;color:#f1c40f")

        main_layout.addWidget(self.status_label)

        # -------- SERIAL MONITOR --------

        log_label = QLabel("System Log")

        self.log = QTextEdit()
        self.log.setReadOnly(True)

        main_layout.addWidget(log_label)
        main_layout.addWidget(self.log)

        self.setLayout(main_layout)

        # serial read timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.read_serial)
        self.timer.start(100)


    def refresh_ports(self):

        self.port_box.clear()

        ports = serial.tools.list_ports.comports()

        for port in ports:
            self.port_box.addItem(port.device)


    def connect_serial(self):

        try:
            port = self.port_box.currentText()

            self.serial_port = serial.Serial(port,115200,timeout=0.1)

            self.status_label.setText("STATUS: CONNECTED")
            self.log.append(f"Connected to {port}")

        except:
            self.log.append("Connection Failed")


    def send_cmd(self,cmd):

        if self.serial_port:

            self.serial_port.write((cmd+"\n").encode())
            self.log.append("> "+cmd)


    def set_time(self):

        dt = self.datetime.dateTime()

        cmd = "SETTIME " + dt.toString("yyyy MM dd HH mm ss")

        self.send_cmd(cmd)


    def read_serial(self):

        if self.serial_port and self.serial_port.in_waiting:

            data = self.serial_port.readline().decode(errors="ignore").strip()

            if data:

                self.log.append(data)

                if "RECORDING_STARTED" in data:
                    self.status_label.setText("STATUS: RECORDING")

                if "RECORDING_STOPPED" in data:
                    self.status_label.setText("STATUS: STOPPED")


app = QApplication(sys.argv)

window = HydrophoneGUI()
window.show()

sys.exit(app.exec_())