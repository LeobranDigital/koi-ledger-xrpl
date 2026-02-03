# 3️⃣ ARCHITECTURE DIAGRAM (Phase-2 Ready)

```
┌───────────────────────────────┐
│  Breeder / Auction Platform   │
│  (Web / Mobile Interface)     │
└───────────────┬───────────────┘
                │
        Koi Registration Data
                ▼
┌──────────────────────────────────────┐
│           KOI LEDGER CORE            │
│                                      │
│  • Koi Profile Management            │
│  • Health & Lineage Records          │
│  • Ownership Transfers               │
│  • QR/NFC Tag Generation             │
│  • Compliance Metadata               │
└───────────────┬──────────────────────┘
                │
        Verified Record Hash
                ▼
┌──────────────────────────────────────┐
│             XRPL LAYER               │
│  • Immutable Records                 │
│  • Atomic Transfers                  │
│  • Public Audit Trail                │
└───────────────┬──────────────────────┘
                │
                ▼
┌──────────────────────────────────────┐
│  Buyer Verification App              │
│  (Scan QR → Verify on XRPL)          │
└──────────────────────────────────────┘
```

---
