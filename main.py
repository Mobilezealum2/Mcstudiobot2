import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.methods import DeleteWebhook
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import BotCommand

# =====================================================
#                    НАСТРОЙКИ
# =====================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
logging.info(f"BOT_TOKEN loaded: {'yes' if BOT_TOKEN else 'NO — is None!'}")

ADMIN_IDS = [
    5751578912,
    6020036331,
]

logging.basicConfig(level=logging.INFO)

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

# =====================================================
#                 PREMIUM EMOJI ID
# =====================================================

CHECK_EMOJI = "5206607081334906820"

EMOJI_RENDER = "5375217356958094316"
EMOJI_SKINS = "5377361228538596572"
EMOJI_ART = "5377831956954237436"
EMOJI_ANIM5 = "5377531622776131578"
EMOJI_ANIM60 = "5377300519175865657"
EMOJI_CLIP = "5379667063335831557"

EMOJI_HI = "5334863012475986105"
EMOJI_BLENDER = "5364290083983736876"
EMOJI_LINK = "5271604874419647061"
EMOJI_DOWN = "5406745015365943482"
EMOJI_NEW = "5382357040008021292"
EMOJI_LIST = "5197269100878907942"
EMOJI_BUCKS = "5197434882321567830"
EMOJI_MCSTUDIO = "5372827766003637704"
EMOJI_RIG = "5377627984662383594"

# =====================================================
#                    УСЛУГИ
# =====================================================

SERVICES = [
    {
        "name": "Рендер проекта",
        "price": 250,
        "emoji": EMOJI_RENDER,
        "style": "success"
    },
    {
        "name": "Риг",
        "price": "~250",
        "emoji": EMOJI_RIG,
        "style": "success"
    },
    {
        "name": "Арт",
        "price": 250,
        "emoji": EMOJI_ART,
        "style": "success"
    },
    {
        "name": "Скины",
        "price": 450,
        "emoji": EMOJI_SKINS,
        "style": "primary"
    },
    {
        "name": "Анимация 5 секунд",
        "price": 500,
        "emoji": EMOJI_ANIM5,
        "style": "primary"
    },
    {
        "name": "Анимация 1:00 (TikTok / Shorts)",
        "price": 5000,
        "emoji": EMOJI_ANIM60,
        "style": "danger"
    },
    {
        "name": "Анимационный клип",
        "price": 10000,
        "emoji": EMOJI_CLIP,
        "style": "default"
    },
]

user_orders = {}
user_order_messages = {}

# =====================================================
#                  ГЛАВНОЕ МЕНЮ
# =====================================================

async def send_services(message: types.Message):
    builder = InlineKeyboardBuilder()

    for index, service in enumerate(SERVICES):

        price = (
            f"от {service['price']}₽"
            if service["price"] >= 10000
            else f"{service['price']}₽"
        )

        builder.row(
            types.InlineKeyboardButton(
                text=f"{service['name']} ({price})",
                callback_data=f"service_{index}",
                style=service["style"],
                icon_custom_emoji_id=service["emoji"]
            )
        )

    text = (
        f"<tg-emoji emoji-id='{EMOJI_HI}'>👋</tg-emoji> "
        "<b>Добро пожаловать в MC Studio!</b>\n\n"
        f"<tg-emoji emoji-id='{EMOJI_MCSTUDIO}'>👋</tg-emoji> "

        "Рады приветствовать вас в нашем сервисе.\n\n"

        f"<tg-emoji emoji-id='{EMOJI_BLENDER}'>🎨</tg-emoji> "
        "Мы создаём качественные Minecraft-арты, риги, скины и анимации любой сложности, а также рендерим Blender-проекты.\n\n"

        f"<tg-emoji emoji-id='{EMOJI_LINK}'>🔗</tg-emoji> "
        "Выберите интересующую услугу ниже."
    )

    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=builder.as_markup()
    )


@dp.message(Command("start"))
async def start(message: types.Message):

    if message.from_user.id in ADMIN_IDS:
        await message.answer(
            "👋 Добро пожаловать, администратор!\n\n"
            "Ожидайте новые заказы от пользователей."
        )
        return

    await send_services(message)


@dp.message(Command("services"))
async def services(message: types.Message):
    await send_services(message)

# =====================================================
#             ВЫБОР УСЛУГИ
# =====================================================

@dp.callback_query(F.data.startswith("service_"))
async def choose_service(callback: types.CallbackQuery):

    index = int(callback.data.split("_")[1])

    service = SERVICES[index]


    user_orders[callback.from_user.id] = service


    await callback.answer()


    # Убираем кнопки после выбора услуги
        # Убираем стартовое меню после выбора услуги
    try:
        await callback.message.delete()
    except:
        pass


    order_msg = await callback.message.answer(
        f"""
<b><tg-emoji emoji-id='{EMOJI_LIST}'>✅</tg-emoji> Вы выбрали:</b>

{service['name']}

<b><tg-emoji emoji-id='{EMOJI_BUCKS}'>✅</tg-emoji> Цена:</b>
{"от " if service['price'] >= 10000 else ""}
{service['price']}₽


<tg-emoji emoji-id='{EMOJI_LINK}'>✅</tg-emoji> Теперь отправьте:

• описание заказа;
• фото (без сжатия);
• видео (без сжатия);
• документы;
• референсы.


После отправки информация автоматически поступит администрации.
""",
        parse_mode="HTML"
    )


    # сохраняем сообщение с ТЗ
    user_order_messages[callback.from_user.id] = order_msg.message_id
   
    # =====================================================
#            ПРИЁМ СООБЩЕНИЙ ПОЛЬЗОВАТЕЛЯ
# =====================================================

@dp.message()
async def new_order(message: types.Message):

    if message.from_user.id not in user_orders:
        return


    service = user_orders[message.from_user.id]
    
        # удаляем сообщение "Вы выбрали" после получения ТЗ
    if message.from_user.id in user_order_messages:
        try:
            await bot.delete_message(
                chat_id=message.chat.id,
                message_id=user_order_messages[message.from_user.id]
            )
        except:
            pass

        del user_order_messages[message.from_user.id]


    if message.from_user.username:
        sender = f"@{message.from_user.username}"
    else:
        sender = f"ID {message.from_user.id}"


    price = (
        f"от {service['price']}₽"
        if service["price"] >= 10000
        else f"{service['price']}₽"
    )


    text = (
        f"<tg-emoji emoji-id='{EMOJI_NEW}'>✅</tg-emoji> "
        "<b>Новый заказ!</b>\n\n"

        f"<b>Услуга:</b> {service['name']}\n"
        f"<b>Цена:</b> {price}\n\n"

        f"<b>Заказчик:</b> {sender}\n\n"

        f"<tg-emoji emoji-id='{EMOJI_DOWN}'>👇</tg-emoji> "
        "<b>Описание сообщением ниже</b>"
    )


    # Кнопка для администратора
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Просмотрено",
        style = "success",
        callback_data=f"viewed_{message.from_user.id}",
        icon_custom_emoji_id=CHECK_EMOJI
    )


    for admin in ADMIN_IDS:

        await bot.send_message(
            admin,
            text,
            parse_mode="HTML",
            reply_markup=builder.as_markup()
        )


        # Копируем фото/файлы/видео админу
        try:
            await bot.copy_message(
                chat_id=admin,
                from_chat_id=message.chat.id,
                message_id=message.message_id
            )
        except:
            pass



    await message.answer(
        f"<tg-emoji emoji-id='{CHECK_EMOJI}'>✅</tg-emoji> "
        "<b>Ваш заказ отправлен!</b>\n\n"

        "Мы получили вашу заявку.\n\n"

        "Администрация ознакомится с заказом, "
        "после чего свяжется с вами для обсуждения деталей.",
        
        parse_mode="HTML"
    )


    del user_orders[message.from_user.id]



# =====================================================
#          КНОПКА "ПРОСМОТРЕНО"
# =====================================================

@dp.callback_query(F.data.startswith("viewed_"))
async def viewed_order(callback: types.CallbackQuery):

    user_id = int(callback.data.split("_")[1])


    # Убираем кнопку у администратора
    try:
        await callback.message.edit_reply_markup(
            reply_markup=None
        )
    except:
        pass


    await callback.answer(
        "Заказ отмечен как просмотренный"
    )


    await bot.send_message(
        user_id,
        f"<tg-emoji emoji-id='{CHECK_EMOJI}'>✅</tg-emoji> "
        "<b>Ваш заказ просмотрен!</b>\n\n"

        "Мы ознакомились с вашей заявкой.\n\n"

        "В ближайшее время с вами свяжутся "
        "для уточнения деталей заказа.",
        
        parse_mode="HTML"
    )



# =====================================================
#                     ЗАПУСК
# =====================================================

async def main():

    await bot(DeleteWebhook(drop_pending_updates=True))


    print("=" * 45)
    print(" MC Studio Bot успешно запущен!")
    print("=" * 45)
    
    await bot.set_my_commands([
    BotCommand(command="start", description="Запустить бота"),
    BotCommand(command="services", description="Список услуг"),
])

    await dp.start_polling(bot)



if __name__ == "__main__":
    asyncio.run(main())
