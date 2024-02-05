import re
import telegram
from telegram.ext import  CallbackContext
from core.connect_solana import SolanaCrypt, SolThrad, CruserSolana
from core.utils.birdeye import getBaseToken
from handler.button import ButtonSniper
from core.utils.serializer import findJson

def HandleMessage(update: telegram.Update, context:CallbackContext):
  with CruserSolana() as solana_client:
    CA_pattern = r'[1-9A-HJ-NP-Za-km-z]{32,44}$'
    birdeye_pattern = r'https?://birdeye\.so/token/(\w+)\?chain=solana'
    dexscreener_pattern = r'https://dexscreener\.com/solana/(\w+)'
    chatText = update.message.text
    pubkeyPattren = re.match(CA_pattern, chatText)
    userId = update.message.chat_id
    if solana_client.is_connected():
      entitiy = update.message.entities
      if len(entitiy) > 0:
        chatType = entitiy[0].type
        if chatType == 'url':
          dex_url = re.search(
            dexscreener_pattern, chatText
          )
          birdeye_url = re.search(
            birdeye_pattern, chatText
          )
          if dex_url:
            token_address = getBaseToken(dex_url.group(1))
            ButtonSniper(update, context, userId, token_address)
          if birdeye_url:
            print(f'Get Public Token {birdeye_url.group(1)}')
            token_address = getBaseToken(birdeye_url.group(1))
            ButtonSniper(update, context, userId, token_address)

      if pubkeyPattren:
        token_address = getBaseToken(chatText)
        ButtonSniper(update, context, userId, token_address)