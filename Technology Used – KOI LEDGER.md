## 🛠 Technology Used – KOI LEDGER

**Blockchain Layer:**

* **XRPL (XRP Ledger)** – Provides atomic settlement, immutable transaction history, and public verification of KOI digital passports.
* **Memo Fields** – Used to store lineage, health, and ownership metadata securely on-chain.

**Backend:**

* **Python 3.11+** – Core logic, API handling, and blockchain integration.
* **Flask / FastAPI (optional for MVP)** – REST API for interacting with the KOI Ledger database and XRPL.
* **xrpl-py SDK** – Python SDK to interact with XRPL for payments and ledger transactions.

**Frontend / User Interface:**

* **PyQt5** – Interactive desktop demo showing KOI passports, ownership verification, and health records.
* **Optional Web Interface:** React.js / TailwindCSS for web-based dashboards and breeder portals.

**Database / Storage:**

* **JSON / SQLite (MVP)** – For off-chain metadata, such as breeder info, fish health logs, and auction history.
* **Future Scale:** IPFS or decentralized storage to store detailed KOI media or certificates.

**AI / Analytics (Future Enhancements):**

* Image base KOI identification through AI ML.
* Health and growth prediction analytics using Python ML libraries.
* Fraud detection for lineage verification and breeding records.

**Security & Compliance:**

* Non-custodial architecture: breeders retain ownership keys.
* Full audit trail: blockchain + local logs for regulatory transparency.
* Japanese regulatory alignment: traceable digital asset for premium Nishikigoi.

**Other Tools:**

* **Git / GitHub** – Source code version control.
* **Docker (optional)** – Containerized deployment for reproducible demo environment.
* **Canva / Figma / Draw.io** – For architecture diagrams and Phase-2 slides.

---
