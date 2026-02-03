## 1️⃣ MVP Feature List – KOI LEDGER

**Core Features:**

1. **Digital Passport Creation**

   * Register a new Koi with breeder info, photo, lineage, and unique ID.
   * Store key metadata on XRPL ledger (Memo fields).

2. **Ownership Transfer**

   * Record sale or transfer between breeder, buyer, or auction house.
   * Immutable blockchain proof of ownership.

3. **Health & Veterinary Records**

   * Log vaccinations, treatments, and health checks.
   * Optional QR code linking to physical Koi tank tags.

4. **Lineage Verification**

   * Track family tree and breeding history.
   * Prevent fraudulent claims.

5. **Public Verification & Query**

   * Any user can verify Koi authenticity via ledger lookup.

**Optional / Stretch MVP Features:**

* Simple marketplace view (price and auction history).
* Exportable Koi certificates.
* Basic analytics: number of registered Koi, active owners.

---

## 2️⃣ Database Schema – MVP

**Table: koi**

| Column         | Type        | Notes                                    |
| -------------- | ----------- | ---------------------------------------- |
| koi_id         | TEXT / UUID | Unique identifier, matches XRPL Memo ID  |
| name           | TEXT        | Optional breeder-assigned name           |
| breed_lineage  | TEXT / JSON | Parent info & genealogy                  |
| breeder_name   | TEXT        | Owner at registration                    |
| birth_date     | DATE        | Date of birth / hatching                 |
| color_pattern  | TEXT        | Nishikigoi variety (Kohaku, Showa, etc.) |
| xrpl_tx_hash   | TEXT        | XRPL transaction storing metadata        |
| health_records | JSON / TEXT | Vaccines, treatments, check-ups          |
| last_owner     | TEXT        | Current owner                            |
| created_at     | TIMESTAMP   | Record creation date                     |
| updated_at     | TIMESTAMP   | Last update                              |

**Table: ownership_history**

| Column        | Type | Notes               |
| ------------- | ---- | ------------------- |
| koi_id        | TEXT | Foreign key         |
| owner_name    | TEXT | Buyer / owner       |
| transfer_date | DATE | Date of transaction |
| xrpl_tx_hash  | TEXT | Transaction proof   |
| remarks       | TEXT | Optional notes      |

---

## 3️⃣ XRPL Transaction Structure – MVP

* **Transaction Type:** `Payment` (minimal XRP sent to self) or `NFTokenMint` for future NFT-like ID.
* **Fields / Memo Example:**

```json
{
  "koi_id": "KOI-0001",
  "breeder": "Tanaka Koi Farm",
  "lineage": "Parent1 x Parent2",
  "health": "Vaccinated, no disease",
  "owner": "Sato Buyer",
  "timestamp": "2026-02-03T12:00:00Z"
}
```

* **Immutable Ledger Proof:** Memo field stores JSON hash or full JSON (if size permits).
* **Ownership Change:** New transaction for each sale / transfer.

---
