import os
import certifi
from algosdk.v2client import algod
from algosdk.transaction import ApplicationCreateTxn, StateSchema
from algosdk import mnemonic, transaction, account
from dotenv import load_dotenv
import base64

os.environ['SSL_CERT_FILE'] = certifi.where()
# Load environment variables
load_dotenv()

# Algonode testnet configuration
algod_address = "https://testnet-api.algonode.cloud"
algod_token = ""
passphrase = os.getenv("PASSPHRASE")

# Initialize the Algod client
algod_client = algod.AlgodClient(algod_token, algod_address)
print("Algod client initialized.")

# Recover account using the mnemonic stored in .env
private_key = mnemonic.to_private_key(passphrase)
print(f"Private key derived from mnemonic: {private_key}")

# Use the sender's address derived from the private key
sender_address = account.address_from_private_key(private_key)
print(f"Sender address: {sender_address}")

# Compile TEAL programs
def compile_teal(teal_file):
    with open(teal_file, "r") as file:
        teal_code = file.read()
        print(f"Read TEAL code from {teal_file}.")
    compiled_teal = algod_client.compile(teal_code)
    print(f"Compiled TEAL code: {compiled_teal['result']}")
    return compiled_teal['result'], compiled_teal['hash']

# Compile approval and clear state programs
approval_result, approval_hash = compile_teal("approval.teal")
clear_result, clear_hash = compile_teal("clear.teal")

# Decode compiled TEAL programs from base64 to bytes
compiled_approval_program = base64.b64decode(approval_result)
compiled_clear_program = base64.b64decode(clear_result)

# Create the schema for global and local state
global_schema = StateSchema(num_uints=0, num_byte_slices=1)  # Allow 1 byte slice for "access"
local_schema = StateSchema(num_uints=0, num_byte_slices=0)   # No local state

print(f"Global Schema: {global_schema}")
print(f"Local Schema: {local_schema}")

# Create the transaction to deploy the application
txn = ApplicationCreateTxn(
    sender=sender_address,
    sp=algod_client.suggested_params(),
    on_complete=transaction.OnComplete.NoOpOC,
    approval_program=compiled_approval_program,
    clear_program=compiled_clear_program,
    global_schema=global_schema,
    local_schema=local_schema,
)

print("Transaction created successfully.")

# Sign the transaction
signed_txn = txn.sign(private_key)
print("Transaction signed successfully.")

# Send the transaction
try:
    txid = algod_client.send_transaction(signed_txn)
    print(f"Transaction ID: {txid}")

    # Wait for the transaction to be confirmed
    transaction_response = transaction.wait_for_confirmation(algod_client, txid)
    app_id = transaction_response['application-index']
    print(f"Smart contract deployed with Application ID: {app_id}")
except Exception as e:
    print(f"Error sending transaction: {str(e)}")

#     Level 4: Authorized Personnel Only
# AppID: 724672210
# This application checks who has access to OptIn by comparing the sender's address with a global state value in a foreign app.

# Solution: Include a foreign application ID which has a global state "access" set to Senders address.