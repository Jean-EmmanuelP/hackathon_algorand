import os
from algosdk import account, mnemonic, transaction
from algosdk.v2client import algod
from dotenv import load_dotenv
import certifi
from pyteal import compileTeal, Mode, Btoi, Itob, Seq, Log, Int, Txn, If, Assert, Bytes
from base64 import b64decode
from sum_contract import sum_contract

def deploy_sum_contract(client, creator_private_key):
    # Compile PyTeal directly instead of reading from file
    teal_code = compileTeal(sum_contract(), mode=Mode.Application, version=5)
    
    # Compile the smart contract
    approval_program = client.compile(teal_code)['result']
    approval_program = b64decode(approval_program)
    
    # Simple clear program that always returns true
    clear_program = client.compile(
        compileTeal(Int(1), mode=Mode.Application, version=5)
    )['result']
    clear_program = b64decode(clear_program)

    # Transaction parameters
    params = client.suggested_params()
    txn = transaction.ApplicationCreateTxn(
        sender=account.address_from_private_key(creator_private_key),
        sp=params,
        on_complete=transaction.OnComplete.NoOpOC,
        approval_program=approval_program,
        clear_program=clear_program,
        global_schema=transaction.StateSchema(0, 0),
        local_schema=transaction.StateSchema(0, 0),
    )

    # Sign and send transaction
    signed_txn = txn.sign(creator_private_key)
    tx_id = client.send_transaction(signed_txn)
    transaction.wait_for_confirmation(client, tx_id)
    response = client.pending_transaction_info(tx_id)
    app_id = response['application-index']
    print(f"Deployed app ID: {app_id}")
    return app_id

# Helper Functions
def connect_to_algorand_testnet():
    return algod.AlgodClient("", "https://testnet-api.algonode.cloud")

def load_passphrase_from_env():
    load_dotenv()
    return os.getenv("PASSPHRASE")

def get_private_key_from_mnemonic(mnemonic_phrase):
    return mnemonic.to_private_key(mnemonic_phrase)

if __name__ == "__main__":
    # Set the SSL_CERT_FILE environment variable for Algonode connections
    os.environ['SSL_CERT_FILE'] = certifi.where()
    
    passphrase = load_passphrase_from_env()
    if not passphrase:
        print("Mnemonic not found in .env file.")
        exit()

    # Account and Client Setup
    private_key = get_private_key_from_mnemonic(passphrase)
    algod_client = connect_to_algorand_testnet()
    
    # Deploy the Sum Contract using the TEAL file
    app_id = deploy_sum_contract(algod_client, private_key)
    print(f"Save this app_id for opt-in: {app_id}")