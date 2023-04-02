import logging
from copy import copy
from datetime import datetime, timedelta
from io import BytesIO
from os import getenv, remove
from os.path import exists, join
from random import randint, seed
from uuid import uuid4

import diskcache as dc
import sentry_sdk
import telegram
import webuiapi
from better_profanity import profanity
from deep_translator import GoogleTranslator
from nsfw_detector import predict
from pyairtable import Api, Base, Table
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram import __version__ as TG_VER
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from tqdm import tqdm

import default

images_folder = "X:\\bot_generations"
airtable_token = getenv("AIRTABLE_TOKEN", "none")
api = Api(airtable_token)
airtable_base = api.get_base(getenv("AIRTABLE_BASE_ID", "none"))
generations = airtable_base.get_table("generations")

nudenet_classifier = predict.load_model("./nsfw_mobilenet2/saved_model.h5")


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
configs = dc.Cache("config")
black_list = dc.Cache("black_list")
generations_cache = dc.Cache("generations")

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

# from PIL import Image, PngImagePlugin

# info = PngImagePlugin.PngInfo()
# info.add_text("text", "This is the text I stored in a png")
# info.add_text("ZIP", "VALUE", zip=True)
# im = Image.open("001.png")
# im.save("001.png", "PNG", pnginfo=info)
# im3 = Image.open("001.png")
# #print(im3.info["text"])
# print(im3.text["text"])

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
all_options = api.get_options()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    reply_markup = ReplyKeyboardRemove()
    init_params(update, context)
    await update.message.reply_text(
        "Now you can start working", reply_markup=reply_markup
    )


def init_params(update, context):
    user = update.effective_user.name
    if user not in configs or configs.get(user, {}).get("version", None) != app_version:
        new_config = {}
        new_config["chat_id"] = context._chat_id
        new_config["version"] = app_version
        new_config["generation_params"] = default.generation_params
        configs[user] = new_config
        return configs[user]
    else:
        return configs[user]


async def send_admin(generation_id, update, user, generation_params, img_io):
    admin_chat_id = getenv("ADMIN_CHAT_ID", None)
    if generation_params:
        buttons = []
        generations_cache[generation_id] = generation_params
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Re-generation", callback_data=f"regenerate:{generation_id}"
                )
            ]
        )
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Upscale", callback_data=f"upscale:{generation_id}"
                )
            ]
        )
        keyboard = InlineKeyboardMarkup(buttons)
    else:
        keyboard = None
    if admin_chat_id:
        bot = update.get_bot()
        return await bot.send_photo(
            admin_chat_id,
            img_io,
            f"image from {user.name} [#{generation_id}]",
            reply_markup=keyboard,
        )


STATE = None
if exists("blacklist.txt"):
    with open("blacklist.txt") as f:
        black_list_users = [x.strip() for x in f.readlines()]
else:
    black_list_users = []

if exists("whitelist.txt"):
    with open("whitelist.txt") as f:
        white_list_users = [x.strip() for x in f.readlines()]
else:
    white_list_users = []


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user:
        init_params(update, context)  # Инициализация пользовательских настроек
        if not update.message or not update.message.text:
            return
        current_strike_count = black_list.get(user.name, 0)
        print(user.name, current_strike_count)
        if (
            user.name in black_list_users
            or current_strike_count >= 5
            and user.name not in white_list_users
        ):
            print(user.name, "[blocked] user request rejected because user has banned")
            await update.message.reply_text(
                f"Strike {current_strike_count}/5 [Access to this bot is blocked for you for creating NSFW content.]",
                reply_to_message_id=update.message.id,
            )
            return
        generation_params = copy(default.generation_params_low)
        translated = GoogleTranslator(source="auto", target="en").translate(
            update.message.text
        )
        if user.name not in white_list_users:
            censored_text = profanity.censor(translated)
        else:
            censored_text = translated
        generation_params["prompt"] = censored_text.replace("*", "")
        if " not " in censored_text.lower():
            generation_params["negative_prompt"] = ",".join(
                translated.lower().split(" not ")[1:]
            )
            generation_params["prompt"] = censored_text.lower().split(" not ")[0]
        if len(translated) < 3:
            return
        generation_params["seed"] = randint(1, 1000000)
        print(user.name, generation_params)
        img_io = None
        try:
            req_uid = str(uuid4())[:8]
            await user.send_chat_action(telegram.constants.ChatAction.TYPING)
            for _ in tqdm(
                range(1),
                desc=f"{datetime.now().isoformat()} Generate image for {user.name}",
            ):
                t = datetime.now()
                meta = generations.create(
                    {
                        "username": user.name,
                        "gid": req_uid,
                        "prompt": generation_params["prompt"],
                        "negative_prompt": generation_params["negative_prompt"],
                        "seed": generation_params["seed"],
                        "status": "processing",
                        "hd": False,
                    }
                )
                await user.send_message(
                    "Generation request accepted", reply_to_message_id=update.message.id
                )
                img_io, filename = generate_image(
                    generation_params, req_uid, generation_params["seed"]
                )
                delta = (datetime.now() - t).total_seconds()
                generations.update(
                    meta["id"],
                    {"status": "done", "duration": delta, "filename": filename},
                )
                await user.send_chat_action(telegram.constants.ChatAction.TYPING)
                censor_result = predict.classify(nudenet_classifier, filename)[filename]
                censored_text, block_porn, block_porn_value = check_filter(
                    censored_text, censor_result, "porn", 0.8
                )
                censored_text, block_hentai, block_hentai_value = check_filter(
                    censored_text, censor_result, "hentai", 0.8
                )
                await send_admin(req_uid, update, user, generation_params, img_io)
                img_io.seek(0)

                if not block_porn and not block_hentai:
                    await user.send_chat_action(
                        telegram.constants.ChatAction.UPLOAD_PHOTO
                    )
                    buttons = []
                    generations_cache[req_uid] = generation_params
                    buttons.append(
                        [
                            InlineKeyboardButton(
                                text="Regenerate", callback_data=f"regenerate:{req_uid}"
                            )
                        ]
                    )
                    buttons.append(
                        [
                            InlineKeyboardButton(
                                text="Upscale", callback_data=f"upscale:{req_uid}"
                            )
                        ]
                    )
                    keyboard = InlineKeyboardMarkup(buttons)
                    await update.message.reply_photo(
                        img_io,
                        f"[#{req_uid}] {censored_text}",
                        filename=f"{req_uid}.png",
                        reply_to_message_id=update.message.id,
                        reply_markup=keyboard,
                    )
                else:
                    current_strike_count = black_list.get(user.name, 0)
                    current_strike_count += 1
                    black_list.set(user.name, current_strike_count)
                    await update.message.reply_text(
                        censored_text, reply_to_message_id=update.message.id
                    )
                    warn_message = f"Strike {current_strike_count}/10 - NSFW content is not welcome in this bot, it was created for a small group of artists and their art experiments. It is not prohibited to use it to create creative content by any user, but when you reach 10 strikes, access to this bot will be blocked for you."
                    await update.message.reply_text(
                        warn_message, reply_to_message_id=update.message.id
                    )
                    print(user.name, warn_message)
                remove(filename)
        except Exception as e:
            await update.message.reply_text(f"An error has occurred: {e}")
            raise e


def check_filter(censored_text, censor_result, filter_name, filter_edge):
    if censor_result[filter_name] > filter_edge:
        block_reason = f"{filter_name}={round(censor_result[filter_name]*100)}%"
        censored_text = f"[BLOCKED {block_reason}] {censored_text}"
        return censored_text, True, round(censor_result[filter_name]*100)
    else:
        return censored_text, False, round(censor_result[filter_name]*100)


def generate_image(job_config, gen_id, seed):
    result1 = api.txt2img(**job_config)
    img_io = BytesIO()
    result1.image.save(img_io, "PNG")
    img_io.seek(0)
    filename = join(images_folder, f"{gen_id}-{job_config['seed']}.png")
    with open(filename, "wb") as f:
        result1.image.save(f, "PNG")
    return img_io, filename


async def handle_callback(update, context):
    user = update.effective_user
    query = update.callback_query
    action, generation_id = query.data.split(":")
    generation_params = generations_cache[generation_id]
    print(action.upper(), generation_params["prompt"])
    for _ in tqdm(
        range(1), desc=f"{datetime.now().isoformat()} Generate image for {user.name}"
    ):
        t = datetime.now()
        meta = generations.create(
            {
                "username": user.name,
                "gid": generation_id,
                "prompt": generation_params["prompt"],
                "negative_prompt": generation_params["negative_prompt"],
                "seed": generation_params["seed"],
                "status": "processing",
                "hd": False,
            }
        )
        if action == "upscale":
            generation_params.update(copy(default.generation_params_hq))
            await user.send_message("Generation request accepted")
            img_io, filename = await create_new_image(
                generation_id, update, user, generation_params
            )
            buttons = []
            generations_cache[generation_id] = generation_params
            buttons.append(
                [
                    InlineKeyboardButton(
                        text="Re-generation",
                        callback_data=f"regenerate:{generation_id}",
                    )
                ]
            )
            keyboard = InlineKeyboardMarkup(buttons)
            await update.callback_query.message.reply_photo(
                img_io,
                f"Upscale: #{generation_id}, seed {generation_params['seed']}",
                filename=f"{filename}.png",
                reply_to_message_id=update.callback_query.message.id,
                reply_markup=keyboard,
            )
            delta = (datetime.now() - t).total_seconds()
            generations.update(
                meta["id"],
                {"status": "done", "duration": delta, "filename": filename, "hd": True},
            )
        if action == "regenerate":
            generation_params["seed"] = randint(1, 1000000)
            await user.send_message("Generation request accepted")
            img_io, filename = await create_new_image(
                generation_id, update, user, generation_params
            )
            buttons = []
            generations_cache[generation_id] = generation_params
            buttons.append(
                [
                    InlineKeyboardButton(
                        text="Re-generation",
                        callback_data=f"regenerate:{generation_id}",
                    )
                ]
            )
            if not generation_params["enable_hr"]:
                buttons.append(
                    [
                        InlineKeyboardButton(
                            text="Upscale", callback_data=f"upscale:{generation_id}"
                        )
                    ]
                )
            keyboard = InlineKeyboardMarkup(buttons)
            await update.callback_query.message.reply_photo(
                img_io,
                f"Re-generation: #{generation_id}, seed {generation_params['seed']}",
                filename=f"{filename}.png",
                reply_to_message_id=update.callback_query.message.id,
                reply_markup=keyboard,
            )
            delta = (datetime.now() - t).total_seconds()
            generations.update(
                meta["id"],
                {
                    "status": "done",
                    "duration": delta,
                    "filename": filename,
                    "seed": generation_params["seed"],
                    "hd": True,
                },
            )


async def create_new_image(generation_id, update, user, generation_params):
    await user.send_chat_action(telegram.constants.ChatAction.TYPING)
    img_io, filename = generate_image(
        generation_params, generation_id, generation_params["seed"]
    )
    await user.send_chat_action(telegram.constants.ChatAction.TYPING)
    await send_admin(generation_id, update, user, generation_params, img_io)
    img_io.seek(0)
    await user.send_chat_action(telegram.constants.ChatAction.UPLOAD_PHOTO)
    return img_io, filename


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(getenv("TOKEN")).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    # application.add_handler(InlineQueryHandler(echo))
    # application.add_handler(MessageHandler(filters.COMMAND, echo))
    application.add_handler(CallbackQueryHandler(handle_callback))
    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
