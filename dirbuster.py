import requests
import queue
import threading 
import sys
import os
from colorama import Fore, Style, init

init(autoreset=True)

TIMEOUT = 5
VALID_CODES = [200, 301, 302, 403]
DEFAULT_WORDLIST = "dirb.txt"

if len(sys.argv) < 3:
    print("Usage: python dirbuster.py <url> <threads> [extension] [wordlist]")
    sys.exit(1)

input_host = sys.argv[1].rstrip("/")
threads = int(sys.argv[2])

if not input_host.startswith(("http://", "https://")):
    try:
        requests.get(f"https://{input_host}", timeout=0.5, verify=False)
        host = f"https://{input_host}"
    except requests.RequestException:
        host = f"http://{input_host}"
else:
    host = input_host

try:
    ext = sys.argv[3]
except:
    ext = False
    pass

wordlist_path = sys.argv[4] if len(sys.argv) > 4 else DEFAULT_WORDLIST

print(f"\n{Fore.CYAN}[+] Target        : {host}")
print(f"{Fore.CYAN}[+] Threads       : {threads}")
print(f"{Fore.CYAN}[+] Extension     : {ext if ext else 'None'}")
print(f"{Fore.CYAN}[+] Wordlist      : {wordlist_path}\n")

print(f"{Fore.GREEN}[+]{Style.RESET_ALL} Scanning for directories...\n")

if not os.path.isfile(wordlist_path):
    print(f"{Fore.RED}[+]{Style.RESET_ALL} Wordlist not found: {wordlist_path}")
    sys.exit(1)

try:
    requests.get(host, timeout=TIMEOUT)
except Exception as e:
    print(f"{Fore.RED}[+]{Style.RESET_ALL} Target unreachable: {e}")
    sys.exit(0)

os.makedirs("recon", exist_ok=True)
safe_host = host.replace("http://", "").replace("https://", "").replace("/", "_")
output_file = f"recon/dirb_{safe_host}.txt"
file_lock = threading.Lock()

q = queue.Queue()

def dirbuster(q):
    session = requests.Session()
    while True:
        url = q.get()
        try:
            response = session.get(url, timeout=TIMEOUT, allow_redirects=True, verify=False)

            status = response.status_code

            if status in VALID_CODES:

                if status == 200:
                    print(f"[{Fore.GREEN}200{Style.RESET_ALL}] {url}")

                elif status in (301, 302):
                    print(f"[{Fore.BLUE}{status}{Style.RESET_ALL}] {url}")

                elif status == 403:
                    print(f"[{Fore.YELLOW}403{Style.RESET_ALL}] {url}")

                with file_lock:
                    with open(output_file, 'a') as f:
                        f.write(f"[{status}] {url}\n")

        except requests.RequestException:
            pass
        finally:
            q.task_done()

with open(wordlist_path, "r", errors="ignore") as wordlist:
    for line in wordlist:
        directory = line.strip()
        if not directory:
            continue

        if ext:
            url = f"{host}/{directory}{ext}"
        else:
            url = f"{host}/{directory}"
        q.put(url)

for i in range(threads):
    t = threading.Thread(target=dirbuster, args=(q,))
    t.daemon = True
    t.start()

q.join()
print(f"\n{Fore.GREEN}[+]{Style.RESET_ALL} Scan completed.\n")