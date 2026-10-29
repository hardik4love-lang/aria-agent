"""
Automated Multi-Source Market Price Tracker & Excel Export
Engineered by ARIA to automate competitor and commodity price monitoring
"""
import csv
import datetime
from typing import List, Dict

class PriceTracker:
    def __init__(self, output_file: str = "market_prices_daily.csv"):
        self.output_file = output_file
        self.records: List[Dict] = []

    def log_price(self, sku: str, item_name: str, competitor: str, price: float, currency: str = "USD", in_stock: bool = True):
        record = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sku": sku,
            "item_name": item_name,
            "competitor": competitor,
            "price": price,
            "currency": currency,
            "in_stock": "YES" if in_stock else "NO"
        }
        self.records.append(record)
        return record

    def export_csv(self):
        fieldnames = ["timestamp", "sku", "item_name", "competitor", "price", "currency", "in_stock"]
        with open(self.output_file, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.records)
        return f"Successfully exported {len(self.records)} price points to {self.output_file}"

if __name__ == "__main__":
    tracker = PriceTracker()
    tracker.log_price("SKU-1001", "Enterprise Cloud Gateway", "Vendor A", 299.00)
    tracker.log_price("SKU-1001", "Enterprise Cloud Gateway", "Vendor B", 285.50)
    tracker.log_price("SKU-1002", "Smart Terminal Node", "Vendor A", 149.99)
    print(tracker.export_csv())
