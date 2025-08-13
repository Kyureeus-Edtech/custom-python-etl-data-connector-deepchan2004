from datetime import datetime, timezone

def map_grade_to_risk(grade):
    mapping = {
        "A+": "low", "A": "low", "A-": "medium",
        "B": "medium", "C": "high", "D": "high",
        "E": "critical", "F": "critical", "T": "critical"
    }
    return mapping.get(grade, "unknown")

def days_until_expiry(not_after_timestamp):
    if not not_after_timestamp:
        return None
    expiry_date = datetime.fromtimestamp(not_after_timestamp / 1000, tz=timezone.utc)
    return (expiry_date - datetime.now(timezone.utc)).days

def transform_ssllabs_data(raw_data):
    endpoints = raw_data.get("endpoints", [])
    enriched_endpoints = []
    risk_levels = ["low", "medium", "high", "critical"]

    worst_risk = "low"
    for ep in endpoints:
        grade = ep.get("grade")
        risk = map_grade_to_risk(grade)
        if risk_levels.index(risk) > risk_levels.index(worst_risk):
            worst_risk = risk

        details = ep.get("details", {})
        cert = details.get("cert", {})
        expiry_days = days_until_expiry(cert.get("notAfter"))

        protocols = [
            f"{p.get('name')} {p.get('version')}"
            for p in details.get("protocols", [])
        ]

       
        suites_data = details.get("suites", {})
        if isinstance(suites_data, dict):
            cipher_list = []
            for v in suites_data.values():
                if isinstance(v, list):
                    cipher_list.extend(v)
        elif isinstance(suites_data, list):
            cipher_list = suites_data
        else:
            cipher_list = []

        weak_ciphers = any(
            "RC4" in c.get("name", "") or c.get("strength", 0) < 128
            for c in cipher_list
        )
       

        enriched_endpoints.append({
            "ipAddress": ep.get("ipAddress"),
            "grade": grade,
            "risk": risk,
            "expiryDays": expiry_days,
            "protocols": protocols,
            "weakCiphers": weak_ciphers,
            "ocspStapling": details.get("stapling", 0) == 1
        })

    return {
        "host": raw_data.get("host"),
        "status": raw_data.get("status"),
        "worstRisk": worst_risk,
        "endpoints": enriched_endpoints,
        "timestamp": int(datetime.now(timezone.utc).timestamp() * 1000),
        "ingestedAt": datetime.now(timezone.utc).isoformat(),
        "raw": raw_data
    }
