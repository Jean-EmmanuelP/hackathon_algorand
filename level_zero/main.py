import os
from algosdk import account, mnemonic, transaction
from dotenv import load_dotenv
from algosdk.v2client import algod

"""
If you are using certifi remember too: 'pip install certifi'
algo account XXXXXXXXXXXXXXXXX :D
"""
import certifi
os.environ['SSL_CERT_FILE'] = certifi.where()

algod_address = "https://testnet-api.algonode.cloud"
algod_token = ""

def connect_to_algorand_testnet():
    algod_client = algod.AlgodClient(algod_token, algod_address)
    return algod_client

def generate_new_account():
    private_key, address = account.generate_account()
    mnemonic_phrase = mnemonic.from_private_key(private_key)
    return address, mnemonic_phrase

def write_mnemonic_to_env(mnemonic_phrase):
    with open('.env', 'w') as f:
        f.write(f"PASSPHRASE=\"{mnemonic_phrase}\"\n")

def load_passphrase_from_env():
    load_dotenv()
    passphrase = os.getenv("PASSPHRASE")
    return passphrase

def get_private_key_from_mnemonic(mnemonic_phrase):
    return mnemonic.to_private_key(mnemonic_phrase)

if __name__ == "__main__":
    passphrase = load_passphrase_from_env()

    if passphrase is None:
        address, mnemonic_phrase = generate_new_account()
        print("New Account Address:", address)
        write_mnemonic_to_env(mnemonic_phrase)
        print("Mnemonic saved to .env file.")
    else:
        private_key = get_private_key_from_mnemonic(passphrase)
        address = account.address_from_private_key(private_key)
        print("Using existing account:", address)

    algod_client = connect_to_algorand_testnet()
    try:
        status = algod_client.status()
        print("Connected to Algorand Testnet.")
    except Exception as e:
        print(f"Failed to connect to Algorand Testnet: {e}")

    try:  
        sp = algod_client.suggested_params()

        app_id = 724672197
        apt_in_txn = transaction.ApplicationOptInTxn(address, sp, app_id)
        signed_opt_in = apt_in_txn.sign(private_key)
        txid = algod_client.send_transaction(signed_opt_in)
        print(f"Opt-in transaction sent with txid: {txid}")

        optin_result = transaction.wait_for_confirmation(algod_client, txid, 4)
        assert optin_result["confirmed-round"] > 0
        print(f"Opt-in confirmed in round {optin_result["confirmed-round"]}.")
    except Exception as e:
        print(f"Failed to do the transaction {e}")