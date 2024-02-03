import logging
import os
import telegram
from telegram.ext import CommandHandler, CallbackContext
from core.repository.solana import SolanaHandler
from handler.button import ButtonCallback
from core.repository.users import CreateUser, GetCurrentUser
from core.repository.wallet import GetCurrentWallet
from core.connect_solana import CruserSolana

def StartBot(update: telegram.Update, context: CallbackContext) -> None:
    with CruserSolana() as solana_client:
        if solana_client.is_connected() == True:
            user_message_info= update.message.chat
            # wallet_info = SolanaHandler.GenerateWallet(user_message_info.id)
            user = GetCurrentUser(user_message_info.id)
            if user is None:
                CreateUser(user_message_info)
                SolanaHandler.GenerateAccountCli(user_message_info.id)
            wallet = GetCurrentWallet(user_message_info.id)
            if wallet is None:
                return logging.error('Wallet not found')
            # if os.getenv('ENV') == 'development':
            #     requestAirdrop = SolanaHandler.RequestAirdrop(wallet[3])
            #     if requestAirdrop is not None:
            #         print(f'Successfully Request Airdrop {requestAirdrop}')
            solanaAccount = SolanaHandler.GetSoalnaAccount(wallet[3])
            if solanaAccount is None:
                return logging.error(solanaAccount)
            print(f"USER CHAT WITH ID: {solanaAccount}")
            keyboard = [
                [
                    telegram.InlineKeyboardButton("Buy & Sell", callback_data='buy_sell'),
                    telegram.InlineKeyboardButton("Snipper Token", callback_data='snipper_token'),
                    telegram.InlineKeyboardButton("Generate Wallet", callback_data='generate_wallet'),
                ],
                [
                    telegram.InlineKeyboardButton("Auto Swap", callback_data='auto_swap'),
                    telegram.InlineKeyboardButton("Kirim Token", callback_data='kirim_token'),
                ]
            ]
            reply_markup = telegram.InlineKeyboardMarkup(keyboard)
            update.message.reply_text('Choose an option:', reply_markup=reply_markup)
        else:
            print('ERROR Connection Solana')