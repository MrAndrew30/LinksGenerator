from aiogram.filters import Command
from aiogram.types import Message
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram import F
from aiogram.filters import BaseFilter


class IsAdminFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        """Фильтр для проверки прав администратора у пользователя.

        Проверяет, является ли отправитель сообщения администратором,
        используя данные из базы данных. Возвращает True если пользователь
        имеет статус администратора, иначе False.

        Args:
            message: Объект сообщения от пользователя для проверки.

        Returns:
            bool: Флаг, указывающий на наличие прав администратора:
                - True: пользователь является администратором
                - False: пользователь не является администратором

        Note:
            Для работы требует предварительной инициализации _db_worker.
        """
        return _db_worker.is_admin(str(message.from_user.id))


router = Router()
_google_worker = None
_vk_api_worker = None
_db_worker = None
_admin_id = None


def setup(dp, google_worker, vk_api_worker, db_worker, admin_id):
    """Инициализирует обработчики команд с зависимостями.

    Устанавливает глобальные экземпляры менеджеров и подключает роутер к диспетчеру.

    Args:
        dp: Экземпляр Dispatcher из aiogram
        google_worker: Экземпляр GoogleSheetsManager для работы с таблицами
        vk_api_worker: Экземпляр VKLinkManager для работы с VK API
        db_worker: Экземпляр DatabaseManager для работы с БД
        admin_id: Телеграм-айди администратора бота
    """
    global _google_worker
    _google_worker = google_worker
    global _vk_api_worker
    _vk_api_worker = vk_api_worker
    global _db_worker
    _db_worker = db_worker
    global _admin_id
    _admin_id = admin_id
    dp.include_router(router)


@router.message(Command(commands=['start']))
async def process_start_command(
    message: Message,
    state: FSMContext
) -> None:
    """Обрабатывает команду /start и отправляет приветственное сообщение.

    Очищает текущее состояние пользователя и отправляет приветственное сообщение
    с инструкциями по использованию бота.
    Добавляет пользователя в базу данных. Если id пользователя
    совпадает с TG_ADMIN_ID, то делает этого пользователя администратором

    Args:
        message: Объект сообщения от пользователя.
        state: Контекст текущего состояния пользователя.
    """
    await state.clear()
    if not _db_worker.user_exists(message.from_user.id):
        if _admin_id == str(message.from_user.id):
            _db_worker.add_user(message.from_user.id, "admin")
        else:
            _db_worker.add_user(message.from_user.id, "user")
    await message.answer('Привет, я бот для генерации коротких ссылок\n'
                         'Нажми /help, чтобы увидеть мои команды')


@router.message(Command(commands=['help']))
async def process_help_command(
    message: Message,
    state: FSMContext
) -> None:
    """Обрабатывает команду /help и предоставляет информацию о командах.

    Очищает текущее состояние пользователя и отправляет сообщение со списком
    доступных команд бота.

    Args:
        message: Объект сообщения от пользователя.
        state: Контекст текущего состояния пользователя.
    """
    await state.clear()
    await message.answer(
        '/start - приветственное сообщение\n'
        '/create_links <link> - создание коротких ссылок из ссылки link\n'
        '/analytics - аналатика переходов по текущим ссылкам в таблице\n'
        '/myID - получить ваш user ID\n'
        '/add_admin <user_id> - добавление админа\n'
        '/remove_admin <user_id> - удаление админа\n'
        '/create_table - создать таблицу по макету\n'
    )


@router.message(Command(commands=['myID']))
async def process_id_command(
    message: Message
) -> None:
    """Обрабатывает команду /myID и отправляет пользователю его ID.

    Извлекает идентификатор пользователя из объекта сообщения и отправляет его
    пользователю в формате Markdown.

    Args:
        message: Объект сообщения от пользователя.
    """
    await message.answer(
        f"Ваш user ID: `{message.from_user.id}`", parse_mode="MARKDOWN"
    )


@router.message(Command(commands=['create_table']), IsAdminFilter())
async def create_table_command(message: Message) -> None:
    """Обрабатывает команду '/create_table' для создания и настройки Google Sheets таблицы.

    Создает новую таблицу с указанными листами и добавляет стандартные заголовки.
    Отправляет пользователю сообщение об успешном выполнении или об ошибке.

    Args:
        message (Message): Объект сообщения от пользователя.

    Raises:
        Exception: Любые исключения, возникшие при работе с Google Sheets API,
            перехватываются и отправляются пользователю в виде сообщения.

    Notes:
        - Требует предварительной инициализации _google_worker.
        - Создает три стандартных листа: "Текущее мероприятие", "Аналитика переходов", "Активные партнеры".
    """
    if _google_worker is None:
        await message.answer("Ошибка: сервис Google Sheets не инициализирован")
        return

    try:
        # Создаем листы
        sheets = ["Текущее мероприятие",
                  "Аналитика переходов", "Активные партнеры"]
        _google_worker.create_sheets(sheets)

        # Добавляем заголовки
        _google_worker.make_headers()

        await message.answer("Таблица успешно создана и настроена!")
    except Exception as e:
        await message.answer(f"Ошибка при создании таблицы: {str(e)}")


@router.message(Command("create_links"), IsAdminFilter())
async def process_create_links(message: Message, command: Command) -> None:
    """Генерирует короткие ссылки для партнеров и сохраняет их в таблицу.

    Args:
        message: Объект сообщения от пользователя.
        command: Объект команды с аргументами.

    Returns:
        None: Отправляет сообщения пользователю через message.answer()

    Raises:
        ValueError: Если аргументы команды не соответствуют ожидаемому формату.

    Notes:
        Пример использования:
        /create_links https://example.com
    """
    if command.args is None:
        await message.answer(
            "Ошибка: Ссылка не была введена. Пример:\n"
            "/create_links <link>"
        )
        return
    try:
        if len(command.args.split()) > 1:
            raise ValueError
        link = command.args.split()[0]
    except ValueError:
        await message.answer(
            "Ошибка: Неверный ввод команды. Пример:\n"
            "/create_links <link>"
        )
        return
    await message.answer("...начинаю генерацию ссылок, подождите...")
    short_links = [_vk_api_worker.get_short_link(link + "?utm_source=" + item[0])
                   for item in _google_worker.get_short_names()]
    _google_worker.insert_event_table("C", short_links)
    await message.answer(
        "Ссылка создана!\n"
        f"Ваша ссылка: {link}"
    )


@router.message(Command("analytics"), IsAdminFilter())
async def process_analytics(message: Message, command: Command) -> None:
    """Собирает и сохраняет статистику переходов по партнерским ссылкам.

    Сохраняет суммарное количество переходов для каждой ссылки в колонку F таблицы.

    Args:
        message: Объект сообщения от пользователя.
        command: Объект команды.

    Returns:
        None: Отправляет сообщения пользователю через message.answer()
    """
    await message.answer(
        "---Начинаю считать переходы по ссылкам---"
    )
    stats = [sum(item["views"] for item in _vk_api_worker.get_link_stats(short_link[0])["stats"])
             for short_link in _google_worker.get_partner_links()]
    _google_worker.insert_event_table("F", stats)
    await message.answer(
        "Обработал команду аналитики переходов"
    )


@router.message(Command("add_admin"), IsAdminFilter())
async def process_add_admin(message: Message, command: Command) -> None:
    """Обрабатывает команду добавления нового администратора.

    Проверяет введенный ID пользователя и добавляет его в список администраторов,
    если пользователь заходил в бота. Команда доступна только текущим администраторам.

    Args:
        message: Объект сообщения от пользователя.
        command: Объект команды с аргументами.

    Raises:
        ValueError: Если аргументы команды не соответствуют ожидаемому формату.

    Examples:
        Правильное использование:
        /add_admin 123456789

    Note:
        - Требует предварительной инициализации _db_worker
        - Пользователь с указанным ID должен был зайти в бота хотя бы один раз
    """
    if command.args is None:
        await message.answer(
            "Ошибка: id нового админа не был введен. Пример:\n"
            "/add_admin <tg_id>"
        )
        return
    try:
        if len(command.args.split()) > 1:
            raise ValueError
        new_admin_id = command.args.split()[0]
    except ValueError:
        await message.answer(
            "Ошибка: Неверный ввод команды. Пример:\n"
            "/add_admin <tg_id>"
        )
        return
    if _db_worker.user_exists(new_admin_id):
        if _db_worker.add_admin(new_admin_id):
            await message.answer("Администратор успешно добавлен")
        else:
            await message.answer("Что-то пошло не так")
    else:
        await message.answer(
            "Ошибка: пользователь с таким id пока не заходил в бота."
        )


@router.message(Command("remove_admin"), IsAdminFilter())
async def process_add_admin(message: Message, command: Command) -> None:
    """Обрабатывает команду удаления пользователя из списка администраторов.

    Проверяет введенный ID пользователя и удаляет его из списка администраторов,
    если пользователь имеет статус администратора.
    Команда доступна только текущим администраторам.

    Args:
        message: Объект сообщения от пользователя.
        command: Объект команды с аргументами.

    Raises:
        ValueError: Если аргументы команды не соответствуют ожидаемому формату
                   (отсутствуют или содержат более одного аргумента).

    Examples:
        Правильное использование:
        /remove_admin 123456789

    Note:
        - Требует предварительной инициализации _db_worker
        - Пользователь с указанным ID должен существовать и быть администратором
    """
    if command.args is None:
        await message.answer(
            "Ошибка: id админа не был введен. Пример:\n"
            "/remove_admin <tg_id>"
        )
        return
    try:
        if len(command.args.split()) > 1:
            raise ValueError
        admin_id = command.args.split()[0]
    except ValueError:
        await message.answer(
            "Ошибка: Неверный ввод команды. Пример:\n"
            "/remove_admin <tg_id>"
        )
        return
    if _db_worker.is_admin(admin_id):
        if _db_worker.remove_admin(admin_id):
            await message.answer("Администратор успешно удален")
        else:
            await message.answer("Что-то пошло не так")
    else:
        await message.answer(
            "Ошибка: такого администратора нет."
        )


@router.message(Command("add_admin", "remove_admin", "create_table"))
async def handle_not_admin(message: Message) -> None:
    """Обрабатывает попытки выполнения административных команд от неавторизованных пользователей.

    Перехватывает команды /add_admin, /remove_admin и /create_table, если они были отправлены
    пользователями без прав администратора. Отправляет соответствующее уведомление.

    Args:
        message: Объект сообщения от пользователя.
    """
    await message.answer("У вас нет прав администратора для выполнения этой команды!")
