import os
import algokit_utils
import algokit_utils.account
import algokit_utils.application_client
from algokit_utils.beta.algorand_client import AlgorandClient
from dotenv import load_dotenv
from algosdk.atomic_transaction_composer import AccountTransactionSigner
from algosdk import transaction

load_dotenv()

PASSPHRASE = os.environ.get("PASSPHRASE")  # Load your passphrase from environment variables
print("Processing account...")

algorand = AlgorandClient.test_net()
creator = algokit_utils.get_account_from_mnemonic(PASSPHRASE)
print(creator.address)

algod_client = algorand.client.algod
signer = AccountTransactionSigner(creator.private_key)

# Uncomment to print account information
# print(algorand.account.get_information(creator.address))

receiver = "5SI33G5ECOYXIXOPX74UMFOPOQSVQVSZOBHQ7XEOQWZXY7JJ27NPA7OWBY"
app_id = 724672235

sp = algorand.client.algod.suggested_params()
sp.fee = 2 * 1000
sp.flat_fee = True

opt_in_txn = transaction.ApplicationOptInTxn(
    sender=creator.address,
    sp=sp,
    index=app_id,
    foreign_apps=[FOREIGN_APP_ID_1, FOREIGN_APP_ID_2]  # Replace with foreign app IDs
)

signed_opt_in = opt_in_txn.sign(creator.private_key)
txid = algorand.client.algod.send_transaction(signed_opt_in)