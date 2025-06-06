# LinksGenerator
Проект по разработке телеграм бота для генерации коротких ссылок. Полезен для анализа трафика от разных партнеров.


## Генерация файла credentials.json

Чтобы редактировать Google Таблицу через Python-скрипт, необходимо использовать Google Sheets API:

1. <b>Включите Google Sheets API</b>
- Перейдите в [Google Cloud Console](https://console.cloud.google.com/).

- Создайте новый проект или выберите существующий.

- В меню слева выберите "APIs & Services" → "Library".

- Найдите Google Sheets API и включите его.

- Также можно включить Google Drive API (если необходимо управлять доступом к файлам).

2. <b>Создайте учетные данные (Credentials)</b>
- В Google Cloud Console перейдите в "APIs & Services" → "Credentials".

- Нажмите "Create Credentials" → "Service Account".

- Заполните данные (название аккаунта, описание).

- Назначьте роль (например, Editor для редактирования таблиц).

- Нажмите "Create Key", выберите JSON и скачайте файл с ключами.

- Сохраните email сервисного аккаунта (вида ваш-аккаунт@ваш-проект.iam.gserviceaccount.com).

3. <b>Добавьте сервисный аккаунт в редакторы таблицы</b>
- Откройте нужную Google Таблицу.

- Нажмите "Share" (в правом верхнем углу).

- В поле "Add people and groups" введите email сервисного аккаунта.

- Выберите уровень доступа (например, Editor).

## Генерация ключа для VK-API
Создайте [приложение VK](https://vk.com/apps?act=manage)
- Нажмите "Создать приложение"

- Выберите тип приложения "Standalone"

- Скопируйте сервисный ключ доступа



## Запуск приложения
docker-compose build --no-cache
docker-compose up 

docker-compose down --rmi all - Удалить предыдущие сборки
