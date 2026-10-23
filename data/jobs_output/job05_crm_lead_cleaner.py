#!/usr/bin/env python3
import re
import csv
from typing import List, Dict

PHONE_CLEAN_RE = re.compile(r"\D")
EMAIL_RE = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

def normalize_phone(raw: str, default_country_code: str = "+1") -> str:
    digits = PHONE_CLEAN_RE.sub("", raw or "")
    if len(digits) == 10:
        return f"{default_country_code}{digits}"
    elif len(digits) == 11 and digits.startswith("1"):
        return f"+{digits}"
    return f"+{digits}" if digits else ""

def clean_lead_records(input_csv: str, output_csv: str) -> Dict[str, int]:
    seen = set()
    cleaned = []
    with open(input_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = (row.get("email") or "").strip().lower()
            if not EMAIL_RE.match(email):
                continue
            if email in seen:
                continue
            seen.add(email)
            phone = normalize_phone(row.get("phone", ""))
            cleaned.append({
                "first_name": row.get("first_name", "").strip().title(),
                "last_name": row.get("last_name", "").strip().title(),
                "email": email,
                "phone": phone,
                "company": row.get("company", "").strip(),
                "lead_status": "QUALIFIED"
            })

    if cleaned:
        with open(output_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=cleaned[0].keys())
            writer.writeheader()
            writer.writerows(cleaned)
    return {"total_cleaned": len(cleaned)}
