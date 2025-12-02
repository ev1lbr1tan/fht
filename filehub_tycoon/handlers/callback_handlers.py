# Обработчики callback-запросов для inline-кнопок

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from game.models import UserRole, InfrastructureLevel, HostingRegion
from utils.config import Config

logger = logging.getLogger(__name__)

class CallbackHandlers:
    """Класс обработчиков callback-запросов"""
    
    def __init__(self, state_manager, game_engine):
        self.state_manager = state_manager
        self.game_engine = game_engine
        self.config = Config()
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Основной обработчик всех callback-запросов"""
        query = update.callback_query
        user_id = update.effective_user.id
        
        try:
            await query.answer()
            
            # Получаем текущее состояние игры
            game_state = self.state_manager.get_game_state(user_id)
            if not game_state:
                await query.edit_message_text("❌ Игра не найдена. Используйте /start для создания новой игры.")
                return
            
            # Разбираем callback_data
            data = query.data
            
            if data.startswith("dashboard_"):
                await self._handle_dashboard_callback(query, game_state, data)
            elif data.startswith("hire_"):
                await self._handle_hire_callback(query, game_state, data)
            elif data.startswith("upgrade_"):
                await self._handle_upgrade_callback(query, game_state, data)
            elif data.startswith("campaign_"):
                await self._handle_marketing_callback(query, game_state, data)
            elif data.startswith("add_hosting_"):
                await self._handle_hosting_callback(query, game_state, data)
            elif data.startswith("event_choice_"):
                await self._handle_event_choice_callback(query, game_state, data)
            elif data.startswith("execute_action_"):
                await self._handle_execute_action_callback(query, game_state, data)
            elif data == "random_action":
                await self._handle_random_action_callback(query, game_state)
            elif data.startswith("legal_"):
                await self._handle_legal_callback(query, game_state, data)
            elif data.startswith("community_"):
                await self._handle_community_callback(query, game_state, data)
            elif data.startswith("setup_"):
                await self._handle_setup_callback(query, game_state, data)
            elif data.startswith("select_option_"):
                await self._handle_select_option_callback(query, game_state, data)
            else:
                await query.edit_message_text("❌ Неизвестная команда")
            
        except Exception as e:
            logger.error(f"Ошибка обработки callback: {e}")
            await query.edit_message_text(f"❌ Ошибка: {str(e)}")
    
    async def _handle_hire_callback(self, query, game_state, data):
        """Обработка найма сотрудников"""
        role = data.replace("hire_", "")
        salary = self.config.get_staff_salary(role)
        
        if game_state.budget < salary:
            await query.edit_message_text(f"❌ Недостаточно средств! Нужно ${salary:,}, у вас ${game_state.budget:,}")
            return
        
        # Генерируем имя для сотрудника
        names = {
            'CTO': ['Александр Техников', 'Дмитрий Кодеров', 'Игорь Серверов'],
            'CMO': ['Елена Маркетологова', 'Анна Рекламова', 'Мария Промо'],
            'COO': ['Михаил Операционер', 'Алексей Процессов', 'Павел Автоматизатор'],
            'CLO': ['Владимир Юридиков', 'Сергей Правоведов', 'Андрей Комплаенс'],
            'COMMUNITY_MANAGER': ['Наталья Комьюнити', 'Екатерина Сообщества', 'Ольга Общения'],
            'DATA_ANALYST': ['Олег Аналитиков', 'Ирина Данных', 'Татьяна Метрик']
        }
        
        names_list = names.get(role, ['Иван Специалистов'])
        name = names_list[hash(game_state.user_id + role) % len(names_list)]
        
        # Нанимаем сотрудника
        success = self.state_manager.hire_staff(
            user_id=game_state.user_id,
            role=UserRole(role),
            name=name,
            salary=salary
        )
        
        if success:
            self.state_manager.update_state(game_state.user_id, {'budget': game_state.budget - salary})
            
            # Формируем сообщение об успешном найме
            message = f"""
✅ **{name} принят на должность {role}!**

💰 Зарплата: ${salary:,}/месяц
📈 Влияние на бизнес:
{self._get_role_impact_description(role)}

💵 Оставшийся бюджет: ${game_state.budget - salary:,}

Используйте /next для продолжения развития хаба.
"""
            await query.edit_message_text(message, parse_mode='Markdown')
        else:
            await query.edit_message_text("❌ Ошибка при найме сотрудника.")
    
    async def _handle_upgrade_callback(self, query, game_state, data):
        """Обработка апгрейдов инфраструктуры"""
        if data == "upgrade_server_advanced":
            cost = self.config.get_infrastructure_cost('server_upgrade', 'advanced')
            if game_state.budget < cost:
                await query.edit_message_text(f"❌ Недостаточно средств! Нужно ${cost:,}")
                return
            
            success = self.state_manager.upgrade_infrastructure(
                user_id=game_state.user_id,
                upgrade_type='server',
                level='advanced'
            )
            
            if success:
                self.state_manager.update_state(game_state.user_id, {'budget': game_state.budget - cost})
                
                message = f"""
🖥️ **Серверы обновлены до Advanced!**

⚡ Увеличена производительность на 25%
💰 Стоимость: ${cost:,}
💵 Оставшийся бюджет: ${game_state.budget - cost:,}

Это улучшит рост пользователей и стабильность работы трекера.
"""
                await query.edit_message_text(message, parse_mode='Markdown')
            else:
                await query.edit_message_text("❌ Ошибка апгрейда серверов.")
                
        elif data == "upgrade_bandwidth_advanced":
            cost = self.config.get_infrastructure_cost('bandwidth_increase', 'advanced')
            if game_state.budget < cost:
                await query.edit_message_text(f"❌ Недостаточно средств! Нужно ${cost:,}")
                return
            
            success = self.state_manager.upgrade_infrastructure(
                user_id=game_state.user_id,
                upgrade_type='bandwidth',
                level='advanced'
            )
            
            if success:
                self.state_manager.update_state(game_state.user_id, {'budget': game_state.budget - cost})
                
                message = f"""
⚡ **Пропускная способность увеличена до Advanced!**

🌐 Больше пользователей могут одновременно использовать трекер
💰 Стоимость: ${cost:,}
💵 Оставшийся бюджет: ${game_state.budget - cost:,}

Снизится нагрузка на серверы во время пикового трафика.
"""
                await query.edit_message_text(message, parse_mode='Markdown')
            else:
                await query.edit_message_text("❌ Ошибка увеличения пропускной способности.")
                
        elif data == "upgrade_security_advanced":
            cost = self.config.get_infrastructure_cost('security_enhancement', 'advanced')
            if game_state.budget < cost:
                await query.edit_message_text(f"❌ Недостаточно средств! Нужно ${cost:,}")
                return
            
            success = self.state_manager.upgrade_infrastructure(
                user_id=game_state.user_id,
                upgrade_type='security',
                level='advanced'
            )
            
            if success:
                self.state_manager.update_state(game_state.user_id, {'budget': game_state.budget - cost})
                
                message = f"""
🛡️ **Безопасность улучшена до Advanced!**

🔒 Защита от кибератак и утечек данных
💰 Стоимость: ${cost:,}
💵 Оставшийся бюджет: ${game_state.budget - cost:,}

Уменьшатся риски и увеличится доверие пользователей.
"""
                await query.edit_message_text(message, parse_mode='Markdown')
            else:
                await query.edit_message_text("❌ Ошибка улучшения безопасности.")
    
    async def _handle_marketing_callback(self, query, game_state, data):
        """Обработка маркетинговых кампаний"""
        # Парсим данные кампании
        campaign_type, level = data.replace("campaign_", "").split('_')
        
        cost = self.config.get_marketing_cost(campaign_type, level)
        
        if game_state.budget < cost:
            await query.edit_message_text(f"❌ Недостаточно средств! Нужно ${cost:,}")
            return
        
        success = self.state_manager.start_marketing_campaign(
            user_id=game_state.user_id,
            campaign_type=campaign_type,
            level=level,
            cost=cost
        )
        
        if success:
            campaign_names = {
                'social_small': 'Социальные сети (малый масштаб)',
                'ads_medium': 'Рекламные кампании (средний масштаб)',
                'content_small': 'Контент-маркетинг (малый масштаб)',
                'influencer_large': 'Партнерство с инфлюенсером (большой масштаб)'
            }
            
            campaign_name = campaign_names.get(data.replace("campaign_", "campaign_"), 'Маркетинговая кампания')
            
            message = f"""
📢 **{campaign_name} запущена!**

📈 Ожидаемый эффект:
• Увеличение активных пользователей
• Рост узнаваемости бренда
• Улучшение NPS

⏱️ Длительность: 3 хода
💰 Инвестиции: ${cost:,}
💵 Оставшийся бюджет: ${game_state.budget - cost:,}

Используйте /next чтобы увидеть результаты кампании.
"""
            await query.edit_message_text(message, parse_mode='Markdown')
        else:
            await query.edit_message_text("❌ Ошибка запуска кампании.")
    
    async def _handle_hosting_callback(self, query, game_state, data):
        """Обработка добавления хостинга"""
        region = data.replace("add_hosting_", "")
        cost = self.config.get_hosting_cost(region, 'basic')
        
        if game_state.budget < cost:
            await query.edit_message_text(f"❌ Недостаточно средств! Нужно ${cost:,}")
            return
        
        success = self.state_manager.add_hosting_region(
            user_id=game_state.user_id,
            region=region,
            level='basic'
        )
        
        if success:
            self.state_manager.update_state(game_state.user_id, {'budget': game_state.budget - cost})
            
            region_names = {
                'russia': 'Россия',
                'netherlands': 'Нидерланды',
                'singapore': 'Сингапур',
                'usa': 'США'
            }
            
            region_name = region_names.get(region, region.title())
            
            message = f"""
🌍 **Новый регион хостинга добавлен: {region_name}!**

🗺️ Географическое покрытие увеличено
🪞 Создано зеркало в новом регионе
💰 Стоимость: ${cost:,}/месяц
💵 Оставшийся бюджет: ${game_state.budget - cost:,}

Это улучшит скорость доступа для пользователей из этого региона.
"""
            await query.edit_message_text(message, parse_mode='Markdown')
        else:
            await query.edit_message_text("❌ Ошибка добавления хостинга.")
    
    async def _handle_event_choice_callback(self, query, game_state, data):
        """Обработка выбора в событии"""
        choice_index = int(data.replace("event_choice_", ""))
        
        # Обрабатываем выбор
        result = self.game_engine.handle_event_choice(game_state, choice_index)
        
        if result['success']:
            choice = result['choice']
            effect = result.get('effect', {})
            
            # Формируем сообщение о результате выбора
            effect_text = "Эффекты:"
            for key, value in effect.items():
                if isinstance(value, int) and value > 0:
                    effect_text += f"\n• {key}: +{value}"
                elif isinstance(value, int) and value < 0:
                    effect_text += f"\n• {key}: {value}"
            
            if effect_text == "Эффекты:":
                effect_text = "Значительных эффектов не произошло."
            
            message = f"""
✅ **{choice}**

{effect_text}

Теперь используйте /next для продолжения развития трекера.
"""
            await query.edit_message_text(message, parse_mode='Markdown')
        else:
            await query.edit_message_text(f"❌ Ошибка обработки выбора: {result.get('message', 'Неизвестная ошибка')}")
    
    async def _handle_execute_action_callback(self, query, game_state, data):
        """Обработка выполнения приоритетных действий"""
        action = data.replace("execute_action_", "")
        
        action_messages = {
            'start_ad_campaign': 'Запуск рекламной кампании поможет привлечь новых пользователей!',
            'request_donations': 'Обращение к сообществу за пожертвованиями увеличит доходы!',
            'hire_staff': 'Найм сотрудников улучшит эффективность всех операций!',
            'upgrade_infrastructure': 'Апгрейд инфраструктуры повысит стабильность и производительность!',
            'start_marketing': 'Маркетинговые кампании увеличат узнаваемость трекера!'
        }
        
        message = action_messages.get(action, 'Это действие поможет развитию вашего трекера!')
        
        await query.edit_message_text(f"🚀 **{message}**\n\nИспользуйте соответствующие команды для выполнения этого действия.\n\n/hire - для найма сотрудников\n/upgrade - для апгрейда инфраструктуры\n/marketing - для маркетинговых кампаний", parse_mode='Markdown')
    
    async def _handle_random_action_callback(self, query, game_state):
        """Обработка случайного действия"""
        actions = [
            "Проанализируйте текущие метрики с /dashboard",
            "Наймите ключевого сотрудника с /hire",
            "Улучшите инфраструктуру с /upgrade",
            "Запустите маркетинговую кампанию с /marketing",
            "Добавьте новый регион хостинга с /hosting",
            "Проверьте юридические риски с /law",
            "Развивайте сообщество с /community"
        ]
        
        import random
        random_action = random.choice(actions)
        
        await query.edit_message_text(f"🎲 **{random_action}**\n\nСлучайное действие выбрано! Последуйте этой рекомендации для развития трекера.", parse_mode='Markdown')
    
    async def _handle_legal_callback(self, query, game_state, data):
        """Обработка юридических действий"""
        actions = {
            'hire_lawyers': {'cost': 40000, 'effect': -15, 'description': 'Снижение юридического риска на 15 пунктов'},
            'increase_transparency': {'cost': 20000, 'effect': -10, 'description': 'Снижение юридического риска на 10 пунктов'},
            'cooperate_rights_holders': {'cost': 30000, 'effect': -12, 'description': 'Снижение юридического риска на 12 пунктов'}
        }
        
        action_info = actions.get(data)
        if not action_info:
            await query.edit_message_text("❌ Неизвестное юридическое действие")
            return
        
        cost = action_info['cost']
        if game_state.budget < cost:
            await query.edit_message_text(f"❌ Недостаточно средств! Нужно ${cost:,}")
            return
        
        # Применяем эффект
        new_risk = max(0, game_state.legal.risk_level + action_info['effect'])
        self.state_manager.update_state(game_state.user_id, {
            'budget': game_state.budget - cost,
            'legal_risk': new_risk
        })
        
        message = f"""
⚖️ **Юридическое действие выполнено!**

✅ {action_info['description']}
💰 Стоимость: ${cost:,}
💵 Оставшийся бюджет: ${game_state.budget - cost:,}
⚠️ Юридический риск: {game_state.legal.risk_level:.1f} → {new_risk:.1f}

Отличная работа по соблюдению требований!
"""
        await query.edit_message_text(message, parse_mode='Markdown')
    
    async def _handle_community_callback(self, query, game_state, data):
        """Обработка действий с сообществом"""
        actions = {
            'host_community_event': {'cost': 25000, 'effect': 'event', 'description': 'Проведение мероприятия для сообщества'},
            'request_donations': {'cost': 0, 'effect': 'donations', 'description': 'Запрос пожертвований у сообщества'},
            'hire_community_manager': {'cost': 80000, 'effect': 'manager', 'description': 'Найм менеджера сообщества'}
        }
        
        action_info = actions.get(data)
        if not action_info:
            await query.edit_message_text("❌ Неизвестное действие с сообществом")
            return
        
        cost = action_info['cost']
        if game_state.budget < cost:
            await query.edit_message_text(f"❌ Недостаточно средств! Нужно ${cost:,}")
            return
        
        if action_info['effect'] == 'donations':
            # Запрос пожертвований
            donation_amount = max(1000, int(game_state.active_users * 10))
            self.state_manager.update_state(game_state.user_id, {
                'donations_monthly': game_state.community.donations_monthly + donation_amount,
                'budget': game_state.budget + donation_amount
            })
            
            message = f"""
👥 **Обращение к сообществу выполнено!**

💝 Сообщество откликнулось и собрало ${donation_amount:,}
💵 Общий бюджет: ${game_state.budget + donation_amount:,}

Спасибо за поддержку от ваших пользователей!
"""
            
        else:
            # Другие действия
            self.state_manager.update_state(game_state.user_id, {'budget': game_state.budget - cost})
            
            message = f"""
👥 **{action_info['description']}**

💰 Стоимость: ${cost:,}
💵 Оставшийся бюджет: ${game_state.budget - cost:,}

Это улучшит здоровье и вовлеченность сообщества!
"""
        
        await query.edit_message_text(message, parse_mode='Markdown')
    
    def _get_role_impact_description(self, role: str) -> str:
        """Получение описания влияния роли"""
        impacts = {
            'CTO': '• +25% к эффективности апгрейдов\n• +15% к стабильности серверов\n• -10% к расходам на инфраструктуру',
            'CMO': '• +20% к эффективности рекламы\n• +10% к конверсии\n• +15% к росту узнаваемости бренда',
            'COO': '• -15% к операционным расходам\n• +10% к общей эффективности\n• +5% к скорости процессов',
            'CLO': '• -20% к юридическим рискам\n• +15% к уровню соответствия\n• +10% к прозрачности',
            'COMMUNITY_MANAGER': '• +15% к удержанию пользователей\n• +20% к здоровью сообщества\n• +10% к пожертвованиям',
            'DATA_ANALYST': '• +10% к точности прогнозов\n• +8% к росту пользователей\n• +5% к общей эффективности'
        }
        return impacts.get(role, '• Улучшает различные аспекты бизнеса')
    
    async def _handle_dashboard_callback(self, query, game_state, data):
        """Обработка детального дашборда"""
        await query.edit_message_text("📊 Детальная аналитика временно недоступна.", parse_mode='Markdown')
    
    async def _handle_setup_callback(self, query, game_state, data):
        """Обработка настройки трекера"""
        if data == "setup_manual":
            # Ручная настройка
            message = """
✏️ **Настройка вручную**

Для настройки вашего трекера отправьте сообщение в формате:

```
Название трекера | Домен
```

Например:
```
Мой Файл Хаб | fileclub.com
```

🌐 **Требования к домену:**
• Домен должен быть в формате "example.com"
• Можно использовать .com, .net, .org, .ru и другие
• Длина домена не должна превышать 63 символа

💡 После отправки мы проверим валидность и применим настройки.
"""
            await query.edit_message_text(message, parse_mode='Markdown')
            
        elif data == "setup_random":
            # Генерация случайных вариантов
            success = self.state_manager.generate_setup_options(game_state.user_id)
            
            if success and game_state.current_setup_options:
                message = """
🎲 **Случайные варианты для вашего трекера**

Выберите один из предложенных вариантов:
"""
                
                keyboard = []
                for i, (name, domain) in enumerate(game_state.current_setup_options):
                    button_text = f"{name} ({domain})"
                    callback_data = f"select_option_{i}"
                    keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(message, parse_mode='Markdown', reply_markup=reply_markup)
            else:
                await query.edit_message_text("❌ Ошибка генерации вариантов. Попробуйте позже.", parse_mode='Markdown')
    
    async def _handle_select_option_callback(self, query, game_state, data):
        """Обработка выбора варианта настройки"""
        option_index = int(data.replace("select_option_", ""))
        
        success = self.state_manager.select_setup_option(game_state.user_id, option_index)
        
        if success:
            # Обновляем состояние в базе
            self.state_manager.save_game(game_state.user_id)
            
            message = f"""
✅ **Трекер успешно настроен!**

🎉 Поздравляем! Ваш файловый хаб настроен и готов к работе.

📊 **Детали настройки:**
• Название: {game_state.tracker_name}
• Домен: {game_state.domain_name}
• Статус: Готов к работе

🚀 **Следующие шаги:**
• Используйте /dashboard для просмотра состояния
• Используйте /upgrade для улучшения инфраструктуры  
• Используйте /hire для найма команды
• Используйте /next для начала первого хода

Удачи в развитии вашего трекера!
"""
            await query.edit_message_text(message, parse_mode='Markdown')
        else:
            await query.edit_message_text("❌ Ошибка выбора варианта. Попробуйте еще раз.", parse_mode='Markdown')