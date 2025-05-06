# Пользовательские исключения для обработки ошибок приложения

class ModelError(Exception):
    """Базовое исключение для ошибок модели"""
    pass


class InvalidXMLError(ModelError):
    """Ошибка парсинга XML-файла"""
    pass


class NoRootClassError(ModelError):
    """Отсутствует корневой класс в модели"""
    pass


class ConfigError(ModelError):
    """Базовое исключение для ошибок конфигурации"""
    pass


class ConfigValidationError(ConfigError):
    """Ошибка валидации конфигурации"""
    pass
