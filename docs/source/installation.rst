Установка и настройка проекта
==============================

.. contents:: Содержание
   :depth: 2
   :local:

Системные требования
----------------------

- Python 3.8+
- Docker
- Учетная запись Google Cloud для работы с Google Sheets
- Учетная запись VK для работы с VK API

Установка зависимостей
-----------------------

1. Клонируйте репозиторий:

.. code-block:: bash

   git clone https://github.com/MrAndrew30/LinksGenerator
   cd links_generator

2. Создайте и активируйте виртуальное окружение:

.. code-block:: bash

   python -m venv .venv
   source .venv/bin/activate  # Linux/MacOS
   .\.venv\Scripts\activate   # Windows

3. Установите зависимости:

.. code-block:: bash

   pip install -r requirements.txt

Настройка окружения
-------------------

1. Создайте файл `.env` в корне проекта:

.. code-block:: bash

   cp .env_example .env

2. Заполните необходимые переменные:

.. code-block:: text

   # Telegram
   BOT_TOKEN=your_telegram_bot_token_here

   # Google Sheets
   GOOGLE_TABLE_ID=your_table_id_here

   # VK API
   VK_API_TOKEN=your_vk_token_here

3. Поместите файл `credentials.json` в корень проекта (полученный из Google Cloud Console)

Запуск приложения
-----------------

Способ 1: ...



Проверка установки
------------------

После запуска проверьте:

1. Бот должен ответить на команду `/start`
2. В Google Sheets должны создаться новые таблицы при выполнении `/create_table`
3. Логи должны отображаться в файле `py_log.log`

Устранение неполадок
--------------------

Если возникли проблемы:

1. Проверьте наличие файла `credentials.json` в корне проекта
2. Убедитесь, что все переменные окружения установлены правильно
3. Проверьте логи:

.. code-block:: bash

   tail py_log.log
