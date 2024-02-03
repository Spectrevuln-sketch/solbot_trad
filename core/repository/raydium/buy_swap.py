from spl.token.instructions import close_account, CloseAccountParams
from spl.token.client import Token
from spl.token.core import _TokenCore

from solana.rpc.commitment import Commitment
from solana.rpc.api import RPCException

from solders.pubkey import Pubkey

from core.repository.raydium.create_close_account import get_token_account,fetch_pool_keys, get_token_account, make_swap_instruction
from core.utils.birdeye import getSymbol
from core.connect_solana import CruserSolana


import time

LAMPORTS_PER_SOL = 1000000000


def BuyToken(TOKEN_TO_SWAP_BUY, payer, amount):
    with CruserSolana() as solana_client:
        token_symbol, SOl_Symbol = getSymbol(TOKEN_TO_SWAP_BUY)
        mint = Pubkey.from_string(TOKEN_TO_SWAP_BUY)
        pool_keys = fetch_pool_keys(str(mint))
        print(f'Pool keys: {pool_keys}')
        if pool_keys == "failed":
            print(f"a|BUY Pool ERROR {token_symbol}",f"[Raydium]: Pool Key Not Found")
            return {
                "status": 404,
                "message": "[Raydium]: Pool Key Not Found"
            }
        """
        Calculate amount
        """
        # amount_in_1 = int(amount * LAMPORTS_PER_SOL)
        slippage = 0.1
        lamports_amm = amount * LAMPORTS_PER_SOL
        amount_in =  int(lamports_amm - (lamports_amm * (slippage/100)))

        # Set Program ID
        AccountMint = solana_client.get_account_info_json_parsed(mint).value
        TOKEN_PROGRAM_ID = AccountMint.owner
        swap_associated_token_address,swap_token_account_Instructions  = get_token_account(solana_client, payer.pubkey(), mint)
        balance_needed = Token.get_min_balance_rent_for_exempt_for_account(solana_client)
        WSOL_token_account, swap_tx, payer, Wsol_account_keyPair, opts, = _TokenCore._create_wrapped_native_account_args(TOKEN_PROGRAM_ID, payer.pubkey(), payer,amount_in, False, balance_needed, Commitment("confirmed"))
        # Create Instruction Transaction
        instructions_swap = make_swap_instruction(  amount_in,
                                                    WSOL_token_account,
                                                    swap_associated_token_address,
                                                    pool_keys,
                                                    mint,
                                                    solana_client,
                                                    payer
                                                )
        params = CloseAccountParams(account=WSOL_token_account, dest=payer.pubkey(), owner=payer.pubkey(),   program_id=TOKEN_PROGRAM_ID)
        closeAcc =(close_account(params))

        if swap_token_account_Instructions != None:
            swap_tx.add(swap_token_account_Instructions)
        swap_tx.add(instructions_swap)
        swap_tx.add(closeAcc)
        try:
            print("7. Execute Transaction...")
            start_time = time.time()
            txn = solana_client.send_transaction(swap_tx, payer, Wsol_account_keyPair)
            txid_string_sig = txn.value

            checkTxn = True
            while checkTxn:
                try:
                    status = solana_client.get_transaction(txid_string_sig,"json")
                    FeesUsed = (status.value.transaction.meta.fee) / 1000000000
                    if status.value.transaction.meta.err == None:
                        print("[create_account] Transaction Success",txn.value)
                        print(f"[create_account] Transaction Fees: {FeesUsed:.10f} SOL")

                        end_time = time.time()
                        execution_time = end_time - start_time
                        print(f"Execution time: {execution_time} seconds")

                        checkTxn = False
                        return txid_string_sig

                    else:
                        print("Transaction Failed")
                        end_time = time.time()
                        execution_time = end_time - start_time
                        print(f"Execution time: {execution_time} seconds")
                        checkTxn = False

                except Exception as e:
                    print(f"e|BUY ERROR {token_symbol}",f"[Raydium]: {e}")
                    print("Sleeping...",e)
                    time.sleep(0.500)
                    print("Retrying...")

        except RPCException as e:
            print(f"Error: [{e.args[0].message}]...\nRetrying...")
            print(f"e|BUY ERROR {token_symbol}",f"[Raydium]: {e.args[0].data.logs}")
            time.sleep(1)
        except Exception as e:
            print(f"e|BUY Exception ERROR {token_symbol}",f"[Raydium]: {e}")
            print(f"Error: [{e}]...\nEnd...")
            checkTxn = False
            return "failed"

        print(f'AccountMint {AccountMint}')



def buy(solana_client, TOKEN_TO_SWAP_BUY, payer, amount):
    token_symbol, SOl_Symbol = getSymbol(TOKEN_TO_SWAP_BUY)

    mint = Pubkey.from_string(TOKEN_TO_SWAP_BUY)

    pool_keys = fetch_pool_keys(str(mint))
    if pool_keys == "failed":
        print(f"a|BUY Pool ERROR {token_symbol}",f"[Raydium]: Pool Key Not Found")
        return "failed"
    """
    Calculate amount
    """
    amount_in = int(amount * LAMPORTS_PER_SOL)
    slippage = 0.1
    lamports_amm = amount * LAMPORTS_PER_SOL
    amount_in =  int(lamports_amm - (lamports_amm * (slippage/100)))

    return print(f"POOOL KEYS {amount_in}")
    txnBool = True
    while txnBool:

        """Get swap token program id"""
        print("1. Get TOKEN_PROGRAM_ID...")
        accountProgramId = solana_client.get_account_info_json_parsed(mint)
        TOKEN_PROGRAM_ID = accountProgramId.value.owner

        """
        Set Mint Token accounts addresses
        """
        print("2. Get Mint Token accounts addresses...")
        swap_associated_token_address,swap_token_account_Instructions  = get_token_account(solana_client, payer.pubkey(), mint)


        """
        Create Wrap Sol Instructions
        """
        print("3. Create Wrap Sol Instructions...")
        balance_needed = Token.get_min_balance_rent_for_exempt_for_account(solana_client)
        WSOL_token_account, swap_tx, payer, Wsol_account_keyPair, opts, = _TokenCore._create_wrapped_native_account_args(TOKEN_PROGRAM_ID, payer.pubkey(), payer,amount_in,
                                                            False, balance_needed, Commitment("confirmed"))
        """
        Create Swap Instructions
        """
        print("4. Create Swap Instructions...")
        instructions_swap = make_swap_instruction(  amount_in,
                                                    WSOL_token_account,
                                                    swap_associated_token_address,
                                                    pool_keys,
                                                    mint,
                                                    solana_client,
                                                    payer
                                                )


        print("5. Create Close Account Instructions...")
        params = CloseAccountParams(account=WSOL_token_account, dest=payer.pubkey(), owner=payer.pubkey(), program_id=TOKEN_PROGRAM_ID)
        closeAcc =(close_account(params))

        print("6. Add instructions to transaction...")
        if swap_token_account_Instructions != None:
            swap_tx.add(swap_token_account_Instructions)
        swap_tx.add(instructions_swap)
        swap_tx.add(closeAcc)

        try:
            print("7. Execute Transaction...")
            start_time = time.time()
            txn = solana_client.send_transaction(swap_tx, payer, Wsol_account_keyPair)
            txid_string_sig = txn.value

            print("8. Confirm transaction...")
            checkTxn = True
            while checkTxn:
                try:
                    status = solana_client.get_transaction(txid_string_sig,"json")
                    FeesUsed = (status.value.transaction.meta.fee) / 1000000000
                    if status.value.transaction.meta.err == None:
                        print("[create_account] Transaction Success",txn.value)
                        print(f"[create_account] Transaction Fees: {FeesUsed:.10f} SOL")

                        end_time = time.time()
                        execution_time = end_time - start_time
                        print(f"Execution time: {execution_time} seconds")

                        txnBool = False
                        checkTxn = False
                        return txid_string_sig

                    else:
                        print("Transaction Failed")
                        end_time = time.time()
                        execution_time = end_time - start_time
                        print(f"Execution time: {execution_time} seconds")
                        checkTxn = False

                except Exception as e:
                    print(f"e|BUY ERROR {token_symbol}",f"[Raydium]: {e}")
                    print("Sleeping...",e)
                    time.sleep(0.500)
                    print("Retrying...")

        except RPCException as e:
            print(f"Error: [{e.args[0].message}]...\nRetrying...")
            print(f"e|BUY ERROR {token_symbol}",f"[Raydium]: {e.args[0].data.logs}")
            time.sleep(1)

        except Exception as e:
            print(f"e|BUY Exception ERROR {token_symbol}",f"[Raydium]: {e}")
            print(f"Error: [{e}]...\nEnd...")
            txnBool = False
            return "failed"
