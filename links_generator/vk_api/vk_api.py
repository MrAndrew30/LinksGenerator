import requests


class VKLinkManager:
    """Менеджер для работы с API VK по сокращению ссылок и получению статистики.

    Позволяет:
    - Создавать короткие ссылки через VK API
    - Получать статистику переходов по коротким ссылкам

    Attributes:
        service_token (str): Сервисный ключ доступа VK API
    """

    def __init__(self, service_token):
        """Инициализирует экземпляр VKLinkManager.

        Args:
            service_token (str): Сервисный ключ доступа из настроек приложения VK.
        """
        self.service_token = service_token

    def get_short_link(self, long_url, private=False):
        """Создает короткую ссылку через VK API.

        Args:
            long_url (str): Длинный URL, который нужно сократить.
            private (bool, optional): Флаг создания приватной ссылки. Defaults to False.

        Returns:
            str | None: Короткая ссылка в формате 'vk.cc/XXXXX' или None в случае ошибки.

        Examples:
            >>> vk_manager = VKLinkManager('service_token')
            >>> vk_manager.get_short_link('https://example.com')
            'https://vk.cc/XXXXX'
        """
        api_url = "https://api.vk.com/method/utils.getShortLink"
        params = {
            "access_token": self.service_token,
            "url": long_url,
            "private": 1 if private else 0,
            "v": "5.131"
        }

        try:
            response = requests.get(api_url, params=params)
            data = response.json()

            if "response" in data:
                return data["response"]["short_url"]

            error_msg = data.get("error", {}).get("error_msg", "Unknown error")
            print(f"VK API Error: {error_msg}")
            return None

        except Exception as e:
            print(f"Request Error: {e}")
            return None

    def get_link_stats(self, short_url, interval="day"):
        """Получает статистику переходов по короткой ссылке VK.

        Args:
            short_url (str): Короткая ссылка в формате 'vk.cc/XXXXX' или полный URL.
            interval (str, optional): Период агрегации статистики. 
                Допустимые значения: 'day', 'week', 'month', 'forever'. Defaults to 'day'.

        Returns:
            dict | None: Словарь с данными статистики или None в случае ошибки.

        Raises:
            ValueError: Если передан недопустимый интервал.

        Examples:
            >>> vk_manager = VKLinkManager('service_token')
            >>> stats = vk_manager.get_link_stats('https://vk.cc/XXXXX')
            >>> print(stats)
            {'key': 'XXXXX', 'stats': [...]}
        """
        valid_intervals = ["day", "week", "month", "forever"]
        if interval not in valid_intervals:
            raise ValueError(
                f"Invalid interval. Must be one of {valid_intervals}")

        api_url = "https://api.vk.com/method/utils.getLinkStats"
        params = {
            "access_token": self.service_token,
            "key": short_url.replace("https://vk.cc/", "").replace("http://vk.cc/", ""),
            "interval": interval,
            "v": "5.131"
        }

        try:
            response = requests.get(api_url, params=params)
            data = response.json()

            if "response" in data:
                return data["response"]

            error_msg = data.get("error", {}).get("error_msg", "Unknown error")
            print(f"VK API Error: {error_msg}")
            return None

        except Exception as e:
            print(f"Request Error: {e}")
            return None
