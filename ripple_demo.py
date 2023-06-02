from xrpl.transaction import safe_sign_and_autofill_transaction, send_reliable_submission
from xrpl.models.transactions.nftoken_mint import NFTokenMint, NFTokenMintFlag
from xrpl.utils import str_to_hex, hex_to_str
from xrpl.wallet import generate_faucet_wallet
from xrpl.models.requests import AccountNFTs
from xrpl.clients import JsonRpcClient

TESTNET_RPC_URL = "https://s.altnet.rippletest.net:51234/"
xrp_client = JsonRpcClient(TESTNET_RPC_URL)

# Let's create a prefunded test account
issuer_wallet = generate_faucet_wallet(xrp_client, debug=True)

# Construct NFTokenMint transaction to mint 1 NFT
mint_tx = NFTokenMint(
    account=issuer_wallet.classic_address,
    nftoken_taxon=1,
    flags=NFTokenMintFlag.TF_TRANSFERABLE,
    uri=str_to_hex("https://deep-ink.ventures")
)

# Sign mint_tx using the issuer account
mint_tx_signed = safe_sign_and_autofill_transaction(transaction=mint_tx, wallet=issuer_wallet, client=xrp_client)
mint_tx_result = send_reliable_submission(transaction=mint_tx_signed, client=xrp_client).result

# Query the minted account for its NFTs
get_account_nfts = xrp_client.request(
    AccountNFTs(account=issuer_wallet.classic_address)
)

for nft in get_account_nfts.result['account_nfts']:
    print(
        f"\nIssuer: {nft['Issuer']}"
        f"\nNFT ID: {nft['NFTokenID']}"
        f"\nNFT Taxon: {nft['NFTokenTaxon']}"
        f"\nNFT URI: {hex_to_str(nft['URI'])}"
    )

print(f"\nMint TX: https://testnet.xrpl.org/transactions/{mint_tx_result['hash']}")
print(f"\All NFTs: https://testnet.xrpl.org/accounts/{issuer_wallet.classic_address}/assets/nft")
