import requests
import threading
import queue

def subdomains(domain, threads, wordlist):
    q = queue.Queue()
    results = []
    lock = threading.Lock()

    with open(wordlist, 'r') as f:
        for sub in f.read().splitlines():
            if sub:
                q.put(sub)
    
    def worker():
        session = requests.Session()
        while not q.empty():
            sub = q.get()
            url = f"http://{sub}.{domain}"
            try:
                r = session.head(url, timeout=3, allow_redirects=True)
                if r.status_code < 400:
                    while lock:
                        full = f"http://{sub}.{domain}"
                        results.append(full)
                        print(f"[SUB] {full}")
            except:
                pass
            q.task_done()
    
    for i in range(threads):
        threading.Thread(target=worker, daemon=True).start()

    q.join()
    return results