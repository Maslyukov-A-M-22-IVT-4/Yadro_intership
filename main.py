import json
import logging
from model.parser import ModelParser
from model.config_processor import ConfigProcessor
from model.config import AppConfig
from model.exceptions import ModelError, ConfigError


def setup_logging():
    """Настройка логирования с гарантированным выводом в консоль и файл"""
    logger = logging.getLogger()

    # Если логгер уже настроен - только проверим обработчики
    if logger.handlers:
        # Проверяем наличие консольного обработчика
        has_console = any(
            isinstance(h, logging.StreamHandler)
            and not isinstance(h, logging.FileHandler)
            for h in logger.handlers
        )

        # Проверяем наличие файлового обработчика
        has_file = any(
            isinstance(h, logging.FileHandler)
            for h in logger.handlers
        )

        # Добавляем недостающие обработчики
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        if not has_console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        if not has_file:
            file_handler = logging.FileHandler('app.log', mode='a', encoding='utf-8')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        return

    # Первоначальная настройка логгера
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Консольный вывод
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Файловый вывод (режим 'a' - добавление в существующий файл)
    file_handler = logging.FileHandler('app.log', mode='a', encoding='utf-8')
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


def ensure_dirs():
    """Создание директорий если их нет"""
    try:
        AppConfig.INPUT_DIR.mkdir(parents=True, exist_ok=True)
        AppConfig.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        logging.info(f"Директории созданы/проверены: {AppConfig.INPUT_DIR}, {AppConfig.OUTPUT_DIR}")
    except PermissionError as e:
        error_msg = f"Нет прав на создание директорий: {e}"
        logging.error(error_msg)
        raise PermissionError(error_msg) from e
    except OSError as e:
        error_msg = f"Ошибка файловой системы при создании директорий: {e}"
        logging.error(error_msg)
        raise OSError(error_msg) from e
    except Exception as e:
        error_msg = f"Неожиданная ошибка при создании директорий: {e}"
        logging.error(error_msg)
        raise RuntimeError(error_msg) from e


def main():
    """Основная функция"""
    setup_logging()
    logging.info("=" * 50)
    logging.info("Запуск программы")

    try:
        ensure_dirs()

        # Проверка входных файлов
        required_files = {
            'xml': AppConfig.get_input_path('xml'),
            'config': AppConfig.get_input_path('config'),
            'patched_config': AppConfig.get_input_path('patched_config')
        }

        missing = [str(f) for f in required_files.values() if not f.exists()]
        if missing:
            raise FileNotFoundError(f"Отсутствуют файлы: {', '.join(missing)}")

        # Обработка модели
        parser = ModelParser(str(required_files['xml']))
        parser.parse()

        # Генерация выходных файлов
        with open(str(AppConfig.get_output_path('config')), 'w', encoding='utf-8') as f:
            f.write(parser.generate_config_xml())

        with open(str(AppConfig.get_output_path('meta')), 'w', encoding='utf-8') as f:
            json.dump(parser.generate_meta_json(), f, indent=4, ensure_ascii=False)

        # Обработка конфигов
        processor = ConfigProcessor()
        original = processor.load_config(str(required_files['config']))
        patched = processor.load_config(str(required_files['patched_config']))

        delta = processor.generate_delta(original, patched)
        processor.save_config(delta, str(AppConfig.get_output_path('delta')))

        result = processor.apply_delta(original, delta)
        processor.save_config(result, str(AppConfig.get_output_path('result')))

        logging.info("Программа завершена успешно")
        return 0

    except FileNotFoundError as e:
        logging.error(f"Ошибка: {e}")
    except ConfigError as e:
        logging.error(f"Ошибка конфигурации: {e}")
    except ModelError as e:
        logging.error(f"Ошибка модели: {e}")
    except Exception as e:
        logging.error(f"Критическая ошибка: {e}", exc_info=True)

    logging.info("=" * 50)
    return 1


if __name__ == '__main__':
    exit(main())
