from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet

from xrpl.transaction import submit_and_wait
from xrpl.models.requests import AccountInfo
from xrpl.models.transactions import Payment, Memo
from xrpl.core.binarycodec import encode_for_signing

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




def send_xrp(from_secret, to_address, amount_xrp, memo_text):

    from xrpl.wallet import Wallet
    from xrpl.clients import JsonRpcClient
    from xrpl.models.transactions import Payment, Memo
    from xrpl.transaction import submit_and_wait
    from xrpl.utils import xrp_to_drops

    client = JsonRpcClient("https://s.altnet.rippletest.net:51234/")

    # wallet = Wallet(seed=from_secret, sequence=0)
    wallet = Wallet.from_seed(from_secret)


    memo = Memo(memo_data=memo_text.encode().hex())

    payment = Payment(
        account=wallet.classic_address,
        amount=xrp_to_drops(amount_xrp),
        destination=to_address,
        memos=[memo]
    )

    response = submit_and_wait(payment, client, wallet)

    return response.result["hash"]

