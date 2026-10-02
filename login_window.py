from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox

class LoginWindow(QWidget):
    def __init__(self, on_login):
        super().__init__()
        self.on_login = on_login
        self.setWindowTitle("LAN Messenger Login")
        self.resize(350, 180)

        layout = QVBoxLayout()

        self.label = QLabel("Enter your name:")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Your display name")

        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.login)

        layout.addWidget(self.label)
        layout.addWidget(self.name_input)
        layout.addWidget(self.login_btn)

        self.setLayout(layout)

    def login(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Warning", "Please enter a name.")
            return
        self.on_login(name)
