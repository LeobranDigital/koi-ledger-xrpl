from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet
from xrpl.models.transactions import Payment
from xrpl.transaction import submit_and_wait
from xrpl.models.requests import AccountInfo

XRPL_URL = "https://s.altnet.rippletest.net:51234"
client = JsonRpcClient(XRPL_URL)

JPY_TO_XRP = 0.0042


def jpy_to_xrp(jpy):
    return round(float(jpy) * JPY_TO_XRP, 6)


def get_balance(address):
    req = AccountInfo(
        account=address,
        ledger_index="validated",
        strict=True
    )
    response = client.request(req)
    balance_drops = response.result["account_data"]["Balance"]
    return float(balance_drops) / 1_000_000


def send_xrp(from_secret, to_address, amount_xrp):
    wallet = Wallet.from_secret(from_secret)

    payment = Payment(
        account=wallet.classic_address,
        amount=str(int(float(amount_xrp) * 1_000_000)),
        destination=to_address,
    )

    response = submit_and_wait(payment, client, wallet)

    return response.result["hash"]
