#!/usr/bin/env python3
import configparser
import os
import sys


class ConfigError(Exception):
    """Кастомное исключение для ошибок конфигурации"""
    pass


class DependencyVisualizer:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = configparser.ConfigParser()
        self.settings = {}

    def load_config(self):
        """Загрузка и валидация конфигурации"""
        try:
            # Проверка существования файла конфигурации
            if not os.path.exists(self.config_path):
                raise ConfigError(f"Конфигурационный файл '{self.config_path}' не найден")

            # Чтение конфигурации
            self.config.read(self.config_path, encoding='utf-8')

            # Проверка наличия обязательных секций
            if not self.config.has_section('package'):
                raise ConfigError("Отсутствует обязательная секция 'package' в конфигурации")
            if not self.config.has_section('repository'):
                raise ConfigError("Отсутствует обязательная секция 'repository' в конфигурации")

            # Загрузка и валидация всех параметров
            self._load_package_settings()
            self._load_repository_settings()

        except configparser.Error as e:
            raise ConfigError(f"Ошибка парсинга конфигурационного файла: {e}")
        except Exception as e:
            raise ConfigError(f"Неожиданная ошибка при загрузке конфигурации: {e}")

    def _load_package_settings(self):
        """Загрузка и валидация настроек пакета"""
        package_section = self.config['package']

        # Имя пакета
        if 'name' not in package_section:
            raise ConfigError("Отсутствует обязательный параметр 'name' в секции 'package'")
        self.settings['package_name'] = package_section['name'].strip()
        if not self.settings['package_name']:
            raise ConfigError("Имя пакета не может быть пустым")

        # Версия пакета
        if 'version' not in package_section:
            raise ConfigError("Отсутствует обязательный параметр 'version' в секции 'package'")
        self.settings['package_version'] = package_section['version'].strip()
        if not self.settings['package_version']:
            raise ConfigError("Версия пакета не может быть пустой")

        # Имя выходного файла
        if 'output_file' not in package_section:
            raise ConfigError("Отсутствует обязательный параметр 'output_file' в секции 'package'")
        self.settings['output_file'] = package_section['output_file'].strip()
        if not self.settings['output_file']:
            raise ConfigError("Имя выходного файла не может быть пустым")

    def _load_repository_settings(self):
        """Загрузка и валидация настроек репозитория"""
        repository_section = self.config['repository']

        # URL репозитория или путь к файлу
        if 'url' not in repository_section:
            raise ConfigError("Отсутствует обязательный параметр 'url' в секции 'repository'")
        self.settings['repository_url'] = repository_section['url'].strip()
        if not self.settings['repository_url']:
            raise ConfigError("URL репозитория не может быть пустым")

        # Режим тестового репозитория
        if 'test_mode' not in repository_section:
            raise ConfigError("Отсутствует обязательный параметр 'test_mode' в секции 'repository'")

        test_mode_str = repository_section['test_mode'].strip().lower()
        if test_mode_str not in ('true', 'false', '1', '0', 'yes', 'no'):
            raise ConfigError("Параметр 'test_mode' должен быть 'true' или 'false'")

        self.settings['test_mode'] = test_mode_str in ('true', '1', 'yes')

    def display_settings(self):
        """Вывод всех настроек в формате ключ-значение"""
        print("=== НАСТРОЙКИ ПРИЛОЖЕНИЯ ===")
        print(f"Конфигурационный файл: {self.config_path}")
        print("\n--- Параметры пакета ---")
        print(f"Имя анализируемого пакета: {self.settings['package_name']}")
        print(f"Версия пакета: {self.settings['package_version']}")
        print(f"Имя сгенерированного файла с изображением графа: {self.settings['output_file']}")

        print("\n--- Параметры репозитория ---")
        print(f"URL-адрес репозитория или путь к файлу тестового репозитория: {self.settings['repository_url']}")
        print(f"Режим работы с тестовым репозиторием: {self.settings['test_mode']}")
        print("\n=============================")

    def run(self):
        """Основной метод запуска приложения"""
        try:
            self.load_config()

            # Вывод всех настроек (требование этапа 3)
            self.display_settings()

        except ConfigError as e:
            print(f"Ошибка конфигурации: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")
            sys.exit(1)


def main():

    # Определяем путь к конфигурационному файлу
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else:
        # Если файл не указан, используем config.ini по умолчанию
        config_path = 'test_configs/config.ini'

    visualizer = DependencyVisualizer(config_path)
    visualizer.run()


if __name__ == "__main__":
    main()