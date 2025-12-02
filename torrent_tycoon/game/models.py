# Модели данных для симулятора файлового хаба

from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from enum import Enum

class UserRole(str, Enum):
    """Роли пользователей в команде"""
    CTO = "CTO"
    CMO = "CMO"
    COO = "COO"
    CLO = "CLO"
    COMMUNITY_MANAGER = "COMMUNITY_MANAGER"
    DATA_ANALYST = "DATA_ANALYST"

class InfrastructureLevel(str, Enum):
    """Уровни инфраструктуры"""
    BASIC = "basic"
    ADVANCED = "advanced"
    ENTERPRISE = "enterprise"

class HostingRegion(str, Enum):
    """Регионы хостинга"""
    RUSSIA = "russia"
    NETHERLANDS = "netherlands"
    SINGAPORE = "singapore"
    USA = "usa"

class Staff(BaseModel):
    """Модель сотрудника"""
    role: UserRole
    name: str
    skill_level: int = Field(default=1, ge=1, le=10)  # Уровень навыков 1-10
    salary: int
    hired: bool = False
    hired_date: Optional[datetime] = None

class Infrastructure(BaseModel):
    """Модель инфраструктуры"""
    server_level: InfrastructureLevel = InfrastructureLevel.BASIC
    bandwidth_level: InfrastructureLevel = InfrastructureLevel.BASIC
    storage_level: InfrastructureLevel = InfrastructureLevel.BASIC
    security_level: InfrastructureLevel = InfrastructureLevel.BASIC
    uptime: float = Field(default=99.0, ge=0, le=100)  # Процент доступности
    load: float = Field(default=50.0, ge=0, le=100)    # Нагрузка на серверы

class Hosting(BaseModel):
    """Модель хостинга"""
    regions: Dict[HostingRegion, InfrastructureLevel] = Field(default_factory=lambda: {
        HostingRegion.RUSSIA: InfrastructureLevel.BASIC
    })
    mirrors_count: int = 1
    failover_enabled: bool = False
    backup_frequency: int = 24  # Часы между резервными копиями

class Marketing(BaseModel):
    """Модель маркетинга"""
    campaigns: Dict[str, Any] = Field(default_factory=dict)
    ad_spend: int = 0
    conversion_rate: float = Field(default=2.5, ge=0, le=100)
    brand_awareness: float = Field(default=10.0, ge=0, le=100)
    nps_score: float = Field(default=50.0, ge=-100, le=100)  # Net Promoter Score

class Community(BaseModel):
    """Модель сообщества"""
    active_users: int = 1000
    retention_rate_30d: float = Field(default=60.0, ge=0, le=100)
    toxicity_level: float = Field(default=20.0, ge=0, le=100)
    moderation_score: float = Field(default=70.0, ge=0, le=100)
    community_health: float = Field(default=75.0, ge=0, le=100)
    events_hosted: int = 0
    donations_monthly: int = 0

class Legal(BaseModel):
    """Модель юридического соответствия"""
    compliance_score: float = Field(default=60.0, ge=0, le=100)
    risk_level: float = Field(default=30.0, ge=0, le=100)
    dmca_notices: int = 0
    transparency_score: float = Field(default=50.0, ge=0, le=100)
    cooperation_level: float = Field(default=40.0, ge=0, le=100)
    legal_budget: int = 0
    pending_cases: int = 0

class Revenue(BaseModel):
    """Модель доходов"""
    ad_revenue: int = 0
    subscription_revenue: int = 0
    donation_revenue: int = 0
    sponsorship_revenue: int = 0
    total_revenue: int = 0
    revenue_growth_rate: float = Field(default=0.0, ge=-100, le=1000)

class Expenses(BaseModel):
    """Модель расходов"""
    infrastructure_cost: int = 0
    staff_cost: int = 0
    marketing_cost: int = 0
    legal_cost: int = 0
    hosting_cost: int = 0
    r_and_d_cost: int = 0
    total_expenses: int = 0

class FinancialMetrics(BaseModel):
    """Финансовые метрики"""
    cash_flow: int = 0
    profit_margin: float = Field(default=0.0, ge=-100, le=100)
    burn_rate: int = 0  # Скорость сжигания денег
    runway_months: float = Field(default=12.0, ge=0)  # Месяцев до банкротства
    roi: float = Field(default=0.0, ge=-100, le=1000)
    customer_acquisition_cost: float = Field(default=0.0, ge=0)

class GameEvent(BaseModel):
    """Модель игрового события"""
    event_type: str
    description: str
    impact: int
    duration_hours: int = 0
    probability: float
    timestamp: datetime
    resolved: bool = False
    choices: List[str] = Field(default_factory=list)
    selected_choice: Optional[str] = None

class GameState(BaseModel):
    """Основное состояние игры"""
    user_id: int
    tracker_name: str = "Мой Файловый Хаб"
    site_name: str = "Мой Трекер"  # Человекочитаемое название
    domain_name: str = "tracker.com"  # Домен сайта
    current_domain_blocked: bool = False  # Заблокирован ли текущий домен
    available_domains: List[str] = Field(default_factory=list)  # Список доступных доменов
    setup_complete: bool = False  # Завершена ли настройка стартового названия и домена
    name_setup_step: str = "none"  # Статус настройки: "none", "name", "domain", "options", "complete"
    current_setup_options: List[Tuple[str, str]] = Field(default_factory=list)  # Текущие варианты для выбора
    current_setup_domain: Optional[str] = None  # Текущий домен для настройки
    domain_block_history: List[Dict[str, Any]] = Field(default_factory=list)  # История блокировок доменов
    last_domain_block_turn: int = 0  # Последний ход блокировки домена
    next_domain_check_turn: int = 5  # Следующая проверка блокировки домена
    current_turn: int = 1
    total_turns: int = 100
    
    # Основные ресурсы
    budget: int = 100000
    active_users: int = 3  # Начальные 2-3 пользователя
    mau: int = 5  # Monthly Active Users
    
    # Компоненты системы
    staff: Dict[str, Staff] = Field(default_factory=dict)
    infrastructure: Infrastructure = Field(default_factory=Infrastructure)
    hosting: Hosting = Field(default_factory=Hosting)
    marketing: Marketing = Field(default_factory=Marketing)
    community: Community = Field(default_factory=Community)
    legal: Legal = Field(default_factory=Legal)
    revenue: Revenue = Field(default_factory=Revenue)
    expenses: Expenses = Field(default_factory=Expenses)
    financial: FinancialMetrics = Field(default_factory=FinancialMetrics)
    
    # Игровая механика
    actions_remaining: int = 3
    last_event: Optional[GameEvent] = None
    recent_events: List[GameEvent] = Field(default_factory=list)
    game_started: datetime = Field(default_factory=datetime.now)
    last_turn_date: datetime = Field(default_factory=datetime.now)
    
    # Настройки игры
    game_speed: int = 24  # Часов за ход
    auto_save: bool = True
    notifications_enabled: bool = True
    
    class Config:
        use_enum_values = True

class GameAction(BaseModel):
    """Модель игрового действия"""
    action_type: str
    description: str
    cost: int
    impact: Dict[str, Any]
    cooldown_turns: int = 0
    prerequisites: List[str] = Field(default_factory=list)
    available: bool = True

class UpgradeOption(BaseModel):
    """Модель варианта апгрейда"""
    upgrade_type: str
    level: InfrastructureLevel
    cost: int
    benefits: Dict[str, Any]
    description: str

class MarketingCampaign(BaseModel):
    """Модель маркетинговой кампании"""
    campaign_type: str
    level: str
    cost: int
    duration_days: int
    expected_impact: Dict[str, Any]
    description: str

class LegalChallenge(BaseModel):
    """Модель юридического вызова"""
    challenge_type: str
    description: str
    severity: int
    response_options: Dict[str, Dict[str, Any]]
    deadline_hours: int
    created_date: datetime