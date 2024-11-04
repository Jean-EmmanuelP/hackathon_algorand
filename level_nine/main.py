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
    return os.getenv("PASSPHRASE")

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

# Add these debug prints right after calculating addresses
print("\n=== Account Details ===")
print(f"Your account address: {sender_address}")

# Get the contract address
contract_address = get_application_address(contract_app_id)

# Add these debug prints right after calculating addresses
print(f"Contract (app_id: {contract_app_id}) address: {contract_address}")

# Check current auth status
account_info_before = algod_client.account_info(sender_address)
auth_addr_before = account_info_before.get('auth-addr')
print("\n=== Rekey Status ===")
print(f"Auth address before: {auth_addr_before if auth_addr_before else 'Not rekeyed'}")

if auth_addr_before:
    print("\n⚠️ WARNING: Account is already rekeyed!")
    print(f"Current auth address: {auth_addr_before}")
    print("This means:")
    print("1. Your mnemonic's private key can no longer control this account")
    print("2. Only the contract at the auth address can sign transactions")
    print("\nTo fix this:")
    print("1. Create a new account, or")
    print("2. If you have access to the contract's logic, use it to rekey back")
    exit(1)

# Only proceed with rekey if account isn't already rekeyed
rekey_txn = transaction.PaymentTxn(
    sender=sender_address,
    sp=params,
    receiver=sender_address,
    amt=0,
    rekey_to=contract_address
)

signed_rekey_txn = rekey_txn.sign(private_key)
tx_id = algod_client.send_transaction(signed_rekey_txn)
transaction.wait_for_confirmation(algod_client, tx_id)

# After rekeying - check new auth address
account_info_after = algod_client.account_info(sender_address)
print(f"Auth address after rekey: {account_info_after.get('auth-addr', 'None')}")
# print(f"Expected auth address: {account.address_from_private_key(private_key)}")

# # Verify rekey was successful
# if account_info_after.get('auth-addr') == account.address_from_private_key(private_key):
#     print("✅ Rekey successful!")
# else:
#     print("❌ Rekey failed!")
#     raise Exception("Rekey operation did not complete successfully")

# Trigger Opt-In via contract
params = algod_client.suggested_params()
params.flat_fee = True
params.fee = 2000  # Increase fee to cover inner transaction

opt_in_txn = transaction.ApplicationCallTxn(
    sender=sender_address,
    sp=params,  # Use modified params with higher fee
    index=contract_app_id,
    on_complete=transaction.OnComplete.NoOpOC,
    app_args=[b"opt_in"],
    foreign_apps=[LEVEL8_APP_ID, LEVEL9_APP_ID]
)

signed_opt_in_txn = opt_in_txn.sign(private_key)
opt_in_tx_id = algod_client.send_transaction(signed_opt_in_txn)
transaction.wait_for_confirmation(algod_client, opt_in_tx_id)
print(f"Opted in to Level 9 app {level9_app_id} via contract. Transaction ID: {opt_in_tx_id}")
