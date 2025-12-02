# Игровой движок для симулятора файлового хаба

import random
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import math

from game.models import GameState, GameEvent, Staff, UserRole, InfrastructureLevel, HostingRegion
from utils.config import Config

logger = logging.getLogger(__name__)

class GameEngine:
    """Основной игровой движок"""
    
    def __init__(self):
        self.config = Config()
        self._event_descriptions = {
            'ddos_attack': {
                'description': '🔥 DDoS атака! Вашу платформу атакуют хакеры.',
                'choices': [
                    'Усилить защиту (+20 к безопасности, -$50,000)',
                    'Переключиться на резервный сервер (+10 к доступности, -$30,000)',
                    'Игнорировать атаку (-30 к популярности)'
                ]
            },
            'server_outage': {
                'description': '⚠️ Отключение серверов! Трекер недоступен.',
                'choices': [
                    'Быстрый ремонт (+15 к доступности, -$25,000)',
                    'Покупка новых серверов (+30 к надежности, -$100,000)',
                    'Миграция в другой дата-центр (+25 к надежности, -$75,000)'
                ]
            },
            'viral_growth': {
                'description': '📈 Вирусный рост! Ваша платформа стала популярной!',
                'choices': [
                    'Увеличить серверы (+50 к активным пользователям, -$40,000)',
                    'Запустить рекламную кампанию (+80 к активным пользователям, -$60,000)',
                    'Сохранить текущую инфраструктуру (+20 к активным пользователям)'
                ]
            },
            'competitor_launch': {
                'description': '⚔️ Конкурент запустился! Новая платформа появилась на рынке.',
                'choices': [
                    'Улучшить функциональность (+15 к репутации, -$50,000)',
                    'Снизить цены на премиум (+10 к конверсии, -$20,000)',
                    'Не реагировать (0 изменений)'
                ]
            },
            'regulatory_check': {
                'description': '🏛️ Проверка регуляторов! Нужно срочно реагировать.',
                'choices': [
                    'Показать полную прозрачность (-15 к юридическому риску)',
                    'Нанять юристов (-10 к юридическому риску, -$40,000)',
                    'Скрыть информацию (+20 к юридическому риску)'
                ]
            },
            'influencer_mention': {
                'description': '🌟 Популярный инфлюенсер упомянул вашу платформу!',
                'choices': [
                    'Запустить промо-акцию (+40 к узнаваемости бренда, -$30,000)',
                    'Сотрудничать с инфлюенсером (+60 к активным пользователям, -$80,000)',
                    'Не использовать возможность (+10 к узнаваемости бренда)'
                ]
            },
            'security_breach': {
                'description': '🔓 Утечка данных! Безопасность под угрозой.',
                'choices': [
                    'Уведомить пользователей и усилить безопасность (+20 к доверию, -$60,000)',
                    'Скрыть факт утечки (+10 к риску, -$30,000)',
                    'Нанять экспертов по безопасности (+35 к безопасности, -$120,000)'
                ]
            },
            'partnership_offer': {
                'description': '🤝 Предложение партнерства от крупной компании.',
                'choices': [
                    'Принять предложение (+25 к доходам, +15 к доверию, -$10,000)',
                    'Отклонить вежливо (+5 к репутации)',
                    'Торговаться за лучшие условия (+35 к доходам, +20 к доверию, -$20,000)'
                ]
            }
        }
    
    def process_turn(self, game_state: GameState) -> Dict[str, Any]:
        """Обработка одного хода игры"""
        try:
            turn_results = {
                'events': [],
                'metrics_changed': {},
                'new_events': [],
                'status': 'success'
            }
            
            # Генерируем события для текущего хода
            events = self._generate_events(game_state)
            for event in events:
                game_state.recent_events.append(event)
                turn_results['new_events'].append(event)
                game_state.last_event = event
            
            # Рассчитываем изменения метрик
            metrics_changes = self._calculate_base_metrics_change(game_state)
            turn_results['metrics_changed'] = metrics_changes
            self._apply_metrics_changes(game_state, metrics_changes)
            
            # Обрабатываем активные маркетинговые кампании
            campaign_effects = self._process_marketing_campaigns(game_state)
            turn_results['metrics_changed'].update(campaign_effects)
            self._apply_metrics_changes(game_state, campaign_effects)
            
            # Рассчитываем доходы и расходы
            financial_changes = self._calculate_financial_changes(game_state)
            turn_results['metrics_changed'].update(financial_changes)
            self._apply_metrics_changes(game_state, financial_changes)
            
            # Проверяем условия победы/поражения
            win_status = self._check_win_conditions(game_state)
            lose_status = self._check_lose_conditions(game_state)
            
            if win_status:
                turn_results['status'] = 'win'
            elif lose_status:
                turn_results['status'] = 'lose'
            
            return turn_results
            
        except Exception as e:
            logger.error(f"Ошибка обработки хода: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _generate_events(self, game_state: GameState) -> List[GameEvent]:
        """Генерация случайных событий для хода"""
        events = []
        
        # Базовая вероятность события в 30%
        if random.random() < 0.3:
            event_type = random.choice(list(self._event_descriptions.keys()))
            event_config = self._event_descriptions[event_type]
            
            event = GameEvent(
                event_type=event_type,
                description=event_config['description'],
                impact=self.config.get_event_impact(event_type),
                duration_hours=self.config.EVENTS.get(event_type, {}).get('duration', 0),
                probability=self.config.get_event_probability(event_type),
                timestamp=datetime.now(),
                resolved=False,
                choices=event_config['choices']
            )
            events.append(event)
        
        # Проверяем блокировку домена
        domain_block_event = self._check_domain_blocking(game_state)
        if domain_block_event:
            events.append(domain_block_event)
        
        return events
    
    def _check_domain_blocking(self, game_state: GameState) -> Optional[GameEvent]:
        """Проверка блокировки домена"""
        # Если настройка не завершена, не проверяем блокировку
        if not game_state.setup_complete:
            return None
        
        # Проверяем, пришло ли время проверки блокировки
        if game_state.current_turn < game_state.next_domain_check_turn:
            return None
        
        # Вероятность блокировки зависит от текущего юридического риска
        base_block_probability = 0.15  # 15% базовая вероятность
        legal_risk_multiplier = game_state.legal.risk_level / 100.0
        final_probability = base_block_probability * (1 + legal_risk_multiplier)
        
        if random.random() < final_probability:
            # Блокируем текущий домен
            game_state.current_domain_blocked = True
            game_state.last_domain_block_turn = game_state.current_turn
            game_state.next_domain_check_turn = game_state.current_turn + random.randint(3, 7)  # Следующая проверка через 3-7 ходов
            
            # Добавляем в историю блокировок
            block_record = {
                'domain': game_state.domain_name,
                'blocked_turn': game_state.current_turn,
                'reason': random.choice(['Роскомнадзор', 'Судебное решение', 'Жалоба правообладателей', 'Хостинг-провайдер'])
            }
            game_state.domain_block_history.append(block_record)
            
            # Создаем событие блокировки
            domain_block_event = GameEvent(
                event_type='domain_blocked',
                description=f"🚫 **Домен заблокирован!** Ваш домен {game_state.domain_name} заблокирован по причине: {block_record['reason']}",
                impact=20,
                duration_hours=0,
                probability=1.0,
                timestamp=datetime.now(),
                resolved=False,
                choices=[
                    'Ввести новый домен вручную',
                    'Использовать генератор доменов',
                    'Перейти на зеркало из доступных'
                ]
            )
            
            return domain_block_event
        
        # Если блокировки не было, планируем следующую проверку
        game_state.next_domain_check_turn = game_state.current_turn + random.randint(3, 7)
        return None
    
    def _calculate_base_metrics_change(self, game_state: GameState) -> Dict[str, Any]:
        """Расчет базовых изменений метрик за ход"""
        changes = {}
        
        # Влияние размера команды на рост
        staff_bonus = len([s for s in game_state.staff.values() if s.hired]) * 0.05
        
        # Влияние инфраструктуры на рост
        infra_multiplier = self._get_infrastructure_multiplier(game_state.infrastructure)
        
        # Базовый рост пользователей (2-5%)
        base_growth = random.uniform(0.02, 0.05)
        user_growth = base_growth * (1 + staff_bonus) * infra_multiplier
        
        changes['active_users'] = int(game_state.active_users * user_growth)
        
        # Изменение MAU
        changes['mau'] = int(game_state.mau * (1 + user_growth * 0.8))
        
        # Изменение удержания пользователей
        retention_change = random.uniform(-0.02, 0.03)
        changes['retention_rate_30d'] = max(0, min(100, 
            game_state.community.retention_rate_30d + retention_change * 100))
        
        # Изменение NPS
        nps_change = random.uniform(-2, 4)
        changes['nps_score'] = max(-100, min(100, 
            game_state.marketing.nps_score + nps_change))
        
        # Изменение юридического риска
        legal_risk_change = random.uniform(-1, 3)
        changes['legal_risk'] = max(0, min(100,
            game_state.legal.risk_level + legal_risk_change))
        
        return changes
    
    def _process_marketing_campaigns(self, game_state: GameState) -> Dict[str, Any]:
        """Обработка активных маркетинговых кампаний"""
        changes = {}
        current_turn = game_state.current_turn
        
        for campaign_key, campaign in game_state.marketing.campaigns.items():
            start_turn = campaign.get('start_turn', 0)
            duration = campaign.get('duration', 0)
            
            if start_turn <= current_turn <= start_turn + duration:
                # Кампания активна
                campaign_type = campaign.get('type', '')
                level = campaign.get('level', 'small')
                
                if campaign_type == 'social_media':
                    changes['active_users'] = changes.get('active_users', 0) + int(500 * self._get_level_multiplier(level))
                elif campaign_type == 'paid_ads':
                    changes['active_users'] = changes.get('active_users', 0) + int(800 * self._get_level_multiplier(level))
                    changes['brand_awareness'] = changes.get('brand_awareness', 0) + int(5 * self._get_level_multiplier(level))
                elif campaign_type == 'content_marketing':
                    changes['nps_score'] = changes.get('nps_score', 0) + int(2 * self._get_level_multiplier(level))
        
        return changes
    
    def _calculate_financial_changes(self, game_state: GameState) -> Dict[str, Any]:
        """Расчет финансовых изменений"""
        changes = {}
        
        # Доходы от рекламы
        base_cpm = self.config.AD_METRICS['base_cpm']
        nps_bonus = self.config.AD_METRICS['nps_bonus']
        retention_bonus = self.config.AD_METRICS['retention_bonus']
        
        ad_revenue_per_user = base_cpm * 0.001 * (
            1 + (game_state.marketing.nps_score * nps_bonus) + 
            (game_state.community.retention_rate_30d * retention_bonus / 100)
        )
        
        ad_revenue = int(game_state.active_users * ad_revenue_per_user)
        
        # Доходы от пожертвований
        donation_revenue = int(game_state.community.donations_monthly * 0.8)
        
        # Общие доходы
        changes['ad_revenue'] = ad_revenue
        changes['donation_revenue'] = donation_revenue
        changes['total_revenue'] = ad_revenue + donation_revenue
        
        # Общие расходы
        total_expenses = (game_state.expenses.staff_cost + 
                         game_state.expenses.marketing_cost +
                         game_state.expenses.legal_cost +
                         game_state.expenses.infrastructure_cost +
                         game_state.expenses.hosting_cost)
        
        changes['total_expenses'] = total_expenses
        
        # Денежный поток
        changes['cash_flow'] = changes['total_revenue'] - changes['total_expenses']
        
        return changes
    
    def _apply_metrics_changes(self, game_state: GameState, changes: Dict[str, Any]):
        """Применение изменений к состоянию игры"""
        for metric, value in changes.items():
            if metric in ['active_users', 'mau']:
                game_state.active_users += value
                game_state.mau += value
            elif metric == 'retention_rate_30d':
                game_state.community.retention_rate_30d = value
            elif metric == 'nps_score':
                game_state.marketing.nps_score = value
            elif metric == 'legal_risk':
                game_state.legal.risk_level = value
            elif metric == 'ad_revenue':
                game_state.revenue.ad_revenue = value
            elif metric == 'donation_revenue':
                game_state.revenue.donation_revenue = value
            elif metric == 'total_revenue':
                game_state.revenue.total_revenue = value
            elif metric == 'total_expenses':
                game_state.expenses.total_expenses = value
            elif metric == 'cash_flow':
                game_state.financial.cash_flow = value
            elif metric == 'brand_awareness':
                game_state.marketing.brand_awareness += value
        
        # Обновляем бюджет
        game_state.budget += changes.get('cash_flow', 0)
        
        # Обновляем MAU
        game_state.mau = int(game_state.active_users * 1.2)
    
    def _get_infrastructure_multiplier(self, infrastructure) -> float:
        """Получение множителя инфраструктуры"""
        multipliers = {
            InfrastructureLevel.BASIC: 1.0,
            InfrastructureLevel.ADVANCED: 1.15,
            InfrastructureLevel.ENTERPRISE: 1.35
        }
        
        server_mult = multipliers.get(infrastructure.server_level, 1.0)
        bandwidth_mult = multipliers.get(infrastructure.bandwidth_level, 1.0)
        storage_mult = multipliers.get(infrastructure.storage_level, 1.0)
        security_mult = multipliers.get(infrastructure.security_level, 1.0)
        
        return (server_mult + bandwidth_mult + storage_mult + security_mult) / 4
    
    def _get_level_multiplier(self, level: str) -> float:
        """Получение множителя для уровня"""
        multipliers = {
            'small': 1.0,
            'medium': 2.0,
            'large': 5.0
        }
        return multipliers.get(level, 1.0)
    
    def _check_win_conditions(self, game_state: GameState) -> bool:
        """Проверка условий победы"""
        win_conditions = [
            game_state.active_users >= 1000000,  # 1 млн пользователей
            game_state.marketing.nps_score >= 70,  # Высокий NPS
            game_state.legal.risk_level <= 40,  # Низкий юридический риск
            game_state.financial.cash_flow > 0  # Положительный денежный поток
        ]
        
        return all(win_conditions)
    
    def _check_lose_conditions(self, game_state: GameState) -> bool:
        """Проверка условий поражения"""
        lose_conditions = [
            game_state.budget <= 0,  # Нет денег
            game_state.legal.risk_level >= 100,  # Критический юридический риск
            game_state.active_users < 100  # Слишком мало пользователей
        ]
        
        return any(lose_conditions)
    
    def handle_event_choice(self, game_state: GameState, choice_index: int) -> Dict[str, Any]:
        """Обработка выбора в событии"""
        try:
            if not game_state.last_event or game_state.last_event.resolved:
                return {'success': False, 'message': 'Нет активных событий'}
            
            if choice_index >= len(game_state.last_event.choices):
                return {'success': False, 'message': 'Неверный выбор'}
            
            choice = game_state.last_event.choices[choice_index]
            game_state.last_event.selected_choice = choice
            game_state.last_event.resolved = True
            
            # Применяем эффект выбора
            effect = self._apply_event_effect(game_state, game_state.last_event.event_type, choice_index)
            
            return {
                'success': True, 
                'choice': choice,
                'effect': effect
            }
            
        except Exception as e:
            logger.error(f"Ошибка обработки выбора события: {e}")
            return {'success': False, 'message': str(e)}
    
    def _apply_event_effect(self, game_state: GameState, event_type: str, choice_index: int) -> Dict[str, Any]:
        """Применение эффекта выбора события"""
        effects = {
            'ddos_attack': [
                {'security_level': +20, 'budget': -50000},
                {'uptime': +10, 'budget': -30000},
                {'active_users': -30, 'nps_score': -15}
            ],
            'server_outage': [
                {'uptime': +15, 'budget': -25000},
                {'server_level': 'advanced', 'budget': -100000},
                {'uptime': +25, 'budget': -75000}
            ],
            'viral_growth': [
                {'active_users': +50, 'budget': -40000},
                {'active_users': +80, 'budget': -60000},
                {'active_users': +20}
            ],
            'competitor_launch': [
                {'nps_score': +15, 'budget': -50000},
                {'conversion_rate': +10, 'budget': -20000},
                {}  # Без изменений
            ],
            'regulatory_check': [
                {'legal_risk': -15},
                {'legal_risk': -10, 'budget': -40000},
                {'legal_risk': +20}
            ],
            'influencer_mention': [
                {'brand_awareness': +40, 'budget': -30000},
                {'active_users': +60, 'budget': -80000},
                {'brand_awareness': +10}
            ],
            'security_breach': [
                {'nps_score': +20, 'budget': -60000},
                {'legal_risk': +10, 'budget': -30000},
                {'security_level': +35, 'budget': -120000}
            ],
            'partnership_offer': [
                {'revenue': +25, 'nps_score': +15, 'budget': -10000},
                {'nps_score': +5},
                {'revenue': +35, 'nps_score': +20, 'budget': -20000}
            ]
        }
        
        if event_type not in effects or choice_index >= len(effects[event_type]):
            return {}
        
        effect = effects[event_type][choice_index]
        applied_effects = {}
        
        for key, value in effect.items():
            applied_effects[key] = value
            
            if key == 'budget':
                game_state.budget += value
            elif key == 'active_users':
                game_state.active_users = max(0, game_state.active_users + value)
            elif key == 'nps_score':
                game_state.marketing.nps_score = max(-100, min(100, game_state.marketing.nps_score + value))
            elif key == 'legal_risk':
                game_state.legal.risk_level = max(0, min(100, game_state.legal.risk_level + value))
            elif key == 'uptime':
                game_state.infrastructure.uptime = max(0, min(100, game_state.infrastructure.uptime + value))
            elif key == 'security_level':
                # Увеличиваем уровень безопасности
                current_level = game_state.infrastructure.security_level
                if current_level == InfrastructureLevel.BASIC:
                    game_state.infrastructure.security_level = InfrastructureLevel.ADVANCED
                elif current_level == InfrastructureLevel.ADVANCED:
                    game_state.infrastructure.security_level = InfrastructureLevel.ENTERPRISE
            elif key == 'server_level':
                current_level = game_state.infrastructure.server_level
                if current_level == InfrastructureLevel.BASIC:
                    game_state.infrastructure.server_level = InfrastructureLevel.ADVANCED
                elif current_level == InfrastructureLevel.ADVANCED:
                    game_state.infrastructure.server_level = InfrastructureLevel.ENTERPRISE
            elif key == 'brand_awareness':
                game_state.marketing.brand_awareness = max(0, min(100, game_state.marketing.brand_awareness + value))
            elif key == 'conversion_rate':
                game_state.marketing.conversion_rate = max(0, min(100, game_state.marketing.conversion_rate + value))
            elif key == 'revenue':
                game_state.revenue.total_revenue += value * 1000
        
        return applied_effects
    
    def calculate_score(self, game_state: GameState) -> int:
        """Расчет итогового счета игры"""
        try:
            # Базовый счет от пользователей
            user_score = int(game_state.active_users / 10)
            
            # Бонусы за метрики
            nps_bonus = int((game_state.marketing.nps_score + 100) * 5)
            retention_bonus = int(game_state.community.retention_rate_30d * 10)
            legal_bonus = int((100 - game_state.legal.risk_level) * 2)
            revenue_bonus = int(game_state.revenue.total_revenue / 1000)
            
            # Штрафы
            legal_penalty = int(game_state.legal.risk_level * 5)
            
            total_score = (user_score + nps_bonus + retention_bonus + 
                          legal_bonus + revenue_bonus - legal_penalty)
            
            return max(0, total_score)
            
        except Exception as e:
            logger.error(f"Ошибка расчета счета: {e}")
            return 0