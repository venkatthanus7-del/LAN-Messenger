from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QFileDialog, QMessageBox, QHBoxLayout
)
from PyQt5.QtCore import Qt
from datetime import datetime

class ChatWindow(QWidget):
    def __init__(self, user_name, on_send_message, on_send_file):
        super().__init__()
        self.user_name = user_name
        self.on_send_message = on_send_message
        self.on_send_file = on_send_file
        self.setWindowTitle(f"LAN Messenger - {user_name}")
        self.resize(700, 500)

        self.peer_list = QListWidget()
        self.messages = QTextEdit()
        self.messages.setReadOnly(True)

        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Type your message...")

        self.send_btn = QPushButton("Send")
        self.send_file_btn = QPushButton("Send File")

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_box)
        input_layout.addWidget(self.send_btn)
        input_layout.addWidget(self.send_file_btn)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.peer_list)
        main_layout.addWidget(self.messages)
        main_layout.addLayout(input_layout)

        self.setLayout(main_layout)

        self.send_btn.clicked.connect(self.send_message)
        self.input_box.returnPressed.connect(self.send_message)
        self.send_file_btn.clicked.connect(self.send_file)
        self.peer_list.itemClicked.connect(self.set_current_peer)

        self.current_peer = None

    def add_peer(self, name, ip):
        for i in range(self.peer_list.count()):
            item = self.peer_list.item(i)
            if item.text() == f"{name} ({ip})":
                return
        self.peer_list.addItem(f"{name} ({ip})")

    def set_current_peer(self, item):
        if item is None:
            return
        text = item.text()
        if " (" in text:
            self.current_peer = text.rsplit(" (", 1)[0]
        else:
            self.current_peer = text

    def send_message(self):
        text = self.input_box.text().strip()
        if not text or not self.current_peer:
            return
        self.on_send_message(self.current_peer, text)
        self.input_box.clear()

    def send_file(self):
        if not self.current_peer:
            QMessageBox.warning(self, "Warning", "Select a peer first.")
            return
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if not file_path:
            return
        self.on_send_file(self.current_peer, file_path)

    def append_message(self, sender, content, kind="text"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.messages.append(f"[{timestamp}] {sender}: {content}")
