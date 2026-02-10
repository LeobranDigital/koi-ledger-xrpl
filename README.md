### Repository Name:   **koi-ledger-xrpl**
---
**KOI LEDGER – Digital Passport for Premium Nishikigoi on XRPL**
---
**Goal:** Bring transparency, trust, and auditability to Japan’s premium Koi industry while creating a global standard for digital Koi authentication.
---
Website:
https://leobran.com/koiledger/

Koi Ledger is a blockchain-based provenance platform that creates immutable digital identities for high-value Nishikigoi (Japanese Koi).

The platform records:

* Breeder origin
* Lineage
* Health history
* Ownership transfers
* Auction records

All critical events are anchored on the XRP Ledger to ensure:

* Tamper-proof authenticity
* Transparent ownership
* Global verifiability

### Core Users

* Koi breeders
* Auction houses
* Collectors
* Veterinarians
* Exporters

### Technology Stack

* XRPL for settlement & records
* Web interface for breeders
* Mobile viewer for buyers
* QR/NFC tags for koi tanks

### Outcome

A trusted digital ecosystem that protects the global Nishikigoi industry from fraud and misinformation.


---

## Core MVP Features

**Objective:** Demonstrate full digital passport lifecycle, ownership verification, and health record tracking on XRPL.

1. **Dashboard / Home Screen**

   * Lists all registered Koi with thumbnails.
   * Search by name or Koi ID.

2. **Koi Detail View**

   * Full digital passport: lineage, photo, breeder info, health records.
   * Displays XRPL transaction hash.
   * `Verify Ownership` button → confirms ledger authenticity.

3. **Register New Koi**

   * Form input: breeder, lineage, color pattern, and initial owner.
   * Submission triggers XRPL transaction and stores metadata.

4. **Transfer Ownership**

   * Select a Koi → input new owner → submit.
   * Updates ownership history with ledger confirmation.

5. **Health Log Update**

   * Add timestamped vaccinations or treatments.
   * Optional QR code linking to tank/Koi tag.

**Demo Flow:**

1. Register a sample Koi → show XRPL transaction hash.
2. Transfer ownership → update history.
3. Verify Koi authenticity → public ledger lookup.
4. Update health record → audit trail visible.

---

## Database Schema (Example)

| Table        | Fields                                                                                       | Description                    |
| ------------ | -------------------------------------------------------------------------------------------- | ------------------------------ |
| `koi`        | `koi_id` (PK), `name`, `photo_url`, `breeder_id`, `lineage`, `color_pattern`, `xrpl_tx_hash` | Core Koi record linked to XRPL |
| `breeder`    | `breeder_id` (PK), `name`, `contact`, `address`                                              | Breeder information            |
| `ownership`  | `ownership_id` (PK), `koi_id` (FK), `owner_name`, `transfer_date`, `xrpl_tx_hash`            | Ownership history              |
| `health_log` | `log_id` (PK), `koi_id` (FK), `description`, `timestamp`, `xrpl_tx_hash`                     | Health / treatment records     |

*All critical events are stored both off-chain (for UI) and on XRPL (for immutable verification).*

---

## XRPL Transaction Structure

Every key event stores minimal, verifiable metadata in the XRPL **Memo field**:

```json
{
  "koi_id": "K1234",
  "event": "REGISTER",      // REGISTER / TRANSFER / HEALTH_UPDATE
  "details": {
      "owner": "Taro Yamamoto",
      "breeder": "Osaka Breeders Association",
      "lineage": "Sanke",
      "color_pattern": "White-Red-Black"
  },
  "timestamp": "2026-02-03T12:34:56Z"
}
```

* `xrpl_tx_hash` saved in database for verification.
* Transfer or health update events follow the same structure.
* Atomic ledger settlement ensures **immutable, auditable history**.

---

## Technology Stack

* **Frontend / Demo UI:** Python + PyQt5 (desktop MVP) / React (optional web)
* **Blockchain Layer:** XRPL Testnet (MVP), Mainnet for production
* **Database:** SQLite (MVP) / PostgreSQL (production)
* **Backend / API:** Python Flask or FastAPI for event submission & ledger integration
* **QR / Tagging:** Optional per-Koi QR codes for tank or breeding verification
* **Hosting:** Local VM or cloud instance for PoC demonstration


---

Designed by: LeObran Ltd.
