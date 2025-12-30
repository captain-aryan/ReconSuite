import requests
import threading
import queue

valid_codes = [200, 301, 302, 403]

def dirb(base_url, threads, wordlist, ext=None):
    q = queue.Queue()
    results = []
    lock = threading.Lock()
    session = requests.Session()

    with open(wordlist, 'r', errors="ignore") as f:
        for line in f:
            d = line.strip()
            if d:
                if ext:
                    q.put(f"{base_url}/{d}{ext}")
                else:
                    q.put(f"{base_url}/{d}")
            
    def worker():
        while not q.empty():
            url = q.get()
            try:
                r = session.get(url, timeout=5, allow_redirects=True, verify=False)
                if r.status_code in valid_codes:
                    with lock:
                        results.append(url)
                        print(f"[DIR] {r.status_code} {url}")
            
            except:
                pass
            q.task_done()

    for i in range(threads):
        threading.Thread(target=worker, daemon=True).start()
    
    q.join()
    return results