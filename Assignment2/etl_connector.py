from extract import extract_wayback
from transform import transform_wayback
from load import load_to_mongodb


def validate_raw_data(raw_data):
    
    if not raw_data:
        print("[ERROR] Empty API response.")
        return False

    if not isinstance(raw_data, dict):
        print("[ERROR] Invalid response type (expected dict).")
        return False

    if "url" not in raw_data:
        print("[ERROR] Missing 'url' in raw data.")
        return False

    if "status" not in raw_data:
        print("[ERROR] Missing 'status' field in raw data.")
        return False

    return True


def validate_transformed_data(data):

    if not isinstance(data, dict):
        print("[ERROR] Transformed data must be a dictionary.")
        return False

    if not data.get("url"):
        print("[ERROR] Missing 'url' in transformed data.")
        return False

    if "latest_snapshot_url" not in data and data.get("status") != "missing":
        print("[WARN] No latest snapshot found — possible missing archive.")

    return True



if __name__ == "__main__":

    url = input("Enter a URL to analyze: ").strip()
    simulate_invalid = input("Simulate invalid response? (y/n): ")
    if simulate_invalid == "y":
        simulate_invalid =  True
    else:
        simulate_invalid = False
    try:
        print("\n[PHASE 1] Extracting Wayback Machine data...")
        raw_data = extract_wayback(url, simulate_invalid = simulate_invalid)
    except Exception as e:
        print(f"[ERROR] Extraction failed: {e}")
        exit(1)


    if not validate_raw_data(raw_data):
        print("[INFO] Skipping transformation due to invalid raw response.")
        exit(1)


    try:
        print("\n[PHASE 2] Transforming Wayback data...")
        transformed = transform_wayback(raw_data)
    except Exception as e:
        print(f"[ERROR] Transformation failed: {e}")
        exit(1)

   
    if not validate_transformed_data(transformed):
        print("[INFO] Skipping load due to invalid transformed data.")
        exit(1)


    try:
        print("\n[PHASE 3] Loading data into MongoDB...")
        load_to_mongodb(transformed, "wayback_raw")
        print(f"[SUCCESS] Wayback data for {url} successfully ingested into 'wayback_raw'.")
    except Exception as e:
        print(f"[ERROR] MongoDB insertion failed: {e}")
        exit(1)
