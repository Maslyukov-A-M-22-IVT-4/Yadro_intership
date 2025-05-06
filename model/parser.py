import xml.etree.ElementTree as ET
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional
from model.exceptions import InvalidXMLError, NoRootClassError

logger = logging.getLogger(__name__)


@dataclass
class ClassAttribute:
    """Атрибут класса модели"""
    name: str
    type: str


@dataclass
class Aggregation:
    """Связь между классами"""
    source: str
    target: str
    source_multiplicity: str
    target_multiplicity: str


@dataclass
class ClassInfo:
    """Информация о классе"""
    name: str
    is_root: bool
    documentation: str
    attributes: List[ClassAttribute]
    min_multiplicity: Optional[str] = None  # Минимальная кратность
    max_multiplicity: Optional[str] = None  # Максимальная кратность


class ModelParser:
    """Парсер UML модели из XML"""

    def __init__(self, xml_file: str):
        self.xml_file = xml_file
        self.classes: Dict[str, ClassInfo] = {}
        self.aggregations: List[Aggregation] = []
        self.root_class: Optional[str] = None

    def parse(self) -> None:
        """Основной метод парсинга XML"""
        try:
            tree = ET.parse(self.xml_file)
            self._parse_classes(tree.getroot())
            self._validate_model()
        except ET.ParseError as e:
            raise InvalidXMLError(f"Ошибка парсинга XML: {e}") from e

    def _parse_classes(self, root: ET.Element) -> None:
        """Парсинг классов и связей"""
        # Парсим классы
        for elem in root.findall('.//Class'):
            if name := elem.get('name'):
                self._parse_class_element(elem, name)

        # Парсим агрегации
        for elem in root.findall('.//Aggregation'):
            if (src := elem.get('source')) and (tgt := elem.get('target')):
                self._parse_aggregation_element(elem, src, tgt)

    def _parse_class_element(self, elem: ET.Element, name: str) -> None:
        """Парсинг отдельного класса"""
        self.classes[name] = ClassInfo(
            name=name,
            is_root=elem.get('isRoot', 'false').lower() == 'true',
            documentation=elem.get('documentation', ''),
            attributes=[
                ClassAttribute(a.get('name'), a.get('type'))
                for a in elem.findall('.//Attribute')
                if a.get('name') and a.get('type')
            ]
        )
        if self.classes[name].is_root:
            self.root_class = name

    def _parse_aggregation_element(self, elem: ET.Element, src: str, tgt: str) -> None:
        """Парсинг отдельной агрегации"""
        agg = Aggregation(
            source=src,
            target=tgt,
            source_multiplicity=elem.get('sourceMultiplicity', '1'),
            target_multiplicity=elem.get('targetMultiplicity', '1')
        )
        self.aggregations.append(agg)

        # Обновляем кратность для класса-источника
        if src in self.classes:
            min_max = agg.source_multiplicity.split('..')
            self.classes[src].min_multiplicity = min_max[0]
            self.classes[src].max_multiplicity = min_max[-1]

    def _validate_model(self) -> None:
        """Проверка валидности модели"""
        if not self.root_class:
            raise NoRootClassError("Не найден корневой класс")

    def generate_config_xml(self) -> str:
        """Генерация config.xml"""
        if not self.root_class:
            raise NoRootClassError("Невозможно сгенерировать XML без корневого класса")

        def build_xml(class_name: str, indent: int = 0) -> str:
            """Рекурсивное построение XML"""
            class_info = self.classes[class_name]
            xml = [f"{' ' * indent}<{class_name}>"]

            # Атрибуты класса
            xml.extend(
                f"{' ' * (indent + 4)}<{attr.name}>{attr.type}</{attr.name}>"
                for attr in class_info.attributes
            )

            # Дочерние классы
            xml.extend(
                build_xml(agg.source, indent + 4)
                for agg in self.aggregations
                if agg.target == class_name
            )

            xml.append(f"{' ' * indent}</{class_name}>")
            return '\n'.join(xml)

        return build_xml(self.root_class)

    def generate_meta_json(self) -> List[Dict]:
        """Генерация meta.json согласно ТЗ"""
        order = ["MetricJob", "CPLANE", "MGMT", "RU", "HWE", "COMM", "BTS"]
        source_classes = {agg.source for agg in self.aggregations}
        result = []

        for cls in order:
            if cls not in self.classes:
                continue

            info = self.classes[cls]
            entry = {
                "class": cls,
                "documentation": info.documentation,
                "isRoot": info.is_root,
                "parameters": [
                                  {"name": attr.name, "type": attr.type}
                                  for attr in info.attributes
                              ] + [
                                  {"name": agg.source, "type": "class"}
                                  for agg in self.aggregations
                                  if agg.target == cls
                              ]
            }

            if cls in source_classes:
                entry.update({
                    "min": info.min_multiplicity,
                    "max": info.max_multiplicity
                })

            result.append(entry)

        return result
