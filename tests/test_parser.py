import unittest
import tempfile
import os
from model.parser import ModelParser
from model.exceptions import InvalidXMLError, NoRootClassError


class TestModelParser(unittest.TestCase):
    def setUp(self):
        self.sample_xml = """<?xml version="1.0"?>
        <XMI>
            <Class name="BTS" isRoot="true">
                <Attribute name="id" type="uint32"/>
            </Class>
            <Class name="RU">
                <Attribute name="ipv4Address" type="string"/>
            </Class>
            <Aggregation source="RU" target="BTS"/>
        </XMI>"""

    def test_parse_valid_xml(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as tmp:
            tmp.write(self.sample_xml)
            tmp_path = tmp.name

        try:
            parser = ModelParser(tmp_path)
            parser.parse()
            self.assertEqual(parser.root_class, "BTS")
            self.assertEqual(len(parser.classes), 2)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_generate_config_xml(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as tmp:
            tmp.write(self.sample_xml)
            tmp_path = tmp.name

        try:
            parser = ModelParser(tmp_path)
            parser.parse()
            xml_content = parser.generate_config_xml()
            self.assertIn("<BTS>", xml_content)
            self.assertIn("<RU>", xml_content)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_generate_meta_json(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as tmp:
            tmp.write(self.sample_xml)
            tmp_path = tmp.name

        try:
            parser = ModelParser(tmp_path)
            parser.parse()
            meta = parser.generate_meta_json()
            self.assertEqual(len(meta), 2)
            self.assertTrue(any(c["class"] == "BTS" for c in meta))
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


class TestModelParserEdgeCases(unittest.TestCase):
    def test_invalid_xml(self):
        # Тест на некорректный XML (синтаксическая ошибка)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as tmp:
            tmp.write("<invalid><unclosed>")  # Намеренно некорректный XML
            tmp_path = tmp.name

        try:
            with self.assertRaises(InvalidXMLError):  # Ожидаем ошибку парсинга XML
                parser = ModelParser(tmp_path)
                parser.parse()
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_missing_root_class(self):
        # Тест на отсутствие корневого класса
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as tmp:
            tmp.write('''<?xml version="1.0"?>
            <XMI>
                <Class name="NotRoot">
                    <Attribute name="id" type="uint32"/>
                </Class>
            </XMI>''')
            tmp_path = tmp.name

        try:
            with self.assertRaises(NoRootClassError):
                parser = ModelParser(tmp_path)
                parser.parse()
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
