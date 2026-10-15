"""
ARIA Persistent Daemon (Runs on Oracle Cloud Always Free ARM VM).
Monitors IMAP IDLE for real-time email arrivals and dispatches GitHub Actions workflows (<5s latency).
"""

import os
import sys
import time
import socket
import imaplib
import email
from email.header import decode_header
import httpx


GITHUB_REPO = os.environ.get("GITHUB_REPOSITORY", "yourusername/aria-agent")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
EMAIL_ACCOUNT = os.environ.get("EMAIL_ACCOUNT", "")
EMAIL_APP_PASSWORD = os.environ.get("EMAIL_APP_PASSWORD", "")
IMAP_SERVER = os.environ.get("IMAP_SERVER", "imap.gmail.com")
HEARTBEAT_INTERVAL_SECONDS = 300


def dispatch_github_workflow(event_type: str, client_payload: dict) -> bool:
    """Dispatches a repository_dispatch event to trigger GitHub Actions runner immediately."""
    if not GITHUB_TOKEN or "yourusername" in GITHUB_REPO:
        print(f"[DAEMON] Simulated dispatch event '{event_type}' with payload: {client_payload}")
        return True

    url = f"https://api.github.com/repos/{GITHUB_REPO}/dispatches"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "event_type": event_type,
        "client_payload": client_payload
    }

    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(url, headers=headers, json=data)
            if resp.status_code == 204:
                print(f"[DAEMON] Successfully dispatched '{event_type}' to GitHub Actions.")
                return True
            print(f"[DAEMON] Failed dispatch: HTTP {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"[DAEMON] Network error dispatching to GitHub: {str(e)}")
    return False


def listen_imap_idle():
    """Listens for new incoming emails using IMAP IDLE push."""
    print(f"[DAEMON] Connecting to {IMAP_SERVER} as {EMAIL_ACCOUNT}...")

    if not EMAIL_ACCOUNT or not EMAIL_APP_PASSWORD:
        print("[DAEMON] Email credentials not configured. Running in polling simulation mode.")
        while True:
            time.sleep(60)
            print("[DAEMON] Heartbeat: Daemon healthy, awaiting events...")

    while True:
        try:
            mail = imaplib.IMAP4_SSL(IMAP_SERVER)
            mail.login(EMAIL_ACCOUNT, EMAIL_APP_PASSWORD)
            mail.select("INBOX")
            print("[DAEMON] IMAP authenticated. Entering IDLE push listening loop...")

            while True:
                # Issue IDLE command
                tag = mail._new_tag()
                mail.send(f"{tag.decode('ascii')} IDLE\r\n".encode("utf-8"))
                
                # Wait for push update from mail server (timeout after 10 min to refresh connection)
                mail.socket().settimeout(600)
                try:
                    line = mail.readline()
                    if line:
                        # Server signaled incoming mail change
                        mail.send(b"DONE\r\n")
                        mail.readline()  # Read IDLE completed tag
                        print("[DAEMON] Push event received from mail server! Dispatching agent...")
                        dispatch_github_workflow("email-received", {"timestamp": time.time()})
                except socket.timeout:
                    # Timeout reached; refresh IDLE to keep socket alive
                    mail.send(b"DONE\r\n")
                    mail.readline()
                    print("[DAEMON] IDLE refreshed (keep-alive heartbeat).")

        except Exception as e:
            print(f"[DAEMON] IMAP connection dropped: {str(e)}. Reconnecting in 15 seconds...")
            time.sleep(15)


if __name__ == "__main__":
    print("=" * 60)
    print("  ARIA OCI Always Free Persistent Daemon")
    print("=" * 60)
    listen_imap_idle()
