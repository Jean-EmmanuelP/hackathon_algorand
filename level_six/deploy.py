import os
from algosdk import account, mnemonic, transaction
from algosdk.v2client import algod
from dotenv import load_dotenv
import certifi
from pyteal import compileTeal, Mode, Btoi, Itob, Seq, Log, Int, Txn, If
from base64 import b64decode

def sum_contract():
    # Check if this is an application call (not creation)
    program = Seq([
        # If it's a creation call, just approve it
        If(Txn.application_id() == Int(0))
        .Then(Int(1))
        # Otherwise, perform the sum operation
        .Else(
            Seq([
                Log(Itob(Btoi(Txn.application_args[0]) + Btoi(Txn.application_args[1]))),
                Int(1)
            ])
        )
    ])
    return program

# Helper Functions
def connect_to_algorand_testnet():
    return algod.AlgodClient("", "https://testnet-api.algonode.cloud")

def load_passphrase_from_env():
    load_dotenv()
    return os.getenv("PASSPHRASE")

def get_private_key_from_mnemonic(mnemonic_phrase):
    return mnemonic.to_private_key(mnemonic_phrase)

def compile_smart_contract(client, teal_code):
    compile_response = client.compile(teal_code)
    return compile_response['result']

def deploy_sum_contract(client, creator_private_key, teal_code):
    # Compile the smart contract
    program = compile_smart_contract(client, teal_code)
    approval_program = b64decode(program)
    clear_program = b64decode(compile_smart_contract(client, compileTeal(Int(1), mode=Mode.Application, version=5)))

    # Transaction parameters
    params = client.suggested_params()
    txn = transaction.ApplicationCreateTxn(
        sender=account.address_from_private_key(creator_private_key),
        sp=params,
        on_complete=transaction.OnComplete.NoOpOC,
        approval_program=approval_program,
        clear_program=clear_program,
        global_schema=transaction.StateSchema(0, 0),
        local_schema=transaction.StateSchema(0, 0),
    )

    # Sign and send transaction
    signed_txn = txn.sign(creator_private_key)
    tx_id = client.send_transaction(signed_txn)
    transaction.wait_for_confirmation(client, tx_id)
    response = client.pending_transaction_info(tx_id)
    app_id = response['application-index']
    print(f"Deployed app ID: {app_id}")
    return app_id

if __name__ == "__main__":
    # Set the SSL_CERT_FILE environment variable for Algonode connections
    os.environ['SSL_CERT_FILE'] = certifi.where()
    
    passphrase = load_passphrase_from_env()
    if not passphrase:
        print("Mnemonic not found in .env file.")
        exit()

    # Account and Client Setup
    private_key = get_private_key_from_mnemonic(passphrase)
    algod_client = connect_to_algorand_testnet()
    
    # Compile and Deploy the Sum Contract
    teal_code = compileTeal(sum_contract(), mode=Mode.Application, version=5)
    app_id = deploy_sum_contract(algod_client, private_key, teal_code)
    print(f"Save this app_id for opt-in: {app_id}")