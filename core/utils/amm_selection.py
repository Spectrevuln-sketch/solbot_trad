# from Wallet_Info import get_wallet_Info


from core.utils.alreadyBought import write_token_to_file , check_token_existence, getSettings, storeSettings

from core.repository.jupiter.buy_swap import buy
from core.repository.jupiter.jupiter import jupiter_swap
from core.utils.birdeye import get_price, getSymbol
from core.utils.checkBalance import checkB
from configparser import ConfigParser

from core.repository.raydium.buy_swap import  BuyTokenSniper as raydium_buy
from core.repository.raydium.Raydium import raydium_swap as raydium_swap_monitor_sell

from core.connect_solana import SolThrad, CruserSolana
import time
import os, sys
import os
import sys

LAMPORTS_PER_SOL = 1000000000
def select_amm2trade(token_address,payer, amount, result_queue):
    with CruserSolana() as ctx:
        with SolThrad() as event_thread:
            config = ConfigParser()
            # using sys and os because sometimes this shitty config reader does not read from curr directory
            config.read(os.path.join(sys.path[0], 'data', 'config.ini'))
            """
            Import the variables from config.ini
            """
            invest_ratio =  float(config.get("INVESTMENT", "invest_ratio"))
            # invest_amount_sol =  float(config.get("INVESTMENT", "invest_amount_in_sol"))
            invest_amount_sol =  amount


            limit_order_sell_Bool = config.getboolean("INVESTMENT", "limit_order_sell")
            take_profit_ratio =  float(config.get("INVESTMENT", "take_profit_ratio"))

            trailing_stop_Bool =  config.getboolean("INVESTMENT", "trailing_stop")
            trailing_stop_ratio =  float(config.get("INVESTMENT", "trailing_stop_ratio"))

            Limit_and_Trailing_Stop_Bool =  config.getboolean("INVESTMENT", "Limit_and_Trailing_Stop")

            desired_token_address= token_address

            """
            get your investment ratio/amount...
            get balance of your wallet
            check if you have enough balance to invest or not.

            balance - investment =  remaining amount
            if remaining amount if less than minimum balance for fees then it will not trade
            e.g. 0.01 Sol required for fees in my case...
            """
            if invest_ratio == 0:
                amount_of_sol_to_swap = int(invest_amount_sol * LAMPORTS_PER_SOL)
            else:
                currBalance = ctx.get_balance(payer.pubkey()).value
                balanceAfterRatio = currBalance * (invest_ratio / 100)
                amount_of_sol_to_swap = int(currBalance - balanceAfterRatio)
                temp = amount_of_sol_to_swap / LAMPORTS_PER_SOL

            accountBalance = ctx.get_balance(payer.pubkey())

            token_symbol, SOl_Symbol = getSymbol(desired_token_address)
            print(f"w|WALLET INFO {token_symbol}",f"SOL: {accountBalance.value / LAMPORTS_PER_SOL}")

            miniumBalanceRequired = 10000000 #for txn fees etc

            remainingAfterInvest = accountBalance.value - amount_of_sol_to_swap


            if check_token_existence(desired_token_address) == False:


                if remainingAfterInvest < miniumBalanceRequired:
                    print("[Wallet Info] Insufficient Balance: {:.10f}".format(remainingAfterInvest))
                    print(f"a|Wallet Info {token_symbol}","Insufficient Balance: {:.10f}".format(remainingAfterInvest))
                    event_thread.set()

                else:
                    """
                    Get current price of token
                    start trading it...
                    """
                    # API calls are limited to 300 requests per minute
                    # desired_token_usd_price = get_price(desired_token_address)
                    # print(f"Token Address: {desired_token_address}\nToken Price USD: {desired_token_usd_price:.15f}")
                    # print(f"a|Token Market Info {token_symbol}",f"Token Address: {desired_token_address}\nToken Price USD: {desired_token_usd_price:.15f}")

                    """
                    ..............................................
                    Jupiter Swap Starts here
                    ..............................................
                    """
                    # Call Buy Method - returns transaction hash (txB= tx for buy)
                    start_time = time.time()
                    txB = buy(payer, ctx, amount_of_sol_to_swap, token_address, config)
                    end_time = time.time()
                    execution_time = end_time - start_time
                    print(f"Total Execution time: {execution_time} seconds")

                    # Check if transaction wasnt success
                    if str(txB) != 'failed':

                        """
                        You can delete the token from the file but you cannot stop the previous thread if you executed another buy...
                        """
                        write_token_to_file(desired_token_address)

                        bought_token_price =  get_price(desired_token_address)
                        # Save the settings into a file
                        storeSettings("Jupiter",
                        desired_token_address,
                        txB,
                        execution_time,
                        limit_order_sell_Bool,
                        take_profit_ratio,
                        trailing_stop_Bool,
                        trailing_stop_ratio,
                        Limit_and_Trailing_Stop_Bool,
                        bought_token_price)


                        event_thread.set() #continue other threads
                        jupiter_swap(config, ctx, payer, desired_token_address, txB, execution_time, limit_order_sell_Bool, take_profit_ratio, trailing_stop_Bool, trailing_stop_ratio, Limit_and_Trailing_Stop_Bool, bought_token_price)


                    else:
                        print("[Jupiter] Buy Failed")
                        print(f"e|Jupiter {token_symbol}",f"Jupiter Officially failed....\nNow trying Raydium")
                        """
                        if Jupiter fails, then try Raydium
                        (if you intrested why? read more about it in docs, liquidity and why some coins are not added to jupiter)

                        Raydium Swap Starts here

                        Just use Raydium man, its much faster and better than Jupiter because of liquidity
                        But issue is that if pair is new then pools gonna be downloaded again... which slows the transaction by 10 seconds
                        """
                        print("---------------[Raydium] Buy Started---------------")
                        start_time = time.time()
                        # [Raydium] -
                        print(f"a|[Raydium] - {token_symbol}",f"Raydium Officially started....")

                        #                                                       in sol (not in lamports)
                        txB_R = raydium_buy(desired_token_address, payer, invest_amount_sol)

                        end_time = time.time()
                        execution_time = end_time - start_time
                        print(f"Total Execution time: {execution_time} seconds")
                        event_thread.set()
                        if txB_R != "failed":
                            """
                            You can delete the token from the file but you cannot stop the previous thread if you executed another buy...
                            """
                            write_token_to_file(desired_token_address)

                            bought_token_price =  get_price(desired_token_address)
                            # Save the settings into a file
                            storeSettings("Raydium",
                            desired_token_address,
                            txB_R,
                            execution_time,
                            limit_order_sell_Bool,
                            take_profit_ratio,
                            trailing_stop_Bool,
                            trailing_stop_ratio,
                            Limit_and_Trailing_Stop_Bool,
                            bought_token_price)

                            event_thread.set() #continue other threads

                            res = raydium_swap_monitor_sell(config, ctx, payer, desired_token_address, txB_R, execution_time, limit_order_sell_Bool, take_profit_ratio, trailing_stop_Bool, trailing_stop_ratio, Limit_and_Trailing_Stop_Bool, bought_token_price)
                            result_queue.put(res)
                        else:
                            print("[Raydium] Buy Failed")
                            print(f"e|Raydium {token_symbol}",f"Raydium Officially failed....")

                            event_thread.set()

            else:
                """
                Token already exists in files...
                """

                Config_settings = getSettings(desired_token_address)
                event_thread.set() #continue other threads

                try:
                    amm_name = Config_settings['amm']
                    txB = Config_settings['txB']
                    execution_time = Config_settings['execution_time']
                    limit_order_sell_Bool = Config_settings['limit_order_sell_Bool']
                    take_profit_ratio = Config_settings['take_profit_ratio']
                    trailing_stop_Bool = Config_settings['trailing_stop_Bool']
                    trailing_stop_ratio = Config_settings['trailing_stop_ratio']
                    Limit_and_Trailing_Stop_Bool = Config_settings['Limit_and_Trailing_Stop_Bool']
                    bought_token_price = Config_settings['bought_token_price']


                    if checkB(desired_token_address, payer, ctx)  == True:

                        print(f"a|Wallet Info {token_symbol}",f"Token already exists in files and ***wallet***\nNow Re-Selling it...\ntrying Jupiter...")

                        if amm_name == 'Jupiter':
                            jupiter_swap(config, ctx, payer, desired_token_address, txB, execution_time, limit_order_sell_Bool, take_profit_ratio, trailing_stop_Bool, trailing_stop_ratio, Limit_and_Trailing_Stop_Bool, bought_token_price)

                        elif amm_name == 'Raydium':
                        # if amm_name == 'Raydium':

                            raydium_swap_monitor_sell(config, ctx, payer, desired_token_address, txB, execution_time, limit_order_sell_Bool, take_profit_ratio, trailing_stop_Bool, trailing_stop_ratio, Limit_and_Trailing_Stop_Bool, bought_token_price)
                            res={
                                'status': 200,
                                'message': 'done snipeing'
                            }
                            result_queue.put(res)
                    else:
                        print(f"a|Wallet Info {token_symbol}",f"Token not found in wallet...\n")


                except Exception as e:
                    print(f"Config file missing settings, ERROR: {e}")
                    print(f"a|Config file {token_symbol}",f"Config file missing settings!\n{e}")

            print("--------------------------END--------------------------------")

