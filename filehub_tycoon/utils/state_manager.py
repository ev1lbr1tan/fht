# Менеджер состояний игры

import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from game.models import GameState, Staff, UserRole
from utils.database import Database

logger = logging.getLogger(__name__)

class StateManager:
    """Класс для управления состоянием игры"""
    
    def __init__(self, db: Database):
        self.db = db
        self._active_states: Dict[int, GameState] = {}
    
    def create_new_game(self, user_id: int, username: str = None, 
                       first_name: str = None, last_name: str = None) -> GameState:
        """Создание новой игры"""
        try:
            # Создаем начальное состояние игры с настройкой
            game_state = GameState(
                user_id=user_id,
                tracker_name="Требуется настройка",
                site_name="Требуется настройка",
                domain_name="setup-required.com",
                setup_complete=False,
                name_setup_step="name"
            )
            
            # Сохраняем игрока в базе данных
            self.db.save_player(user_id, username, first_name, last_name)
            
            # Сохраняем игру в базе данных
            game_id = self.db.save_game(
                user_id=user_id,
                tracker_name=game_state.tracker_name,
                game_state=game_state.model_dump()
            )
            
            # Кэшируем состояние в памяти
            self._active_states[user_id] = game_state
            
            logger.info(f"Создана новая игра для пользователя {user_id}")
            return game_state
            
        except Exception as e:
            logger.error(f"Ошибка создания новой игры для пользователя {user_id}: {e}")
            raise
    
    def load_game(self, user_id: int) -> Optional[GameState]:
        """Загрузка активной игры"""
        try:
            # Проверяем кэш
            if user_id in self._active_states:
                return self._active_states[user_id]
            
            # Загружаем из базы данных
            game_data = self.db.load_active_game(user_id)
            if game_data:
                game_state = GameState(**game_data['game_state'])
                self._active_states[user_id] = game_state
                return game_state
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка загрузки игры для пользователя {user_id}: {e}")
            return None
    
    def save_game(self, user_id: int) -> bool:
        """Сохранение игры в базу данных"""
        try:
            if user_id not in self._active_states:
                logger.warning(f"Нет активной игры для пользователя {user_id}")
                return False
            
            game_state = self._active_states[user_id]
            game_data = self.db.load_active_game(user_id)
            game_id = game_data['game_id'] if game_data else None
            
            self.db.save_game(
                user_id=user_id,
                tracker_name=game_state.tracker_name,
                game_state=game_state.model_dump(),
                game_id=game_id
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка сохранения игры для пользователя {user_id}: {e}")
            return False
    
    def update_state(self, user_id: int, updates: Dict[str, Any]) -> bool:
        """Обновление состояния игры"""
        try:
            if user_id not in self._active_states:
                logger.warning(f"Нет активной игры для пользователя {user_id}")
                return False
            
            game_state = self._active_states[user_id]
            
            # Применяем обновления
            for key, value in updates.items():
                if hasattr(game_state, key):
                    setattr(game_state, key, value)
                else:
                    logger.warning(f"Неизвестное поле состояния игры: {key}")
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обновления состояния для пользователя {user_id}: {e}")
            return False
    
    def get_game_state(self, user_id: int) -> Optional[GameState]:
        """Получение текущего состояния игры"""
        return self._active_states.get(user_id)
    
    def advance_turn(self, user_id: int) -> bool:
        """Переход к следующему ходу игры"""
        try:
            if user_id not in self._active_states:
                return False
            
            game_state = self._active_states[user_id]
            
            # Увеличиваем номер хода
            game_state.current_turn += 1
            
            # Восстанавливаем количество действий
            game_state.actions_remaining = 3
            
            # Обновляем время последнего хода
            game_state.last_turn_date = datetime.now()
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка перехода к следующему ходу для пользователя {user_id}: {e}")
            return False
    
    def hire_staff(self, user_id: int, role: UserRole, name: str, 
                  salary: int, skill_level: int = 1) -> bool:
        """Найм сотрудника"""
        try:
            if user_id not in self._active_states:
                return False
            
            game_state = self._active_states[user_id]
            
            # Проверяем, не нанят ли уже сотрудник на эту роль
            if role in game_state.staff and game_state.staff[role].hired:
                return False
            
            # Создаем нового сотрудника
            staff_member = Staff(
                role=role,
                name=name,
                salary=salary,
                skill_level=skill_level,
                hired=True,
                hired_date=datetime.now()
            )
            
            # Добавляем в команду
            game_state.staff[role.value] = staff_member
            
            # Увеличиваем расходы на персонал
            game_state.expenses.staff_cost += salary
            
            # Увеличиваем общие расходы
            game_state.expenses.total_expenses += salary
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка найма сотрудника для пользователя {user_id}: {e}")
            return False
    
    def upgrade_infrastructure(self, user_id: int, upgrade_type: str, level: str) -> bool:
        """Апгрейд инфраструктуры"""
        try:
            if user_id not in self._active_states:
                return False
            
            game_state = self._active_states[user_id]
            infrastructure = game_state.infrastructure
            
            # Обновляем соответствующий компонент инфраструктуры
            if upgrade_type == 'server' and hasattr(infrastructure, 'server_level'):
                infrastructure.server_level = level
            elif upgrade_type == 'bandwidth' and hasattr(infrastructure, 'bandwidth_level'):
                infrastructure.bandwidth_level = level
            elif upgrade_type == 'storage' and hasattr(infrastructure, 'storage_level'):
                infrastructure.storage_level = level
            elif upgrade_type == 'security' and hasattr(infrastructure, 'security_level'):
                infrastructure.security_level = level
            else:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка апгрейда инфраструктуры для пользователя {user_id}: {e}")
            return False
    
    def add_hosting_region(self, user_id: int, region: str, level: str) -> bool:
        """Добавление региона хостинга"""
        try:
            if user_id not in self._active_states:
                return False
            
            game_state = self._active_states[user_id]
            hosting = game_state.hosting
            
            # Добавляем новый регион
            hosting.regions[region] = level
            hosting.mirrors_count += 1
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка добавления региона хостинга для пользователя {user_id}: {e}")
            return False
    
    def start_marketing_campaign(self, user_id: int, campaign_type: str, level: str, cost: int) -> bool:
        """Запуск маркетинговой кампании"""
        try:
            if user_id not in self._active_states:
                return False
            
            game_state = self._active_states[user_id]
            marketing = game_state.marketing
            
            # Добавляем кампанию
            campaign_key = f"{campaign_type}_{level}"
            marketing.campaigns[campaign_key] = {
                'type': campaign_type,
                'level': level,
                'cost': cost,
                'start_turn': game_state.current_turn,
                'duration': 3  # Ходы
            }
            
            # Увеличиваем расходы на маркетинг
            marketing.ad_spend += cost
            game_state.expenses.marketing_cost += cost
            game_state.expenses.total_expenses += cost
            
            # Уменьшаем бюджет
            game_state.budget -= cost
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка запуска маркетинговой кампании для пользователя {user_id}: {e}")
            return False
    
    def calculate_metrics(self, user_id: int) -> bool:
        """Расчет игровых метрик"""
        try:
            if user_id not in self._active_states:
                return False
            
            game_state = self._active_states[user_id]
            
            # Расчет доходов
            ad_revenue = int(game_state.active_users * 0.1)  # 10 копеек за пользователя
            donation_revenue = int(game_state.community.donations_monthly * 0.8)
            
            game_state.revenue.ad_revenue = ad_revenue
            game_state.revenue.donation_revenue = donation_revenue
            game_state.revenue.total_revenue = ad_revenue + donation_revenue
            
            # Расчет денежного потока
            game_state.financial.cash_flow = game_state.revenue.total_revenue - game_state.expenses.total_expenses
            
            # Обновляем бюджет
            game_state.budget += game_state.financial.cash_flow
            
            # Расчет скорости сжигания денег
            if game_state.financial.cash_flow < 0:
                game_state.financial.burn_rate = abs(game_state.financial.cash_flow)
                # Расчет оставшихся месяцев
                if game_state.financial.burn_rate > 0:
                    game_state.financial.runway_months = game_state.budget / game_state.financial.burn_rate
            else:
                game_state.financial.burn_rate = 0
                game_state.financial.runway_months = 999
            
            # Расчет прибыльности
            if game_state.revenue.total_revenue > 0:
                game_state.financial.profit_margin = (game_state.revenue.total_revenue - game_state.expenses.total_expenses) / game_state.revenue.total_revenue * 100
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка расчета метрик для пользователя {user_id}: {e}")
            return False
    
    def handle_event_response(self, user_id: int, choice: str) -> bool:
        """Обработка ответа на событие"""
        try:
            if user_id not in self._active_states:
                return False
            
            game_state = self._active_states[user_id]
            
            if game_state.last_event and not game_state.last_event.resolved:
                game_state.last_event.selected_choice = choice
                game_state.last_event.resolved = True
                
                # Применяем влияние выбора
                # Это будет реализовано в зависимости от типа события
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки ответа на событие для пользователя {user_id}: {e}")
            return False
    
    def check_win_conditions(self, user_id: int) -> bool:
        """Проверка условий победы"""
        try:
            if user_id not in self._active_states:
                return False
            
            game_state = self._active_states[user_id]
            
            # Условия победы:
            # 1. Больше 1 млн активных пользователей
            # 2. NPS больше 70
            # 3. Юридический риск меньше 40
            # 4. Положительный денежный поток
            
            win_conditions = [
                game_state.active_users >= 1000000,
                game_state.marketing.nps_score >= 70,
                game_state.legal.risk_level <= 40,
                game_state.financial.cash_flow > 0
            ]
            
            return all(win_conditions)
            
        except Exception as e:
            logger.error(f"Ошибка проверки условий победы для пользователя {user_id}: {e}")
            return False
    
    def check_lose_conditions(self, user_id: int) -> bool:
        """Проверка условий поражения"""
        try:
            if user_id not in self._active_states:
                return False
            
            game_state = self._active_states[user_id]
            
            # Условия поражения:
            # 1. Бюджет меньше или равен 0
            # 2. Юридический риск больше или равен 100
            # 3. Активных пользователей меньше 100
            
            lose_conditions = [
                game_state.budget <= 0,
                game_state.legal.risk_level >= 100,
                game_state.active_users < 100
            ]
            
            return any(lose_conditions)
            
        except Exception as e:
            logger.error(f"Ошибка проверки условий поражения для пользователя {user_id}: {e}")
            return False
    
    def generate_setup_options(self, user_id: int) -> bool:
        """Генерация вариантов для настройки названия и домена"""
        try:
            if user_id not in self._active_states:
                return False
            
            game_state = self._active_states[user_id]
            
            # Импортируем генератор
            from utils.name_generator import TrackerNameGenerator
            
            # Генерируем варианты
            options = TrackerNameGenerator.generate_multiple_options(5)
            game_state.current_setup_options = options
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка генерации вариантов настройки для пользователя {user_id}: {e}")
            return False
    
    def setup_hub_name(self, user_id: int, name: str) -> bool:
        """Настройка названия хаба"""
        try:
            if user_id not in self._active_states:
                return False
            
            game_state = self._active_states[user_id]
            
            # Устанавливаем название
            game_state.tracker_name = name
            game_state.site_name = name
            game_state.name_setup_step = "domain"
            
            logger.info(f"Установлено название хаба для пользователя {user_id}: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка настройки названия хаба для пользователя {user_id}: {e}")
            return False
    
    def setup_hub_domain(self, user_id: int, domain: str) -> bool:
        """Настройка домена хаба"""
        try:
            if user_id not in self._active_states:
                return False
            
            game_state = self._active_states[user_id]
            
            # Устанавливаем домен
            game_state.domain_name = domain
            game_state.available_domains = [domain]
            game_state.name_setup_step = "complete"
            game_state.setup_complete = True
            
            logger.info(f"Установлен домен хаба для пользователя {user_id}: {domain}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка настройки домена хаба для пользователя {user_id}: {e}")
            return False
    
    def select_setup_option(self, user_id: int, option_index: int) -> bool:
        """Выбор варианта настройки из предложенных"""
        try:
            if user_id not in self._active_states:
                return False
            
            game_state = self._active_states[user_id]
            
            if option_index >= len(game_state.current_setup_options):
                return False
            
            # Получаем выбранный вариант
            name, domain = game_state.current_setup_options[option_index]
            
            # Устанавливаем название и домен
            game_state.tracker_name = name
            game_state.site_name = name
            game_state.domain_name = domain
            game_state.available_domains = [domain]
            game_state.name_setup_step = "complete"
            game_state.setup_complete = True
            game_state.current_setup_options = []
            
            logger.info(f"Выбран вариант настройки для пользователя {user_id}: {name} ({domain})")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка выбора варианта настройки для пользователя {user_id}: {e}")
            return False
    
    def change_domain(self, user_id: int, new_domain: str) -> bool:
        """Смена домена хаба"""
        try:
            if user_id not in self._active_states:
                return False
            
            game_state = self._active_states[user_id]
            
            # Проверяем, что домен валиден
            from utils.name_generator import TrackerNameGenerator
            if not TrackerNameGenerator.validate_domain(new_domain):
                return False
            
            # Добавляем новый домен в список доступных
            if new_domain not in game_state.available_domains:
                game_state.available_domains.append(new_domain)
            
            # Устанавливаем новый домен как текущий
            game_state.domain_name = new_domain
            
            # Если текущий домен был заблокирован, разблокируем
            if game_state.current_domain_blocked:
                game_state.current_domain_blocked = False
            
            logger.info(f"Сменен домен хаба для пользователя {user_id}: {new_domain}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка смены домена для пользователя {user_id}: {e}")
            return False