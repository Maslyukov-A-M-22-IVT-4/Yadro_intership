import unittest
import os
import tempfile
from pathlib import Path

from main import ensure_dirs
from model.config import AppConfig


class TestAppConfig(unittest.TestCase):
    def setUp(self):
        # Создаем временную директорию для тестов
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_input = AppConfig.INPUT_DIR
        self.original_output = AppConfig.OUTPUT_DIR
        AppConfig.INPUT_DIR = Path(self.temp_dir.name) / "input"
        AppConfig.OUTPUT_DIR = Path(self.temp_dir.name) / "out"
        os.makedirs(AppConfig.INPUT_DIR, exist_ok=True)
        os.makedirs(AppConfig.OUTPUT_DIR, exist_ok=True)

    def tearDown(self):
        self.temp_dir.cleanup()
        AppConfig.INPUT_DIR = self.original_input
        AppConfig.OUTPUT_DIR = self.original_output

    def test_path_generation(self):
        # Создаем тестовые файлы
        test_files = {
            'xml': 'impulse_test_input.xml',
            'config': 'config.json',
            'patched_config': 'patched_config.json'
        }

        for file in test_files.values():
            (AppConfig.INPUT_DIR / file).touch()

        # Проверяем пути (используем os.path для кроссплатформенности)
        xml_path = AppConfig.get_input_path('xml')
        expected_path = os.path.join('input', 'impulse_test_input.xml')
        self.assertTrue(str(xml_path).endswith(expected_path) or
                        str(xml_path).endswith(expected_path.replace('/', '\\')))

        meta_path = AppConfig.get_output_path('meta')
        expected_meta_path = os.path.join('out', 'meta.json')
        self.assertTrue(str(meta_path).endswith(expected_meta_path) or
                        str(meta_path).endswith(expected_meta_path.replace('/', '\\')))

    def test_validate_input_files(self):
        # Сначала проверяем, что файлов нет
        self.assertFalse(AppConfig.validate_input_files())

        # Создаем тестовые файлы
        test_files = {
            'xml': 'impulse_test_input.xml',
            'config': 'config.json',
            'patched_config': 'patched_config.json'
        }

        for file in test_files.values():
            (AppConfig.INPUT_DIR / file).touch()

        # Теперь проверяем, что файлы есть
        self.assertTrue(AppConfig.validate_input_files())

    def test_ensure_dirs(self):
        """Тест создания директорий"""
        # Удаляем директории если существуют
        if AppConfig.INPUT_DIR.exists():
            AppConfig.INPUT_DIR.rmdir()
        if AppConfig.OUTPUT_DIR.exists():
            AppConfig.OUTPUT_DIR.rmdir()

        # Проверяем создание
        ensure_dirs()
        self.assertTrue(AppConfig.INPUT_DIR.exists())
        self.assertTrue(AppConfig.OUTPUT_DIR.exists())

        # Проверяем повторный вызов (должен работать с exist_ok=True)
        ensure_dirs()  # Не должно вызывать ошибок
