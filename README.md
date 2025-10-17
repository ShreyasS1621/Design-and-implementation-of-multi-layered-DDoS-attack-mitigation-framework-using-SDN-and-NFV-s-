This project appears to simulate a **Slowloris-like Denial-of-Service (DoS) attack** and a basic defense mechanism against it, using Python's `socket` and `threading` modules.

To run this project, you need **three separate terminal windows** (or command prompts) because each Python file represents a different component that runs independently.

-----

## 1\. Prerequisites and Setup

Before running the files, ensure you have:

  * **Python 3** installed.
  * **Three terminal windows** open.
  * The three files (`DDOS.py`, `mitigate_attack.py`, and `systemlog_info.py`) saved in the same directory.
  * **Note on `mitigate_attack.py`**: This script uses `netsh advfirewall` which is a **Windows-specific command**. If you are on Linux or macOS, the IP blocking functionality will **fail** unless you replace the `block_ip` function with an equivalent command for your operating system's firewall (e.g., `iptables` or `pfctl`).

-----

## 2\. Step-by-Step Execution Guide

### Step 1: Start the System Log Server

This script acts as a simple web server that logs incoming connections, acting as a non-mitigating 'target' for the attack, but *only* if the attack is directed to its port (`80`).

1.  **Open the first terminal.**
2.  **Run the log server:**
    ```bash
    python systemlog_info.py
    ```
3.  **Expected Output:**
    ```
    [+] Listening on 10.44.1.186:80
    ```
      * **Note:** The `DDOS.py` attack script is configured to hit `HOST:PORT` which is `"10.44.1.186": 80`. This means the attack traffic will be directed here by default.

-----

### Step 2: Start the Defense Server (Mitigation)

This script implements the **Slow Header/Slow Read mitigation** by setting a timeout for receiving the full request headers. This server listens on a different port (`8080`) than the log server.

1.  **Open the second terminal.**
2.  **Run the defense server:**
    ```bash
    python mitigate_attack.py
    ```
3.  **Expected Output:**
    ```
    [+] Defense server listening on 10.44.1.186:8080
    ```
      * **Crucial Step:** Since the attack script (`DDOS.py`) is targeting port `80`, you must **edit `DDOS.py`** to target the defense server's port (`8080`) for the mitigation to be tested.

#### **Edit `DDOS.py` (Before running Step 3):**

Change the `PORT` variable in **`DDOS.py`** from `80` to `8080`.

| Original (`DDOS.py`) | Edited (`DDOS.py`) |
| :--- | :--- |
| `PORT = 80` | `PORT = 8080` |

-----

### Step 3: Launch the Slowloris Attack

The `DDOS.py` script simulates a Slowloris-like attack by establishing a large number of connections and then sending the POST body **very slowly** (one byte every `7` seconds, based on `BYTE_DELAY = 7`).

1.  **Open the third terminal.**
2.  **Run the attack script:**
    ```bash
    python DDOS.py
    ```
3.  **Expected Output:**
      * **In the attack terminal (`DDOS.py`):** You'll see thousands of connections being launched, followed by slow byte transmission logs (e.g., `[0] Sent byte 1/10000`).
    <!-- end list -->
    ```
    Launching 10000 slow connections to 10.44.1.186:8080
    Each connection sends 10000 bytes with 7s delay.
    ...
    [0] Connecting to 10.44.1.186:8080
    [0] Headers sent. Beginning body transmission...
    [0] Sent byte 1/10000
    ...
    ```
      * **In the defense terminal (`mitigate_attack.py`):** You will see the mitigation script detecting that the client took too long to send its headers (even though the attack sends them quickly, the script is designed to detect *slow headers* or general timeouts). The slow byte-by-byte transmission *after* the headers are sent might trigger the client socket to be closed and the simulated IP to be blocked if the client's subsequent slow actions are misinterpreted as a header timeout.
    <!-- end list -->
    ```
    [+] Defense server listening on 10.44.1.186:8080
    [!] Header timeout from 123.45.67.89. Blocking...
    [!] Blocking IP: 123.45.67.89
    [!] Slow header detected from 98.76.54.32. Blocking...
    [!] Blocking IP: 98.76.54.32
    ...
    ```

-----

## Project Overview

| File | Role | Attack/Defense Strategy | Port |
| :--- | :--- | :--- | :--- |
| **`DDOS.py`** | **Attacker** | Simulates a **Slow POST/Slowloris** attack by establishing many connections and sending the body content byte-by-byte with a long delay. | `80` (Default) or **`8080` (for testing mitigation)** |
| **`mitigate_attack.py`** | **Defense Server** | Implements a mitigation by setting a **short timeout (`THRESHOLD_HEADER_TIME = 10`s)** for receiving the full HTTP request headers. IPs that timeout are blocked using the Windows Firewall. | `8080` |
| **`systemlog_info.py`** | **Log Server** | A basic server that accepts connections, reads the request, extracts the `User-Agent`, and logs the connection details to text and JSON files. | `80` |
