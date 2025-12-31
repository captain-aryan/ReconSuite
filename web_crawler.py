import requests
import sys
import os
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from colorama import Fore, Style, init

init(autoreset=True)

if len(sys.argv) < 2:
    print("Usage: python web_crawler.py <url>")
    sys.exit(1)

input_url = sys.argv[1].rstrip("/")

if not input_url.startswith(("http://", "https://")):
    try:
        requests.get(f"https://{input_url}", timeout=0.5, verify=False)
        start_url = f"https://{input_url}"
    except requests.RequestException:
        start_url = f"http://{input_url}"
else:
    start_url = input_url

visited = set()
queue = [start_url]

os.makedirs("recon", exist_ok=True)
safe_host = urlparse(start_url).netloc.replace(".", "_")
output_file = f"recon/crawl_{safe_host}.txt"

print(f"{Fore.CYAN}[+]{Style.RESET_ALL} Crawling: {Fore.YELLOW}{start_url}")

def is_same_domain(url):
    return urlparse(url).netloc == urlparse(start_url).netloc

while queue:
    url = queue.pop(0)
    if url in visited:
        continue

    visited.add(url)

    try:
        r = requests.get(url, timeout=5, verify=False, allow_redirects=True)

        print(f"{Fore.GREEN}[+] Found:{Style.RESET_ALL} {url}")

        with open(output_file, "a") as f:
            f.write(url + "\n")

        soup = BeautifulSoup(r.text, "html.parser")

        for tag in soup.find_all("a", href=True):
            link = urljoin(url, tag["href"]).split("#")[0]

            if is_same_domain(link) and link not in visited:
                queue.append(link)

        for form in soup.find_all("form", action=True):
            link = urljoin(url, form["action"]).split("#")[0]

            if is_same_domain(link) and link not in visited:
                queue.append(link)

    except requests.RequestException:
        pass

print(f"\n{Fore.GREEN}[+]{Style.RESET_ALL} Crawl completed")
