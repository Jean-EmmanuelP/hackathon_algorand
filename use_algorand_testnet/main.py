import os
from algosdk import account, mnemonic, transaction
from dotenv import load_dotenv
from algosdk.v2client import algod

"""
If you are using certifi remember too: 'pip install certifi'
algo account 5SI33G5ECOYXIXOPX74UMFOPOQSVQVSZOBHQ7XEOQWZXY7JJ27NPA7OWBY
"""
import certifi
# Set the SSL_CERT_FILE environment variable for Algonode connections
os.environ['SSL_CERT_FILE'] = certifi.where()

# Algonode testnet configuration (no token needed)
algod_address = "https://testnet-api.algonode.cloud"
algod_token = ""

# Initialize the Algod client
def connect_to_algorand_testnet():
    algod_client = algod.AlgodClient(algod_token, algod_address)
    return algod_client

def generate_new_account():
    # Generate a new Algorand account and return the address and secret key (mnemonic)
    private_key, address = account.generate_account()
    mnemonic_phrase = mnemonic.from_private_key(private_key)
    return address, mnemonic_phrase

def write_mnemonic_to_env(mnemonic_phrase):
    # Save the mnemonic (secret key) to a .env file for future use
    with open('.env', 'w') as f:
        f.write(f"PASSPHRASE=\"{mnemonic_phrase}\"\n")

def load_passphrase_from_env():
    # Load the mnemonic from the .env file
    load_dotenv()
    passphrase = os.getenv("PASSPHRASE")
    return passphrase

def get_private_key_from_mnemonic(mnemonic_phrase):
    # Convert mnemonic back to private key
    return mnemonic.to_private_key(mnemonic_phrase)

if __name__ == "__main__":
    # Try to load the mnemonic from the .env file
    passphrase = load_passphrase_from_env()

    if passphrase is None:
        # Generate a new account if no mnemonic is found and save it to .env
        address, mnemonic_phrase = generate_new_account()
        print("New Account Address:", address)
        write_mnemonic_to_env(mnemonic_phrase)
        print("Mnemonic saved to .env file.")
    else:
        # If mnemonic already exists, use the existing account
        private_key = get_private_key_from_mnemonic(passphrase)
        address = account.address_from_private_key(private_key)
        print("Using existing account:", address)

    # Connect to Algorand Testnet using Algonode
    algod_client = connect_to_algorand_testnet()
    try:
        # Get and display node status
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