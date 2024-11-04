import os
from algosdk import account, mnemonic, transaction
from algosdk.v2client import algod
from dotenv import load_dotenv
import certifi
from pyteal import compileTeal, Mode, Btoi, Itob, Seq, Log, Int, Txn, If, Assert, Bytes
from contract import approval_program
import base64

level_8_id = 724672240

def deploy_opt_in_contract(client, creator_private_key):
    teal_code = compileTeal(approval_program(), mode=Mode.Application, version=6)
    compiled_approval = client.compile(teal_code)['result']
    compiled_approval = base64.b64decode(compiled_approval)

    clear_program = client.compile(compileTeal(Int(1), mode=Mode.Application, version=6))['result']
    clear_program = base64.b64decode(clear_program)

    params = client.suggested_params()
    txn = transaction.ApplicationCreateTxn(
        sender=account.address_from_private_key(creator_private_key),
        sp=params,
        on_complete=transaction.OnComplete.NoOpOC,
        approval_program=compiled_approval,
        clear_program=clear_program,
        global_schema=transaction.StateSchema(0, 0),
        local_schema=transaction.StateSchema(0, 0),
        foreign_apps=[level_8_id]
    )

    signed_txn = txn.sign(creator_private_key)
    tx_id = client.send_transaction(signed_txn)
    transaction.wait_for_confirmation(client, tx_id)
    response = client.pending_transaction_info(tx_id)
    app_id = response['application-index']
    print(f"Deployed app ID: {app_id}")
    return app_id

if __name__ == "__main__":
    load_dotenv()
    algod_client = algod.AlgodClient("", "https://testnet-api.algonode.cloud")
    passphrase = os.getenv("PASSPHRASE")
    private_key = mnemonic.to_private_key(passphrase)

    deploy_opt_in_contract(algod_client, private_key)
