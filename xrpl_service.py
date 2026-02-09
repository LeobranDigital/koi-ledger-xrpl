from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet
from xrpl.models.transactions import Payment
from xrpl.transaction import submit_and_wait

JSON_RPC_URL = "https://s.altnet.rippletest.net:51234"

client = JsonRpcClient(JSON_RPC_URL)

wallet = Wallet.create()

def send_xrpl_memo(data):

    payment = Payment(
        account=wallet.classic_address,
        destination=wallet.classic_address,
        amount="10",
        memos=[{
            "memo": {
                "memo_data": data.encode().hex()
            }
        }]
    )

    response = submit_and_wait(payment, client, wallet)
    return response.result["hash"]
