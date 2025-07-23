from django import template

register = template.Library()

# Словарь с правилами склонения для часто используемых слов
PLURAL_RULES = {
    'продукт': 'продукт|продукта|продуктов',
    'задача': 'задача|задачи|задач',
    'элемент': 'элемент|элемента|элементов',
    'файл': 'файл|файла|файлов',
    'проект': 'проект|проекта|проектов',
    'пользователь': 'пользователь|пользователя|пользователей',
    'документ': 'документ|документа|документов',
    'результат': 'результат|результата|результатов',
    'отчет': 'отчет|отчета|отчетов',
    'ошибка': 'ошибка|ошибки|ошибок',
    'строка': 'строка|строки|строк',
    'запись': 'запись|записи|записей',
    'тест': 'тест|теста|тестов',
}

# Правила автоматического склонения для существительных
AUTO_PLURAL_RULES = {

    # Мужской род
    'т': ('т|та|тов', ['продукт', 'проект', 'результат', 'отчет']),
    'нт': ('нт|нта|нтов', ['элемент', 'документ']),
    'ль': ('ль|ля|лей', ['пользователь']),
    'ст': ('ст|ста|стов', ['тест']),

    # Женский род
    'ча': ('ча|чи|ч', ['задача']),
    'ка': ('ка|ки|ок', ['ошибка', 'строка']),
    'сь': ('сь|си|сей', ['запись']),
}


def get_word_variants(word):
    """
    Определяет варианты склонения слова автоматически.

    Сначала ищет в предопределенном словаре,
    затем пытается применить правила автоматического склонения.
    """
    # Проверка в словаре готовых правил
    if word.lower() in PLURAL_RULES:
        return PLURAL_RULES[word.lower()]

    # Автоматическое определение правила
    word_lower = word.lower()
    for ending, (rule, examples) in AUTO_PLURAL_RULES.items():

        if word_lower.endswith(ending):
            base = word_lower[:-len(ending)]
            singular, few, many = rule.split('|')
            return f"{base}{singular}|{base}{few}|{base}{many}"

    # Возврат базового склонения в случае неудачи
    return f"{word}|{word}а|{word}ов"


@register.filter
def replace_dj(value, arg):
    """Заменяет символы в строке"""
    old, new = arg.split('|')
    return value.replace(old, new)


@register.filter
def get_item(dictionary, key):
    """Получает значение из словаря по ключу"""
    return dictionary.get(str(key), [])


@register.filter
def pluralize(number, word):
    """
    Возвращает правильное склонение слова в зависимости от числа.

    Аргументы:
        number (int): Число для склонения
        word (str): Слово в единственном числе или строка с вариантами
                   в формате "слово|слова|слов"

    Использование в шаблоне:
        {{ 5|pluralize:"продукт" }}  # Автоматическое определение
        {{ items|length|pluralize:"задача" }}
        {{ count|pluralize:"элемент|элемента|элементов" }}  # Ручное указание
    """
    try:

        # Проверка передачи вариантов в строке
        if '|' in word:
            variants = word

        else:
            variants = get_word_variants(word)

        singular, few, many = variants.split('|')
        last_digit = number % 10
        last_two_digits = number % 100

        if last_two_digits in range(11, 20):
            form = many

        elif last_digit == 1:
            form = singular

        elif last_digit in range(2, 5):
            form = few

        else:
            form = many

        return f"{number} {form}"

    except (ValueError, AttributeError):
        return f"{number} {word}"
