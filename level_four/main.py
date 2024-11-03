import os
from algosdk import mnemonic, transaction
from algosdk.encoding import decode_address, encode_address
from dotenv import load_dotenv
from algosdk.v2client import algod
import base64
import certifi

# Set the SSL_CERT_FILE environment variable for Algonode connections
os.environ['SSL_CERT_FILE'] = certifi.where()

# Algonode testnet configuration
algod_address = "https://testnet-api.algonode.cloud"
algod_token = ""

# Application IDs
previous_app_id = 724672209  # Previous application ID (must be included in foreign apps)
reference_app_id = 728309730  # App with global state containing 'access'
current_app_id = 724672210    # Your current application

# Initialize the Algod client
def connect_to_algorand_testnet():
    return algod.AlgodClient(algod_token, algod_address)

# Load passphrase from environment variable
def load_passphrase_from_env():
    load_dotenv()
    return os.getenv("PASSPHRASE")

# Convert mnemonic to private key
def get_private_key_from_mnemonic(mnemonic_phrase):
    return mnemonic.to_private_key(mnemonic_phrase)

# Fetch global state from a specific app (e.g., 724089092)
def fetch_global_state(algod_client, app_id):
    app_info = algod_client.application_info(app_id)
    global_state = app_info['params']['global-state']

    # Iterate through global state to find the 'access' key
    decoded_state = {}
    for entry in global_state:
        key = entry['key']
        value = entry['value']
        
        # Decode the key from base64 to human-readable format
        decoded_key = base64.b64decode(key).decode('utf-8')
        
        # Check for the 'access' key and store the value
        if decoded_key == "access":
            decoded_state['access'] = value['bytes']  # 'bytes' contains base64-encoded address
    
    return decoded_state

# Check if the sender's address is authorized by comparing with the 'access' value
def is_authorized(sender_address, access_value):
    # Decode the 'access' value from base64 into raw bytes
    access_bytes = base64.b64decode(access_value)

    # Encode the raw bytes back into an Algorand address format
    access_address = encode_address(access_bytes)

    # Compare the decoded address with the sender's address
    return sender_address == access_address


if __name__ == "__main__":
    passphrase = load_passphrase_from_env()
    private_key = get_private_key_from_mnemonic(passphrase)
    algod_client = connect_to_algorand_testnet()

    try:
        status = algod_client.status()
        print("Connected to Algorand Testnet.")
    except Exception as e:
        print(f"Failed to connect to Algorand Testnet: {e}")
        exit(1)

    try:
        # Step 1: Fetch the global state from the reference app (728302900)
        global_state = fetch_global_state(algod_client, reference_app_id)

        # Print the global state for debugging
        print(f"Global State Retrieved: {global_state}")

        # Assuming 'access' is in global state, retrieve its value
        access_value = global_state.get('access')  # Now this holds the authorized address (base64-encoded)
        print(f"Access Value (expected authorized address): {access_value}")

        # Hardcode the sender's address
        address = "5SI33G5ECOYXIXOPX74UMFOPOQSVQVSZOBHQ7XEOQWZXY7JJ27NPA7OWBY"
        print(f"Sender's Address: {address}")

        if is_authorized(address, access_value):
            # Get suggested transaction parameters
            sp = algod_client.suggested_params()

            # Step 3: Create OptIn transaction for current app (724672210)
            opt_in_txn = transaction.ApplicationOptInTxn(
                sender=address,
                sp=sp,
                index=current_app_id,
                foreign_apps=[previous_app_id, reference_app_id]  # Include previous app and app with 'access'
            )

            # Sign and send the transaction
            signed_opt_in = opt_in_txn.sign(private_key)
            txid = algod_client.send_transaction(signed_opt_in)
            print(f"Opt-in transaction sent with ID: {txid}")

            # Wait for confirmation
            result = transaction.wait_for_confirmation(algod_client, txid, 4)
            if result and result['confirmed-round'] > 0:
                print(f"Opt-in confirmed in round {result['confirmed-round']}.")
        else:
            print("Access denied: sender is not authorized.")
    except Exception as e:
        print(f"Error fetching global state or processing transaction: {e}")
