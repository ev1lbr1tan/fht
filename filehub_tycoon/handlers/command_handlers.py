# Обработчики команд для телеграм-бота

import logging
from typing import Optional, Dict, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from game.models import UserRole, InfrastructureLevel, HostingRegion
from utils.config import Config

logger = logging.getLogger(__name__)

class CommandHandlers:
    """Класс обработчиков команд бота"""
    
    def __init__(self, state_manager, game_engine):
        self.state_manager = state_manager
        self.game_engine = game_engine
        self.config = Config()
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user = update.effective_user
        
        # Проверяем, есть ли у пользователя активная игра
        game_state = self.state_manager.load_game(user.id)
        
        if not game_state:
            # Создаем новую игру
            game_state = self.state_manager.create_new_game(
                user_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name
            )
            
            welcome_text = """
🎮 **Добро пожаловать в File Hub Tycoon!**

Вы - CEO файлового хаба, который только начинает свой путь.
Ваша цель - стать самым популярным и устойчивым файловым центром на рынке!

🎯 **Первый шаг - настройка вашего хаба**

Сначала давайте придумаем название для вашего хаба и выберем домен.
Это определит идентичность вашего проекта на весь игровой процесс.

**Способы настройки:**
1️⃣ Ввести свое название и домен вручную
2️⃣ Использовать генератор случайных вариантов

💡 Выберите способ настройки:
"""
            
            keyboard = [
                [InlineKeyboardButton("✏️ Ввести вручную", callback_data="setup_manual")],
                [InlineKeyboardButton("🎲 Случайные варианты", callback_data="setup_random")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
        else:
            # Проверяем, завершена ли настройка
            if not game_state.setup_complete:
                welcome_text = """
🎯 **Настройка хаба не завершена**

Для продолжения игры необходимо настроить название и домен вашего хаба.

**Выберите способ настройки:**
"""
                
                keyboard = [
                    [InlineKeyboardButton("✏️ Ввести вручную", callback_data="setup_manual")],
                    [InlineKeyboardButton("🎲 Случайные варианты", callback_data="setup_random")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
            else:
                welcome_text = f"""
🎮 **Добро пожаловать обратно!**

📊 **Состояние вашего хаба:**
• Название: {game_state.tracker_name}
• Домен: {game_state.domain_name}
• Бюджет: ${game_state.budget:,}
• Активные пользователи: {game_state.active_users:,}
• Ход: {game_state.current_turn}
• Действий осталось: {game_state.actions_remaining}

Используйте /dashboard для подробной информации или /next для продолжения игры.
"""
                reply_markup = None
        
        await update.message.reply_text(welcome_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def dashboard_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /dashboard"""
        user_id = update.effective_user.id
        game_state = self.state_manager.get_game_state(user_id)
        
        if not game_state:
            await update.message.reply_text("❌ Игра не найдена. Используйте /start для создания новой игры.")
            return
        
        dashboard_text = self._format_dashboard(game_state)
        
        # Кнопки для навигации
        keyboard = [
            [InlineKeyboardButton("📈 Детали", callback_data="dashboard_details")],
            [InlineKeyboardButton("💰 Финансы", callback_data="dashboard_finance")],
            [InlineKeyboardButton("👥 Команда", callback_data="dashboard_team")],
            [InlineKeyboardButton("🔧 Инфраструктура", callback_data="dashboard_infra")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(dashboard_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def plan_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /plan"""
        user_id = update.effective_user.id
        game_state = self.state_manager.get_game_state(user_id)
        
        if not game_state:
            await update.message.reply_text("❌ Игра не найдена. Используйте /start для создания новой игры.")
            return
        
        # Анализ текущего состояния и рекомендации
        analysis = self._analyze_current_state(game_state)
        
        plan_text = f"""
🎯 **Стратегический план**

{analysis['status']}

💡 **Рекомендации:**
{analysis['recommendations']}

🎲 **Случайные события следующего хода:**
{analysis['events_preview']}

⚡ **Приоритетные действия:**
{analysis['priorities']}
"""
        
        keyboard = [
            [InlineKeyboardButton("🚀 Приоритет #1", callback_data=f"execute_action_{analysis['priority_1_action']}")],
            [InlineKeyboardButton("⚡ Приоритет #2", callback_data=f"execute_action_{analysis['priority_2_action']}")],
            [InlineKeyboardButton("🎲 Случайное действие", callback_data="random_action")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(plan_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def hire_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /hire"""
        user_id = update.effective_user.id
        game_state = self.state_manager.get_game_state(user_id)
        
        if not game_state:
            await update.message.reply_text("❌ Игра не найдена. Используйте /start для создания новой игры.")
            return
        
        # Формируем список доступных ролей
        available_roles = []
        for role in UserRole:
            if role.value not in game_state.staff or not game_state.staff[role.value].hired:
                salary = self.config.get_staff_salary(role.value)
                skill_effect = self._get_role_skill_effect(role.value)
                available_roles.append(f"{role.value} - ${salary:,}/мес\n{skill_effect}")
        
        hire_text = f"""
👥 **Найм персонала**

💰 Бюджет: ${game_state.budget:,}
👨‍💼 Нанято сотрудников: {len([s for s in game_state.staff.values() if s.hired])}

**Доступные роли:**

{chr(10).join(available_roles) if available_roles else 'Вся команда уже нанята!'}

💡 Влияние персонала:
• CTO - Ускоряет апгрейды инфраструктуры
• CMO - Увеличивает эффективность рекламы  
• COO - Снижает операционные расходы
• CLO - Уменьшает юридические риски
• Community Manager - Улучшает удержание пользователей
• Data Analyst - Дает преимущества в аналитике
"""
        
        # Создаем кнопки для найма
        keyboard = []
        for role in UserRole:
            if role.value not in game_state.staff or not game_state.staff[role.value].hired:
                salary = self.config.get_staff_salary(role.value)
                name = f"Hire {role.value} (${salary:,})"
                callback_data = f"hire_{role.value}"
                keyboard.append([InlineKeyboardButton(name, callback_data=callback_data)])
        
        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
        
        await update.message.reply_text(hire_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def upgrade_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /upgrade"""
        user_id = update.effective_user.id
        game_state = self.state_manager.get_game_state(user_id)
        
        if not game_state:
            await update.message.reply_text("❌ Игра не найдена. Используйте /start для создания новой игры.")
            return
        
        upgrade_text = f"""
🔧 **Апгрейд инфраструктуры**

💰 Бюджет: ${game_state.budget:,}

**Текущая инфраструктура:**
• Серверы: {game_state.infrastructure.server_level.value}
• Пропускная способность: {game_state.infrastructure.bandwidth_level.value}  
• Хранилище: {game_state.infrastructure.storage_level.value}
• Безопасность: {game_state.infrastructure.security_level.value}

**Доступные апгрейды:**
"""
        
        keyboard = []
        
        # Добавляем кнопки для апгрейда серверов
        server_cost = self.config.get_infrastructure_cost('server_upgrade', 'advanced')
        if game_state.infrastructure.server_level == InfrastructureLevel.BASIC:
            keyboard.append([InlineKeyboardButton(f"🔧 Апгрейд серверов до Advanced (${server_cost:,})", callback_data="upgrade_server_advanced")])
        
        bandwidth_cost = self.config.get_infrastructure_cost('bandwidth_increase', 'advanced')
        if game_state.infrastructure.bandwidth_level == InfrastructureLevel.BASIC:
            keyboard.append([InlineKeyboardButton(f"⚡ Увеличить пропускную способность до Advanced (${bandwidth_cost:,})", callback_data="upgrade_bandwidth_advanced")])
        
        security_cost = self.config.get_infrastructure_cost('security_enhancement', 'advanced')
        if game_state.infrastructure.security_level == InfrastructureLevel.BASIC:
            keyboard.append([InlineKeyboardButton(f"🛡️ Улучшить безопасность до Advanced (${security_cost:,})", callback_data="upgrade_security_advanced")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(upgrade_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def marketing_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /marketing"""
        user_id = update.effective_user.id
        game_state = self.state_manager.get_game_state(user_id)
        
        if not game_state:
            await update.message.reply_text("❌ Игра не найдена. Используйте /start для создания новой игры.")
            return
        
        marketing_text = f"""
📢 **Маркетинг и реклама**

💰 Бюджет: ${game_state.budget:,}
📊 Текущие метрики:
• NPS: {game_state.marketing.nps_score:.1f}
• Узнаваемость бренда: {game_state.marketing.brand_awareness:.1f}%
• Конверсия в премиум: {game_state.marketing.conversion_rate:.1f}%

**Активные кампании:**
{self._format_active_campaigns(game_state.marketing.campaigns)}

**Доступные кампании:**
"""
        
        keyboard = [
            [InlineKeyboardButton("📱 Соц. сети (small $20k)", callback_data="campaign_social_small")],
            [InlineKeyboardButton("🎯 Реклама (medium $75k)", callback_data="campaign_ads_medium")],
            [InlineKeyboardButton("📝 Контент-маркетинг (small $35k)", callback_data="campaign_content_small")],
            [InlineKeyboardButton("🌟 Партнерство с инфлюенсером (large $150k)", callback_data="campaign_influencer_large")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(marketing_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def hosting_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /hosting"""
        user_id = update.effective_user.id
        game_state = self.state_manager.get_game_state(user_id)
        
        if not game_state:
            await update.message.reply_text("❌ Игра не найдена. Используйте /start для создания новой игры.")
            return
        
        hosting_text = f"""
🌍 **Управление хостингом**

🌐 Текущие регионы: {len(game_state.hosting.regions)}
🪞 Зеркала: {game_state.hosting.mirrors_count}

**Активные локации:**
"""
        
        for region, level in game_state.hosting.regions.items():
            hosting_text += f"• {region.title()}: {level.value}\n"
        
        hosting_text += "\n**Доступные регионы:**"
        
        keyboard = []
        
        for region in HostingRegion:
            if region.value not in game_state.hosting.regions:
                cost = self.config.get_hosting_cost(region.value, 'basic')
                keyboard.append([InlineKeyboardButton(f"🌍 {region.value.title()} (${cost:,})", callback_data=f"add_hosting_{region.value}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(hosting_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def law_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /law"""
        user_id = update.effective_user.id
        game_state = self.state_manager.get_game_state(user_id)
        
        if not game_state:
            await update.message.reply_text("❌ Игра не найдена. Используйте /start для создания новой игры.")
            return
        
        law_text = f"""
⚖️ **Юридические вопросы**

⚠️ Юридический риск: {game_state.legal.risk_level:.1f}/100
✅ Уровень соответствия: {game_state.legal.compliance_score:.1f}%
📋 DMCA уведомления: {game_state.legal.dmca_notices}
💡 Прозрачность: {game_state.legal.transparency_score:.1f}%

**Состояние:**
{self._get_legal_status(game_state.legal.risk_level)}

**Действия по снижению риска:**
"""
        
        keyboard = [
            [InlineKeyboardButton("⚖️ Нанять юристов ($40k)", callback_data="hire_lawyers")],
            [InlineKeyboardButton("📋 Повысить прозрачность ($20k)", callback_data="increase_transparency")],
            [InlineKeyboardButton("🤝 Сотрудничать с правообладателями ($30k)", callback_data="cooperate_rights_holders")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(law_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def community_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /community"""
        user_id = update.effective_user.id
        game_state = self.state_manager.get_game_state(user_id)
        
        if not game_state:
            await update.message.reply_text("❌ Игра не найдена. Используйте /start для создания новой игры.")
            return
        
        community_text = f"""
👥 **Управление сообществом**

👨‍👩‍👧‍👦 Активные пользователи: {game_state.active_users:,}
📈 Удержание 30 дней: {game_state.community.retention_rate_30d:.1f}%
🎯 Здоровье сообщества: {game_state.community.community_health:.1f}%
💰 Пожертвования в месяц: ${game_state.community.donations_monthly:,}

**Действия:**
"""
        
        keyboard = [
            [InlineKeyboardButton("🎉 Провести мероприятие ($25k)", callback_data="host_community_event")],
            [InlineKeyboardButton("💝 Запросить пожертвования", callback_data="request_donations")],
            [InlineKeyboardButton("👨‍💼 Нанять Community Manager", callback_data="hire_community_manager")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(community_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def next_turn_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /next"""
        user_id = update.effective_user.id
        game_state = self.state_manager.get_game_state(user_id)
        
        if not game_state:
            await update.message.reply_text("❌ Игра не найдена. Используйте /start для создания новой игры.")
            return
        
        # Проверяем, есть ли нерешенные события
        if game_state.last_event and not game_state.last_event.resolved:
            await update.message.reply_text(
                "⚠️ У вас есть нерешенное событие! Сначала решите его.",
                reply_markup=self._create_event_keyboard(game_state.last_event)
            )
            return
        
        # Обрабатываем ход
        turn_results = self.game_engine.process_turn(game_state)
        
        # Формируем отчет о ходе
        turn_report = f"""
🎲 **Ход {game_state.current_turn} завершен!**

📊 **Изменения:**
{self._format_turn_changes(turn_results['metrics_changed'])}

🎯 **Новое событие:**
{self._format_event_info(turn_results.get('new_events', []))}

💰 **Финансы:**
• Доходы: ${turn_results['metrics_changed'].get('total_revenue', 0):,}
• Расходы: ${turn_results['metrics_changed'].get('total_expenses', 0):,}
• Денежный поток: ${turn_results['metrics_changed'].get('cash_flow', 0):,}

{self._get_turn_status(turn_results['status'])}
"""
        
        # Если есть новое событие, показываем кнопки для решения
        if turn_results.get('new_events'):
            reply_markup = self._create_event_keyboard(turn_results['new_events'][0])
            await update.message.reply_text(turn_report, parse_mode='Markdown', reply_markup=reply_markup)
        else:
            await update.message.reply_text(turn_report, parse_mode='Markdown')
        
        # Переходим к следующему ходу
        self.state_manager.advance_turn(user_id)
        self.state_manager.save_game(user_id)
    
    async def save_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /save"""
        user_id = update.effective_user.id
        
        if self.state_manager.save_game(user_id):
            await update.message.reply_text("✅ Игра сохранена!")
        else:
            await update.message.reply_text("❌ Ошибка сохранения игры.")
    
    async def load_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /load"""
        user_id = update.effective_user.id
        game_state = self.state_manager.load_game(user_id)
        
        if game_state:
            await update.message.reply_text("✅ Игра загружена! Используйте /dashboard для просмотра состояния.")
        else:
            await update.message.reply_text("❌ Активная игра не найдена.")
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений"""
        text = update.message.text.lower()
        
        # Проверяем, есть ли у пользователя активная игра
        user_id = update.effective_user.id
        game_state = self.state_manager.get_game_state(user_id)
        
        # Если игра есть и настройка не завершена, обрабатываем как настройку
        if game_state and not game_state.setup_complete:
            await self._handle_setup_text(update, context)
            return
        
        # Обработка обычных команд
        if 'help' in text or 'помощь' in text:
            await update.message.reply_text(self._get_help_text())
        elif 'stats' in text or 'статистика' in text:
            await self.dashboard_command(update, context)
        elif 'продолжить' in text or 'next' in text:
            await self.next_turn_command(update, context)
        else:
            await update.message.reply_text("💡 Используйте команды: /dashboard, /plan, /hire, /upgrade, /marketing, /hosting, /law, /community, /next")
    
    async def _handle_setup_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений для настройки"""
        user_id = update.effective_user.id
        game_state = self.state_manager.get_game_state(user_id)
        
        if not game_state or game_state.setup_complete:
            return
        
        text = update.message.text.strip()
        
        # Парсим формат "Название | Домен"
        if '|' in text:
            parts = text.split('|', 1)
            if len(parts) == 2:
                name = parts[0].strip()
                domain = parts[1].strip()
                
                # Проверяем валидность домена
                from utils.name_generator import TrackerNameGenerator
                if not TrackerNameGenerator.validate_domain(domain):
                    await update.message.reply_text(
                        f"❌ **Ошибка валидации домена**\n\n"
                        f"Домен '{domain}' не соответствует требованиям:\n"
                        f"• Должен быть в формате example.com\n"
                        f"• Можно использовать .com, .net, .org, .ru и другие\n"
                        f"• Длина не более 63 символов\n\n"
                        f"Попробуйте еще раз в формате:\n"
                        f"`Название файлообменника | Корректный домен`",
                        parse_mode='Markdown'
                    )
                    return
                
                # Устанавливаем название и домен
                name_success = self.state_manager.setup_hub_name(user_id, name)
                domain_success = self.state_manager.setup_hub_domain(user_id, domain)
                
                if name_success and domain_success:
                    # Сохраняем игру
                    self.state_manager.save_game(user_id)
                    
                    message = f"""
✅ **Трекер успешно настроен!**

🎉 Поздравляем! Ваш файловый хаб настроен и готов к работе.

📊 **Детали настройки:**
• Название: {name}
• Домен: {domain}
• Статус: Готов к работе

🚀 **Следующие шаги:**
• Используйте /dashboard для просмотра состояния
• Используйте /upgrade для улучшения инфраструктуры  
• Используйте /hire для найма команды
• Используйте /next для начала первого хода

Удачи в развитии вашего файлообменника!
"""
                    await update.message.reply_text(message, parse_mode='Markdown')
                else:
                    await update.message.reply_text("❌ Ошибка настройки. Попробуйте еще раз.", parse_mode='Markdown')
            else:
                await update.message.reply_text(
                    "❌ Неверный формат. Используйте:\n"
                    "`Название файлообменника | Домен`\n\n"
                    "Например:\n"
                    "`Мой Файл Хаб | fileclub.com`",
                    parse_mode='Markdown'
                )
        else:
            await update.message.reply_text(
                "❌ Неверный формат. Используйте:\n"
                "`Название файлообменника | Домен`\n\n"
                "Например:\n"
                "`Мой Файл Хаб | fileclub.com`",
                parse_mode='Markdown'
            )
    
    def _format_dashboard(self, game_state) -> str:
        """Форматирование дашборда"""
        return f"""
📊 **Дашборд файлообменника "{game_state.tracker_name}"**

💰 **Финансы:**
• Бюджет: ${game_state.budget:,}
• Денежный поток: ${game_state.financial.cash_flow:,}/ход
• Расходы: ${game_state.expenses.total_expenses:,}/ход

👥 **Пользователи:**
• Активные: {game_state.active_users:,}
• MAU: {game_state.mau:,}
• Удержание 30д: {game_state.community.retention_rate_30d:.1f}%

🏢 **Команда:**
• Сотрудников: {len([s for s in game_state.staff.values() if s.hired])}

🔧 **Инфраструктура:**
• Уровень серверов: {game_state.infrastructure.server_level.value}
• Доступность: {game_state.infrastructure.uptime:.1f}%

🎯 **Цели:**
• NPS: {game_state.marketing.nps_score:.1f}
• Юридический риск: {game_state.legal.risk_level:.1f}/100

⚡ Действий осталось: {game_state.actions_remaining}
"""
    
    def _format_active_campaigns(self, campaigns: Dict) -> str:
        """Форматирование активных кампаний"""
        if not campaigns:
            return "• Нет активных кампаний"
        
        campaign_list = []
        for name, campaign in campaigns.items():
            campaign_list.append(f"• {name} (запуск в ходу {campaign.get('start_turn', 0)})")
        
        return "\n".join(campaign_list)
    
    def _get_role_skill_effect(self, role: str) -> str:
        """Получение эффекта роли"""
        effects = {
            'CTO': '+20% к эффективности апгрейдов инфраструктуры',
            'CMO': '+15% к эффективности рекламных кампаний',
            'COO': '-10% к операционным расходам',
            'CLO': '-15% к юридическим рискам',
            'COMMUNITY_MANAGER': '+10% к удержанию пользователей',
            'DATA_ANALYST': '+5% к росту пользователей'
        }
        return effects.get(role, 'Улучшает различные аспекты бизнеса')
    
    def _analyze_current_state(self, game_state) -> Dict[str, str]:
        """Анализ текущего состояния игры"""
        analysis = {
            'status': '',
            'recommendations': '',
            'events_preview': '',
            'priorities': '',
            'priority_1_action': '',
            'priority_2_action': ''
        }
        
        # Анализ бюджета
        if game_state.budget < 50000:
            analysis['status'] = "⚠️ **Критическое состояние бюджета**\nНужны срочные меры по увеличению доходов!"
            analysis['recommendations'] = "• Запустить рекламную кампанию\n• Сократить необязательные расходы\n• Попросить пожертвования у сообщества"
            analysis['priority_1_action'] = 'start_ad_campaign'
            analysis['priority_2_action'] = 'request_donations'
        elif game_state.budget < 100000:
            analysis['status'] = "⚠️ **Низкий бюджет**\nРекомендуется увеличить доходы."
            analysis['recommendations'] = "• Нанять опытных сотрудников\n• Улучшить инфраструктуру\n• Развивать сообщество"
            analysis['priority_1_action'] = 'hire_staff'
            analysis['priority_2_action'] = 'upgrade_infrastructure'
        else:
            analysis['status'] = "✅ **Стабильное состояние**\nПродолжайте развитие!"
            analysis['recommendations'] = "• Масштабировать инфраструктуру\n• Расширять маркетинг\n• Диверсифицировать хостинг"
            analysis['priority_1_action'] = 'upgrade_infrastructure'
            analysis['priority_2_action'] = 'start_marketing'
        
        analysis['events_preview'] = "• DDoS атака (15% вероятность)\n• Вирусный рост (8% вероятность)\n• Проверка регуляторов (6% вероятность)"
        analysis['priorities'] = "1. Увеличить доходы\n2. Снизить риски\n3. Масштабировать систему"
        
        return analysis
    
    def _get_legal_status(self, risk_level: float) -> str:
        """Получение статуса юридических рисков"""
        if risk_level >= 80:
            return "🚨 **КРИТИЧЕСКИЙ РИСК** - Немедленные действия требуются!"
        elif risk_level >= 60:
            return "⚠️ **ВЫСОКИЙ РИСК** - Рекомдуется снижение рисков"
        elif risk_level >= 40:
            return "🟡 **СРЕДНИЙ РИСК** - Внимание к юридическим вопросам"
        else:
            return "🟢 **НИЗКИЙ РИСК** - Хорошее состояние соответствия"
    
    def _format_turn_changes(self, changes: Dict) -> str:
        """Форматирование изменений за ход"""
        if not changes:
            return "• Значительных изменений не произошло"
        
        change_list = []
        for metric, value in changes.items():
            if value > 0:
                change_list.append(f"• {metric}: +{value}")
            elif value < 0:
                change_list.append(f"• {metric}: {value}")
        
        return "\n".join(change_list[:5])  # Показываем только первые 5 изменений
    
    def _format_event_info(self, events: list) -> str:
        """Форматирование информации о событиях"""
        if not events:
            return "• Событий не произошло"
        
        event_info = []
        for event in events:
            event_info.append(f"• {event.description}")
        
        return "\n".join(event_info)
    
    def _get_turn_status(self, status: str) -> str:
        """Получение статуса хода"""
        if status == 'win':
            return "🏆 **ПОЗДРАВЛЯЕМ!** Вы достигли всех целей и стали лучшим файлообменником!"
        elif status == 'lose':
            return "💀 **ИГРА ОКОНЧЕНА** Критические проблемы привели к банкротству"
        else:
            return "➡️ Готов к следующему ходу. Используйте /next"
    
    def _create_event_keyboard(self, event) -> InlineKeyboardMarkup:
        """Создание клавиатуры для события"""
        keyboard = []
        for i, choice in enumerate(event.choices):
            keyboard.append([InlineKeyboardButton(choice, callback_data=f"event_choice_{i}")])
        
        return InlineKeyboardMarkup(keyboard)
    
    def _get_help_text(self) -> str:
        """Получение текста помощи"""
        return """
🤖 **File Hub Tycoon - Помощь**

**Основные команды:**
/start - Начать новую игру или продолжить
/dashboard - Просмотр состояния файлообменника  
/plan - Стратегический анализ и рекомендации
/upgrade - Апгрейд серверов и инфраструктуры
/hire - Найм сотрудников в команду
/marketing - Запуск рекламных кампаний
/hosting - Управление регионами хостинга
/law - Юридические вопросы и риски
/community - Развитие сообщества пользователей
/next - Переход к следующему ходу
/save - Сохранение игры
/load - Загрузка сохраненной игры

**Цель игры:**
Стать самым популярным и устойчивым файловым хабом!
Достигните 1 млн пользователей, высокий NPS и низкие риски.

**Удачи в развитии! 🚀**
"""