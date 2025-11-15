#!/usr/bin/env python3
import configparser
import os
import sys
import json
import urllib.request
import urllib.error
from collections import deque


class ConfigError(Exception):
    """Кастомное исключение для ошибок конфигурации"""
    pass


class DependencyError(Exception):
    """Кастомное исключение для ошибок получения зависимостей"""
    pass


class GraphError(Exception):
    """Кастомное исключение для ошибок работы с графом"""
    pass


class DependencyVisualizer:
    def __init__(self, config_path, graph_file_path=None):
        self.config_path = config_path
        self.graph_file_path = graph_file_path
        self.config = configparser.ConfigParser()
        self.settings = {}
        self.dependencies = {}
        self.dependency_graph = {}
        self.cycles_detected = []

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

        # Тестовый режим
        if 'test_mode' in repository_section:
            test_mode_str = repository_section['test_mode'].strip().lower()
            self.settings['test_mode'] = test_mode_str in ('true', '1', 'yes')
        else:
            self.settings['test_mode'] = True

    def load_graph_from_file(self):
        """Загрузка графа из текстового файла"""
        try:
            if not os.path.exists(self.graph_file_path):
                raise GraphError(f"Файл графа '{self.graph_file_path}' не найден")

            graph_data = {}

            with open(self.graph_file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue

                    if ':' not in line:
                        raise GraphError(f"Неверный формат в строке {line_num}: {line}")

                    package, deps_str = line.split(':', 1)
                    package = package.strip()

                    # Проверяем что пакет состоит из больших латинских букв
                    if not package.isupper() or not package.isalpha():
                        raise GraphError(f"Имя пакета '{package}' должно состоять только из больших латинских букв")

                    # Обрабатываем зависимости
                    dependencies = []
                    if deps_str.strip():
                        for dep in deps_str.split(','):
                            dep = dep.strip()
                            if dep:
                                # Проверяем что зависимость состоит из больших латинских букв
                                if not dep.isupper() or not dep.isalpha():
                                    raise GraphError(
                                        f"Имя зависимости '{dep}' должно состоять только из больших латинских букв")
                                dependencies.append(dep)

                    graph_data[package] = dependencies

            return graph_data

        except Exception as e:
            raise GraphError(f"Ошибка чтения файла графа: {e}")

    def build_dependency_graph_dfs(self, start_package):
        """Построение графа зависимостей с помощью DFS без рекурсии"""
        if start_package not in self.dependency_graph:
            return {}, []

        stack = [(start_package, [start_package], 0)]  # (current_node, path, depth)
        visited = set()
        full_graph = {}
        cycles = []

        while stack:
            current_node, path, depth = stack.pop()

            if current_node not in visited:
                visited.add(current_node)
                # Инициализируем список зависимостей для текущего узла
                full_graph[current_node] = []

                # Получаем зависимости текущего узла из исходного графа
                if current_node in self.dependency_graph:
                    for dependency in self.dependency_graph[current_node]:
                        # Добавляем зависимость без версии
                        full_graph[current_node].append(dependency)

                        # Проверка на циклы
                        if dependency in path:
                            cycle = path[path.index(dependency):] + [dependency]
                            cycles.append(cycle)
                        elif dependency not in visited:
                            # Добавляем зависимость в стек для дальнейшего обхода
                            stack.append((dependency, path + [dependency], depth + 1))

        return full_graph, cycles

    def get_dependencies(self):
        """Основной метод получения зависимостей"""
        if self.graph_file_path:
            self.dependency_graph = self.load_graph_from_file()

            # Автоматически используем первый пакет из графа если указанный не найден
            if self.settings['package_name'] not in self.dependency_graph:
                available_packages = list(self.dependency_graph.keys())
                if available_packages:
                    self.settings['package_name'] = available_packages[0]
            return {}
        else:
            return self.get_dependencies_from_npm()

    def display_settings(self):
        """Вывод параметров конфигурации"""
        print("Параметры конфигурации:")
        print(f"Пакет: {self.settings['package_name']}")
        print(f"Репозиторий: {self.graph_file_path if self.graph_file_path else self.settings['repository_url']}")
        print(f"Тестовый режим: {self.settings['test_mode']}")
        print(f"Версия: {self.settings['package_version']}")
        print(f"Выходной файл: {self.settings['output_file']}")
        print()

    def display_dependency_graph(self):
        """Вывод графа зависимостей"""
        print(f"Построение графа зависимостей для: {self.settings['package_name']}")
        print()

        start_package = self.settings['package_name']
        full_graph, cycles = self.build_dependency_graph_dfs(start_package)

        print("Граф зависимостей:")
        for package in sorted(full_graph.keys()):
            dependencies = full_graph[package]
            print(f"{package} -> {dependencies}")

        print()
        print("Статистика:")
        total_packages = len(full_graph)
        total_dependencies = sum(len(deps) for deps in full_graph.values())
        print(f"Всего пакетов: {total_packages}")
        print(f"Всего зависимостей: {total_dependencies}")

    def run(self):
        """Основной метод запуска приложения"""
        try:
            self.load_config()
            self.display_settings()
            self.dependencies = self.get_dependencies()
            self.display_dependency_graph()

        except (ConfigError, DependencyError, GraphError) as e:
            print(f"Ошибка: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")
            sys.exit(1)


def main():
    # Обрабатываем аргументы командной строки
    config_path = 'config.ini'
    graph_file_path = None

    for arg in sys.argv[1:]:
        if arg.endswith('.ini'):
            config_path = arg
        elif arg.endswith('.txt'):
            graph_file_path = arg

    visualizer = DependencyVisualizer(config_path, graph_file_path)
    visualizer.run()


if __name__ == "__main__":
    main()