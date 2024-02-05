from configparser import ConfigParser
import logging
from queue import Queue
import sys
from threading import Thread
import requests
import json
import os
import base58
import subprocess
from pybip39 import Mnemonic, Seed
from solders.keypair import Keypair
from spl.token.core import MintInfo
from jsonrpcclient import request, parse, Ok
from solders.pubkey import Pubkey
from solders.system_program import CreateAccountParams, TransferParams, transfer
from solana.transaction import Transaction, AccountMeta
from solana.rpc.types import TokenAccountOpts
from spl.token.instructions import initialize_mint, mint_to, InitializeMintParams
from spl.token.constants import TOKEN_PROGRAM_ID, MINT_LEN, ASSOCIATED_TOKEN_PROGRAM_ID
from core.connect_solana import CruserSolana, SolThrad
from core.repository.raydium.buy_swap import BuyToken as raydium_buy
from core.repository.raydium.create_close_account import get_token_account
from core.repository.raydium.sell_swap import sellCurrentToken as raydium_sell
from core.repository.users import GetCurrentUser, CreateUser
from core.repository.wallet import GetCurrentWallet, NewWalletUser, GetAllCurrentWallet, UpdateWallet
from dotenv import load_dotenv

from core.utils.amm_selection import select_amm2trade
from core.utils.metaplex.metadata import  get_metadata, get_edition, get_auction_house
from core.utils.serializer import serializeJson, findJson, filterJson
load_dotenv()

class SolanaHandler():
  # Health check
  @classmethod
  def HealthCheck(cls):
    with CruserSolana() as solana_client:
      res = requests.post(os.getenv('SOLANA_URL'), json=request('getHealth'))
      data = parse(res.json())
      if isinstance(data, Ok) and solana_client.is_connected() is not False:
          print(f'Solana client connected {data.result}')
          return True
      else:
          logging.error("Health error")
          return False

  @classmethod
  def GetAccountTokenDelegate(cls, tokenAddress, programID):
    with CruserSolana() as solana_client:
      tokenDelegated = solana_client.get_token_accounts_by_delegate_json_parsed(Pubkey.from_string(tokenAddress), TokenAccountOpts(program_id=programID))
      print(f'Token Delegated {tokenDelegated}')

  @classmethod
  def GetSupply(cls, tokenMint):
    with CruserSolana() as solana_client:
      supply = solana_client.get_token_supply(Pubkey.from_string(tokenMint))
      print(f'supply token {supply}')

  @classmethod
  def TransferSol(cls, keyPairWallet, toWalletPub, amount):
    with CruserSolana() as solana_client:
      walletAccount = solana_client.get_account_info_json_parsed(keyPairWallet.pubkey())
      print(f'wallet account: %s' % walletAccount)
      transfer_params = TransferParams(from_pubkey=keyPairWallet.pubkey(), to_pubkey=toWalletPub, lamports=amount * 10**9)
      transaction_id, blockhash = transfer(solana_client, transfer_params, sender_account)

  @classmethod
  def CheckReleaseToken(cls, pubkeyToken, ownerToken):
     with CruserSolana() as solana_client:
      getMetaData = get_metadata(str(pubkeyToken))
      if getMetaData is not None:
        tokenAccount = solana_client.get_token_largest_accounts(pubkeyToken)
        res = requests.get(getMetaData['data']['uri']).json()
        getMintAccountInfo = solana_client.get_account_info_json_parsed(pubkeyToken).value
        if tokenAccount is not None and res is not None:
          return{
            "status": "00",
            "data":{
              **getMetaData,
              "tokenData": res,
              "accountInfo" : getMintAccountInfo.data
            },
            "message": "Success get token information"
          }
        else:
          return{
            'status': '99',
            'message': 'Token is not available'
          }
      else:
        return{
            'status': '99',
            'message': 'Token is not available'
          }


  @classmethod
  def GetAssetsInfo(cls, ownerPub):
    with CruserSolana() as solana_client:
      payload = {
          "jsonrpc": "2.0",
          "id": 1,
          "method": "getAssetsByOwner",
          "params": {
              "ownerAddress": str(ownerPub),
              "limit": 10,
              "page": 1
          }
      }
      res = requests.post(os.getenv('SOLANA_URL'), json=payload)
      data = parse(res.json())
      print(f'DATA ON OWNER ASSETS {data}')
      if isinstance(data, Ok) and solana_client.is_connected() is not False:
        print(f'result data  {data}')
        return data
      else:
        logging.error('Error Get Assets Token')
        return None

  @classmethod
  def CheckLunchToken(cls, tokenTargetMint):
    with CruserSolana() as solana_client:
      if solana_client.is_connected():
         tokenAccount = solana_client.get_token_largest_accounts(tokenTargetMint)
         print(f"Token Account Data : {tokenAccount}")
      else:
        return {
          "status": 400,
          "message": "solana is not connected"
        }
  @classmethod
  def SnapeToken(cls, wallet_payer, token_address, amount):
    with CruserSolana() as solana_account:
      config = ConfigParser()
      config.read(os.path.join(sys.path[0], 'data', 'config.ini'))
      serialize = serializeJson(wallet_payer)
      findCurrentWallet = filterJson(serialize, "status", True)
      if findCurrentWallet is not None:
        for data in findCurrentWallet:
          pairKeyWallet = Keypair().from_base58_string(data["private_key"])
          # print(f"MY BALANCE: {pairKeyWallet.pubkey()}")
          # currBalance = solana_client.get_balance(pairKeyWallet.pubkey()).value
          # print(f"MY BALANCE: {currBalance}")

          # balanceAfterRatio = currBalance * (amount / 100)
          # balence_last = int(currBalance - balanceAfterRatio)
          # update={
          #   "balance": balence_last,
          # }
          # UpdateWallet(data["id"], update)
          # print(f'AMOUNT OF SOL   {amount}')
          # raydium_sell(token_address, pairKeyWallet, amount)
          select_amm2trade(token_address, pairKeyWallet,amount)
      else:
        print(f'Sell token data is none')
        return None

  @classmethod
  def SellToken(cls, wallet_payer, amount, token_address):
    with CruserSolana() as solana_client:
      config = ConfigParser()
      config.read(os.path.join(sys.path[0], 'data', 'config.ini'))
      serialize = serializeJson(wallet_payer)
      findCurrentWallet = filterJson(serialize, "status", True)
      if findCurrentWallet is not None:
        for data in findCurrentWallet:
          pairKeyWallet = Keypair().from_base58_string(data["private_key"])
          # print(f"MY BALANCE: {pairKeyWallet.pubkey()}")
          # currBalance = solana_client.get_balance(pairKeyWallet.pubkey()).value
          # print(f"MY BALANCE: {currBalance}")

          # balanceAfterRatio = currBalance * (amount / 100)
          # balence_last = int(currBalance - balanceAfterRatio)
          # update={
          #   "balance": balence_last,
          # }
          # UpdateWallet(data["id"], update)
          # print(f'AMOUNT OF SOL   {amount}')
          raydium_sell(token_address, pairKeyWallet, amount)
      else:
        print(f'Sell token data is none')
        return None

  @classmethod
  def BuyToken(cls, wallet_payer, amount_sol_to_invest, token_address):
    with CruserSolana() as  solana_client:
      config = ConfigParser()
      config.read(os.path.join(sys.path[0], 'data', 'config.ini'))
      serializer = serializeJson(wallet_payer)
      findCurrentData = filterJson(serializer, "status", True)
      if findCurrentData is not None:
        for data in findCurrentData:
          pairKeyWallet = Keypair().from_base58_string(data["private_key"])
          currBalance = solana_client.get_balance(pairKeyWallet.pubkey()).value
          balanceAfterRatio = currBalance * (amount_sol_to_invest / 100)
          balence_last = int(currBalance - balanceAfterRatio)
          update={
            "balance": balence_last,
          }
          UpdateWallet(data["id"], update)
          raydiumBuy=True
          while raydiumBuy:
            buyToken = raydium_buy(token_address, pairKeyWallet, amount_sol_to_invest)
            print(f'Buy token return {buyToken}')
            if buyToken["status"] == 404:
              raydiumBuy=False
              return{
                "status": 404,
                "message": buyToken["message"]
              }
            else:
              raydiumBuy=False
              return{
                "status": 200,
                "message": buyToken["message"]
              }
      else:
        print(f'Buy Token data is none')
        return None

  @classmethod
  def GetTokenSupply(cls, token_address: []):
      response = requests.post(os.getenv('SOLANA_URL'), json=request("getTokenSupply", params=(["7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU"])))
      parsed = parse(response.json())
      print(f'Token Mint Data ================================================================= {parsed}')
      return parsed.result

    # with CruserSolana() as solana_client:
    #   print(f'TOKEN ADDRESS {token_address}')
    #   if solana_client.is_connected():
    #     try:
    #       response = requests.post(os.getenv('SOLANA_URL'), json=request("getTokenSupply", params=(["4cLX1cHWEEGr9iUg7gkNcheHuoAZfW1n6QkPnJNb6XTt"])))
    #       parsed = parse(response.json())

    #       if isinstance(parsed, Ok):
    #           return parsed.result
    #       else:
    #         logging.error(parsed.message)
    #         return None
    #     except Exception as e:
    #       print(f'Token Supply Error :  {e} ')
    #       return None
    #   else:
    #     print(f'Solana Has Been Error')

# REQUEST AIR DROP IS FOR DEVELOPMENT
  @classmethod
  def RequestAirdrop(cls, public_key:str):
    with CruserSolana() as solana_clinet:
      try:
        requestAirdrop = solana_clinet.request_airdrop(Pubkey.from_string(public_key), 100000)
        print(f"Airdrop request {requestAirdrop}")
        if requestAirdrop is not None:
          return requestAirdrop
        else:
          return None
      except Exception as e:
        print(f'Request airdrop failed with error {e}')

  @classmethod
  def GetSoalnaAccount(cls, public_key):
    with CruserSolana() as solana_client:
      account_info = solana_client.get_account_info(Pubkey.from_string(public_key))
      if account_info is None:
        return None

      return account_info

  # Generate Account With Solana CLI
  @classmethod
  def GenerateAccountCli(cls,chat_id):
    with CruserSolana() as solana_client:
      script_directory = os.path.dirname(os.path.abspath(__file__))
      output_directory = os.path.join(script_directory, '../../json/')
      os.makedirs(output_directory, exist_ok=True)
      os.chdir(output_directory)

      command = f'solana-keygen new --force --no-bip39-passphrase --outfile account-{chat_id}.json'

      try:
          # Open a subprocess and provide input
          result = subprocess.run(command, shell=True, text=True, capture_output=True)

            # Check for errors
          if result.returncode == 0:
              print(f'Solana CLI Output: {result.stdout}')

              # Read and print the content of the JSON file
              file_path = os.path.join(output_directory, f'account-{chat_id}.json')
              with open(file_path, 'r') as file:
                  json_content = json.load(file)
                  print(f'KEY PAIR  keypairBytes {json_content}')
                  # KEYPAIR FOR WALLET
                  keypair = Keypair.from_bytes(json_content)
                  public_key = keypair.pubkey()
                  private_key = base58.b58encode(bytes(keypair)).decode()
                  # END KEYPAIR FOR WALLET

                  print(
                    f'Private key : === {private_key} \n',
                    f'Public key : === {public_key} \n'
                  )
                  # if os.getenv('ENV') == 'development':
                  #   print(f'Requesting airdrop for {solana_client.request_airdrop(Pubkey.from_string(public_key), 1000000000)}')
                  #  Store the private key
                  user = GetCurrentUser(chat_id)
                  print(f'user data {user}')
                  if user is not None:
                      balance = solana_client.get_balance(pubkey=public_key).value
                      payload ={
                          'tele_id': user[4],
                          'private_key': private_key,
                          'public_key': str(public_key),
                          'is_connected': True,
                          'balance': balance,
                          'default': True,
                      }
                      NewWalletUser(payload)
                      wallet_info = (
                            f"New Wallet Info:\n"
                            f"Address: {public_key}\n"
                            f"Private key: {private_key}\n"
                        )
                      return wallet_info
                  else:
                    print('ERROR Connecting to solana')
                    return None

          else:
              print(f'Solana CLI Error: {result.stderr}')
      except Exception as e:
          print(f'Error: {e}')

  @classmethod
  def MakeWalletFirst(cls, chat_id):
    with CruserSolana() as solana_client:
      if solana_client.is_connected():
        pair_byte = Keypair()
        private_key = base58.b58encode(bytes(pair_byte)).decode()
        public_key = pair_byte.pubkey()
        wallet_key_address = private_key
        print(f'PUBLIC KEY {public_key}')

        user = GetCurrentUser(chat_id)
        if user is not None:
            balance = solana_client.get_balance(pubkey=public_key).value
            payload ={
                'tele_id': user[4],
                'private_key': wallet_key_address,
                'public_key': str(public_key),
                'is_connected': True,
                'balance': balance,
                'default': True
            }
            print(f'payload data {payload}')
            NewWalletUser(payload)
            wallet_info = (
                  f"New Wallet Info:\n"
                  f"Address: {public_key}\n"
                  f"Private key: {wallet_key_address}"
              )
            return wallet_info
      else:
        print('Cannot Connect to solana')
        return None

# Connect Wallet data
  @classmethod
  def ConnectWallet(cls, chat_id, private_key):
    print(f'Connecting wallet ....')
    with CruserSolana() as solana_client:
      if solana_client.is_connected():
        privateKeyBytes = base58.b58decode(private_key)
        keypair = Keypair().from_bytes(privateKeyBytes)
        public_key = keypair.pubkey()
        print(f" public_key: %s" % public_key)
        user = GetCurrentUser(chat_id)
        if user is None:
          print('User not found / Not Registered')
          return None
        else:
          balance = solana_client.get_balance(pubkey=public_key).value
          print(f'Balance: %s' % balance)
          payload = {
            'tele_id': user[4],
            'private_key': private_key,
            'public_key': str(public_key),
            'is_connected': True,
            'balance': str(balance),
            'default': False
          }
          NewWalletUser(payload)
          return payload
      else:
        print('Cannot Connect to solana')
        return None


  @classmethod
  def GenerateWallet(cls, chat_id):
    with CruserSolana() as solana_client:
      if solana_client.is_connected() is True:
        pair_byte = Keypair()
        private_key = base58.b58encode(bytes(pair_byte)).decode()
        public_key = pair_byte.pubkey()
        wallet_key_address = private_key
        print(f'PUBLIC KEY {public_key}')

        user = GetCurrentUser(chat_id)
        if user is not None:
            payload ={
                'tele_id': user[4],
                'private_key': wallet_key_address,
                'public_key': str(public_key),
                'is_connected': True,
                'default': False
            }
            print(f'payload data {payload}')
            NewWalletUser(payload)
        wallet_info = (
              f"New Wallet Info:\n"
              f"Address: {public_key}\n"
              f"Private key: {wallet_key_address}"
          )
        return wallet_info
      else:
        print('ERROR Connecting to solana')
        return None


  @classmethod
  def StartSniping(cls, public_key):
     solana_client = cls.client
     program_id = cls.client.get_account_info(public_key)
     for signature in solana_client.events().subscribe(program_id, encoding="base64"):
      #  Ananlize New Transaction
        event = solana_client.get_confirmed_transaction(signature)
        print(f'EVENT ANALIZE New Transaction {event}')
        if event['meta']['type'] == 'createAccount':
            mint_address = event["result"]["value"]["data"]["parsed"]["info"]["mint"]
            try:
              cls.PlaceBuyOrder(mint_address)
            except Exception as e:
              print(f"Error placing order: {e}")

  @classmethod
  def SnipeToken(cls, wallet_payer, token_address, amount):
    with CruserSolana() as solana_client:
      print(f'WAllet Data {wallet_payer}')
      serializer = serializeJson(wallet_payer)
      findCurrentData = filterJson(serializer, "status", True)
      if findCurrentData is not None:
        for data in findCurrentData:
          pairKeyWallet = Keypair().from_base58_string(data["private_key"])
          currBalance = solana_client.get_balance(pairKeyWallet.pubkey()).value
          balanceAfterRatio = currBalance * (amount / 100)
          balence_last = int(currBalance - balanceAfterRatio)
          update={
            "balance": balence_last,
          }
          UpdateWallet(data["id"], update)
          result_queue = Queue()
          with SolThrad() as event_thread:
              Thread(target=select_amm2trade, name=token_address, args=(
                  token_address, pairKeyWallet, amount, result_queue)).start()
              event_thread.wait()
              event_thread.clear()
              return_value = result_queue.get()
              return return_value




  def PlaceBuyOrder(cls, mint_address):
      print(f'Place Buy Order {mint_address}')
