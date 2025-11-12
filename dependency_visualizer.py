#!/usr/bin/env python3
import configparser
import os
import sys
import json
import urllib.request
import urllib.error


class ConfigError(Exception):
    """Кастомное исключение для ошибок конфигурации"""
    pass


class DependencyError(Exception):
    """Кастомное исключение для ошибок получения зависимостей"""
    pass


class DependencyVisualizer:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = configparser.ConfigParser()
        self.settings = {}
        self.dependencies = {}

    def load_config(self):
        """Загрузка и валидация конфигурации"""
        try:
            if not os.path.exists(self.config_path):
                raise ConfigError(f"Конфигурационный файл '{self.config_path}' не найден")

            self.config.read(self.config_path, encoding='utf-8')

            if not self.config.has_section('package'):
                raise ConfigError("Отсутствует обязательная секция 'package' в конфигурации")
            if not self.config.has_section('repository'):
                raise ConfigError("Отсутствует обязательная секция 'repository' в конфигурации")

            self._load_package_settings()
            self._load_repository_settings()

        except configparser.Error as e:
            raise ConfigError(f"Ошибка парсинга конфигурационного файла: {e}")
        except Exception as e:
            raise ConfigError(f"Неожиданная ошибка при загрузке конфигурации: {e}")

    def _load_package_settings(self):
        """Загрузка и валидация настроек пакета"""
        package_section = self.config['package']

        if 'name' not in package_section:
            raise ConfigError("Отсутствует обязательный параметр 'name' в секции 'package'")
        self.settings['package_name'] = package_section['name'].strip()
        if not self.settings['package_name']:
            raise ConfigError("Имя пакета не может быть пустым")

        if 'version' not in package_section:
            raise ConfigError("Отсутствует обязательный параметр 'version' в секции 'package'")
        self.settings['package_version'] = package_section['version'].strip()
        if not self.settings['package_version']:
            raise ConfigError("Версия пакета не может быть пустой")

        if 'output_file' not in package_section:
            raise ConfigError("Отсутствует обязательный параметр 'output_file' в секции 'package'")
        self.settings['output_file'] = package_section['output_file'].strip()
        if not self.settings['output_file']:
            raise ConfigError("Имя выходного файла не может быть пустым")

    def _load_repository_settings(self):
        """Загрузка и валидация настроек репозитория"""
        repository_section = self.config['repository']

        if 'url' not in repository_section:
            raise ConfigError("Отсутствует обязательный параметр 'url' в секции 'repository'")
        self.settings['repository_url'] = repository_section['url'].strip()
        if not self.settings['repository_url']:
            raise ConfigError("URL репозитория не может быть пустым")

    def get_dependencies(self):
        """Получение зависимостей из npm registry"""
        try:
            package_name = self.settings['package_name']
            package_version = self.settings['package_version']
            registry_url = self.settings['repository_url']

            # Формируем URL для запроса к npm registry
            url = f"{registry_url}/{package_name}/{package_version}"

            print(f"Запрос к npm registry: {url}")

            # Выполняем HTTP запрос
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode('utf-8'))

            # Извлекаем зависимости
            dependencies = data.get('dependencies', {})

            return dependencies

        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise DependencyError(f"Пакет {package_name}@{package_version} не найден в registry")
            else:
                raise DependencyError(f"Ошибка HTTP при запросе к registry: {e.code}")
        except urllib.error.URLError as e:
            raise DependencyError(f"Ошибка подключения к registry: {e.reason}")
        except Exception as e:
            raise DependencyError(f"Неожиданная ошибка при получении зависимостей: {e}")

    def display_dependencies(self):
        """Вывод прямых зависимостей (требование этапа 4)"""
        print("\n=== ПРЯМЫЕ ЗАВИСИМОСТИ ПАКЕТА ===")
        print(f"Пакет: {self.settings['package_name']}@{self.settings['package_version']}")

        if not self.dependencies:
            print("Зависимости не найдены")
            return

        print("\nСписок прямых зависимостей:")
        for dep_name, dep_version in self.dependencies.items():
            print(f"  - {dep_name}: {dep_version}")
        print(f"\nВсего зависимостей: {len(self.dependencies)}")

    def display_settings(self):
        """Вывод всех настроек в формате ключ-значение"""
        print("=== НАСТРОЙКИ ПРИЛОЖЕНИЯ ===")
        print(f"Конфигурационный файл: {self.config_path}")
        print("\n--- Параметры пакета ---")
        print(f"Имя анализируемого пакета: {self.settings['package_name']}")
        print(f"Версия пакета: {self.settings['package_version']}")
        print(f"Имя сгенерированного файла с изображением графа: {self.settings['output_file']}")

        print("\n--- Параметры репозитория ---")
        print(f"URL-адрес репозитория: {self.settings['repository_url']}")
        print("\n=============================")

    def run(self):
        """Основной метод запуска приложения"""
        try:
            self.load_config()
            self.display_settings()

            # Получение зависимостей (этап 2)
            print("\nПолучение информации о зависимостях...")
            self.dependencies = self.get_dependencies()

            # Вывод зависимостей (требование этапа 4)
            self.display_dependencies()

        except (ConfigError, DependencyError) as e:
            print(f"Ошибка: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")
            sys.exit(1)


def main():
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else:
        config_path = 'config.ini'

    visualizer = DependencyVisualizer(config_path)
    visualizer.run()


if __name__ == "__main__":
    main()