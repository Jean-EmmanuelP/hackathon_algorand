import os
from algosdk import account, mnemonic, transaction
from algosdk.v2client import algod
from algosdk.transaction import ApplicationNoOpTxn, ApplicationOptInTxn
import base64
from dotenv import load_dotenv
import certifi

# Set SSL certificate for Algonode connections
os.environ['SSL_CERT_FILE'] = certifi.where()

def load_passphrase_from_env():
    load_dotenv()
    return os.getenv("PASSPHRASE")

# Initialize Algod client
algod_address = "https://testnet-api.algonode.cloud"
algod_token = ""
algod_client = algod.AlgodClient(algod_token, algod_address)

# Load account from environment
passphrase = load_passphrase_from_env()
if not passphrase:
    print("Mnemonic not found in .env file.")
    exit()

private_key = mnemonic.to_private_key(passphrase)
sender_address = account.address_from_private_key(private_key)

# Application IDs
authorize_app_id = 728334394
level7_app_id = 724672237
level6_app_id = 724672235

# Suggested params
params = algod_client.suggested_params()
params.fee = 0
params.flat_fee = True

# Create the 'authorize' method call transaction
# authorize_method_selector = "forward_auth()void"
authorize_txn = ApplicationNoOpTxn(
    sender=sender_address,
    sp=params,
    index=authorize_app_id,
    app_args=[bytes.fromhex("73bc6501")],
    foreign_apps=[level7_app_id, level6_app_id]
)

params = algod_client.suggested_params()
params.fee = 3 * 1000
params.flat_fee = True

# Create the Opt-In transaction for Level 7 application
opt_in_txn = ApplicationOptInTxn(
    sender=sender_address,
    sp=params,
    index=level7_app_id,
    foreign_apps=[level6_app_id]
)

# Group transactions
transaction.assign_group_id([authorize_txn, opt_in_txn])

# Sign transactions
signed_authorize_txn = authorize_txn.sign(private_key)
signed_opt_in_txn = opt_in_txn.sign(private_key)

# Send transactions
tx_id = algod_client.send_transactions([signed_authorize_txn, signed_opt_in_txn])

# Wait for confirmation
transaction.wait_for_confirmation(algod_client, tx_id)
print(f"Opted in to Level 7 application with authorization. Transaction ID: {tx_id}")
