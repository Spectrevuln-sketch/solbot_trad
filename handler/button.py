import json
import re
import textwrap
import solana
import telegram
from telegram.ext import CallbackContext
from core.generate_wallet import ButtonWallet, GenerateWallet
from core.repository.raydium.create_close_account import getAccountPool
from core.repository.solana import SolanaHandler
from core.repository.wallet import DeleteWallet, GetAllCurrentWallet, GetCurrentWallet, GetCurrentWalletByID
from core.repository.wallet_tf import WalletTF
from core.snip_token import ButtonSnipping
from solana.rpc.api import Client
from solana.rpc.types import TokenAccountOpts
from solders.account import Account
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from core.connect_solana import CruserSolana
from core.utils.birdeye import getTokenDexInfo
from core.utils.serializer import ConvertMatch
from handler.buttonNest.buttonWalletDetail import ButtonWalletDetail


BUY_MODE = "buy_mode"
SELL_MODE = "sell_mode"
SNIPE_MODE = "snipe_mode"

payload = {
    BUY_MODE: True,
    SELL_MODE: False,
    SNIPE_MODE: False,
    "wallet":[],
    "token_address": ""
}

keyboard = []
def update_button_status(key: str, label: str) -> telegram.InlineKeyboardButton:
    status = payload[key]
    icon = "✅" if status else "❌"
    return telegram.InlineKeyboardButton(f"🎯 {label} {icon}", callback_data=key)


def add_status_to_wallets(wallets):
        for idx, wallet in enumerate(wallets):
            if wallet['default'] == True:
                wallet["status"] = True
            else:
                wallet["status"] = False
        return payload["wallet"]



def updateWalletButtonStatus(wallet_index: int) -> telegram.InlineKeyboardButton:
    wallet_status = payload["wallet"][wallet_index]["status"]
    icon = "✅" if wallet_status else "❌"
    return telegram.InlineKeyboardButton(f"💳 Wallet {wallet_index + 1} {'...'+ payload['wallet'][wallet_index]['public_key'][-5:]} {icon}", callback_data=f'wallet_{wallet_index}')

def create_wallet_buttons(getCurrentWallet):
      num_buttons_per_row = 2
      keyboard = []
    #   obj = json.loads(getCurrentWallet)
    #   payload['wallet'] = obj
      for idx, wallet in enumerate(getCurrentWallet):
          if idx % num_buttons_per_row == 0:
              current_row = []
              keyboard.append(current_row)

          current_row.append(updateWalletButtonStatus(idx))

      return keyboard

def create_buy_buttons():
    buy_button = [
        [
            telegram.InlineKeyboardButton("🚀 Buy 0.1 SOL", callback_data='buy_0_1'),
            telegram.InlineKeyboardButton("🚀 Buy 0.3 SOL", callback_data='buy_0_3'),
        ],
        [
            telegram.InlineKeyboardButton("🚀 Buy 0.5 SOL", callback_data='buy_0_5'),
            telegram.InlineKeyboardButton("🚀 Buy 1 SOL", callback_data='buy_1'),
        ],
        [
            telegram.InlineKeyboardButton("🚀 Buy 2 SOL", callback_data='buy_2'),
            telegram.InlineKeyboardButton("🚀 Buy 0.00001 SOL", callback_data='buy_0_00001'),
        ],
        [
            telegram.InlineKeyboardButton("🚀 Buy X SOL", callback_data='buy_x')
        ],
        [
            telegram.InlineKeyboardButton("Close", callback_data='close')
        ]
    ]
    return buy_button

def create_sell_buttons(num_buttons_per_row=3):
    sell_button = [
        telegram.InlineKeyboardButton(f"🚀 Sell {i}0%", callback_data=f'sell_{i * 10}')
        for i in range(1, 10)
    ]

    # Reshape the list into rows based on the specified number of buttons per row
    sell_button_rows = [sell_button[i:i + num_buttons_per_row] for i in range(0, len(sell_button), num_buttons_per_row)]

    # Add additional buttons
    sell_button_rows.extend([
        [
            telegram.InlineKeyboardButton("Sell All", callback_data='sell_all'),
            telegram.InlineKeyboardButton("Sell X Token", callback_data='sell_x_token')
        ],
        [
            telegram.InlineKeyboardButton("Close", callback_data='close'),
        ]
    ])

    return sell_button_rows

def create_keyboard(update: telegram.Update, getCurrentWallet):
    buy_mode_icon = update_button_status(BUY_MODE, "Buy Mode")
    sell_mode_icon = update_button_status(SELL_MODE, "Sell Mode")
    snipe_mode_icon = update_button_status(SNIPE_MODE, "Sniper Mode")

    keyboard = [
        [
            telegram.InlineKeyboardButton("Refresh", callback_data='refresh_snipe'),
        ],
        [
            buy_mode_icon,
            sell_mode_icon,
            snipe_mode_icon,
        ],
        [
            telegram.InlineKeyboardButton("--Wallet--settings--", callback_data="wallet_settings"),
        ]
    ]
    keyboard.extend(create_wallet_buttons(getCurrentWallet))

    action = [telegram.InlineKeyboardButton("__Actions__", callback_data="action_data")]
    keyboard.append(action)

    if payload[BUY_MODE] or payload[SNIPE_MODE]:
        keyboard.extend(create_buy_buttons())

    if payload[SELL_MODE]:
        keyboard.extend(create_sell_buttons())



    return keyboard

def AddtionalData(tokenPair):
    # print(f"Token Pair {tokenPair}")
    #   checkToken = SolanaHandler().CheckLunchToken(payload["token_address"])
    # Dapatkan token price
    token_price = 0 if tokenPair["pairs"] is None else float(tokenPair["pairs"][0]["priceUsd"])  # Gunakan pair pertama

    # Dapatkan market cap
    # supplyToken = SolanaHandler().GetTokenSupply([tokenPair["pairs"][0]["baseToken"]["address"]])
    # marketCap = token_price * supplyToken
    # Dapatkan token Liquidity
    liquidity_usd = 0 if tokenPair["pairs"] is None else tokenPair["pairs"][0]["liquidity"]["usd"]
    # Dapatkan Pooled Pair
    pooled_sol = 0
    if liquidity_usd > 0 and token_price > 0:
        pooled_sol = liquidity_usd / token_price
    return {
        "total_liquidity": liquidity_usd,
        "pooled_sol": pooled_sol,
        "token_price": token_price,
        # "marketCap" : marketCap
    }
def TitleText(token_address, user_id):
    with CruserSolana() as solana_client:
        tokenPair = getTokenDexInfo(token_address)
        getTokenAccount = solana_client.get_account_info_json_parsed(Pubkey.from_string(token_address))
        additionalData = AddtionalData(tokenPair)
        metaplexTokenInfo = SolanaHandler().CheckReleaseToken(Pubkey.from_string(token_address), getTokenAccount.value.owner)
        if metaplexTokenInfo['status'] == '00':
            exchage =""
            tokenInfo=""
            websites=""
            reply_text=""
            baseName= ""
            symbolToken=""
            if tokenPair['pairs'] is not None:
                if additionalData["pooled_sol"] > 0:
                    baseName= tokenPair['pairs'][0]['baseToken']['name']
                    symbolToken=tokenPair['pairs'][0]['baseToken']['symbol']
                    exchage=tokenPair['pairs'][0]['dexId']
                    tokenInfo = tokenPair["pairs"][0].get('info')
                    websites= f'{tokenPair["pairs"][0]["info"]["websites"][0]["label"]}{tokenPair["pairs"][0]["info"]["websites"][0]["url"]}' if tokenInfo is not None  else ""
                    reply_text = textwrap.dedent(f"""
                                                {baseName} (${symbolToken})\n
                                                🪅 CA: [{token_address}](https://birdeye.so/token/{token_address}?chain=solana&id=1706204535342)
                                                🎯 Exchange: {exchage}
                                                💧 Liquidity: ${additionalData["total_liquidity"]:.2f}K
                                                💰 Token Price: ${additionalData["token_price"]:.7f}
                                                ⛽️ Pooled SOL: {additionalData["pooled_sol"]:.1f} SOL
                                                👤 Renounced: ❌
                                                📖 Description:\n
                                                website : {websites}\n
                                                {metaplexTokenInfo['data']['tokenData']['description'][:32]}\n
                                                📈 [Birdeye](https://birdeye.so/token/{token_address}?chain=solana) | 📈 [DexScreen](https://dexscreener.com/solana/B5uP8Zincgjc6psTzy3poAXTWEX6ZbHz6nJYgMVzVrxt) | 📈 [Dextools](https://www.dextools.io/app/en/solana/pair-explorer/B5uP8Zincgjc6psTzy3poAXTWEX6ZbHz6nJYgMVzVrxt) | 🔥 [Raydium](http://raydium.io/swap/?inputCurrency=sol&outputCurrency={token_address}&fixed=in) | ⚖️ [Owner](https://solscan.io/account/89oNwxpAssUhCHcMYd5zNrqGcGtW5kdPTfazTnNnRqst) | ⚖️ [Pair](https://solscan.io/account/B5uP8Zincgjc6psTzy3poAXTWEX6ZbHz6nJYgMVzVrxt) | 🔎 TTF: [Scan](https://t.me/ttfbotbot?start={token_address}) | [Chart](https://t.me/ttfbotbot?start=chart{token_address})""")
                    return {
                        'status': '00',
                        'data': reply_text
                    }
            elif additionalData["pooled_sol"] <= 0:
                if metaplexTokenInfo['status'] == '00':
                    reply_text = textwrap.dedent(f"""
                    {metaplexTokenInfo['data']['data']['name']} ({'$' + metaplexTokenInfo['data']['data']['symbol']})\n
                    🪅 CA: [{token_address}](https://birdeye.so/token/{token_address}?chain=solana&id=1706204535342)\n
                    💧 No Pool Found\n
                    📖 Description:\n
                    {metaplexTokenInfo['data']['tokenData']['description'][:32]}\n
                    📈 [Birdeye](https://birdeye.so/token/{token_address}?chain=solana) |  📈 [DexScreen](https://dexscreener.com/solana/B5uP8Zincgjc6psTzy3poAXTWEX6ZbHz6nJYgMVzVrxt) | 📈 [Dextools](https://www.dextools.io/app/en/solana/pair-explorer/B5uP8Zincgjc6psTzy3poAXTWEX6ZbHz6nJYgMVzVrxt) | 🔥 [Raydium](http://raydium.io/swap/?inputCurrency=sol&outputCurrency={token_address}&fixed=in) | ⚖️ [Owner](https://solscan.io/account/89oNwxpAssUhCHcMYd5zNrqGcGtW5kdPTfazTnNnRqst) | ⚖️ [Pair](https://solscan.io/account/B5uP8Zincgjc6psTzy3poAXTWEX6ZbHz6nJYgMVzVrxt) | 🔎 TTF: [Scan](https://t.me/ttfbotbot?start={token_address}) | 📈 [Chart](https://t.me/ttfbotbot?start=chart{token_address})
                    """)
                    return {
                        'status': '00',
                        'data': reply_text
                    }
                else:
                    reply_text = 'No data found! becareful for scam tokens'
                    return {
                        'status': '99',
                        'data': reply_text
                    }
        else:
            reply_text = 'No data found! becareful for scam tokens'
            return{
                    'status': '99',
                    'data': reply_text
                }


def ButtonCallback (update: telegram.Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    buyPattren = r'^buy_(?!x$)[^\s]+$'
    wallet_pattern = r'^wallet_\d+$'
    detailWalletPattren = r'wallet_detail_(\d+)$'
    matchDetailWallet = re.match(detailWalletPattren, query.data)

    deleteWalletPattren = r'delete_wallet_(\d+)$'
    matchDeleteWallet = re.match(deleteWalletPattren, query.data)

    transferSol = r'transfer_balance_(\d+)$'
    matchTransferSol = re.match(transferSol, query.data)

    sellPattern = re.compile(r'^sell_(\d+)$', re.IGNORECASE)
    sellSearch = sellPattern.search(query.data)
    print(f'Query is {query.data}')
    print(f'SELL TOKENS {sellSearch}')
    with CruserSolana() as solana_client:
      if query.data == 'generate_wallet':
          ButtonWallet(update, context)
    #   Wallet Details
      elif matchDetailWallet:
          walletID = matchDetailWallet.group(1)
          currentWallet = GetCurrentWalletByID(walletID, True)
          ButtonWalletDetail(update, context, currentWallet)
        #   print(f'Get current wallet {currentWallet}')
        #   Wallet Delete
      elif matchDeleteWallet:
          walletID = matchDeleteWallet.group(1)
          deletedWallet = DeleteWallet(walletID)
          query.message.reply_text(deletedWallet['message'])
        #  Transfer SOL
      elif matchTransferSol:
          walletID = matchDeleteWallet.group(1)
          currentWallet = GetCurrentWalletByID(walletID, True)
          prepareTF = WalletTF().PrepareTF(currentWallet)
          if prepareTF['status'] == '99':
              return query.message.reply_text('Cannot send balance')
          query.message.reply_text(
              f'Enter Transfer Sol example:\n'
              f'EwR1iMRLoXEQR8qTn1AF8ydwujqdMZVs53giNbDCxicH,0.001'
              f'EwR1iMRLoXEQR8qTn1AF8ydwujqdMZVs53giNbDCxicH,0.1',
              reply_markup=telegram.ForceReply(selective=True, input_field_placeholder="Enter Transfer SOL like example")
                                   )
      elif query.data == 'generate_new_wallet':
          GenerateWallet(update, context, solana_client, query)
          ButtonWallet(update, context)
      elif query.data == 'connect_wallet':
          query.message.reply_text('Enter private key list', reply_markup=telegram.ForceReply(selective=True, input_field_placeholder='Enter private key'))
      elif query.data == 'snipper_token':
          ButtonSnipping(update, context)
      elif query.data == 'auto_swap':
          SolanaHandler.SwapToken(query.message.chat_id)
      elif query.data == 'start_snipe':
          query.message.reply_text('Enter the token Address you would like to snipe', reply_markup=telegram.ForceReply(selective=True, input_field_placeholder='Enter token Address'))
    #   Change WAllet Button
      elif re.match(wallet_pattern, query.data):
          wallet_index = int(query.data.split("_")[1])
          payload['wallet'][wallet_index]["status"] = not payload['wallet'][wallet_index]["status"]
          keyboard = create_keyboard(update, payload['wallet'])
          reply_markup = telegram.InlineKeyboardMarkup(keyboard)
          query.edit_message_reply_markup(reply_markup=reply_markup)
      elif query.data in [BUY_MODE, SELL_MODE, SNIPE_MODE]:
          for val in payload.keys():
              if val != query.data and val != 'wallet' and val != 'token_address':
                payload[val] = False
          payload[query.data] = not payload[query.data]
          keyboard = create_keyboard(update, payload['wallet'])
          reply_markup = telegram.InlineKeyboardMarkup(keyboard)
          query.edit_message_reply_markup(reply_markup=reply_markup)
      elif re.match(buyPattren, query.data):
          convertQuery = ConvertMatch(query.data)
          if payload[SNIPE_MODE]:
              SolanaHandler().SnipeToken(payload["wallet"], payload["token_address"])
          ammPDA = getAccountPool(payload["token_address"])
          print(f'AMM PDA {ammPDA}')
          buyToken = SolanaHandler().BuyToken(payload["wallet"], float(convertQuery), payload["token_address"])
          if buyToken["status"] == 404:
              query.message.reply_text(buyToken["message"])
          else:
              query.message.reply_text(buyToken["message"])
      elif sellSearch:
          sellNum = sellSearch.group(1)
          SolanaHandler().SellToken(payload["wallet"], int(sellNum), payload["token_address"])




def ButtonSniper(update: telegram.Update, context: CallbackContext, tele_id=None, token_address=None):
  for val in payload.keys():
    if val != BUY_MODE:
      payload[val] = False
  payload[BUY_MODE]= True
  if token_address is not None:
    payload["token_address"] = token_address

  user_id = tele_id if tele_id != None else update.callback_query.message.chat.id
  wallets = GetAllCurrentWallet(user_id, True)
  obj = json.loads(wallets)
  payload["wallet"] = obj
  getCurrentWallet = add_status_to_wallets(payload["wallet"])
  keyboard = create_keyboard(update, getCurrentWallet)

  if update.callback_query and update.callback_query.message:
      reply_markup = telegram.InlineKeyboardMarkup(keyboard)
      reply_text = TitleText(token_address, user_id)
      if reply_text['status'] == '99':
          return update.callback_query.message.reply_text(f'{reply_text["data"]}')
      update.callback_query.message.reply_text(reply_text['data'], reply_markup=reply_markup)
  else:
      reply_markup = telegram.InlineKeyboardMarkup(keyboard)
      reply_text = TitleText(token_address, user_id)
      if reply_text['status'] == '99':
          return update.message.reply_text(f'{reply_text["data"]}')
      update.message.reply_text(reply_text['data'], reply_markup=reply_markup, parse_mode=telegram.ParseMode.MARKDOWN)

