# Генератор названий для файловых хабов

import random
import re
from typing import List, Tuple

class TrackerNameGenerator:
    """Генератор названий файловых хабов"""
    
    # Словарь для генерации названий
    PREFIXES = [
        "Хаб", "Центр", "Hub", "Center", "Bit", "Share", "Download", 
        "Upload", "Files", "Files", "File", "Sharing", "P2P", "Peer", "Net",
        "Мир", "Хаб", "Центр", "Сервис", "Клуб", "Портал", "Сайт", "База"
    ]
    
    SUFFIXES = [
        "Зона", "Мир", "Хаб", "Центр", "Клуб", "Портал", "Сайт", "База", 
        "Zone", "World", "Hub", "Center", "Club", "Portal", "Service",
        "Икс", "Про", "Премиум", "Плюс", "Макс", "Супер", "Ультра", 
        "X", "Pro", "Premium", "Plus", "Max", "Super", "Ultra"
    ]
    
    # Домены для генерации
    DOMAINS = [
        "com", "net", "org", "io", "co", "ru", "su", "by", "kz", "ua",
        "hub", "share", "sync", "cloud", "bit", "share", 
        "download", "upload", "files", "file", "p2p", "peer", "net"
    ]
    
    # Дополнительные суффиксы для доменов
    DOMAIN_PREFIXES = [
        "hub", "share", "sync", "bit", "share", "download", 
        "upload", "files", "p2p", "peer", "cloud", "file", "dl", "up"
    ]
    
    @classmethod
    def generate_random_name(cls) -> Tuple[str, str]:
        """Генерация случайного названия сайта и домена"""
        
        # Генерируем название сайта
        name_parts = []
        
        # Добавляем префикс (50% вероятность)
        if random.random() < 0.5:
            prefix = random.choice(cls.PREFIXES)
            name_parts.append(prefix)
        
        # Добавляем основное слово или оставляем пустым
        main_word = random.choice([
            "", "Мир", "Клуб", "Зона", "Центр", "Портал", "Сервис",
            "World", "Club", "Zone", "Center", "Portal", "Service",
            "Топ", "Бест", "Лучший", "Первый", "Главный",
            "Top", "Best", "First", "Main", "Prime"
        ])
        if main_word:
            name_parts.append(main_word)
        
        # Добавляем суффикс (30% вероятность)
        if random.random() < 0.3:
            suffix = random.choice(cls.SUFFIXES)
            name_parts.append(suffix)
        
        # Формируем название
        if not name_parts:
            name_parts = ["Хаб", "Центр"]
        
        site_name = " ".join(name_parts)
        
        # Генерируем домен
        domain = cls._generate_domain()
        
        return site_name, domain
    
    @classmethod
    def _generate_domain(cls) -> str:
        """Генерация случайного домена"""
        
        # Случайно выбираем тип генерации
        generation_type = random.choice(["prefix_domain", "full_name", "number_domain"])
        
        if generation_type == "prefix_domain":
            # Используем префикс + стандартный домен
            prefix = random.choice(cls.DOMAIN_PREFIXES)
            domain_tld = random.choice(cls.DOMAINS)
            domain = f"{prefix}{random.randint(1, 99)}.{domain_tld}"
            
        elif generation_type == "full_name":
            # Используем полное название в домене
            main_word = random.choice(cls.PREFIXES + cls.SUFFIXES)
            domain_tld = random.choice(cls.DOMAINS)
            # Убираем пробелы и делаем lowercase
            main_word = re.sub(r'\s+', '', main_word.lower())
            domain = f"{main_word}.{domain_tld}"
            
        else:  # number_domain
            # Простой домен с номером
            domain_tld = random.choice(cls.DOMAINS)
            domain = f"hub{random.randint(100, 999)}.{domain_tld}"
        
        # Проверяем длину домена (не более 25 символов)
        if len(domain) > 25:
            domain = f"fh{random.randint(1000, 9999)}.{random.choice(cls.DOMAINS)}"
        
        return domain
    
    @classmethod
    def generate_multiple_options(cls, count: int = 5) -> List[Tuple[str, str]]:
        """Генерация нескольких вариантов названий"""
        options = []
        used_domains = set()
        
        while len(options) < count:
            name, domain = cls.generate_random_name()
            
            # Избегаем повторяющихся доменов
            if domain not in used_domains:
                options.append((name, domain))
                used_domains.add(domain)
        
        return options
    
    @classmethod
    def validate_domain(cls, domain: str) -> bool:
        """Проверка валидности домена"""
        # Проверяем базовую структуру домена
        pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?\.([a-zA-Z]{2,})$'
        if not re.match(pattern, domain):
            return False
        
        # Проверяем длину
        if len(domain) > 63 or len(domain.split('.')[0]) > 63:
            return False
        
        # Проверяем, что домен не содержит запрещенных символов
        if any(char in domain for char in ['..', '--', '-']):
            # Допускаем тире, но не в начале или конце
            parts = domain.split('.')
            for part in parts:
                if part.startswith('-') or part.endswith('-'):
                    return False
        
        return True
    
    @classmethod
    def suggest_alternatives(cls, current_name: str, current_domain: str) -> List[Tuple[str, str]]:
        """Предложение альтернативных названий на основе текущего"""
        alternatives = []
        
        # Создаем вариации текущего названия
        words = current_name.split()
        
        # Добавляем суффиксы к текущему названию
        for suffix in ["Про", "Плюс", "Макс", "Премиум"]:
            new_name = f"{current_name} {suffix}"
            new_domain = cls._modify_domain(current_domain, suffix)
            alternatives.append((new_name, new_domain))
        
        # Добавляем числовые варианты
        for num in [2, 3, 2024]:
            new_name = f"{current_name} {num}"
            new_domain = cls._modify_domain(current_domain, str(num))
            alternatives.append((new_name, new_domain))
        
        # Добавляем полностью случайные варианты
        random_options = cls.generate_multiple_options(3)
        alternatives.extend(random_options)
        
        return alternatives[:5]  # Возвращаем только 5 вариантов
    
    @classmethod
    def _modify_domain(cls, domain: str, addition: str) -> str:
        """Модификация домена с добавлением суффикса"""
        parts = domain.split('.')
        if len(parts) >= 2:
            name_part = parts[0]
            tld = parts[-1]
            new_name = f"{name_part}{addition.lower()}"
            return f"{new_name}.{tld}"
        return domain