from spl.token.instructions import create_associated_token_account, get_associated_token_address

from solders.pubkey import Pubkey
from solders.instruction import Instruction

from solana.rpc.types import TokenAccountOpts
from solana.transaction import AccountMeta
from core.connect_solana import CruserSolana

from core.repository.raydium.layouts import SWAP_LAYOUT

import json,requests

LAMPORTS_PER_SOL = 1000000000
AMM_PROGRAM_ID = Pubkey.from_string('675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8')
SERUM_PROGRAM_ID = Pubkey.from_string('srmqPvymJeFKQ4zGQed1GFppgkRHL9kaELCbyksJtPX')

def make_swap_instruction(amount_in: int, token_account_in: Pubkey.from_string, token_account_out: Pubkey.from_string,
                              accounts: dict, mint, ctx, owner) -> Instruction:
        tokenPk = mint
        accountProgramId = ctx.get_account_info_json_parsed(tokenPk)
        TOKEN_PROGRAM_ID = accountProgramId.value.owner

        keys = [
            AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
            AccountMeta(pubkey=accounts["amm_id"], is_signer=False, is_writable=True),
            AccountMeta(pubkey=accounts["authority"], is_signer=False, is_writable=False),
            AccountMeta(pubkey=accounts["open_orders"], is_signer=False, is_writable=True),
            AccountMeta(pubkey=accounts["target_orders"], is_signer=False, is_writable=True),
            AccountMeta(pubkey=accounts["base_vault"], is_signer=False, is_writable=True),
            AccountMeta(pubkey=accounts["quote_vault"], is_signer=False, is_writable=True),
            AccountMeta(pubkey=SERUM_PROGRAM_ID, is_signer=False, is_writable=False),
            AccountMeta(pubkey=accounts["market_id"], is_signer=False, is_writable=True),
            AccountMeta(pubkey=accounts["bids"], is_signer=False, is_writable=True),
            AccountMeta(pubkey=accounts["asks"], is_signer=False, is_writable=True),
            AccountMeta(pubkey=accounts["event_queue"], is_signer=False, is_writable=True),
            AccountMeta(pubkey=accounts["market_base_vault"], is_signer=False, is_writable=True),
            AccountMeta(pubkey=accounts["market_quote_vault"], is_signer=False, is_writable=True),
            AccountMeta(pubkey=accounts["market_authority"], is_signer=False, is_writable=False),
            AccountMeta(pubkey=token_account_in, is_signer=False, is_writable=True),  #UserSourceTokenAccount
            AccountMeta(pubkey=token_account_out, is_signer=False, is_writable=True), #UserDestTokenAccount
            AccountMeta(pubkey=owner.pubkey(), is_signer=True, is_writable=False) #UserOwner
        ]

        data = SWAP_LAYOUT.build(
            dict(
                instruction=9,
                amount_in=int(amount_in),
                min_amount_out=0
            )
        )
        return Instruction(AMM_PROGRAM_ID, data, keys)

def get_token_account(ctx,
                      owner: Pubkey.from_string,
                      mint: Pubkey.from_string):
    try:
        account_data = ctx.get_token_accounts_by_owner(owner, TokenAccountOpts(mint))
        print(f'TokenAccount {account_data}')
        return account_data.value[0].pubkey, None
    except:
        swap_associated_token_address = get_associated_token_address(owner, mint)
        swap_token_account_Instructions = create_associated_token_account(owner, owner, mint)
        print(f'SWAP ASSOCIATED TOKEN {swap_associated_token_address}\n\n'f'TOKEN ACCOUNT SWAP INST {swap_token_account_Instructions}')
        return swap_associated_token_address, swap_token_account_Instructions

def sell_get_token_account(ctx,
                      owner: Pubkey.from_string,
                      mint: Pubkey.from_string):
    try:
        account_data = ctx.get_token_accounts_by_owner(owner, TokenAccountOpts(mint))
        return account_data.value[0].pubkey
    except:
        print("Mint Token Not found")
        return None


def extract_pool_info(pools_list: list, mint: str) -> dict:
    for pool in pools_list:

        if pool['baseMint'] == mint and pool['quoteMint'] == 'So11111111111111111111111111111111111111112':
            return pool
        elif pool['quoteMint'] == mint and pool['baseMint'] == 'So11111111111111111111111111111111111111112':
            return pool
    raise Exception(f'{mint} pool not found!')



def getAccountAMM(mint:str):
    return Pubkey.find_program_address(
        [bytes(AMM_PROGRAM_ID), bytes(Pubkey.from_string(mint)), b'amm_associated_seed'],
        AMM_PROGRAM_ID
    )[0]

def getAccountPool(mint:str):
    with CruserSolana() as solana_client:
        ammAccount = getAccountAMM(mint)
        ammAccountInfo = solana_client.get_account_info_json_parsed(ammAccount).value
        print(f'ACCOUNT AMM INFO  {ammAccount}')


def fetch_pool_keys(mint: str):
    amm_info = {}
    all_pools = {}
    try:
        # Using this so it will be faster else no option, we go the slower way.
        with open('all_pools.json', 'r') as file:
            all_pools = json.load(file)
        amm_info = extract_pool_info(all_pools, mint)
    except:
        resp = requests.get('https://api.raydium.io/v2/sdk/liquidity/mainnet.json', stream=True)
        print(f'POOLS DATA {resp.status_code}')
        if resp.status_code == 200:
            pools = resp.json()
            official = pools['official']
            unofficial = pools['unOfficial']
            all_pools = official + unofficial

            # Store all_pools in a JSON file
            with open('all_pools.json', 'w') as file:
                json.dump(all_pools, file)
            try:
                amm_info = extract_pool_info(all_pools, mint)
                print(f'POOLS: %s' % all_pools)
            except:
                return "failed"
        else:
            return "failed"
    print(f'AMM TOKEN  {amm_info}')
    return {
    'amm_id': Pubkey.from_string(amm_info['id']),
    'authority': Pubkey.from_string(amm_info['authority']),
    'base_mint': Pubkey.from_string(amm_info['baseMint']),
    'base_decimals': amm_info['baseDecimals'],
    'quote_mint': Pubkey.from_string(amm_info['quoteMint']),
    'quote_decimals': amm_info['quoteDecimals'],
    'lp_mint': Pubkey.from_string(amm_info['lpMint']),
    'open_orders': Pubkey.from_string(amm_info['openOrders']),
    'target_orders': Pubkey.from_string(amm_info['targetOrders']),
    'base_vault': Pubkey.from_string(amm_info['baseVault']),
    'quote_vault': Pubkey.from_string(amm_info['quoteVault']),
    'market_id': Pubkey.from_string(amm_info['marketId']),
    'market_base_vault': Pubkey.from_string(amm_info['marketBaseVault']),
    'market_quote_vault': Pubkey.from_string(amm_info['marketQuoteVault']),
    'market_authority': Pubkey.from_string(amm_info['marketAuthority']),
    'bids': Pubkey.from_string(amm_info['marketBids']),
    'asks': Pubkey.from_string(amm_info['marketAsks']),
    'event_queue': Pubkey.from_string(amm_info['marketEventQueue'])
        }
