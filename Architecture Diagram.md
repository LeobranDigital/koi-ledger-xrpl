# ARCHITECTURE DIAGRAM (JFIIP Phase-2 Ready)

---

## High-Level System Architecture

````
┌──────────────────────────────────────────┐
│  Breeder / Auction Platform              │
│  (Web Dashboard / Desktop / Mobile UI)  │
└───────────────┬──────────────────────────┘
                │
                │
Koi Registration / Transfer / Health Data
                ▼
┌──────────────────────────────────────────┐
│             KOI LEDGER CORE             │
│                                          │
│  • Koi Passport Management              │
│  • Ownership Engine                     │
│  • Health Record Tracking               │
│  • XRPL Transaction Builder             │
│  • QR/NFC Tag Generator                 │
│  • Compliance & Export Metadata         │
└───────────────┬──────────────────────────┘
                │
                │
    Hashed / Structured Metadata
                ▼
┌──────────────────────────────────────────┐
│               XRPL LAYER                │
│                                          │
│  • Immutable Transaction Records        │
│  • Memo-Encoded Event Metadata          │
│  • Atomic XRP Settlement                │
│  • Public Verification                  │
└───────────────┬──────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────┐
│         Buyer Verification App          │
│                                          │
│  Scan QR → Fetch TX Hash →              │
│  Validate on XRPL → Confirm Authenticity│
└──────────────────────────────────────────┘

```
