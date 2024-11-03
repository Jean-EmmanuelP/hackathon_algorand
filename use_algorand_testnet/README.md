# Algorand Testnet Account Generator

NOTE: before jumping in, it's as simple as typing `"python main.py"` in the CLI when your codespace or local machine is set up, feel free to continue reading for more info and details! :) 

This project demonstrates how to connect to the Algorand testnet, generate a new account, and manage the mnemonic phrase securely using a `.env` file. The code utilizes the `algosdk` library for interacting with the Algorand blockchain.

## Prerequisites

Before running this project, ensure you have the following installed:

- Python 3.12 or higher
- Pip (Python package manager)
- Algokit (pipx install algokit)

## Getting Started (Local Machine or Codespace!)

Follow the instructions below to set up the project on your Local Machine or GitHub Codespace.

### 1. Clone the Repository or Skip Setup and Enter Codespace!

If you're running locally:

```bash
git clone https://github.com/yourusername/use_algorand_testnet.git
cd use_algorand_testnet
```

Alternatively, if you're using GitHub Codespace, simply open this repository in a Codespace, and proceed to the next step. The container setup and environment will be handled for you automatically!

### 2. Codespace Setup

When entering the Codespace for the first time, the following will happen automatically:

- Required ports (algod, kmd, indexer, etc.) will be forwarded.
- Dependencies will be installed (algosdk, python-dotenv, and algokit).
- The Algokit localnet will start.

Just wait for this setup to complete before proceeding to run the script.

### 3. Local Machine Setup (for VSCode without Docker)

If you're using VSCode on your local machine, you do not need Docker as the project connects directly to a testnet node.

- Open the cloned project in VSCode.
- Ensure you have Python 3.12 or higher installed.
- If --> you are already an algokit user just `python main.py` it!
- Else --> Install the dependencies manually:

```bash
pip3 install py-algorand-sdk python-dotenv
pipx install algokit
```

### 4. Run the Script

To generate a new Algorand account or use an existing one, run the following command:

```bash
python main.py
```

### 5. Understanding the Output

- If a mnemonic phrase is not found in the `.env` file, a new Algorand account will be generated, and the mnemonic will be saved to the `.env` file.
- If the mnemonic already exists, the script will load the existing account and display the account address.
- The script will also confirm the connection to the Algorand testnet.

## Code Overview

- `main.py`: The main script that connects to the Algorand testnet, generates accounts, and manages the mnemonic phrase.
- `.env`: A file that stores the mnemonic phrase securely after you run the main.py file.

### Key Functions

- `connect_to_algorand_testnet()`: Initializes the Algorand client to connect to the testnet.
- `generate_new_account()`: Generates a new Algorand account and returns the address and mnemonic phrase.
- `write_mnemonic_to_env(mnemonic_phrase)`: Saves the generated mnemonic to a `.env` file.
- `load_passphrase_from_env()`: Loads the mnemonic from the `.env` file.
- `get_private_key_from_mnemonic(mnemonic_phrase)`: Converts the mnemonic back to the private key.

## How to fund your testnet account with AlgoKit CLI

To obtain ALGO for testing on the Algorand testnet, follow these steps:

1. **Login to the Dispenser**:
   ```bash
   algokit dispenser login
   ```

2. **Fund Your Account**:
   ```bash
   algokit dispenser fund -r <your-account-address> -a 10000000
   ```

3. **Confirm the Transaction**:
   After funding, you'll receive a transaction confirmation. You can view the transaction details at the provided link.

### Fund your account with the online testnet dispenser

You can also fund online with the testnet dispenser, but its not as fun..: https://bank.testnet.algorand.network/ 

## Important Notes

- The mnemonic phrase is sensitive information. Store it securely and do not expose it publicly.
- The testnet is a simulated environment for testing purposes.

## Acknowledgments

- [Download AlgoKit!](https://developer.algorand.org/algokit/?utm_source=af_employee&utm_medium=social&utm_campaign=algokit_sarajane&utm_content=download&utm_term=EME)
- [Algorand Developer Documentation](https://developer.algorand.org/docs/)
- [Algorand SDK for Python](https://github.com/algorand/py-algorand-sdk)
- [Nodely](https://nodely.io/docs/free/start) 

## Join the AlgoDevs Community!

- [Join us on X](https://x.com/algodevs) 
- [Join us on Discord](https://discord.com/invite/algorand) 
# algorand_challenges
