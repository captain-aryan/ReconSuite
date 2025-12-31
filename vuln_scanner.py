import requests
import argparse
import os
from urllib.parse import urlparse, parse_qs, urlencode
from colorama import Fore, Style, init

init(autoreset=True)

requests.packages.urllib3.disable_warnings()

PAYLOAD_DIR = "payloads"

class WebVulnerabilityScanner:

    def __init__(self, target, wordlist=None):
        self.target = target.strip()
        self.session = requests.Session()
        self.session.verify = False
        self.wordlist = wordlist

    def banner(self):
        print(f"{Fore.CYAN}[+]{Style.RESET_ALL} Target: {Fore.YELLOW}{self.target}")

    def load_payloads(self, filename, fallback):
        if self.wordlist and os.path.exists(self.wordlist):
            with open(self.wordlist, "r", encoding="utf-8") as f:
                return [x.strip() for x in f if x.strip()]

        path = os.path.join(PAYLOAD_DIR, filename)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return [x.strip() for x in f if x.strip()]

        return fallback

    def is_alive(self):
        try:
            r = self.session.get(self.target, timeout=6)
            return r.status_code < 500
        except:
            return False

    def get_params(self):
        return parse_qs(urlparse(self.target).query)

    def build_url(self, params):
        parsed = urlparse(self.target)
        query = urlencode(params, doseq=True)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{query}"

    def scan_sqli(self):
        print(f"\n{Fore.CYAN}[+]{Style.RESET_ALL} SQL Injection Scan")

        payloads = self.load_payloads(
            "sqli.txt",
            ["' OR '1'='1", "' OR 1=1--"]
        )

        errors = ["sql", "mysql", "syntax", "warning", "database"]
        params = self.get_params()

        if not params:
            print(f"{Fore.RED}[-]{Style.RESET_ALL} No parameters found for SQL")
            return

        for param in params:
            for payload in payloads:
                test = params.copy()
                test[param] = payload
                url = self.build_url(test)

                try:
                    r = self.session.get(url, timeout=7)
                    if any(e in r.text.lower() for e in errors):
                        print(f"{Fore.RED}[!]{Style.RESET_ALL} SQL Detected")
                        print(f"    Payload   : {Fore.YELLOW}{payload}")
                        print(f"    URL       : {Fore.YELLOW}{url}")
                except:
                    pass

    def scan_xss(self):
        print(f"\n{Fore.CYAN}[+]{Style.RESET_ALL} XSS Scan")

        payloads = self.load_payloads(
            "xss.txt",
            ["<script>alert(1)</script>"]
        )

        params = self.get_params()
        if not params:
            print(f"{Fore.RED}[-]{Style.RESET_ALL} No parameters found for XSS")
            return

        for param in params:
            for payload in payloads:
                test = params.copy()
                test[param] = payload
                url = self.build_url(test)

                try:
                    r = self.session.get(url, timeout=6)
                    if payload in r.text:
                        print(f"{Fore.RED}[!]{Style.RESET_ALL} XSS Detected")
                        print(f"    Payload   : {Fore.YELLOW}{payload}")
                        print(f"    URL       : {Fore.YELLOW}{url}")
                except:
                    pass

    def run(self, mode="all"):
        self.banner()

        if not self.is_alive():
            print(f"{Fore.RED}[-]{Style.RESET_ALL} Target not reachable")
            return

        if mode in ("sql", "all"):
            self.scan_sqli()

        if mode in ("xss", "all"):
            self.scan_xss()

        print(f"\n{Fore.GREEN}[+]{Style.RESET_ALL} Scan completed")

def main():
    parser = argparse.ArgumentParser(
        description="Web Vulnerability Scanner (SQL Injection & XSS)"
    )
    parser.add_argument("-u", "--url", help="Single target URL")
    parser.add_argument("--url-file", help="File with list of URLs")
    parser.add_argument("-w", "--wordlist", help="Custom payload wordlist")
    parser.add_argument(
        "-m", "--mode",
        choices=["sql", "xss", "all"],
        default="all",
        help="Scan mode"
    )

    args = parser.parse_args()
    targets = []

    if args.url:
        targets.append(args.url)

    if args.url_file:
        if not os.path.exists(args.url_file):
            print(f"{Fore.RED}[-]{Style.RESET_ALL} URL file not found")
            return
        with open(args.url_file, "r") as f:
            targets.extend([x.strip() for x in f if x.strip()])

    if not targets:
        print(f"{Fore.RED}[-]{Style.RESET_ALL} usage: python vuln_scanner.py -u <url> [-w wordlist] [-m mode]")
        return

    for target in targets:
        WebVulnerabilityScanner(
            target,
            wordlist=args.wordlist
        ).run(args.mode)


if __name__ == "__main__":
    main()