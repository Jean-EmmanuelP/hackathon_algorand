import os
from algosdk import account, mnemonic, transaction
from algosdk.v2client import algod
from algosdk.transaction import AssetTransferTxn
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

# Asset details
asset_id = 724672253

# Get suggested params
params = algod_client.suggested_params()

# Create opt-in transaction
# Note: Opt-in is just a 0 amount transfer to yourself
opt_in_txn = AssetTransferTxn(
    sender=sender_address,
    sp=params,
    receiver=sender_address,
    amt=0,
    index=asset_id
)

# Sign transaction
signed_txn = opt_in_txn.sign(private_key)

# Send transaction
tx_id = algod_client.send_transaction(signed_txn)

# Wait for confirmation
transaction.wait_for_confirmation(algod_client, tx_id)
print(f"Successfully opted in to ASA (ID: {asset_id}). Transaction ID: {tx_id}") 