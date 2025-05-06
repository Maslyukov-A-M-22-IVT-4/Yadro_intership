import json
import logging
from typing import Dict, Any
from .types import Delta, DeltaOperation, ConfigDict
from .exceptions import ConfigError, ConfigValidationError

logger = logging.getLogger(__name__)


class ConfigProcessor:
    """Обработчик конфигурационных JSON-файлов"""

    @staticmethod
    def load_config(file_path: str) -> ConfigDict:
        """
        Загружает конфигурацию из JSON-файла
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if not isinstance(config, dict):
                    raise ConfigValidationError("Конфигурация должна быть JSON-объектом")
                return config
        except json.JSONDecodeError as e:
            raise ConfigError(f"Ошибка декодирования JSON в файле {file_path}: {e}") from e
        except OSError as e:
            raise ConfigError(f"Ошибка доступа к файлу {file_path}: {e}") from e

    @staticmethod
    def save_config(config: Dict[str, Any], file_path: str) -> None:
        """
        Сохраняет конфигурацию в JSON-файл

        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except OSError as e:
            raise ConfigError(f"Ошибка записи в файл {file_path}: {e}") from e

    @staticmethod
    def generate_delta(original: ConfigDict, patched: ConfigDict) -> Delta:
        """
        Вычисляет разницу между двумя версиями конфигурации
        """
        additions = [
            {"key": k, "value": v, "from_": None, "to": None}
            for k, v in patched.items()
            if k not in original
        ]

        deletions = [k for k in original if k not in patched]

        updates = [
            {"key": k, "value": None, "from_": original[k], "to": patched[k]}
            for k in original
            if k in patched and original[k] != patched[k]
        ]

        return {
            "additions": additions,
            "deletions": deletions,
            "updates": updates
        }

    @staticmethod
    def apply_delta(original: ConfigDict, delta: Delta) -> ConfigDict:
        """
        Применяет изменения к исходной конфигурации
        """
        result = original.copy()

        # Удаляем удаленные ключи
        for key in delta["deletions"]:
            result.pop(key, None)

        # Обновляем измененные значения
        for update in delta["updates"]:
            result[update["key"]] = update["to"]

        # Добавляем новые параметры
        result.update({a["key"]: a["value"] for a in delta["additions"]})

        return result
