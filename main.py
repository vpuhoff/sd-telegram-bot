from copy import copy
import json
import logging
from io import BytesIO
from os import getenv
from random import randint
from uuid import uuid4

from better_profanity import profanity
import diskcache as dc
import sentry_sdk
import telegram
import webuiapi
from deep_translator import GoogleTranslator
from telegram import (ForceReply, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultCachedPhoto, InlineQueryResultPhoto,
                      KeyboardButton, ReplyKeyboardMarkup, Update)
from telegram import __version__ as TG_VER
from telegram.ext import (Application, InlineQueryHandler, CommandHandler,
                          ContextTypes, MessageHandler, filters)

import default

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)
configs = dc.Cache('config')

sentry_dsn = getenv("DSN", None)
sentry_sdk.init(sentry_dsn)
sentry_sdk.capture_message("Service started", "info")

labels = {
    "prompt": "Затравка для генерации",
    "negative_prompt": "Негативные условия (чего быть не должно)",
    # "seed": "Зерно для генерации",
    # "width": "Ширина",
    # "height": "Высота",
    # "styles": None,
    # "cfg_scale": "Соответствие результата затравке",
    # "sampler_index": None,
    # "steps": "Глубина прорисовки",
    # "enable_hr": None,
    # "hr_scale": None,
    # "hr_upscaler": None,
    # "hr_second_pass_steps": "Увеличение детализации",
    # "hr_resize_x": None,
    # "hr_resize_y": None,
    # "denoising_strength": "Сила сглаживания перед детализацией"
}

app_version = "1.0"

commands = [] 
menu_commands = []

for k, v in labels.items():
    if v:
        menu_commands.append(v)
        commands.append([InlineKeyboardButton(v, callback_data=k)])

reply_markup = InlineKeyboardMarkup(commands)

main_commands = [["/start"]]
reply_main_markup = ReplyKeyboardMarkup(main_commands, is_persistent=True)

# create API client with custom host, port
api = webuiapi.WebUIApi(host=getenv("API_HOST"), port=getenv("API_PORT"))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    init_params(update, context)


def init_params(update, context):
    user = update.effective_user.name
    if user not in configs or configs.get(user,{}).get('version', None) != app_version:
        new_config = {}
        new_config['chat_id'] = context._chat_id
        new_config['version'] = app_version
        new_config['generation_params'] = default.generation_params
        configs[user] = new_config
        return configs[user]
    else:
        return configs[user]


async def send_admin(update, user, promt, img_io):
    admin_chat_id = getenv("ADMIN_CHAT_ID", None)
    if admin_chat_id:
        bot = update.get_bot()
        return await bot.send_photo(admin_chat_id, img_io, f"image from {user.name} [{promt}]")

STATE = None

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user:
        init_params(update, context) # Инициализация пользовательских настроек
        #generation_params = None
        # if update.inline_query:
        #     translated = GoogleTranslator(source='auto', target='en') \
        #         .translate(update.inline_query.query)
        #     generation_params = default.generation_params_low
        # elif update.message and update.message.text:
        if not update.message or not update.message.text:
            return
        generation_params = copy(default.generation_params_hq)
        translated = GoogleTranslator(source='auto', target='en') \
            .translate(update.message.text)
        censored_text = profanity.censor(translated)

        generation_params['prompt'] = censored_text.replace("*", '')
        if ' not ' in censored_text.lower():
            generation_params["negative_prompt"] = ','.join(censored_text.lower().split(' not ')[1:])
        if len(translated) < 3:
            return

        generation_params['seed'] = randint(1, 10^5)
        print(user.name, generation_params)
        img_io = None
        try:
            await user.send_chat_action(telegram.constants.ChatAction.UPLOAD_PHOTO)
            img_io = generate_image(generation_params)
            req_uid = str(uuid4())
            await send_admin(update, user, censored_text, img_io)
            img_io.seek(0)
            await update.message.reply_photo(img_io,
                censored_text, 
                filename=f"{req_uid}.png",
                reply_to_message_id=update.message.id)
        except Exception as e:
            await update.message.reply_text(f"Произошла ошибка: {e}")
            raise e
        #file_id = result.photo[-1].file_id
        # elif update.inline_query:
        #     result = InlineQueryResultCachedPhoto(req_uid, file_id)
        #     await update.inline_query.answer([result])

def generate_image(job_config):
    result1 = api.txt2img(**job_config)
    img_io = BytesIO()
    result1.image.save(img_io, 'PNG')
    img_io.seek(0)
    return img_io
        # image is shorthand for images[0]

async def handle_callback(update, context):
    query = update.callback_query
    data = query.data
    context.user_data["state"] = data
    bot = context.bot
    await bot.send_message(chat_id=context._chat_id,
    text="Введите новое значение параметра:")


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(getenv("TOKEN")).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    #application.add_handler(InlineQueryHandler(echo))
    # application.add_handler(MessageHandler(filters.COMMAND, echo))
    # application.add_handler(CallbackQueryHandler(handle_callback))
    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()