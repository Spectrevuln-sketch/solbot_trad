import telegram
from core.repository.wallet import CountSnipe
def ButtonSnipping(update, context):
    print("Choose item")
    query = update.callback_query
    keyboard = [
        [
            telegram.InlineKeyboardButton("Lists", callback_data='lists_token')
        ],
        [
            telegram.InlineKeyboardButton("Start Snipe", callback_data='start_snipe'),
        ]
    ]


    if update.callback_query and update.callback_query.message:
        count_snipe = CountSnipe(str(query.message.chat.id))
        print(f'count snipe {count_snipe}')
        reply_markup = telegram.InlineKeyboardMarkup(keyboard)
        update.callback_query.message.reply_text(f'Active Snipers: {count_snipe}\n\nPaste token address to create new sniper!', reply_markup=reply_markup)
    else:
        print("No message to reply to")
def ReplyTokenWanToSnap(update, context):
    query = update.callback_query
    print(f'Choose Token to reply')


