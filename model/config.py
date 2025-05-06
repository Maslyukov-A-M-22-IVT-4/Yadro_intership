from pathlib import Path


class AppConfig:
    """Управление путями к файлам приложения"""

    INPUT_DIR = Path('input')
    OUTPUT_DIR = Path('out')

    _INPUT_MAPPING = {
        'xml': 'impulse_test_input.xml',
        'config': 'config.json',
        'patched_config': 'patched_config.json'
    }

    _OUTPUT_MAPPING = {
        'config': 'config.xml',
        'meta': 'meta.json',
        'delta': 'delta.json',
        'result': 'res_patched_config.json'
    }

    @classmethod
    def get_input_path(cls, file_type: str) -> Path:
        """Полный путь к входному файлу"""
        if file_type not in cls._INPUT_MAPPING:
            raise ValueError(f"Неизвестный тип файла: {file_type}")
        return cls.INPUT_DIR / cls._INPUT_MAPPING[file_type]

    @classmethod
    def get_output_path(cls, file_type: str) -> Path:
        """Полный путь к выходному файлу"""
        if file_type not in cls._OUTPUT_MAPPING:
            raise ValueError(f"Неизвестный тип файла: {file_type}")
        return cls.OUTPUT_DIR / cls._OUTPUT_MAPPING[file_type]

    @classmethod
    def validate_input_files(cls) -> bool:
        """Проверка наличия входных файлов"""
        try:
            return all(
                cls.get_input_path(ft).exists()
                for ft in cls._INPUT_MAPPING
            )
        except (ValueError, OSError):
            return False
