from typing import TypedDict, List, Dict, Optional


class Parameter(TypedDict):
    """Атрибут класса модели"""
    name: str
    type: str


class ClassMeta(TypedDict):
    """Структура метаданных класса для генерации meta.json"""
    class_name: str
    documentation: str
    isRoot: bool
    parameters: List[Parameter]
    min: Optional[str]  # Только для классов-источников агрегаций
    max: Optional[str]  # Только для классов-источников агрегаций


class DeltaOperation(TypedDict):
    """Элемент разницы между конфигами"""
    key: str
    value: Optional[str]  # Для новых параметров
    from_: Optional[str]  # Старое значение
    to: Optional[str]  # Новое значение


class Delta(TypedDict):
    """Структура файла delta.json"""
    additions: List[DeltaOperation]
    deletions: List[str]
    updates: List[DeltaOperation]


ConfigDict = Dict[str, str]  # Тип для JSON-конфигов
