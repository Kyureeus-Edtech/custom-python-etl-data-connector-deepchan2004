import time
import requests

BASE_URL = "https://api.ssllabs.com/api/v3/analyze"

def extract_ssllabs(domain, max_retries=5, backoff_factor=5):
    params = {"host": domain, "publish": "off", "all": "done"}
    retries = 0

    while retries < max_retries:
        try:
            resp = requests.get(BASE_URL, params=params, timeout=15)
            #resp.status_code = 429  # Simulate rate limit for testing
            # Uncomment the line above to simulate rate limiting during testing
            if resp.status_code == 429: 
                wait_time = backoff_factor * (retries + 1)
                print(f"[WARN] Rate limited by API. Retrying in {wait_time}s...")
                time.sleep(wait_time)
                retries += 1
                continue

            resp.raise_for_status()
            data = resp.json()

            status = data.get("status")
            if status in ("READY", "ERROR"):
                return data

            
            print(f"[INFO] Scan status: {status}. Polling again in 10s...")
            time.sleep(10)

        except requests.exceptions.Timeout:
            wait_time = backoff_factor * (retries + 1)
            print(f"[WARN] Request timed out. Retrying in {wait_time}s...")
            time.sleep(wait_time)
            retries += 1

        except requests.RequestException as e:
            wait_time = backoff_factor * (retries + 1)
            print(f"[ERROR] Network/API error: {e}. Retrying in {wait_time}s...")
            time.sleep(wait_time)
            retries += 1

    raise RuntimeError(f"Failed to fetch SSL Labs data for {domain} after {max_retries} retries")
