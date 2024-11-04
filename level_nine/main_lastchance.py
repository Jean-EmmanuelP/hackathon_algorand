import os
from algosdk import account, mnemonic, transaction
from algosdk.v2client import algod
from dotenv import load_dotenv
import certifi
from algosdk.logic import get_application_address

# Set SSL certificate for Algonode connections
os.environ['SSL_CERT_FILE'] = certifi.where()

def load_passphrase_from_env():
    load_dotenv()
    return os.getenv("PASSPHRASE_LASTCHANCE")

algod_client = algod.AlgodClient("", "https://testnet-api.algonode.cloud")
passphrase = load_passphrase_from_env()
private_key = mnemonic.to_private_key(passphrase)
sender_address = account.address_from_private_key(private_key)

# Deployed App ID (replace with actual deployed ID)
# contract_app_id = 728340050  # Replace with the app ID from deployment this is manual optin first
contract_app_id = 728340322 # this is vanilla first try
level9_app_id = 724672278

# Add Level 8 app ID constant
LEVEL8_APP_ID = 724672240
LEVEL9_APP_ID = 724672278

# Get suggested params and modify for the opt-in call
params = algod_client.suggested_params()
params.flat_fee = True
params.fee = 2000  # Higher fee to cover inner transaction

# Create opt-in transaction from new account
opt_in_txn = transaction.ApplicationCallTxn(
    sender=sender_address,
    sp=params,
    index=contract_app_id,
    on_complete=transaction.OnComplete.NoOpOC,
    app_args=[b"opt_in"],
    foreign_apps=[LEVEL8_APP_ID, LEVEL9_APP_ID]
)

# Sign and send transaction
signed_opt_in_txn = opt_in_txn.sign(private_key)
opt_in_tx_id = algod_client.send_transaction(signed_opt_in_txn)
transaction.wait_for_confirmation(algod_client, opt_in_tx_id)
print(f"\n=== Transaction Details ===")
print(f"Opt-in transaction ID: {opt_in_tx_id}")
