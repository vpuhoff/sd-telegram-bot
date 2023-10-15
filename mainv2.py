from os import getenv

import telebot


def init_proxy():
    PROXY_HOST = getenv("PROXY_HOST", None)
    PROXY_PORT = getenv("PROXY_PORT", None)
    PROXY_USER = getenv("PROXY_USER", None)
    PROXY_PASS = getenv("PROXY_PASS", None)
    if PROXY_HOST and PROXY_PORT:
        if PROXY_USER and PROXY_PASS:
            telebot.apihelper.proxy = {
                "https": f"socks5://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"
            }
        else:
            telebot.apihelper.proxy = {"https": f"socks5://{PROXY_HOST}:{PROXY_PORT}"}


init_proxy()
token = getenv("TOKEN")
token = "1922962749:AAFkrEx0e0k0CjGyDzFgH6Nl9gWOGGrOVp0"
maintenance_message = "The bot is temporarily under maintenance. I am actively engaged in its revision due to the increased workload. I recommend using the bot for now https://t.me/ai_nox_bot?start=33497099"
if not token:
    print("Token required!")
    exit(-1)
bot = telebot.TeleBot(token, parse_mode=None)


@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    bot.reply_to(message, maintenance_message)


@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.reply_to(message, maintenance_message)


bot.infinity_polling()
