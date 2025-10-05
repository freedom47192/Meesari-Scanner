import requests

# ---------------- Fixed Meesari addresses (replace with real ones) ---------------- #
MEESARI_ETH = "0x000000000000000000000000000000000000dead"
MEESARI_SOL = "6VrkEwujanbChtqqDabAoZXKGkJKvjzcU9PDDL6Lce8x"  # replace with real one

# ---------------- ETH ---------------- #
def get_eth_transactions(wallet):
    url = f"https://api.etherscan.io/api"
    params = {
        "module": "account",
        "action": "txlist",
        "address": wallet,
        "startblock": 0,
        "endblock": 99999999,
        "sort": "asc",
        "apikey": "TAU4QI8TQAZKR6FPI4ZKDGJ5EWFYB5M3GY"  # get from etherscan.io
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        return data.get("result", [])
    except Exception as e:
        print(f"⚠️ ETH fetch error: {e}")
        return []

def check_meesari_eth(wallet):
    txs = get_eth_transactions(wallet)
    count = 0
    total = 0.0
    for tx in txs:
        if tx.get("to", "").lower() == MEESARI_ETH.lower() or tx.get("from", "").lower() == MEESARI_ETH.lower():
            count += 1
            eth_value = int(tx["value"]) / 1e18
            total += eth_value
    print(f"\nWallet: {wallet}")
    print("Blockchain: Ethereum")
    print(f"Payments with Meesari: {count}")
    print(f"Total ETH transferred: {total:.6f}")

# ---------------- SOL (Helius) ---------------- #
# Insert your Helius API key here
HELIUS_API_KEY = "8abfe7bd-db97-43ec-ac37-1e46352a4738"
HELIUS_URL = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"

def get_sol_signatures(wallet, limit=10):
    headers = {"Content-Type": "application/json"}
    data = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [wallet, {"limit": limit}]
    }
    try:
        r = requests.post(HELIUS_URL, headers=headers, json=data, timeout=10)
        return r.json().get("result", [])
    except Exception as e:
        print(f"⚠️ Solana fetch error: {e}")
        return []

def get_sol_transaction(signature):
    headers = {"Content-Type": "application/json"}
    data = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [signature, {"encoding": "jsonParsed"}]
    }
    try:
        r = requests.post(HELIUS_URL, headers=headers, json=data, timeout=10)
        return r.json().get("result")
    except Exception as e:
        print(f"⚠️ Error fetching transaction {signature}: {e}")
        return None

def check_meesari_sol(wallet):
    signatures = get_sol_signatures(wallet, limit=10)
    print(f"Found {len(signatures)} recent transactions on Solana")

    count = 0
    total_sol = 0.0

    for sig_info in signatures:
        sig = sig_info["signature"]
        print(f"🔍 Checking {sig} ...")
        tx = get_sol_transaction(sig)
        if not tx:
            print("  ⚠️ No tx data")
            continue

        instructions = tx["transaction"]["message"]["instructions"]
        for instr in instructions:
            if "parsed" in instr:
                parsed = instr["parsed"]
                if parsed.get("type") == "transfer":
                    if (parsed["info"]["source"] == MEESARI_SOL or 
                        parsed["info"]["destination"] == MEESARI_SOL):
                        count += 1
                        total_sol += float(parsed["info"]["lamports"]) / 1e9

    print(f"\nWallet: {wallet}")
    print("Blockchain: Solana")
    print(f"Payments with Meesari: {count}")
    print(f"Total SOL transferred: {total_sol:.6f}")

# ---------------- Main ---------------- #
def main():
    wallet = input("Enter your wallet address: ").strip()

    if wallet.startswith("0x"):  # ETH
        check_meesari_eth(wallet)
    else:  # assume SOL
        check_meesari_sol(wallet)

if __name__ == "__main__":
    main()