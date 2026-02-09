import tkinter as tk
from tkinter import ttk, messagebox
from threading import Thread
from xrpl.clients import JsonRpcClient
from xrpl.models.requests import AccountInfo, AccountTx
from xrpl.utils import drops_to_xrp

BUYER_ADDRESS = "rM3Eq9kfVmEYBWTVZYripuLwkkCdvhH7Zz"
TESTNET_URL = "https://s.altnet.rippletest.net:51234/"
client = JsonRpcClient(TESTNET_URL)

def open_buyer_wallet():
    win = tk.Tk()
    win.title("Buyer Wallet")
    win.geometry("800x450")

    tk.Label(win, text="Buyer XRP Wallet", font=("Arial", 16)).pack(pady=5)

    balance_label = tk.Label(win, text="Balance: -- XRP", font=("Arial", 14))
    balance_label.pack(pady=5)

    # Transactions tree
    tree_frame = tk.Frame(win)
    tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

    columns = ("hash", "type", "from", "to", "amount")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col.upper())
        tree.column(col, width=140)
    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # -------------------- BALANCE --------------------
    def refresh_balance():
        try:
            resp = client.request(AccountInfo(account=BUYER_ADDRESS, ledger_index="validated"))
            drops = resp.result["account_data"]["Balance"]
            # Convert drops safely
            balance_label.config(text=f"Balance: {drops_to_xrp(str(drops))} XRP")
        except Exception as e:
            messagebox.showerror("Balance Error", str(e))

    # -------------------- TRANSACTIONS --------------------
    def load_transactions():
        def fetch():
            try:
                # Clear old entries
                for i in tree.get_children():
                    tree.delete(i)

                resp = client.request(AccountTx(account=BUYER_ADDRESS, limit=10))
                txs = resp.result.get("transactions", [])

                for entry in txs:
                    tx = entry.get("tx", {})
                    tx_hash = tx.get("hash", "")
                    tx_type = tx.get("TransactionType", "")
                    from_addr = tx.get("Account", "")
                    to_addr = tx.get("Destination", "")
                    amt = tx.get("Amount", "")

                    # Handle Amount safely
                    if isinstance(amt, dict):
                        # Issued currency
                        amt = f"{amt.get('value','?')} {amt.get('currency','?')}"
                    else:
                        # XRP in drops, ensure string
                        amt = drops_to_xrp(str(amt))

                    tree.insert("", "end", values=(tx_hash, tx_type, from_addr, to_addr, amt))

            except Exception as e:
                messagebox.showerror("TX Error", str(e))

        Thread(target=fetch, daemon=True).start()

    tk.Button(win, text="Refresh Balance",
              command=lambda: Thread(target=refresh_balance, daemon=True).start()).pack(pady=5)
    tk.Button(win, text="Load Transactions", command=load_transactions).pack(pady=5)

    # Auto-load balance
    Thread(target=refresh_balance, daemon=True).start()

    win.mainloop()

# Run page
if __name__ == "__main__":
    open_buyer_wallet()
