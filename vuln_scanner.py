import requests
from urllib.parse import urlparse, parse_qs, urlencode

requests.packages.urllib3.disable_warnings()

def vulns(url, payloads, mode='all'):
    session = requests.Session()
    session.verify = False
    findings = []
    parsed = urlparse(url)
    params = parse_qs(parsed.query)

    if not params:
        return findings
    
    def build(p):
        q = urlencode(p, doseq=True)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{q}"
    
    if mode in ("sql", "all"):
        errors = ["sql", "mysql", "syntax", "database"]
        for param in params:
            for payload in payloads["sqli"]:
                test = params.copy()
                test[param] = payload
                target = build(test)
                try:
                    r = session.get(target, timeout=6)
                    if any(e in r.text.lower() for e in errors):
                        findings.append(f"[SQL] {target}")
                        print(f"[SQL] {target}")        
                except:
                    pass

    if mode in ("xss", "all"):
        for param in params:
            for payload in payloads["xss"]:
                test = params.copy()
                test[param] = payload
                target = build(test)
                try:
                    r = session.get(target, timeout=6)
                    if payload in r.text:
                        findings.append(f"[XSS] {target}")
                        print(f"[XSS] {target}")
                except:
                    pass
    
    return findings