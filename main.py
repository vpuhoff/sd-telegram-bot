import logging
from os import getenv
from uuid import uuid4
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, __version__ as TG_VER
import yaml
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
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)
from io import BytesIO

import webuiapi

# create API client
#api = webuiapi.WebUIApi()



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

commands = [] 
menu_commands = []

for k, v in labels.items():
    if v:
        menu_commands.append(v)
        commands.append([InlineKeyboardButton(v, callback_data=k)])

reply_markup = InlineKeyboardMarkup(commands)

main_commands = [["/new_image","/start"]]
reply_main_markup = ReplyKeyboardMarkup(main_commands, is_persistent=True)

# create API client with custom host, port
api = webuiapi.WebUIApi(host='127.0.0.1', port=7860)
# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    if 'config' not in context.user_data:
        context.user_data['config'] = {
            "prompt": "cute squirrel",
            "negative_prompt": "ugly, out of frame",
            "seed": -1,
            "width": 512,
            "height": 512,
            "styles": [],
            "cfg_scale": 7,
            "sampler_index": 'Euler a',
            "steps": 90,
            "enable_hr": True,
            "hr_scale": 2,
            "hr_upscaler": webuiapi.HiResUpscaler.ESRGAN_4x,
            "hr_second_pass_steps": 45,
            "hr_resize_x": 1024,
            "hr_resize_y": 1024,
            "denoising_strength": 0.4
        }
    await update.message.reply_html(
        "Привет, чтобы начать работу настрой параметры затравки!",
        reply_markup=reply_markup,
    )
    await update.message.reply_html(
        rf"Для запуска генерации выбери команду /new_image или введи текст (он будет добавлен к тому что указан в параметрах)",
        reply_markup=reply_main_markup,
    )



async def new_image_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    try:
        if 'config' not in context.user_data:
            await update.message.reply_text("Нет настроенных параметров, выполните настройку командой /start")
            return
        await update.message.reply_text(f"Начинаю генерацию c параметрами: {context.user_data['config']}")
        print(context.user_data['config']['prompt'])
        img_io = generate_image(context.user_data['config'])
        await update.message.reply_photo(img_io, f"{update.message.text.replace(' ', '_')}.jpg", reply_to_message_id=update.message.id)
    except Exception as e:
        if '' in str(e):
            await update.message.reply_text(f"SD API недоступен, сообщите сами знаете кому :)")
        else:
            await update.message.reply_text(f"Произошла ошибка: {e}")
        raise e

STATE = None

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        """Echo the user message."""
        if 'config' not in context.user_data:
            await update.message.reply_text("Нет настроенных параметров, выполните настройку командой /start")
            return
        text_message = update.message.text
        state = context.user_data.get("state", None)
        if state:
            context.user_data['config'][state] = text_message
            del context.user_data["state"]
            await update.message.reply_text(f"Параметр {state} изменен на {text_message}")
            return
        job_config = dict(context.user_data['config'])
        job_config['prompt'] =f"({str(job_config.get('prompt', ''))},({str(update.message.text)})"
        print(job_config['prompt'])
        try:
            await update.message.reply_text(f"Начинаю генерацию c параметрами: {job_config}")
            img_io = generate_image(job_config)
            await update.message.reply_photo(img_io, f"{update.message.text.replace(' ', '_')}.jpg", reply_to_message_id=update.message.id)
        except Exception as e:
            await update.message.reply_text(f"Произошла ошибка: {e}")
            raise e
        
        

def generate_image(job_config):
    result1 = api.txt2img(**job_config)
    img_io = BytesIO()
    result1.image.save(img_io, 'PNG')
    img_io.seek(0)
    with open(f"{uuid4()}.png", 'wb') as f:
        result1.image.save(f, 'PNG')
    return img_io
        # image is shorthand for images[0]

async def handle_callback(update, context):
    query = update.callback_query
    data = query.data
    context.user_data["state"] = data
    bot = context.bot
    await bot.send_message(chat_id=context._chat_id, text="Введите новое значение параметра:")
    # ...

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(getenv("TOKEN")).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("config", start))
    application.add_handler(CommandHandler("new_image", new_image_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.add_handler(CallbackQueryHandler(handle_callback))
    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()