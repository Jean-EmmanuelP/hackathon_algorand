import os
from base64 import b64decode
from dotenv import load_dotenv
import algokit_utils
import algokit_utils.account
import algokit_utils.application_client
from algokit_utils.beta.algorand_client import AlgorandClient
from algosdk import transaction
from algosdk.atomic_transaction_composer import (
    AccountTransactionSigner,
    AtomicTransactionComposer,
    TransactionWithSigner,
)
import certifi

os.environ["SSL_CERT_FILE"] = certifi.where();

# Charger les variables d'environnement
load_dotenv()
PASSPHRASE = os.environ.get("PASSPHRASE")

print("Processing account...")

# Initialiser le client Algorand
algorand = AlgorandClient.test_net()
algod_client = algorand.client.algod

# Obtenir le compte à partir de la phrase mnémonique
creator = algokit_utils.get_account_from_mnemonic(PASSPHRASE)
print(creator.address)

signer = AccountTransactionSigner(creator.private_key)

# Remplacez par votre propre adresse de réception
receiver = "5SI33G5ECOYXIXOPX74UMFOPOQSVQVSZOBHQ7XEOQWZXY7JJ27NPA7OWBY"

# Remplacez par votre propre ID d'application
app_id = 724672212

# Obtenir les paramètres suggérés
sp = algod_client.suggested_params()

# Obtenir les boîtes de l'application
box_names = algod_client.application_boxes(app_id)["boxes"]
box_contents = []
pos = 0

# Décoder les noms et contenus des boîtes
for box in box_names:
    decoded_box_name = b64decode(box["name"])
    decoded_box_content = b64decode(
        algod_client.application_box_by_name(app_id, decoded_box_name)["value"]
    )
    print(decoded_box_content)
    box_contents.append(decoded_box_content)

# Trouver la boîte actuelle
for i in box_contents:
    if i == b"ball":
        current_box = pos
    pos += 1

print(box_contents)
print(current_box)

# Créer une transaction d'opt-in
opt_in_txn = transaction.ApplicationOptInTxn(
    sender=creator.address,
    sp=sp,
    index=app_id,
    app_args=[b64decode(box_names[current_box]["name"])],
    foreign_apps=[724672210],
    boxes=[(app_id, b64decode(box["name"])) for box in box_names],
)

# Signer et envoyer la transaction
signed_opt_in = opt_in_txn.sign(creator.private_key)
txid = algod_client.send_transaction(signed_opt_in)