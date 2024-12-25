import requests
from concurrent.futures import ThreadPoolExecutor
import re

# Files containing proxies
PROXY_FILES = ['connect.txt', 'http.txt', 'https.txt', 'socks4.txt', 'socks5.txt']
REPORT_FILE = 'proxy_report.md'

# Function to test a single proxy
def test_proxy(proxy, proxy_type):
    try:
        proxies = {"http": proxy, "https": proxy}
        response = requests.get("https://httpbin.org/ip", proxies=proxies, timeout=5)
        if response.status_code == 200:
            ip_info = response.json()
            anonymity = (
                "High Anonymity"
                if "X-Forwarded-For" not in response.headers else "Anonymous"
            )
            return {
                "proxy": proxy,
                "type": proxy_type,
                "response_time": response.elapsed.total_seconds(),
                "anonymity": anonymity,
            }
    except Exception as e:
        print(f"Proxy {proxy} failed: {e}")  # Debug output
    return None

# Function to load and parse proxies from files
def load_proxies():
    proxies = []
    for file in PROXY_FILES:
        proxy_type = file.split('.')[0]
        try:
            with open(file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Extract IP:Port using regex
                    match = re.match(r'^(\d+\.\d+\.\d+\.\d+:\d+)', line)
                    if match:
                        proxies.append((match.group(1), proxy_type))
        except UnicodeDecodeError:
            with open(file, 'r', encoding='latin-1') as f:
                for line in f:
                    line = line.strip()
                    match = re.match(r'^(\d+\.\d+\.\d+\.\d+:\d+)', line)
                    if match:
                        proxies.append((match.group(1), proxy_type))
        except FileNotFoundError:
            print(f"Warning: {file} not found.")
    return proxies

# Function to generate the Markdown report
def generate_report(results):
    with open(REPORT_FILE, 'w') as f:
        f.write("# Proxy Test Report\n\n")
        f.write("| Proxy           | Type    | Response Time (s) | Anonymity       |\n")
        f.write("|-----------------|---------|-------------------|-----------------|\n")
        for result in results:
            f.write(
                f"| {result['proxy']} | {result['type']} | {result['response_time']:.2f} | {result['anonymity']} |\n"
            )

# Main execution
if __name__ == "__main__":
    print("Loading proxies...")
    proxies = load_proxies()
    if not proxies:
        print("No proxies found. Ensure proxy files are populated.")
        exit(1)
    print(f"Loaded {len(proxies)} proxies.")
    
    results = []
    print("Testing proxies...")
    with ThreadPoolExecutor(max_workers=100) as executor:
        for proxy_result in executor.map(lambda p: test_proxy(*p), proxies):
            if proxy_result:
                results.append(proxy_result)
    
    if results:
        print(f"Tested {len(results)} working proxies. Generating report...")
        generate_report(results)
        print(f"Report generated: {REPORT_FILE}")
    else:
        print("No working proxies found. No report generated.")
