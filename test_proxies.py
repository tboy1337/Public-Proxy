import requests
from concurrent.futures import ThreadPoolExecutor
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import os

@dataclass
class ProxyResult:
    proxy: str
    type: str
    response_time: float
    anonymity: str
    country: str

# Constants
PROXY_FILES = ['connect.txt', 'http.txt', 'https.txt', 'socks4.txt', 'socks5.txt']
REPORTS_DIR = 'proxy_reports'

def test_proxy(proxy_info: Tuple[str, str, str]) -> Optional[ProxyResult]:
    proxy, proxy_type, country = proxy_info
    try:
        proxies = {"http": f"{proxy_type}://{proxy}", "https": f"{proxy_type}://{proxy}"}
        response = requests.get("https://httpbin.org/ip", proxies=proxies, timeout=10)
        
        if response.status_code == 200:
            anonymity = (
                "High Anonymity"
                if "X-Forwarded-For" not in response.headers
                else "Anonymous"
            )
            return ProxyResult(
                proxy=proxy,
                type=proxy_type,
                response_time=response.elapsed.total_seconds(),
                anonymity=anonymity,
                country=country
            )
    except Exception as e:
        print(f"Proxy {proxy} ({country}) failed: {e}")
    return None

def load_proxies() -> List[Tuple[str, str, str]]:
    proxies = []
    for file in PROXY_FILES:
        proxy_type = file.split('.')[0]
        try:
            with open(file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Extract IP:Port:Country using regex
                    match = re.match(r'^(\d+\.\d+\.\d+\.\d+:\d+):(.+)$', line)
                    if match:
                        proxy, country = match.groups()
                        proxies.append((proxy, proxy_type, country))
        except (UnicodeDecodeError, FileNotFoundError) as e:
            print(f"Warning processing {file}: {e}")
    return proxies

def generate_report(results: List[ProxyResult]) -> Dict[str, List[ProxyResult]]:
    # Create reports directory if it doesn't exist
    os.makedirs(REPORTS_DIR, exist_ok=True)
    
    # Group results by proxy type
    grouped_results = {}
    for result in results:
        if result.type not in grouped_results:
            grouped_results[result.type] = []
        grouped_results[result.type].append(result)
    
    # Generate individual reports for each proxy type
    for proxy_type, type_results in grouped_results.items():
        # Sort by response time
        type_results.sort(key=lambda x: x.response_time)
        
        report_path = os.path.join(REPORTS_DIR, f'{proxy_type}_proxies.md')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"# {proxy_type.upper()} Proxy Test Report\n\n")
            f.write(f"Total working proxies: {len(type_results)}\n\n")
            f.write("| Proxy | Response Time (s) | Anonymity | Country |\n")
            f.write("|-------|------------------|-----------|----------|\n")
            
            for result in type_results:
                f.write(
                    f"| {result.proxy} | {result.response_time:.2f} | {result.anonymity} | {result.country} |\n"
                )
    
    # Generate summary report
    with open(os.path.join(REPORTS_DIR, 'summary.md'), 'w', encoding='utf-8') as f:
        f.write("# Proxy Test Summary\n\n")
        
        total_proxies = sum(len(proxies) for proxies in grouped_results.values())
        f.write(f"Total working proxies: {total_proxies}\n\n")
        
        f.write("## Breakdown by Type\n\n")
        for proxy_type, type_results in grouped_results.items():
            avg_response = sum(r.response_time for r in type_results) / len(type_results)
            f.write(f"### {proxy_type.upper()}\n")
            f.write(f"- Working proxies: {len(type_results)}\n")
            f.write(f"- Average response time: {avg_response:.2f}s\n")
            
            # Country statistics
            countries = {}
            for result in type_results:
                countries[result.country] = countries.get(result.country, 0) + 1
            
            f.write("- Top countries:\n")
            for country, count in sorted(countries.items(), key=lambda x: x[1], reverse=True)[:5]:
                f.write(f"  - {country}: {count} proxies\n")
            f.write("\n")
    
    return grouped_results

def main():
    print("Loading proxies...")
    proxies = load_proxies()
    if not proxies:
        print("No proxies found. Ensure proxy files are populated.")
        exit(1)
    print(f"Loaded {len(proxies)} proxies.")
    
    results = []
    print("Testing proxies...")
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(test_proxy, proxy_info) for proxy_info in proxies]
        for future in futures:
            result = future.result()
            if result:
                results.append(result)
    
    if results:
        print(f"Found {len(results)} working proxies. Generating reports...")
        grouped_results = generate_report(results)
        print(f"Reports generated in {REPORTS_DIR}/")
        
        # Print summary to console
        for proxy_type, type_results in grouped_results.items():
            print(f"{proxy_type.upper()}: {len(type_results)} working proxies")
    else:
        print("No working proxies found. No reports generated.")

if __name__ == "__main__":
    main()
