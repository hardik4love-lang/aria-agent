import os
import json
import time
import sys

sys.path.append('D:/aria-agent/src')
from aria.bounties.fast_cash_engine import FastCashEngine

def main():
    bounties_path = 'D:/aria-agent/dashboard/bounties.json'
    with open(bounties_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Execute fast-cash cycle to get fresh data
    res = FastCashEngine.execute_master_fast_cash_cycle()
    with open(res['feed_file'], 'r', encoding='utf-8') as f:
        feed = json.load(f)

    # Attach Top 5 Gemini Platforms and Live Urgent Feed
    data['top5_gemini_platforms'] = feed.get('top5_platforms', [])
    data['live_freelancer_urgent_jobs'] = feed.get('live_freelancer_urgent_jobs', [])
    data['packaged_solutions'] = feed.get('packaged_solutions', [])
    data['last_updated'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())

    with open(bounties_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    print('Successfully synchronized dashboard/bounties.json with Top 5 Gemini Platforms + Live Freelancer Feed!')

if __name__ == '__main__':
    main()
