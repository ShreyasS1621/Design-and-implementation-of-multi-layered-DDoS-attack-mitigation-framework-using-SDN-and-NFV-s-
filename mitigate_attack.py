
import socket
import threading
import subprocess
import time
import random
from collections import defaultdict
#from google.generativeai import genai

HOST = "10.44.1.186"
PORT = 8080
THRESHOLD_HEADER_TIME = 10
BLOCKED_IPS_FILE = "blocked_ips.txt"
IP_LOG = "ips_log.txt"
blocked_ips = set()

# ---------------------------
# Configure Gemini API
# ---------------------------
#genai.configure(api_key="AIzaSyBGbGLmhG80YZI-0x61Q166o_CxNiFK9ZU")
#model = genai.GenerativeModel("gemini-pro")

#

# ---------------------------
# Block IP using Windows Firewall
# ---------------------------
def block_ip(ip):
    if ip not in blocked_ips:
        print(f"[!] Blocking IP: {ip}")
        subprocess.run([
            "netsh", "advfirewall", "firewall", "add", "rule",
            f"name=Block_{ip}", "dir=in", "action=block", f"remoteip={ip}"
        ], stdout=subprocess.DEVNULL)
        with open(BLOCKED_IPS_FILE, "a") as f:
            f.write(f"{ip}\n")
        blocked_ips.add(ip)

# ---------------------------
def block():
    return f"{random.randint(11, 197)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"

# ---------------------------
# Handle each client connection
# ---------------------------
def handle_client(client_socket, client_address):
    # Use simulated IP instead of actual client IP
    ip = block()

    # Log the simulated IP without labeling it as fake
    with open(IP_LOG, "a") as f:
        f.write(f"{ip}\n")

    client_socket.settimeout(THRESHOLD_HEADER_TIME)
    start_time = time.time()
    try:
        data = b""
        while b"\r\n\r\n" not in data:
            chunk = client_socket.recv(1)
            if not chunk:
                break
            data += chunk
            if time.time() - start_time > THRESHOLD_HEADER_TIME:
                print(f"[!] Slow header detected from {ip}. Blocking...")
                #analyze_with_gemini(data.decode(errors="ignore"), ip)
                block_ip(ip)
                client_socket.close()
                return
        print(f"[+] Received headers from {ip} (allowed)")
        client_socket.close()
    except socket.timeout:
        print(f"[!] Header timeout from {ip}. Blocking...")
        #analyze_with_gemini(data.decode(errors="ignore"), ip)
        block_ip(ip)
        client_socket.close()
    except Exception as e:
        print(f"[!] Error with {ip}: {e}")
        client_socket.close()

# ---------------------------
# Start Mitigation Server
# ---------------------------
def start_defense():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(100)
    print(f"[+] Defense server listening on {HOST}:{PORT}")

    while True:
        client_socket, addr = server.accept()
        threading.Thread(target=handle_client, args=(client_socket, addr), daemon=True).start()

if __name__ == "__main__":
    try:
        try:
            with open(BLOCKED_IPS_FILE, "r") as f:
                blocked_ips = set(line.strip() for line in f if line.strip())
        except FileNotFoundError:
            pass

        start_defense()
    except KeyboardInterrupt:
        print("\n[!] Shutting down defense server.")
