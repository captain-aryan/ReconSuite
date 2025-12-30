from subdomain import subdomains
from dirbuster import dirb
from vuln_scanner import vulns

def payloads():
    return {
        "xss": open("xss.txt").read().splitlines(),
        "sql": open("sql.txt").read().splitlines()
    }

def main():
    target = input("[+] Domain: ").strip()
    threads = 20
    payloads = payloads()
    subdomains = subdomains(target, threads, "subdomains_small.txt")

    with open("subdomains.txt", 'w') as f:
        f.write("\n".join(subdomains))

    for sub in subdomains:
        dirs = dirb(sub, threads, "dirb.txt")

        with open("dirs.txt", 'a') as f:
            for d in dirs:
                f.write(d + "\n")

        for d in dirs:
            if "?" in d:
                vuln = vulns(d, payloads, mode='all')
                with open("vuln.txt", 'a') as f:
                    for v in vulns:
                        f.write(v + "\n")

if __name__ == "__main__":
    main()
