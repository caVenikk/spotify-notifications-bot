from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
import json

from excel import ExcelHelper


with open('config.json') as file:
    config = json.load(file)

MAX_AMOUNT = 100
TOKEN = config['token']
PATH = config['path']
WHITE_USERS = config['white_users']

bot = Bot(token=TOKEN)
eh = ExcelHelper(PATH)
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def process_start_command(message: types.Message):
    if message.from_user.id not in WHITE_USERS:
        return
    await message.answer("Type /track <number>")


@dp.message_handler(commands=["track"])
async def process_track_command(message: types.Message):
    if message.from_user.id not in WHITE_USERS:
        return
    global MAX_AMOUNT
    args = message.get_args()
    if args:
        argument = args.split()[0]
        try:
            number = int(argument)
            MAX_AMOUNT = number
            print(f'UPDATED MAX AMOUNT TO {MAX_AMOUNT}')
        except ValueError:
            await message.answer('Неверный формат! Введите число.')
    await message.answer(f"Отслеживаем первые <b><i>{MAX_AMOUNT}</i></b> подписчиков", parse_mode="HTML")


@dp.message_handler(commands=["earnings"])
async def process_earnings_command(message: types.Message):
    if message.from_user.id not in WHITE_USERS:
        return
    earnings = eh.get_earnings()
    await message.answer(f"Заработок: <b>{earnings}</b>", parse_mode='HTML')


@dp.message_handler(commands=["clean"])
async def process_clean_command(message: types.Message):
    if message.from_user.id not in WHITE_USERS:
        return
    clean_earnings = eh.get_clean_earnings()
    await message.answer(f"Чистыми: <b>{clean_earnings}</b>", parse_mode='HTML')
    
    
@dp.message_handler(commands=["update"])
async def process_update_command(message: types.Message):
    if message.from_user.id not in WHITE_USERS:
        return
    args = message.get_args()
    text = "Excel-файл обновлен"
    if args:
        path = args.split()[0]
        eh.update(path)
        text += f"\nНовый путь - <i>{path}</i>"
    else:
        eh.update()
    await message.answer(text, parse_mode='HTML')


async def check_task():
    global CHECKED_TODAY
    print(f'CHECKING WITH MAX AMOUNT {MAX_AMOUNT}')
    eh.update()
    subs = eh.get_subscribers(MAX_AMOUNT)
    outdated_subs = eh.get_outdated_subscribers(subs)
    if outdated_subs:
        now = datetime.now()
        text = f"Сегодня <b>{now.strftime('%d.%m.%y')}</b>\n<b><i>{len(outdated_subs)}</i></b> подписчиков, которые должны внести оплату:\n"
        subs_text = "\n".join([sub.__str__() for sub in outdated_subs])
        text += subs_text
        await bot.send_message(385475150, text, parse_mode="HTML")


if __name__ == "__main__":
    scheduler = AsyncIOScheduler()
    tr = IntervalTrigger(hours=4, start_date=datetime.now()-timedelta(hours=3, minutes=58))
    scheduler.add_job(check_task, trigger=tr)
    scheduler.start()

    executor.start_polling(dp)
