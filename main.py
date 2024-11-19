import random
from bip_utils import Bip39MnemonicGenerator, Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
import requests
import phrases_2048  # Assuming phrases_2048 is a Python module with a list named 'phrases_2048'
import time

def generate_seed_phrase():
    # Generate a valid 12-word seed phrase
    mnemonic = Bip39MnemonicGenerator().FromWordsNumber(12)
    return mnemonic

def derive_wallet_address(mnemonic):
    # Generate seed from mnemonic
    seed_bytes = Bip39SeedGenerator(mnemonic).Generate()
    # Generate wallet (BIP-44 standard for Bitcoin in this example)
    bip44_mst_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.BITCOIN)
    bip44_acc_ctx = bip44_mst_ctx.Purpose().Coin().Account(0)
    bip44_chg_ctx = bip44_acc_ctx.Change(Bip44Changes.CHAIN_EXT)
    bip44_addr_ctx = bip44_chg_ctx.AddressIndex(0)
    return bip44_addr_ctx.PublicKey().ToAddress()

def check_wallet_existence_and_balance(address):
    try:
        # Blockchain.com API call for Bitcoin
        response = requests.get(f"https://blockchain.info/rawaddr/{address}")
        response.raise_for_status()
        data = response.json()

        # Debug: Print raw response data
        print(f"API Response: {data}")

        if 'final_balance' in data:
            balance = data['final_balance']
            return True, balance
        else:
            return False, 0
    except requests.exceptions.RequestException as e:
        # Debug: Print exception details
        print(f"Request failed: {e}")
        return False, 0

def save_to_file(seed_phrase, wallet_address, balance, file_name):
    with open(file_name, "a") as file:
        file.write(f"Seed Phrase: {seed_phrase}\n")
        file.write(f"Wallet Address: {wallet_address}\n")
        file.write(f"Balance: {balance}\n\n")

# Main function
def main():
    for _ in range(3600):
        # Step 1: Generate seed phrase
        seed_phrase = generate_seed_phrase()
        print(f"Generated Seed Phrase: {seed_phrase}")

        # Step 2: Derive wallet address
        wallet_address = derive_wallet_address(seed_phrase)
        print(f"Derived Wallet Address: {wallet_address}")

        # Step 3: Check wallet existence and balance
        exists, balance = check_wallet_existence_and_balance(wallet_address)
        if exists:
            print(f"Wallet exists with balance: {balance}")
            if balance > 0:
                # Save to a file for wallets with non-zero balance
                save_to_file(seed_phrase, wallet_address, balance, "non_zero_balance_wallets.txt")
            else:
                # Save to the original file for wallets with zero balance
                save_to_file(seed_phrase, wallet_address, balance, "wallet_info.txt")
        else:
            print("Wallet does not exist or cannot retrieve balance.")
            # Save to the original file for wallets that do not exist
            save_to_file(seed_phrase, wallet_address, balance, "wallet_info.txt")

        # Wait for 1 second before the next request
        time.sleep(5)

if __name__ == "__main__":
    main()
