import os
import unittest
import tempfile
from model.config_processor import ConfigProcessor


class TestConfigProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = ConfigProcessor()
        self.test_data = {"test": "value"}

    def test_file_operations(self):
        # Используем временный файл с автоматическим удалением
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # Тест записи
            self.processor.save_config(self.test_data, tmp_path)

            # Тест чтения
            loaded = self.processor.load_config(tmp_path)
            self.assertEqual(loaded, self.test_data)

        finally:
            # Удаляем временный файл
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_generate_delta(self):
        original = {"a": 1, "b": 2}
        patched = {"a": 1, "b": 3, "c": 4}
        delta = self.processor.generate_delta(original, patched)

        self.assertEqual(delta["updates"][0]["key"], "b")
        self.assertEqual(delta["additions"][0]["key"], "c")

    def test_apply_delta(self):
        original = {"a": 1, "b": 2}
        delta = {
            "additions": [{"key": "c", "value": 3}],
            "deletions": ["b"],
            "updates": [{"key": "a", "to": 10}]
        }
        result = self.processor.apply_delta(original, delta)
        self.assertEqual(result, {"a": 10, "c": 3})
