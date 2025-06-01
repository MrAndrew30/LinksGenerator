import sqlite3


class DatabaseManager:
    """Менеджер базы данных SQLite для управления пользователями и их ролями.

    Обеспечивает взаимодействие с базой данных для выполнения операций:
    - Создание и инициализация структуры БД
    - Управление пользователями (добавление, проверка существования)
    - Управление ролями (назначение/снятие прав администратора)

    Attributes:
        path (str): Путь к файлу базы данных
        connection (sqlite3.Connection): Активное соединение с БД
    """

    def __init__(self, path):
        """Инициализирует соединение с базой данных и создает структуру таблиц.

        Args:
            path (str): Путь к файлу базы данных SQLite
        """
        self.path = path
        self.connection = sqlite3.connect(self.path)
        self.create_db()

    def __del__(self):
        """Закрывает соединение с базой данных при уничтожении объекта."""
        self.connection.close()

    def create_db(self):
        """Создает структуру базы данных при первом запуске.

        Создает таблицы:
        - role: Справочник ролей пользователей
        - users: Таблица зарегистрированных пользователей

        Добавляет стандартные роли (admin, user) при их отсутствии.
        """
        conn = self.connection
        cur = conn.cursor()

        cur.execute("PRAGMA foreign_keys = ON")

        cur.execute("""CREATE TABLE IF NOT EXISTS role (
                        id_role integer NOT NULL PRIMARY KEY,
                        role_name varchar(500) NOT NULL UNIQUE
                        )""")

        cur.execute("""CREATE TABLE IF NOT EXISTS users (
                        id integer PRIMARY KEY AUTOINCREMENT,
                        tg_id integer NOT NULL UNIQUE,
                        id_role integer NOT NULL,
                        FOREIGN KEY (id_role) REFERENCES role(id_role)
                        )""")

        default_roles = [(1, 'admin'), (2, 'user')]
        cur.executemany(
            "INSERT OR IGNORE INTO role (id_role, role_name) VALUES (?, ?)",
            default_roles
        )
        conn.commit()

    def user_exists(self, tg_id: int) -> bool:
        """Проверяет существование пользователя в базе данных.

        Args:
            tg_id (int): Telegram ID пользователя для проверки

        Returns:
            bool: True если пользователь существует, иначе False
        """
        cur = self.connection.cursor()
        cur.execute("SELECT 1 FROM users WHERE tg_id = ?", (tg_id,))
        return cur.fetchone() is not None

    def add_user(self, tg_id: int, role_name: str = "user") -> bool:
        """Добавляет нового пользователя в базу данных.

        Args:
            tg_id (int): Telegram ID пользователя
            role_name (str, optional): Название роли. По умолчанию "user".

        Returns:
            bool: True при успешном добавлении, False если пользователь уже существует
                  или произошла ошибка

        Raises:
            ValueError: Если указанная роль не найдена в базе
        """
        if self.user_exists(tg_id):
            return False

        try:
            cur = self.connection.cursor()

            cur.execute(
                "SELECT id_role FROM role WHERE role_name = ?",
                (role_name,)
            )
            role_data = cur.fetchone()

            if not role_data:
                raise ValueError(f"Роль '{role_name}' не найдена")

            cur.execute(
                "INSERT INTO users (tg_id, id_role) VALUES (?, ?)",
                (tg_id, role_data[0])
            )
            self.connection.commit()
            return True

        except sqlite3.Error as e:
            print(f"Ошибка при добавлении пользователя: {e}")
            return False

    def add_admin(self, tg_id: int) -> bool:
        """Назначает пользователя администратором.

        Args:
            tg_id (int): Telegram ID пользователя

        Returns:
            bool: True при успешном обновлении, False при ошибке

        Note:
            Пользователь должен существовать в базе данных
        """
        try:
            cur = self.connection.cursor()

            cur.execute("SELECT id_role FROM role WHERE role_name = 'admin'")
            admin_role_id = cur.fetchone()

            admin_role_id = admin_role_id[0]
            cur.execute(
                "UPDATE users SET id_role = ? WHERE tg_id = ?",
                (admin_role_id, tg_id)
            )
            self.connection.commit()
            return True

        except sqlite3.Error as e:
            print(f"Ошибка при назначении администратора: {e}")
            return False

    def is_admin(self, tg_id: int) -> bool:
        """Проверяет наличие прав администратора у пользователя.

        Args:
            tg_id (int): Telegram ID пользователя

        Returns:
            bool: True если пользователь является администратором,
                  False если нет или пользователь не существует
        """
        cur = self.connection.cursor()
        cur.execute("""
            SELECT 1 FROM users u
            JOIN role r ON u.id_role = r.id_role
            WHERE u.tg_id = ? AND r.role_name = 'admin'
        """, (tg_id,))
        return cur.fetchone() is not None

    def remove_admin(self, tg_id: int) -> bool:
        """Снимает права администратора с пользователя.

        Args:
            tg_id (int): Telegram ID пользователя

        Returns:
            bool: True при успешном обновлении, False при ошибке

        Note:
            Пользователь должен существовать в базе данных
        """
        try:
            cur = self.connection.cursor()

            cur.execute("SELECT id_role FROM role WHERE role_name = 'user'")
            admin_role_id = cur.fetchone()

            admin_role_id = admin_role_id[0]
            cur.execute(
                "UPDATE users SET id_role = ? WHERE tg_id = ?",
                (admin_role_id, tg_id)
            )
            self.connection.commit()
            return True

        except sqlite3.Error as e:
            print(f"Ошибка при удалении администратора: {e}")
            return False
