import os
import certifi
from algosdk import account, mnemonic, transaction
from algosdk.v2client import algod
from algosdk.logic import get_application_address
from dotenv import load_dotenv

os.environ['SSL_CERT_FILE'] = certifi.where()
algod_address = "https://testnet-api.algonode.cloud"
algod_token = ""

def connect_to_algorand_testnet():
    return algod.AlgodClient(algod_token, algod_address)

def load_passphrase_from_env():
    load_dotenv()
    return os.getenv("PASSPHRASE")

def get_private_key_from_mnemonic(mnemonic_phrase):
    return mnemonic.to_private_key(mnemonic_phrase)

if __name__ == "__main__":
    passphrase = load_passphrase_from_env()

    if passphrase is None:
        print("Veuillez définir votre phrase mnémonique (PASSPHRASE) dans le fichier .env.")
        exit()
    else:
        private_key = get_private_key_from_mnemonic(passphrase)
        address = account.address_from_private_key(private_key)
        print("Utilisation du compte existant :", address)

    algod_client = connect_to_algorand_testnet()
    try:
        status = algod_client.status()
        print("Connecté au testNet d'Algorand.")
    except Exception as e:
        print(f"Échec de la connexion au testNet d'Algorand : {e}")
        exit()

    try:
        sp = algod_client.suggested_params()

        app_id = 724672199
        previous_app_id = 724672198

        opt_in_txn = transaction.ApplicationOptInTxn(
            sender=address,
            sp=sp,
            index=app_id,
            foreign_apps=[previous_app_id]
        )
        opt_in_txn.fee = 0

        payment_txn = transaction.PaymentTxn(
            sender=address,
            sp=sp,
            receiver=address,
            amt=0
        )
        total_fee = 1000 * 2 
        payment_txn.fee = total_fee

        gid = transaction.calculate_group_id([opt_in_txn, payment_txn])
        opt_in_txn.group = gid
        payment_txn.group = gid

        signed_opt_in_txn = opt_in_txn.sign(private_key)
        signed_payment_txn = payment_txn.sign(private_key)
        signed_group = [signed_opt_in_txn, signed_payment_txn]

        txid = algod_client.send_transactions(signed_group)
        print(f"Transactions groupées envoyées avec txid : {txid}")

        optin_result = transaction.wait_for_confirmation(algod_client, txid, 4)
        print(f"Opt-in confirmé dans le round {optin_result['confirmed-round']}.")

    except Exception as e:
        print(f"Erreur lors de la transaction : {e}")