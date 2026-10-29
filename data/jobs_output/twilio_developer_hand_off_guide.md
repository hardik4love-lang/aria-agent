# Full Twilio Architecture & Developer Hand-off Guide
**Client:** Shir (@shirh5)  
**Project:** Full Twilio Account, IVR, A2P SMS & WhatsApp Business Setup  

---

## 1. Number Routing Architecture
- **Line 1 (Main Line):** Assigned to Twilio Studio Flow (`twilio_studio_flow_ivr.json`).
  - Option 1 -> Warm transfer to Line 2 (Receptionist).
  - Option 2 -> Voicemail recording with automatic transcription callback.
  - Option 3 -> Team ring group with fallback to voicemail.
- **Line 2 (Receptionist Direct Line):** Configured with `<Conference>` support for warm multi-party transfers and direct inbound/outbound calls.

---

## 2. Conference & Ad-Hoc Warm Transfer TwiML
When the receptionist needs to pull an additional party onto the line or perform a warm transfer, use this TwiML endpoint:
```xml
<Response>
    <Dial>
        <Conference startConferenceOnEnter="true" endConferenceOnExit="false" waitUrl="https://twimlets.com/holdmusic?Bucket=com.twilio.music.classical">
            Room_{{CallSid}}
        </Conference>
    </Dial>
</Response>
```
To dial in the third party via API (Node.js/Python):
```bash
curl -X POST "https://api.twilio.com/2010-04-01/Accounts/$TWILIO_ACCOUNT_SID/Calls.json" \
  --data-urlencode "To=+1THIRD_PARTY_NUMBER" \
  --data-urlencode "From=+1RECEPTIONIST_NUMBER" \
  --data-urlencode "Url=https://your-domain.com/join-conference?room=Room_{{CallSid}}" \
  -u $TWILIO_ACCOUNT_SID:$TWILIO_AUTH_TOKEN
```

---

## 3. A2P 10DLC Compliance Checklist (US Messaging)
To guarantee your SMS is approved by carriers without filtering:
1. **Brand Registration:** Low-Volume Standard or Sole Proprietor Brand registered with official business name, EIN, and address.
2. **Campaign Details:**
   - Use Case: Mixed / Customer Care.
   - Sample Messages: Include opt-out keyword (`Reply STOP to cancel`).
   - Message Flow & Opt-in: Direct link to website contact form with explicit checkbox: *"By submitting this form, you consent to receive SMS notifications. Reply STOP to opt out."*

---

## 4. WhatsApp Business Sender Activation
1. Inside **Twilio Console -> Messaging -> Senders -> WhatsApp Senders**.
2. Link your Facebook Business Manager Account ID.
3. Submit display name and business profile details.
4. Webhook URL for incoming WhatsApp chats: `https://your-domain.com/webhooks/twilio/whatsapp`.

---

## 5. Developer Environment Variables
```env
TWILIO_ACCOUNT_SID=ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_MAIN_NUMBER=+1XXXXXXXXXX
TWILIO_RECEPTIONIST_NUMBER=+1XXXXXXXXXX
TWILIO_STUDIO_FLOW_SID=FWXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
TWILIO_MESSAGING_SERVICE_SID=MGXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```
