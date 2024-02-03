from handler.button import ButtonSniper
import telegram
import re
from telegram.ext import  CallbackContext
from core.connect_solana import CruserSolana
# from core.generate_wallet import ButtonWallet
from core.repository.wallet import GetWalletByPrivate, NewWalletUser, UpdateConnectionWallet
from core.repository.solana import SolanaHandler
from handler.start import StartBot
from core.utils.birdeye import getBaseToken
def HandleReply(update: telegram.Update, context:CallbackContext):
    birdeye_pattern = r'https?://birdeye\.so/token/(\w+)\?chain=solana'
    dexscreener_pattern = r'https://dexscreener\.com/solana/(\w+)'
    user_info = update.message.chat
    user_reply = update.message.text
    min_length = 60
    patternConnectWallet = re.compile(fr'^[a-zA-Z0-9]{{{min_length},}}$')
    connectWallet = re.match(patternConnectWallet, user_reply)
    print(f'CONNECT WALLET  {connectWallet}')
    dex_url = re.search(
      dexscreener_pattern, user_reply
    )
    birdeye_url = re.search(
      birdeye_pattern, user_reply
    )
    print(f'birdeye_url: %s' %birdeye_url)
    print(f'dex_url: %s' %dex_url)
    if dex_url:
      print(f'PREPARE SNIPER.....')
      token_address = getBaseToken(dex_url.group(1))
      print(f'birdeye_url.group(2) data {dex_url.group(1)}')
      # simpan data
      ButtonSniper(update, context, user_info.id, token_address)
    if birdeye_url:
      print(f'PREPARE SNIPER.....')
      token_address = getBaseToken(birdeye_url.group(1))
      print(f'birdeye_url.group(2) data {birdeye_url.group(1)}')
      # simpan data
      ButtonSniper(update, context, user_info.id, token_address)
      # SolanaHandler.SnipeToken(user_info.id, token_address)
    # if
    if connectWallet:
      print(f'connectWallet here')
      wallet = GetWalletByPrivate(user_reply)
      if wallet is None:
        with CruserSolana() as solana_client:
          if solana_client.is_connected() == True:
            connect_wallet = SolanaHandler.ConnectWallet(user_info.id, user_reply)
            if connect_wallet is None:
              return update.message.reply_text("Can't connect to Solana Wallet")
            StartBot(update, context)
      else:
        with CruserSolana() as solana_client:
          if solana_client.is_connected() == True:
              UpdateConnectionWallet(wallet[0])
              update.message.reply_text(f"Successfully connected with Public Key: {wallet[3]}")
              StartBot(update, context)

          # print(f"Invalid input: {user_reply}")
          # update.message.reply_text("Please enter a valid response (letters and numbers only).")