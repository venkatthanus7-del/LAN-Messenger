import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer

from login_window import LoginWindow
from chat_window import ChatWindow
from db import init_db, get_connection
from network import (
    get_local_ip, send_udp_broadcast, listen_for_peers,
    start_chat_server, send_text_message, send_file, start_file_server
)

class LANMessengerApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.user_name = None
        self.peers = {}

        init_db()
        self.login_window = LoginWindow(self.on_login)
        self.login_window.show()

        self.chat_window = None

    def on_login(self, name):
        self.user_name = name
        self.login_window.close()

        self.chat_window = ChatWindow(name, self.on_send_message, self.on_send_file)
        self.chat_window.show()

        self.local_ip = get_local_ip()
        self.start_network()

    def start_network(self):
        def on_peer_found(name, ip):
            if name == self.user_name:
                return
            self.peers[ip] = name
            self.chat_window.add_peer(name, ip)

        self.udp_listener = listen_for_peers(on_peer_found)
        self.chat_server = start_chat_server(self.on_incoming_message)
        self.file_server = start_file_server(self.on_incoming_file)

        send_udp_broadcast(self.user_name, self.local_ip)

        self.timer = QTimer()
        self.timer.timeout.connect(lambda: send_udp_broadcast(self.user_name, self.local_ip))
        self.timer.start(5000)

    def on_send_message(self, peer_name, message):
        ip = self.find_ip_by_name(peer_name)
        if not ip:
            QMessageBox.warning(self.chat_window, "Warning", "Peer not found.")
            return

        success = send_text_message(ip, self.user_name, message)
        if success:
            self.chat_window.append_message("You", message)
            self.save_message(peer_name, message)
        else:
            QMessageBox.warning(self.chat_window, "Error", "Could not send message.")

    def on_send_file(self, peer_name, file_path):
        ip = self.find_ip_by_name(peer_name)
        if not ip:
            QMessageBox.warning(self.chat_window, "Warning", "Peer not found.")
            return

        success = send_file(ip, self.user_name, file_path)
        if success:
            self.chat_window.append_message("You", f"[File sent] {os.path.basename(file_path)}")
        else:
            QMessageBox.warning(self.chat_window, "Error", "Could not send file.")

    def on_incoming_message(self, payload):
        sender = payload.get("sender")
        content = payload.get("content")
        self.chat_window.append_message(sender, content)
        self.save_message(sender, content)

    def on_incoming_file(self, payload):
        pass

    def save_message(self, sender, content):
        conn = get_connection()
        conn.execute(
            "INSERT INTO messages(sender, receiver, content, file_name, file_path, msg_type, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (sender, self.user_name, content, "", "", "text", __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()
        conn.close()

    def find_ip_by_name(self, name):
        for ip, peer_name in self.peers.items():
            if peer_name == name:
                return ip
        return None

    def run(self):
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    app = LANMessengerApp()
    app.run()
