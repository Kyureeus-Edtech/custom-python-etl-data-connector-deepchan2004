import time
import requests

AVAILABLE_URL = "https://archive.org/wayback/available"
SAVE_URL = "https://web.archive.org/save/"
CDX_URL = "https://web.archive.org/cdx/search/cdx"

def extract_wayback(url: str,  simulate_invalid, max_retries: int = 5, backoff_factor: int = 5) -> dict:
    
    def _handle_backoff(retries):
        wait_time = backoff_factor * (retries + 1)
        print(f"[WAIT] Retrying in {wait_time}s...\n")
        time.sleep(wait_time)

    retries = 0
    while retries < max_retries:
        try:
            print(f"[STEP 1] Checking snapshot availability for: {url}")
            available_resp = requests.get(AVAILABLE_URL, params={"url": url}, timeout=30)

            if url.endswith("/simulate429"):
                available_resp.status_code = 429
            if available_resp.status_code == 429:
                print("[WARN] Rate limited by Wayback API.")
                _handle_backoff(retries)
                retries += 1
                continue

            available_resp.raise_for_status()
            available_data = available_resp.json()
            archived_snap = available_data.get("archived_snapshots", {}).get("closest")

            if archived_snap:
                snapshot_url = archived_snap["url"]
                timestamp = archived_snap["timestamp"]
                print(f"[INFO] Snapshot already exists: {snapshot_url}")

                
                print("[STEP 2] Fetching all historical snapshots from CDX API...")
                cdx_params = {"url": url, "output": "json", "fl": "timestamp,original,statuscode,mimetype,length","limit": 5}
                cdx_resp = requests.get(CDX_URL, params=cdx_params, timeout=20)
                cdx_resp.raise_for_status()
                cdx_data = cdx_resp.json()
                if simulate_invalid:
                    available_resp.status_code = 200
                    available_resp._content = b"this is not valid json"
                    return available_resp
                return {
                    "status": "exists",
                    "url": url,
                    "latest_snapshot": {
                        "timestamp": timestamp,
                        "snapshot_url": snapshot_url
                    },
                    "history": cdx_data[1:] if len(cdx_data) > 1 else [],
                    "source": "wayback"
                }

            
            print(f"[STEP 3] No snapshot found. Requesting new archive for: {url}")
            save_resp = requests.get(f"{SAVE_URL}{url}", timeout=20)
            if save_resp.status_code in (200, 201):
                print("[INFO] Archive request successful, waiting for snapshot creation...")
                time.sleep(15)  
                continue
            else:
                print(f"[WARN] Save request returned {save_resp.status_code}")
                _handle_backoff(retries)

        except requests.exceptions.Timeout:
            print(f"[WARN] Timeout while processing {url}.")
            _handle_backoff(retries)

        except requests.RequestException as e:
            print(f"[ERROR] Network/API error: {e}")
            _handle_backoff(retries)

        retries += 1

    raise RuntimeError(f"[FAIL] Could not obtain Wayback data for {url} after {max_retries} retries.")


