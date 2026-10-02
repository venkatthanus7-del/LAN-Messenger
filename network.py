import socket
import json
import threading
import os
import time
from datetime import datetime

HOST = "0.0.0.0"
DISCOVERY_PORT = 5000
CHAT_PORT = 5001
FILE_PORT = 5002
MULTICAST_GROUP = "239.255.0.1"

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

def send_udp_broadcast(name, ip):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    packet = {
        "type": "hello",
        "name": name,
        "ip": ip
    }
    sock.sendto(json.dumps(packet).encode(), (MULTICAST_GROUP, DISCOVERY_PORT))
    sock.close()

def listen_for_peers(on_peer_found):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, DISCOVERY_PORT))
    mreq = socket.inet_aton(MULTICAST_GROUP) + socket.inet_aton(HOST)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    def receiver():
        while True:
            data, addr = sock.recvfrom(65535)
            try:
                packet = json.loads(data.decode())
            except:
                continue
            if packet.get("type") == "hello":
                on_peer_found(packet.get("name"), packet.get("ip"))

    t = threading.Thread(target=receiver, daemon=True)
    t.start()
    return sock

def send_text_message(target_ip, sender_name, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    try:
        sock.connect((target_ip, CHAT_PORT))
        payload = {
            "type": "text",
            "sender": sender_name,
            "content": message,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        sock.sendall(json.dumps(payload).encode())
        sock.close()
        return True
    except Exception:
        return False

def start_chat_server(on_message_received):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, CHAT_PORT))
    server.listen(10)

    def accept_loop():
        while True:
            conn, addr = server.accept()
            data = conn.recv(65535)
            conn.close()
            try:
                payload = json.loads(data.decode())
            except:
                continue
            if payload.get("type") == "text":
                on_message_received(payload)

    t = threading.Thread(target=accept_loop, daemon=True)
    t.start()
    return server

def send_file(target_ip, sender_name, file_path):
    if not os.path.exists(file_path):
        return False
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)

    info = {
        "type": "file_info",
        "sender": sender_name,
        "file_name": file_name,
        "file_size": file_size,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((target_ip, FILE_PORT))
        sock.sendall(json.dumps(info).encode())
        sock.close()
    except Exception:
        return False

    time.sleep(0.2)

    try:
        fs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        fs.settimeout(10)
        fs.connect((target_ip, FILE_PORT + 1))
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(65536)
                if not chunk:
                    break
                fs.sendall(chunk)
        fs.close()
        return True
    except Exception:
        return False

def start_file_server(on_file_received):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, FILE_PORT))
    server.listen(10)

    def accept_loop():
        while True:
            conn, addr = server.accept()
            data = conn.recv(65535)
            conn.close()
            try:
                payload = json.loads(data.decode())
            except:
                continue
            if payload.get("type") == "file_info":
                on_file_received(payload)

    t = threading.Thread(target=accept_loop, daemon=True)
    t.start()

    recv_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    recv_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    recv_server.bind((HOST, FILE_PORT + 1))
    recv_server.listen(10)

    def recv_loop():
        while True:
            conn, addr = recv_server.accept()
            raw = b""
            while True:
                chunk = conn.recv(65536)
                if not chunk:
                    break
                raw += chunk
            conn.close()

    t2 = threading.Thread(target=recv_loop, daemon=True)
    t2.start()
    return server
