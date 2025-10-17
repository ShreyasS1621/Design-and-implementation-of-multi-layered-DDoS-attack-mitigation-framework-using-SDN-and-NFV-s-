import socket
import json
from datetime import datetime

LOG_TXT_FILE = "connections_log.txt"
LOG_JSON_FILE = "connections_log.json"
HOST = "10.44.1.186"  # Listen on all interfaces
PORT = 80       # Match the stress test

def log_connection(ip, port, user_agent):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {
        "timestamp": timestamp,
        "ip": ip,
        "port": port,
        "user_agent": user_agent
    }

    # Write to text file
    with open(LOG_TXT_FILE, "a") as txt_file:
        txt_file.write(f"{timestamp} - {ip}:{port} - UA: {user_agent}\n")

    # Write to JSON file
    try:
        with open(LOG_JSON_FILE, "r") as json_file:
            data = json.load(json_file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    data.append(log_entry)
    with open(LOG_JSON_FILE, "w") as json_file:
        json.dump(data, json_file, indent=4)

def extract_user_agent(request_data):
    try:
        lines = request_data.decode(errors="ignore").split("\r\n")
        for line in lines:
            if line.lower().startswith("user-agent:"):
                return line[len("User-Agent:"):].strip()
    except Exception:
        pass
    return "Unknown"

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(10)
    print(f"[+] Listening on {HOST}:{PORT}")

    while True:
        client_socket, addr = server.accept()
        ip, port = addr
        print(f"[+] Connection from {ip}:{port}")

        try:
            request_data = client_socket.recv(1024)
            user_agent = extract_user_agent(request_data)
            print(f"    -> UA: {user_agent}")
            log_connection(ip, port, user_agent)
        except Exception as e:
            print(f"[!] Error reading from {ip}: {e}")

        client_socket.close()

if __name__ == "__main__":
    start_server()
