import solana
import telegram
import base58
from solders.keypair import Keypair
from telegram.ext import CommandHandler, CallbackContext
from core.connect_solana import SolanaCrypt
from core.repository.solana import SolanaHandler
from core.repository.users import GetCurrentUser
from core.repository.wallet import GetCurrentWallet, NewWalletUser, GetAllCurrentWallet


def ButtonSnipe(update=telegram.Update, context=CallbackContext, tele_id=None):
  print('Setup Snipe')
  payload = {
    "buy_mode": True,
    "sell_mode": False,
    "sniper_mode": False,

  }
  user_info = update.callback_query
  user_id = tele_id if tele_id != None else user_info.message.chat.id
  keyboard=[]
  getCurrentWallet = GetAllCurrentWallet(user_id)
  additionalKeyboard = [
    [
      telegram.InlineKeyboardButton("Refresh", callback_data='refresh_snipe'),
    ],
    [
      telegram.InlineKeyboardButton("Buy Mode ❌ ", callback_data='buy_mode'),
      telegram.InlineKeyboardButton("Sell Mode ❌ ", callback_data='sell_mode'),

    ]

  ]