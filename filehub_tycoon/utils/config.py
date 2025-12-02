# Конфигурация бота и настройки симулятора

import os
from typing import Dict, Any

class Config:
    """Класс конфигурации для бота и игры"""
    
    def __init__(self):
        # Настройки Telegram бота
        self.BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
        
        # Настройки базы данных
        self.DB_PATH = os.getenv('DB_PATH', 'file_hub_tycoon.db')
        
        # Игровые константы
        self.GAME_CONFIG = {
            'STARTING_BUDGET': 100000,  # Начальный бюджет в рублях
            'STARTING_USERS': 3,        # Начальное количество пользователей
            'TICK_DURATION': 24,        # Часов в одном ходу игры
            'MAX_ACTIONS_PER_TURN': 3,  # Максимум действий за ход
            'SUCCESS_THRESHOLD': 80,    # Порог для победы
            'BANKRUPTCY_THRESHOLD': 0,  # Порог банкротства
            'DOMAIN_BLOCK_PROBABILITY': 0.12,  # Вероятность блокировки домена за ход
            'DOMAIN_CHANGE_COST': 5000,  # Стоимость смены домена
            'MIRROR_CREATION_COST': 10000  # Стоимость создания зеркала
        }
        
        # Генератор названий сайтов
        self.SITE_NAME_COMPONENTS = {
            'prefixes': ['Torrent', 'Tracker', 'Share', 'Files', 'P2P', 'Download', 'Media'],
            'middle': ['Pro', 'Max', 'Plus', 'Ultra', 'Super', 'Elite', 'Hub'],
            'suffixes': ['Zone', 'Space', 'World', 'Center', 'Network', 'Hub', 'Portal'],
            'domains': ['.com', '.net', '.org', '.info', '.biz', '.xyz', '.online']
        }
        
        # Популярные домены для генерации
        self.DOMAIN_SUGGESTIONS = [
            'file sharing', 'p2p download', 'media files',
            'music hub', 'movie center', 'game files', 'software download'
        ]
        
        # Регионы для зеркал
        self.MIRROR_REGIONS = {
            'russia': {
                'domain_suffix': '.ru',
                'hosting_cost_multiplier': 1.0,
                'block_probability': 0.25
            },
            'netherlands': {
                'domain_suffix': '.nl', 
                'hosting_cost_multiplier': 1.2,
                'block_probability': 0.05
            },
            'singapore': {
                'domain_suffix': '.sg',
                'hosting_cost_multiplier': 1.3,
                'block_probability': 0.08
            },
            'usa': {
                'domain_suffix': '.us',
                'hosting_cost_multiplier': 1.5,
                'block_probability': 0.03
            }
        }
        
        # Стоимость услуг персонала (рублей в месяц)
        self.STAFF_SALARIES = {
            'CTO': 150000,     # CTO - инфраструктура
            'CMO': 120000,     # CMO - маркетинг
            'COO': 100000,     # COO - операции
            'CLO': 130000,     # CLO/Legal - комплаенс
            'COMMUNITY_MANAGER': 80000,   # Community Manager
            'DATA_ANALYST': 90000        # Data Analyst
        }
        
        # Стоимость апгрейдов инфраструктуры
        self.INFRASTRUCTURE_COSTS = {
            'server_upgrade': {
                'basic': 50000,
                'advanced': 150000,
                'enterprise': 500000
            },
            'bandwidth_increase': {
                'basic': 30000,
                'advanced': 100000,
                'enterprise': 300000
            },
            'storage_expansion': {
                'basic': 25000,
                'advanced': 75000,
                'enterprise': 250000
            },
            'security_enhancement': {
                'basic': 40000,
                'advanced': 120000,
                'enterprise': 400000
            }
        }
        
        # Стоимость маркетинговых кампаний
        self.MARKETING_COSTS = {
            'social_media': {
                'small': 20000,
                'medium': 60000,
                'large': 200000
            },
            'influencer_partnership': {
                'small': 15000,
                'medium': 50000,
                'large': 150000
            },
            'content_marketing': {
                'small': 10000,
                'medium': 35000,
                'large': 100000
            },
            'paid_ads': {
                'small': 25000,
                'medium': 75000,
                'large': 250000
            }
        }
        
        # Стоимость хостинга по регионам
        self.HOSTING_COSTS = {
            'russia': {
                'basic': 20000,
                'advanced': 60000,
                'enterprise': 200000
            },
            'netherlands': {
                'basic': 30000,
                'advanced': 90000,
                'enterprise': 300000
            },
            'singapore': {
                'basic': 35000,
                'advanced': 105000,
                'enterprise': 350000
            },
            'usa': {
                'basic': 40000,
                'advanced': 120000,
                'enterprise': 400000
            }
        }
        
        # Юридические риски и штрафы
        self.LEGAL_RISKS = {
            'base_risk': 30,      # Базовый риск
            'dmca_notice': 10,    # Риск за каждое DMCA уведомление
            'transparency_bonus': -5,  # Бонус за прозрачность
            'compliance_bonus': -8,    # Бонус за соответствие требованиям
            'max_risk': 100,
            'penalty_threshold': 70
        }
        
        # Рекламные метрики
        self.AD_METRICS = {
            'base_cpm': 50,       # Базовый CPM в рублях
            'seasonal_multiplier': {
                'winter': 0.8,
                'spring': 1.0,
                'summer': 0.7,
                'autumn': 1.2
            },
            'nps_bonus': 0.05,    # Бонус к CPM за каждый пункт NPS
            'retention_bonus': 0.03  # Бонус за удержание пользователей
        }
        
        # События и их вероятности
        self.EVENTS = {
            'ddos_attack': {
                'probability': 0.15,
                'impact': -20,
                'duration': 12  # часов
            },
            'server_outage': {
                'probability': 0.10,
                'impact': -15,
                'duration': 6
            },
            'viral_growth': {
                'probability': 0.08,
                'impact': 50,
                'duration': 0
            },
            'competitor_launch': {
                'probability': 0.12,
                'impact': -10,
                'duration': 0
            },
            'regulatory_check': {
                'probability': 0.06,
                'impact': -25,
                'duration': 0
            },
            'influencer_mention': {
                'probability': 0.05,
                'impact': 30,
                'duration': 0
            },
            'security_breach': {
                'probability': 0.04,
                'impact': -40,
                'duration': 24
            },
            'partnership_offer': {
                'probability': 0.07,
                'impact': 25,
                'duration': 0
            }
        }
    
    def get_staff_salary(self, role: str) -> int:
        """Получить зарплату для роли"""
        return self.STAFF_SALARIES.get(role, 0)
    
    def get_infrastructure_cost(self, upgrade_type: str, level: str) -> int:
        """Получить стоимость апгрейда инфраструктуры"""
        return self.INFRASTRUCTURE_COSTS.get(upgrade_type, {}).get(level, 0)
    
    def get_marketing_cost(self, campaign_type: str, level: str) -> int:
        """Получить стоимость маркетинговой кампании"""
        return self.MARKETING_COSTS.get(campaign_type, {}).get(level, 0)
    
    def get_hosting_cost(self, region: str, level: str) -> int:
        """Получить стоимость хостинга в регионе"""
        return self.HOSTING_COSTS.get(region, {}).get(level, 0)
    
    def get_event_probability(self, event_type: str) -> float:
        """Получить вероятность события"""
        return self.EVENTS.get(event_type, {}).get('probability', 0.0)
    
    def get_event_impact(self, event_type: str) -> int:
        """Получить влияние события"""
        return self.EVENTS.get(event_type, {}).get('impact', 0)
    
    def generate_site_name(self) -> str:
        """Генерация случайного названия сайта"""
        import random
        
        prefix = random.choice(self.SITE_NAME_COMPONENTS['prefixes'])
        middle = random.choice(self.SITE_NAME_COMPONENTS['middle'])
        suffix = random.choice(self.SITE_NAME_COMPONENTS['suffixes'])
        domain = random.choice(self.SITE_NAME_COMPONENTS['domains'])
        
        # Случайно добавляем middle или нет
        if random.random() < 0.7:  # 70% шанс добавить middle
            name = f"{prefix}{middle}{suffix}"
        else:
            name = f"{prefix}{suffix}"
        
        return name + domain
    
    def generate_custom_domain(self, site_name: str) -> str:
        """Генерация домена на основе названия сайта"""
        import random
        
        # Убираем пробелы и превращаем в нижний регистр
        clean_name = ''.join(c for c in site_name.lower() if c.isalnum())
        
        # Добавляем случайный суффикс
        suffixes = ['hub', 'zone', 'net', 'pro', 'plus', 'max', 'ultra']
        suffix = random.choice(suffixes)
        
        domain = f"{clean_name}{suffix}"
        
        # Добавляем случайный домен
        domains = ['.com', '.net', '.org', '.info', '.xyz']
        domain += random.choice(domains)
        
        return domain
    
    def get_domain_block_probability(self) -> float:
        """Получить вероятность блокировки домена"""
        return self.GAME_CONFIG.get('DOMAIN_BLOCK_PROBABILITY', 0.1)
    
    def get_mirror_regions(self) -> dict:
        """Получить список регионов для зеркал"""
        return self.MIRROR_REGIONS
    
    def get_domain_change_cost(self) -> int:
        """Получить стоимость смены домена"""
        return self.GAME_CONFIG.get('DOMAIN_CHANGE_COST', 5000)
    
    def get_mirror_creation_cost(self) -> int:
        """Получить стоимость создания зеркала"""
        return self.GAME_CONFIG.get('MIRROR_CREATION_COST', 10000)