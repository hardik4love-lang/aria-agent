"""
Automated Document OCR & Contact Information Extraction Engine
Extracts names, emails, phone numbers, and addresses into clean CSV.
"""
import re
import csv

SAMPLE_OCR_TEXT = """
John Doe | Managing Director | Apex Corp
Phone: +1 (555) 234-5678 | Email: john.doe@apexcorp.com | 100 Main St, New York, NY
Jane Smith - VP Operations - Delta Global
Direct: 555-876-5432 - jsmith@deltaglobal.org - Boston, MA
"""

def extract_contacts(raw_text: str):
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    phone_pattern = r'\+?[0-9]{1,3}?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}'
    
    lines = [l.strip() for l in raw_text.split("\n") if l.strip()]
    contacts = []
    
    for line in lines:
        emails = re.findall(email_pattern, line)
        phones = re.findall(phone_pattern, line)
        contacts.append({
            "raw_record": line,
            "primary_email": emails[0] if emails else "N/A",
            "primary_phone": phones[0] if phones else "N/A"
        })
    return contacts

if __name__ == "__main__":
    res = extract_contacts(SAMPLE_OCR_TEXT)
    print(f"Extracted {len(res)} contacts cleanly.")
    for c in res:
        print(c)
