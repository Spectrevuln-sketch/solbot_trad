import json
import telegram
from telegram.ext import CallbackContext

def ButtonWalletDetail(update: telegram.Update, context: CallbackContext, walletData):
  query = update.callback_query
  # {"id": 43, "tele_id": "6447754588", "private_key": "XTmMTis7K8A1n8qeVFe39MkkaYYJwLnXJeX8FJ2f1uEYuwsYxLc8vcVLiTsKGnNXdJSZqaDqm8uvjKu6eKJBVEN", "public_key": "FJXu8zmnjc72tgGZUdpQaQaqbou345YjcUYVcWSA2xSS", "is_connected": true, "is_snipe": null, "balance": "460192544", "default": false}
  objWallet = json.loads(walletData)
  print(f'WALLET DATA {objWallet["id"]}')
  wallet_button = [
    [
      telegram.InlineKeyboardButton('🗑️ Delete', callback_data=f'delete_wallet_{objWallet["id"]}'),
    ],
    [
      telegram.InlineKeyboardButton('Transfer SOL', callback_data=f'transfer_balance_{objWallet["id"]}'),
      telegram.InlineKeyboardButton('Wrap SOL', callback_data=f'wrap_sol_wsol_{objWallet["id"]}'),
    ]
  ]

  if update.callback_query and update.callback_query.message:
        reply_markup = telegram.InlineKeyboardMarkup(wallet_button)
        walletAddress = objWallet['public_key']
        reply_text = (
            "Here is the wallet information:\n\n"
            f"*Address:* `{walletAddress}`\n"
            f"*Key:* `3dCxS2TWu2SseRc1w1cea892CkruQYP2WDzYEh3KB4m5AWn1v5axExpiMpXR7bJk5GoBpDQUW6fCqpXnTF5H84Ea`"
        )
        update.callback_query.message.reply_text(
          reply_text,
          reply_markup=reply_markup
          )
  else:
        print("No message to reply to")