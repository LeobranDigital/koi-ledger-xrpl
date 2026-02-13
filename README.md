# 🐟 KOI LEDGER – Digital Passport for Premium Nishikigoi on XRPL

![Koi Ledger](Koi.png)
![Koi Passport](Website%20koiledger/koipassport.png)

### Repository: **koi-ledger-xrpl**

🌐 Website: https://leobran.com/koiledger/

---

## 🎯 Mission

To bring **transparency, trust, and global verifiability** to Japan’s premium Nishikigoi industry by creating immutable digital identities anchored on the **XRP Ledger (XRPL)**.

Koi Ledger establishes a blockchain-based provenance system that protects breeders, auction houses, and collectors from fraud and misinformation.

---

## 🌏 The Problem

The global Nishikigoi market handles high-value koi worth thousands to millions of dollars. However:

- Ownership history can be unclear
- Health records can be manipulated
- Breeder lineage can be falsified
- Auction transparency is limited
- International buyers lack trust mechanisms

---

## 💡 The Solution

Koi Ledger creates a **tamper-proof digital passport** for each premium koi.

Every critical lifecycle event is:
- Stored off-chain for UI access
- Anchored on XRPL for immutable verification
- Publicly verifiable via transaction hash

---

## 🧬 What Gets Recorded

- 🐣 Breeder origin
- 🌳 Lineage & bloodline
- 🏥 Health and vaccination logs
- 🔄 Ownership transfers
- 🏷 Auction events
- 💰 XRP settlement proof

---

## 👥 Core Users

- Koi Breeders
- Auction Houses
- Private Collectors
- Veterinarians
- Exporters
- International Buyers

---

## 🚀 Core MVP Features

### 1️⃣ Dashboard
- Lists all registered Koi
- Thumbnail preview
- Search by Name or Koi ID

### 2️⃣ Koi Digital Passport
- Complete lineage record
- Health history timeline
- Ownership audit trail
- XRPL transaction hash display
- **Verify Ownership** button (ledger confirmation)

### 3️⃣ Register New Koi
- Enter breeder + lineage data
- Assign initial owner
- Submit → XRPL transaction created
- Transaction hash stored for verification

### 4️⃣ Transfer Ownership
- Select Koi
- Choose new owner
- Execute XRPL-backed transfer
- Immutable transfer history recorded

### 5️⃣ Health Log Updates
- Timestamped treatments or vaccinations
- Optional QR/NFC integration
- XRPL memo anchor for audit trail

---

## 🔐 XRPL Integration

Each lifecycle event writes verifiable metadata to the XRPL Memo field.

Example:

```json
{
  "koi_id": "KOI-JPN-01-20260203-0001",
  "event": "TRANSFER",
  "owner": "Taro Yamamoto",
  "timestamp": "2026-02-03T12:34:56Z"
}
````

Stored:

* On-chain → Immutable hash
* Off-chain → UI-readable metadata

---

## 🏗 Technology Stack

### MVP

* Python (Desktop UI)
* XRPL Testnet
* SQLite
* QR Code generation

### Production (Phase 2)

* React Web App
* FastAPI / Flask Backend
* PostgreSQL
* XRPL Mainnet
* Mobile Verification App

---

## 🗄 Database Overview

| Table               | Purpose             |
| ------------------- | ------------------- |
| `koi`               | Core Koi passport   |
| `breeder`           | Breeder identity    |
| `ownership`         | Transfer history    |
| `health_log`        | Medical audit trail |
| `xrpl_transactions` | On-chain references |

All critical events are dual-recorded:

* Database for performance
* XRPL for immutability

---

## 🧩 Architecture Overview

See full architecture diagram below in repository documentation.

---

## 🌍 Vision

To establish a **global digital authentication standard** for high-value aquatic livestock, starting with Japan’s premium Nishikigoi industry.

Koi Ledger protects heritage bloodlines, ensures trust in auctions, and creates a new digital infrastructure layer for aquatic asset verification.

---

## 📌 Designed By

**LeObran Ltd.**

Built for innovation. Designed for transparency. Powered by XRPL.

````

---

# ✅ 2️⃣ ARCHITECTURE DIAGRAM (Phase-2 Ready – GitHub Version)

## High-Level System Architecture
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


🔁 Event Lifecycle Flow

1. Register Koi  
2. XRPL transaction created  
3. Transaction hash stored in DB  
4. Ownership transfer occurs  
5. Health update recorded  
6. Buyer verifies via QR scan  

Each step leaves a cryptographic audit trail.



🔐 Security Design

- XRPL provides immutable ledger anchoring
- Database stores human-readable metadata
- Transaction hashes ensure tamper detection
- Dual-layer storage ensures speed + security
- No private keys stored client-side in production phase



📈 Phase-2 Enhancements

- NFT-backed Koi identity (XLS-20)
- On-chain compliance metadata
- International auction integration
- Mobile app for global buyers
- IoT tank integration (water quality logs)
- API for third-party marketplace integration

=====================================================
🐠 Full Feature List – KoiLedger Desktop & Passport
=====================================================
1️⃣ Dashboard

* List all registered Koi
* Thumbnail preview of Koi photos
* Search by Name, Koi ID, or Variety
* Quick access to Passport, Health Log, and Ownership history
* Filter by breeder, owner, or bloodline

2️⃣ Koi Digital Passport

* Full Koi identification and lineage record
* Health history timeline with vaccinations and treatments
* Ownership audit trail with timestamps
* Display XRPL transaction hashes for verification
* QR Code encoding **Passport No** and key Koi info
* Barcode for scanning Passport No
* Digital Signature of issuing authority
* MRZ (Machine-Readable Zone) format at bottom
* Action buttons:

  * Print Passport
  * Save as PDF
  * Share Passport (PNG)
  * Update Photo (file upload / camera capture)
* Automatic fallback if no photo exists (`No_Koi.png`)

3️⃣ Register New Koi

* Input breeder, bloodline, variety, and Koi name
* Assign initial owner
* Optional photo upload
* Submission → generates XRPL-backed transaction
* Stores transaction hash and standard Koi ID for verification

4️⃣ Transfer Ownership

* Select Koi from dashboard
* Choose new owner (fetch name from database)
* Execute XRPL-backed transfer
* Immutable ownership history recorded in DB and XRPL
* Passport updated automatically with new owner and nationality

5️⃣ Health Log Updates

* Add timestamped treatments, vaccinations, or medical notes
* Optional QR/NFC integration
* Anchored in XRPL memo for audit trail
* Visual timeline available on Passport and dashboard

6️⃣ Photo Management

* View current main photo
* Upload new photo from file
* Capture directly from camera
* Preview before saving
* Automatic database update with timestamp
* Ensures main photo always visible on Passport

7️⃣ QR & Barcode Integration

* QR code encodes full Koi Passport information (Passport No, Name, Variety, Owner)
* Barcode represents **Passport No** for scanning
* Displayed on Passport next to Koi photo
* Automatic regeneration on Passport updates

8️⃣ XRPL Integration

* All critical events (Registration, Transfer, Health Log) anchored on XRPL
* Memo field stores structured metadata for public verification
* Transaction hashes displayed in Passport for auditing
* Ensures tamper-proof, immutable record

9️⃣ PDF & Printing

* Export Passport to high-resolution PDF
* Print directly from app
* Full-color Koi image and QR/Barcode included
* PDF includes MRZ and digital signature

🔄 Workflow Summary

1. Register Koi → generates Passport & XRPL hash
2. Add Health Logs → anchored on XRPL
3. Transfer Ownership → Passport auto-updates
4. Update Photo → QR & Barcode refresh
5. Print/Share Passport or Export PDF
6. Buyers verify via QR scan and XRPL transaction hash

---

🌏 Long-Term Vision

Koi Ledger becomes the digital trust layer for:
- It is SAAS ready, We need to Add Login.
- Fix Print, Pdf, Share options o capture full page.
- Premium livestock
- Aquaculture exports
- Rare biological assets
- International breeder certification




Designed by LeObran Ltd.
Powered by XRPL
