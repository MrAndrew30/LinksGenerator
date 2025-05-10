from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build


class GoogleSheetsManager:
    """Класс для работы с Google Таблицами.

    Содержит методы для:

    - Загрузки данных в таблицы

    - Чтения данных из таблиц

    - Создания листов и заголовков

    - Генерации отчетов

    Attributes:
        SPREADSHEET_ID (str): ID Google таблицы из переменных окружения.
        service (Resource): Объект сервиса Google Sheets API.
    """

    def __init__(self, table_id):
        """Инициализирует GoogleSheetsManager с авторизацией через сервисный аккаунт.

        Args:
            table_id (str): ID Google-таблицы для работы
        """
        self._SPREADSHEET_ID = table_id
        credentials = Credentials.from_service_account_file(
            "credentials.json",
            scopes=["https://www.googleapis.com/auth/spreadsheets"],
        )
        self._service = build("sheets", "v4", credentials=credentials)

    def insert_headers(self, sheet: str, values: list[str]) -> None:
        """Вставляет заголовки в указанный лист таблицы.

        Args:
            sheet: Название листа (должен существовать в таблице)
            values: Список строк с заголовками (каждый элемент - отдельная строка)

        Raises:
            googleapiclient.errors.HttpError: При ошибках API
            ValueError: Если лист не существует
        """
        body = {"values": values}
        result = (
            self._service.spreadsheets()
            .values()
            .update(
                spreadsheetId=self._SPREADSHEET_ID,
                range=sheet + "!A1",
                valueInputOption="RAW",
                body=body,
            )
            .execute()
        )

    def make_headers(self) -> None:
        """Создает стандартные заголовки для всех листов таблицы.

        Формирует и вставляет шаблонные заголовки для трех листов:

        - Текущее мероприятие

        - Аналитика переходов

        - Активные партнеры

        Raises:
            googleapiclient.errors.HttpError: При ошибках API
        """
        event_sheet = "Текущее мероприятие"
        analytics_sheet = "Аналитика переходов"
        partners_sheet = "Активные партнеры"
        values_event = [
            ["Партнер", "Аббревиатура", "Ссылка для партнера",
                "Пост отправлен", "Пост опубликован", "Количество переходов"],
        ]
        values_analytics = [
            ["Партнер", "Количество переходов"],
        ]
        values_partners = [
            ["Партнер", "Аббревиатура", "Ссылка на партнера",
             "Контактное лицо", "Ответственный"],
        ]

        self.insert_headers(event_sheet, values_event)
        self.insert_headers(analytics_sheet, values_analytics)
        self.insert_headers(partners_sheet, values_partners)

    def create_sheets(self, sheets: list[str]) -> None:
        """Создает новые листы в таблице, если они не существуют.

        Args:
            sheets: Список названий листов для создания.

        Raises:
            googleapiclient.errors.HttpError: При ошибках API
        """
        spreadsheet = self._service.spreadsheets().get(
            spreadsheetId=self._SPREADSHEET_ID).execute()
        existing_sheets = {sheet['properties']['title']
                           for sheet in spreadsheet.get('sheets', [])}

        # Формируем запрос для добавления новых листов
        request = {"requests": []}
        for sheet in sheets:
            if sheet not in existing_sheets:
                request["requests"].append({
                    "addSheet": {
                        "properties": {
                            "title": sheet,
                        }
                    }
                })

        # Выполняем запрос только если есть новые листы для добавления
        if request["requests"]:
            self._service.spreadsheets().batchUpdate(
                spreadsheetId=self._SPREADSHEET_ID,
                body=request,
            ).execute()

    def get_short_names(self) -> list[list]:
        """Возвращает все аббревиатуры партнеров из листа 'Активные партнеры', исключая заголовок.

        Returns:
            list[list]: Список списков строк, где каждая строка - аббревиатура партнера.
                        Возвращает пустой список, если нет данных или произошла ошибка.

        Examples:
            >>> manager.get_active_events()
            [['part1', ], ['part2', ]]
        """
        try:
            # Получаем все данные с листа (начиная с первой строки)
            result = (
                self._service.spreadsheets()
                .values()
                .get(
                    spreadsheetId=self._SPREADSHEET_ID,
                    range="Активные партнеры!B:B"
                )
                .execute()
            )

            values = result.get('values', [])

            if len(values) > 1:
                # Фильтруем непустые строки (исключая заголовок)
                non_empty_rows = [
                    row for row in values[1:]
                    if any(cell.strip() for cell in row)
                ]
                return non_empty_rows

            return []

        except Exception as e:
            print(f"Ошибка при получении аббревиатур партнеров: {str(e)}")
            return []

    def insert_event_table(self, column: str, values: list[str]) -> dict:
        """Вставляет значения в столбец column листа 'Текущее мероприятие'.

        Args:
            column: Буква столбца (A-Z)
            values: Список значений для вставки

        Returns:
            dict: Ответ API Google Sheets с результатами операции

        Raises:
            ValueError: Если values пуст или column некорректен
            googleapiclient.errors.HttpError: При ошибках API

        Example:
            >>> manager.insert_event_table("C", ["link1", "link2"])
            {'spreadsheetId': '...', 'updatedCells': 2, ...}
        """
        if not values:
            raise ValueError("Список значений не может быть пустым")

        try:
            # Формируем тело запроса
            body = {
                # Каждое значение в отдельный список (отдельная строка)
                "values": [[value] for value in values]
            }

            # Выполняем запрос к API
            result = (
                self._service.spreadsheets()
                .values()
                .update(
                    spreadsheetId=self._SPREADSHEET_ID,
                    range=f"Текущее мероприятие!{column}2:{column}",
                    valueInputOption="RAW",
                    body=body,
                )
                .execute()
            )

            return result

        except Exception as e:
            print(f"Ошибка при вставке значений: {str(e)}")
            raise

    def get_partner_links(self) -> list[list]:
        """Возвращает все ссылки партнеров из столбца C листа 'Текущее мероприятие', исключая заголовок.

        Returns:
            list[list]: Список списков, где каждый внутренний список содержит одну ссылку.
                        Возвращает пустой список, если нет данных или произошла ошибка.

        Examples:
            >>> manager.get_partner_links()
            [['https://example.com/partner1'], 
            ['https://example.com/partner2'],
            ['https://example.com/partner3']]
        """
        try:
            # Получаем данные из столбца C, начиная со 2 строки
            result = (
                self._service.spreadsheets()
                .values()
                .get(
                    spreadsheetId=self._SPREADSHEET_ID,
                    range="Текущее мероприятие!C2:C"  # Столбец C, со 2 строки до конца
                )
                .execute()
            )

            values = result.get('values', [])

            # Фильтруем непустые строки
            non_empty_links = [
                # Каждую ссылку помещаем в отдельный список
                [row[0]] for row in values
                if row and row[0].strip()    # Проверяем что строка не пустая
            ]

            return non_empty_links

        except Exception as e:
            print(f"Ошибка при получении ссылок партнеров: {str(e)}")
            return []
