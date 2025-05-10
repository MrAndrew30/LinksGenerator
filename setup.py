from setuptools import setup, find_packages
from distutils.cmd import Command
import os
import subprocess


class BuildDocsCommand(Command):
    """Кастомная команда для сборки документации Sphinx.

    Attributes:
        description (str): Описание команды.
        user_options (list): Список опций команды.
    """
    description = 'Build Sphinx documentation'
    user_options = []

    def initialize_options(self):
        """Инициализирует опции команды.

        Реализация обязательного метода из базового класса Command.
        """
        pass

    def finalize_options(self):
        """Финализирует опции команды.

        Реализация обязательного метода из базового класса Command.
        """
        pass

    def run(self):
        """Выполняет сборку документации.

        Генерирует документацию с помощью sphinx-apidoc и собирает HTML версию.

        Raises:
            ImportError: Если Sphinx не установлен.
            subprocess.CalledProcessError: Если выполнение команды завершилось ошибкой.
        """
        try:
            import sphinx
        except ImportError:
            raise ImportError(
                "Sphinx is required to build documentation. "
                "Install with: pip install sphinx sphinx-rtd-theme"
            )

        docs_dir = os.path.abspath(os.path.join(
            os.path.dirname(__file__), 'docs'))
        source_dir = os.path.join(docs_dir, 'source')
        modules_dir = os.path.join(source_dir, 'modules')

        # Очищаем предыдущую документацию
        if os.path.exists(modules_dir):
            for f in os.listdir(modules_dir):
                if f.endswith('.rst'):
                    os.remove(os.path.join(modules_dir, f))

        # Генерация документации для всего пакета
        subprocess.check_call([
            'sphinx-apidoc',
            '-o', modules_dir,
            os.path.abspath('links_generator'),
            '--force',
            '--separate',
            '--module-first',
            '--templatedir=' + os.path.join(source_dir, '_templates')
        ])

        # Удаляем некоторые автоматически созданные файлы
        files_to_remove = [
            'modules.rst',
            'links_generator.rst',
            'links_generator.googletables.rst',
            'links_generator.vk_api.rst'
        ]
        for filename in files_to_remove:
            filepath = os.path.join(modules_dir, filename)
            if os.path.exists(filepath):
                os.remove(filepath)

        # Сборка HTML документации
        subprocess.check_call(
            ['sphinx-build', '-b', 'html', source_dir,
                os.path.join(docs_dir, 'build/html')],
            cwd=docs_dir
        )


setup(
    name="links_generator",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        line.strip() for line in open("requirements.txt")
        if line.strip() and not line.startswith("#")
    ],
    entry_points={
        "console_scripts": ["run-bot=links_generator.main:main"]
    },
    cmdclass={
        'build_docs': BuildDocsCommand,
    },
    extras_require={
        'docs': [
            'sphinx>=4.0',
            'sphinx-rtd-theme>=0.5',
            'sphinx-autodoc-typehints>=1.0',
        ],
    },
)
