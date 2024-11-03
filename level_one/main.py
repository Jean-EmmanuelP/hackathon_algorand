import os
import certifi
from algosdk import account, mnemonic, transaction
from algosdk.v2client import algod
from dotenv import load_dotenv

# Configuration de la connexion au testnet via Algonode
os.environ['SSL_CERT_FILE'] = certifi.where()
algod_address = "https://testnet-api.algonode.cloud"
algod_token = ""

def connect_to_algorand_testnet():
    return algod.AlgodClient(algod_token, algod_address)

def generate_new_account():
    private_key, address = account.generate_account()
    mnemonic_phrase = mnemonic.from_private_key(private_key)
    return address, mnemonic_phrase

def write_mnemonic_to_env(mnemonic_phrase):
    with open('.env', 'w') as f:
        f.write(f"PASSPHRASE=\"{mnemonic_phrase}\"\n")

def load_passphrase_from_env():
    load_dotenv()
    return os.getenv("PASSPHRASE")

def get_private_key_from_mnemonic(mnemonic_phrase):
    return mnemonic.to_private_key(mnemonic_phrase)

if __name__ == "__main__":
    passphrase = load_passphrase_from_env()

    if passphrase is None:
        address, mnemonic_phrase = generate_new_account()
        print("Nouvelle adresse de compte :", address)
        write_mnemonic_to_env(mnemonic_phrase)
        print("La phrase mnémonique a été sauvegardée dans le fichier .env.")
    else:
        private_key = get_private_key_from_mnemonic(passphrase)
        address = account.address_from_private_key(private_key)
        print("Utilisation du compte existant :", address)

    algod_client = connect_to_algorand_testnet()
    try:
        status = algod_client.status()
        print("Connecté au testnet d'Algorand.")
    except Exception as e:
        print(f"Échec de la connexion au testnet d'Algorand : {e}")

    try:
        sp = algod_client.suggested_params()

        app_id = 724672198
        previous_app_id = 724672197
        smart_contract_address = "Z4XODJ4POELTV4J3SWL7DTAIVSH2KDPB2LS2RXR2E5F5VKNZVAFVJNBPNQ"

        # Créer la transaction d'Opt-In
        opt_in_txn = transaction.ApplicationOptInTxn(
            sender=address,
            sp=sp,
            index=app_id,
            foreign_apps=[previous_app_id]
        )

        # Créer la transaction de paiement de 1 Algo vers l'adresse de l'application
        payment_txn = transaction.PaymentTxn(
            sender=address,
            sp=sp,
            receiver=smart_contract_address,
            amt=1000000
        )

        # Grouper les transactions avec l'Opt-In en première position
        transaction.assign_group_id([payment_txn, opt_in_txn])

        # Signer les transactions
        signed_opt_in_txn = opt_in_txn.sign(private_key)
        signed_payment_txn = payment_txn.sign(private_key)
        signed_group = [signed_payment_txn, signed_opt_in_txn]

        # Envoyer le groupe de transactions
        txid = algod_client.send_transactions(signed_group)
        print(f"Transactions groupées envoyées avec txid : {txid}")

        # Attendre la confirmation
        optin_result = transaction.wait_for_confirmation(algod_client, txid, 4)
        print(f"Opt-in et paiement confirmés dans le round {optin_result['confirmed-round']}.")

    except Exception as e:
        print(f"Erreur lors de la transaction : {e}")