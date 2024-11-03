import os
import certifi
import algokit_utils
from algosdk.v2client import algod
from algosdk import mnemonic, transaction, account
from algosdk.transaction import ApplicationCreateTxn, StateSchema
from dotenv import load_dotenv
from pyteal import *

# Load environment variables
os.environ['SSL_CERT_FILE'] = certifi.where()
load_dotenv()

# Algonode testnet configuration
algod_address = "https://testnet-api.algonode.cloud"
algod_token = ""
PASSPHRASE = os.getenv("PASSPHRASE")

# Initialize the Algod client
algod_client = algod.AlgodClient(algod_token, algod_address)
print("Algod client initialized.")

# Recover account using the mnemonic stored in .env
creator = algokit_utils.get_account_from_mnemonic(PASSPHRASE)
sender_address = creator.address

print(f"Sender address: {sender_address}")

# Define the smart contract with an ABI-compliant method `sum(uint64,uint64)uint64`
def sum_contract():
    num1 = Btoi(Txn.application_args[0])  # Convert the first argument to uint64
    num2 = Btoi(Txn.application_args[1])  # Convert the second argument to uint64
    result = num1 + num2  # Perform the addition

    # Log the result as a big-endian integer
    return Seq([
        Log(Itob(result)),
        Int(1)
    ])

# Compile the approval program
approval_teal = compileTeal(sum_contract(), mode=Mode.Application, version=5)
clear_teal = compileTeal(Approve(), mode=Mode.Application, version=5)

# Compile the TEAL programs to bytecode
approval_program = algod_client.compile(approval_teal)["result"]
clear_program = algod_client.compile(clear_teal)["result"]

# Create the application transaction for deploying the contract
txn = ApplicationCreateTxn(
    sender=sender_address,
    sp=algod_client.suggested_params(),
    on_complete=transaction.OnComplete.NoOpOC,
    approval_program=approval_program,
    clear_program=clear_program,
    global_schema=StateSchema(num_uints=0, num_byte_slices=0),
    local_schema=StateSchema(num_uints=0, num_byte_slices=0),
)

print("Transaction created successfully.")

# Sign the transaction
signed_txn = txn.sign(creator.private_key)
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