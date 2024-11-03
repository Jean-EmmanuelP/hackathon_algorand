import os
from algosdk import account, mnemonic, transaction, encoding
from algosdk.v2client import algod
from algosdk.transaction import AssetTransferTxn, ApplicationOptInTxn, LogicSigAccount
from algosdk.transaction import assign_group_id
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

# Asset and application details
asset_id = 724672253
clawback_address = "LLPFMBH3LQIGP4JRKFK7PYFHJPQR2LQCEXY2N4XGB5IIFYQ2FWUS5QNUDE"
level8_app_id = 724672240
previous_app_id = 724672237  # Replace with the actual previous app ID

# Suggested params
params = algod_client.suggested_params()
params.flat_fee = True

# Step 1: Create the LogicSig for the clawback transaction
teal_source = """
#pragma version 9
txn RekeyTo
global ZeroAddress
==
assert
txn AssetCloseTo
global ZeroAddress
==
assert
txn TypeEnum
int 4
==
assert
txn XferAsset
int 724672253
==
assert
txn Fee
int 0
==
assert
int 1
"""
compiled_teal = algod_client.compile(teal_source)
lsig = LogicSigAccount(encoding.base64.b64decode(compiled_teal['result']))

# Step 2: Clawback transaction to transfer the ASA to your account
clawback_txn = AssetTransferTxn(
    sender=clawback_address,
    sp=params,
    receiver=sender_address,
    amt=1,
    index=asset_id,
    revocation_target="RDU4L7HHENQBIMGVEEHZL7IXDJUPWK2HASGZ5XMHFWWOXJPRD23M3RRRPQ"  # Updated address
)

# Step 3: Opt-In to the Level 8 application
params.fee = 2000  # Adjust fee for grouped transactions
opt_in_app_txn = ApplicationOptInTxn(
    sender=sender_address,
    sp=params,
    index=level8_app_id,
    foreign_apps=[previous_app_id],
    foreign_assets=[asset_id]  # Add the asset ID as a foreign asset
)

# Group transactions
assign_group_id([clawback_txn, opt_in_app_txn])

# Sign transactions
signed_clawback_txn = transaction.LogicSigTransaction(clawback_txn, lsig)
signed_opt_in_app_txn = opt_in_app_txn.sign(private_key)

# Send transactions
tx_id = algod_client.send_transactions([signed_clawback_txn, signed_opt_in_app_txn])

# Wait for confirmation
transaction.wait_for_confirmation(algod_client, tx_id)
print(f"Opted in to Level 8 application and received ASA. Transaction ID: {tx_id}")
