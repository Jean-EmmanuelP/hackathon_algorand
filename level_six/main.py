import os
from algosdk import account, mnemonic, transaction
from algosdk.v2client import algod
from algosdk.transaction import ApplicationCallTxn
from dotenv import load_dotenv
import certifi

# Constants
LEVEL6_APP_ID = 724672235

def connect_to_algorand_testnet():
    return algod.AlgodClient("", "https://testnet-api.algonode.cloud")

def load_passphrase_from_env():
    load_dotenv()
    return os.getenv("PASSPHRASE")

def get_private_key_from_mnemonic(mnemonic_phrase):
    return mnemonic.to_private_key(mnemonic_phrase)

def opt_in_with_level6_call(client, level6_app_id, sum_app_id, sender_address, sender_private_key):
    params = client.suggested_params()
    
    # Increase the fee to account for additional computation
    params.fee = params.min_fee * 2
    
    # Remove any arguments since they're not needed for this opt-in call
    txn = ApplicationCallTxn(
        sender=sender_address,
        sp=params,
        index=level6_app_id,
        on_complete=transaction.OnComplete.OptInOC,
        foreign_apps=[724672212, sum_app_id]  # Keep the foreign apps references
    )
    signed_txn = txn.sign(sender_private_key)
    txid = client.send_transaction(signed_txn)
    transaction.wait_for_confirmation(client, txid)
    print(f"Opted in to level 6 with callback to our app. TxID: {txid}")

def clear_state_app(client, app_id, sender_address, sender_private_key):
    params = client.suggested_params()
    
    # Create the ClearState transaction
    txn = transaction.ApplicationCallTxn(
        sender=sender_address,
        sp=params,
        index=app_id,
        on_complete=transaction.OnComplete.ClearStateOC,
    )
    
    signed_txn = txn.sign(sender_private_key)
    txid = client.send_transaction(signed_txn)
    transaction.wait_for_confirmation(client, txid)
    print(f"Cleared state for app {app_id}. TxID: {txid}")

if __name__ == "__main__":
    # Set the SSL_CERT_FILE environment variable for Algonode connections
    os.environ['SSL_CERT_FILE'] = certifi.where()
    
    # Use hardcoded app_id
    sum_app_id = 728326319 #v2
    # sum_app_id = 728312226
    
    passphrase = load_passphrase_from_env()
    if not passphrase:
        print("Mnemonic not found in .env file.")
        exit()

    # Account and Client Setup
    private_key = get_private_key_from_mnemonic(passphrase)
    address = account.address_from_private_key(private_key)
    algod_client = connect_to_algorand_testnet()
    
    # First clear state (opt out)
    try:
        clear_state_app(algod_client, LEVEL6_APP_ID, address, private_key)
    except Exception as e:
        print(f"Clear state failed (this is ok if not opted in): {e}")
    
    # Then opt in again
    opt_in_with_level6_call(algod_client, LEVEL6_APP_ID, sum_app_id, address, private_key) 