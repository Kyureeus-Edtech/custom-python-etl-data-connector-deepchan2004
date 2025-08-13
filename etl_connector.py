from extract import extract_ssllabs
from transform import transform_ssllabs_data
from load import load_to_mongodb

def validate_raw_data(raw_data):

    if not raw_data:
        print("[ERROR] Empty API response.")
        return False
    if "status" not in raw_data:
        print("[ERROR] Invalid API payload — missing 'status'.")
        return False
    return True

def validate_transformed_data(data):

    if not isinstance(data, dict):
        print("[ERROR] Transformed data is not a dict.")
        return False
    if not data.get("host"):
        print("[ERROR] Transformed data missing 'host'.")
        return False
    if not isinstance(data.get("endpoints"), list):
        print("[ERROR] Endpoints field is not a list.")
        return False
    return True

if __name__ == "__main__":
    domain = input("Enter a domain: ").strip()
    try:
        raw_data = extract_ssllabs(domain)
    except Exception as e:
        print(f"[ERROR] Failed to extract from API: {e}")
        exit(1)

    if not validate_raw_data(raw_data):
        print("[INFO] Skipping insertion due to invalid API response.")
        exit(1)

    if raw_data.get("status") == "ERROR":
        print(f"[ERROR] API returned error for {domain}: {raw_data}")
        exit(1)

    try:
        transformed = transform_ssllabs_data(raw_data)
    except Exception as e:
        print(f"[ERROR] Transformation failed: {e}")
        exit(1)

    if not validate_transformed_data(transformed):
        exit(1)

    try:
        load_to_mongodb(transformed, "ssllabs_raw")
        print(f"[SUCCESS] Ingested SSL Labs data for {domain} into ssllabs_raw")
    except Exception as e:
        print(f"[ERROR] Failed to insert into MongoDB: {e}")
        exit(1)
