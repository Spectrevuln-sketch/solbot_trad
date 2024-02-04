import solana
import telegram
import base58
from solders.keypair import Keypair
from telegram.ext import CommandHandler, CallbackContext
from core.connect_solana import SolanaCrypt
from core.repository.solana import SolanaHandler
from core.repository.users import GetCurrentUser
from core.repository.wallet import GetCurrentWallet, NewWalletUser, GetAllCurrentWallet

def ButtonWallet(update=telegram.Update, context=CallbackContext, tele_id=None):
    print("Choose item")
    user_info = update.callback_query
    user_id = tele_id if tele_id != None else user_info.message.chat.id
    keyboard=[]
    getCurrentWallet = GetAllCurrentWallet(user_id)
    for wallet in getCurrentWallet:
        print(f'Current wallet {wallet}')
        sol = '0.00'
        if wallet[6] is not None:
            sol = str(round(int(wallet[6])*10**(-9), 9))
        print(f'WAllet {wallet[0]}')
        wallet_button = [
            telegram.InlineKeyboardButton(wallet[3][0:20], callback_data=f'wallet_detail_{wallet[0]}'),
            telegram.InlineKeyboardButton(f'{sol} SOL', callback_data='generate_new_wallet')
        ]
        keyboard.append(wallet_button)
    additional_buttons = [
            telegram.InlineKeyboardButton("Connect Wallet", callback_data='connect_wallet', **{
                "one_time_keyboard": True,
                "resize_keyboard": True,
            }),
            telegram.InlineKeyboardButton("Generate New Wallet", callback_data='generate_new_wallet'),
        ]
        # [
        #     telegram.InlineKeyboardButton("Generate 5 Wallets", callback_data='generate_5_wallets'),
        #     telegram.InlineKeyboardButton("Generate 10 Wallets", callback_data='generate_10_wallets'),
        # ]

    keyboard.append(additional_buttons)

    if update.callback_query and update.callback_query.message:
        reply_markup = telegram.InlineKeyboardMarkup(keyboard)
        update.callback_query.message.reply_text('Wallets (12) 💳 0.0000000 SOL, 0.00 WSOL:', reply_markup=reply_markup)
    else:
        print("No message to reply to")

def GenerateWallet(update, context : CallbackContext, client, query):
    chat_id = query.message.chat.id
    wallet_info = SolanaHandler.GenerateWallet(chat_id=chat_id)
    if wallet_info is None:
        return
    update.callback_query.message.reply_text(wallet_info)

