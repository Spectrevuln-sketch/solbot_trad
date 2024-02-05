from dotenv import load_dotenv

from core.connect_solana import SolanaCrypt
from core.repository.solana import SolanaHandler
load_dotenv()
import asyncio
import os
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, CallbackQueryHandler, Filters
from handler.button import ButtonCallback
from handler.start import StartBot
from handler.reply import HandleReply
from handler.message import HandleMessage
from solana.rpc.api import Client
from core.db_connection import Database
from spl.token.instructions import ApproveCheckedParams

def main():
    updater = Updater(os.getenv("TELEGRAM_BOT_TOKEN"))

    dp = updater.dispatcher

    # Connection DB
    Database.initialise(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            port=int(os.getenv("DB_PORT"))
    )
    SolanaCrypt.initialise()
    connected = SolanaHandler.HealthCheck()
    if not connected:
        print(f'Solana Not Connected OK')
    # HANDLER
    dp.add_handler(CommandHandler('start',	StartBot))
    dp.add_handler(CallbackQueryHandler(ButtonCallback))
    dp.add_handler(MessageHandler(Filters.reply & ~Filters.command, HandleReply))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, HandleMessage))

    # http_client = Client("https://api.devnet.solana.com")
    # print(f"Client Connected to Solana :  {http_client.is_connected()}")
    # dp.add_handler(CommandHandler('coin',	coin))

    # dp.add_error_handler(error_callback)


    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()