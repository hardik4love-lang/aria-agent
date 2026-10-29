"""
ARIA Autonomous Operations Suite v2
Email Filtering, Document Compilation, and Calendar Coordination
"""
def filter_vip_communications(inbox_items: list) -> list:
    vip_domains = ["investor.com", "client.com", "partner.io"]
    flagged = []
    for item in inbox_items:
        sender = item.get("sender", "")
        if any(d in sender for d in vip_domains):
            flagged.append({
                "action": "FLAG_URGENT",
                "subject": item.get("subject"),
                "sender": sender
            })
    return flagged

if __name__ == "__main__":
    sample = [
        {"sender": "ceo@investor.com", "subject": "Term sheet update"},
        {"sender": "newsletter@spam.org", "subject": "Weekly digest"}
    ]
    print(filter_vip_communications(sample))
