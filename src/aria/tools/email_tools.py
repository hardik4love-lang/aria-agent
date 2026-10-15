"""
Email Management Tools: IMAP and SMTP Integration with Prompt Injection Sanitization.
"""

import os
from typing import List, Dict, Any, Optional
from aria.security.guards import PromptInjectionGuard, CredentialRedactor


class EmailTools:
    """Provides safe, isolated tools for reading, drafting, and sending emails."""

    def __init__(self):
        self.account = os.environ.get("EMAIL_ACCOUNT")
        self.password = os.environ.get("EMAIL_APP_PASSWORD")
        self.imap_server = os.environ.get("IMAP_SERVER", "imap.gmail.com")
        self.smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.environ.get("SMTP_PORT", 587))

    def email_list_unread(self, max_count: int = 10) -> List[Dict[str, Any]]:
        """Lists unread emails from the inbox with sanitized subjects and senders."""
        if not self.account or not self.password:
            # Fallback mock for testing and local simulation
            return [
                {
                    "uid": "101",
                    "sender": "colleague@example.com",
                    "subject": "Review requested: Quarterly Roadmap",
                    "date": "2026-10-15T10:00:00Z",
                    "snippet": "Could you please take a look at the proposed changes in the repository?"
                }
            ]

        try:
            import imaplib
            import email
            from email.header import decode_header

            mail = imaplib.IMAP4_SSL(self.imap_server)
            mail.login(self.account, self.password)
            mail.select("INBOX")

            status, messages = mail.search(None, "UNSEEN")
            if status != "OK":
                return []

            email_ids = messages[0].split()
            results = []

            for uid in email_ids[-max_count:]:
                res, data = mail.fetch(uid, "(RFC822.HEADER)")
                if res != "OK":
                    continue
                raw_email = data[0][1]
                msg = email.message_from_bytes(raw_email)
                subject, encoding = decode_header(msg.get("Subject", ""))[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding or "utf-8", errors="ignore")

                sender = msg.get("From", "unknown")
                is_safe, clean_subject, _ = PromptInjectionGuard.inspect(subject)

                results.append({
                    "uid": uid.decode("utf-8"),
                    "sender": CredentialRedactor.redact(sender),
                    "subject": clean_subject,
                    "date": msg.get("Date", "")
                })

            mail.close()
            mail.logout()
            return results
        except Exception as e:
            return [{"error": f"IMAP failure: {str(e)}"}]

    def email_read(self, uid: str) -> Dict[str, Any]:
        """Reads full email body by UID, passing content through injection quarantine."""
        if not self.account or not self.password:
            return {
                "uid": uid,
                "sender": "colleague@example.com",
                "subject": "Review requested: Quarterly Roadmap",
                "body": PromptInjectionGuard.wrap_external_content(
                    "Hi ARIA,\nPlease review the latest pull request on the infrastructure repo and check if the free tier limits hold.\nThanks!",
                    source_identifier=f"email:{uid}"
                )
            }

        try:
            import imaplib
            import email

            mail = imaplib.IMAP4_SSL(self.imap_server)
            mail.login(self.account, self.password)
            mail.select("INBOX")

            res, data = mail.fetch(uid.encode("utf-8"), "(RFC822)")
            if res != "OK":
                return {"error": f"Message UID {uid} not found"}

            msg = email.message_from_bytes(data[0][1])
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        payload = part.get_payload(decode=True)
                        if payload:
                            body = payload.decode(errors="ignore")
                            break
            else:
                body = msg.get_payload(decode=True).decode(errors="ignore")

            mail.close()
            mail.logout()

            safe_body = PromptInjectionGuard.wrap_external_content(body, source_identifier=f"email:{uid}")
            return {
                "uid": uid,
                "sender": CredentialRedactor.redact(msg.get("From", "")),
                "subject": CredentialRedactor.redact(msg.get("Subject", "")),
                "body": safe_body
            }
        except Exception as e:
            return {"error": f"Error fetching email {uid}: {str(e)}"}

    def email_draft_reply(self, uid: str, recipient: str, subject: str, body: str) -> Dict[str, Any]:
        """Creates a prepared draft without transmitting it."""
        draft = {
            "draft_id": f"draft_{uid}",
            "reply_to_uid": uid,
            "recipient": recipient,
            "subject": f"Re: {subject}" if not subject.startswith("Re:") else subject,
            "body": body,
            "status": "ready_for_review"
        }
        return draft

    def email_send(self, recipient: str, subject: str, body: str) -> Dict[str, Any]:
        """Sends an email via SMTP. High-risk action guarded by human approval gate."""
        if not self.account or not self.password:
            return {
                "success": True,
                "status": "mock_sent",
                "recipient": recipient,
                "subject": subject
            }

        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            msg = MIMEMultipart()
            msg["From"] = self.account
            msg["To"] = recipient
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.account, self.password)
                server.send_message(msg)

            return {
                "success": True,
                "status": "transmitted",
                "recipient": recipient
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"SMTP delivery failure: {str(e)}"
            }
