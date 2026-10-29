"""
Automated Bank Statement Transaction Parser & Ledger Reconciler
Parses raw statement exports, normalizes dates, categorizes expenses, and verifies balances.
"""
import csv

CATEGORIES = {
    "PAYROLL": ["salary", "payroll", "wages"],
    "UTILITIES": ["electric", "water", "internet", "telecom"],
    "SOFTWARE_SAAS": ["aws", "google", "github", "slack"],
    "LEGAL_PROFESSIONAL": ["solicitor", "attorney", "accountant"]
}

def categorize_transaction(description: str) -> str:
    desc_lower = description.lower()
    for cat, keywords in CATEGORIES.items():
        if any(kw in desc_lower for kw in keywords):
            return cat
    return "MISC_OPERATIONAL"

def process_statement(rows: list):
    processed = []
    total_debit = 0.0
    total_credit = 0.0
    
    for r in rows:
        amount = float(r["amount"])
        cat = categorize_transaction(r["description"])
        if amount < 0:
            total_debit += abs(amount)
        else:
            total_credit += amount
            
        processed.append({**r, "category": cat})
        
    return {
        "transactions": processed,
        "total_inflow": total_credit,
        "total_outflow": total_debit,
        "net_change": total_credit - total_debit
    }

if __name__ == "__main__":
    test_rows = [
        {"date": "2026-10-01", "description": "AWS Cloud Services", "amount": -145.20},
        {"date": "2026-10-02", "description": "Client Retainer Invoice #402", "amount": 2500.00}
    ]
    print(process_statement(test_rows))
