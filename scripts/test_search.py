import httpx

headers = {
    'User-Agent': 'ARIAHeritageBot/1.0 (https://github.com/hardik4love-lang/aria-agent; bot@aria.ai)'
}
# Search for files with media type video on commons
url = 'https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch=Konark+Sun+Temple&srnamespace=6&srlimit=10&format=json'
r = httpx.get(url, headers=headers, timeout=10.0)
print("Status:", r.status_code)
print(r.text[:300])
