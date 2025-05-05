from aiogram.filters import Command
from aiogram.types import Message
from aiogram import Router
from aiogram.fsm.context import FSMContext

router = Router()


@router.message(Command(commands=['start']))
async def process_help_command(
    message: Message,
    state: FSMContext
):
    await state.clear()
    await message.answer('Привет, я бот для генерации коротких ссылок\n'
                         'Нажми /help, чтобы увидеть мои команды')


@router.message(Command(commands=['help']))
async def process_start_command(
    message: Message,
    state: FSMContext
):
    await state.clear()
    await message.answer(
        '/start - приветственное сообщение\n'
        '/create_links <link> - создание коротких ссылок из ссылки link\n'
        '/analytics - аналатика переходов по текущим ссылкам в таблице\n'
        '/myID - получить ваш user ID\n'
        '/add_admin <user_id> - добавление админа\n'
        '/remove_admin <user_id> - удаление админа'
    )


@router.message(Command(commands=['myID']))
async def process_start_command(
    message: Message,
    state: FSMContext
):
    await message.answer(
        f"Ваш user ID: `{message.from_user.id}`", parse_mode="MARKDOWN"
    )
