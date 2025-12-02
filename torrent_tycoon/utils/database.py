# Модуль базы данных для симулятора

import sqlite3
import json
import logging
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class Database:
    """Класс для работы с базой данных игры"""
    
    def __init__(self, db_path: str = "file_hub_tycoon.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Инициализация базы данных"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Таблица игроков
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS players (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        first_name TEXT,
                        last_name TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_played TIMESTAMP,
                        total_games INTEGER DEFAULT 0,
                        best_score INTEGER DEFAULT 0,
                        current_game_id INTEGER
                    )
                ''')
                
                # Таблица игр
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS games (
                        game_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        tracker_name TEXT,
                        game_state TEXT,  -- JSON
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        completed_at TIMESTAMP,
                        is_active BOOLEAN DEFAULT 1,
                        FOREIGN KEY (user_id) REFERENCES players (user_id)
                    )
                ''')
                
                # Таблица событий
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS game_events (
                        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        game_id INTEGER,
                        event_type TEXT,
                        description TEXT,
                        impact INTEGER,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        resolved BOOLEAN DEFAULT 0,
                        choices TEXT,  -- JSON
                        selected_choice TEXT,
                        FOREIGN KEY (game_id) REFERENCES games (game_id)
                    )
                ''')
                
                # Таблица действий
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS game_actions (
                        action_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        game_id INTEGER,
                        action_type TEXT,
                        description TEXT,
                        cost INTEGER,
                        turn_number INTEGER,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (game_id) REFERENCES games (game_id)
                    )
                ''')
                
                # Таблица достижений
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS achievements (
                        achievement_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        achievement_type TEXT,
                        achievement_name TEXT,
                        description TEXT,
                        earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        game_id INTEGER,
                        FOREIGN KEY (user_id) REFERENCES players (user_id),
                        FOREIGN KEY (game_id) REFERENCES games (game_id)
                    )
                ''')
                
                conn.commit()
                logger.info("База данных успешно инициализирована")
                
        except Exception as e:
            logger.error(f"Ошибка инициализации базы данных: {e}")
            raise
    
    def save_player(self, user_id: int, username: str = None, 
                   first_name: str = None, last_name: str = None) -> bool:
        """Сохранение информации о игроке"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO players 
                    (user_id, username, first_name, last_name, last_played)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (user_id, username, first_name, last_name))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка сохранения игрока {user_id}: {e}")
            return False
    
    def get_player(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получение информации о игроке"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM players WHERE user_id = ?
                ''', (user_id,))
                row = cursor.fetchone()
                
                if row:
                    columns = [description[0] for description in cursor.description]
                    return dict(zip(columns, row))
                return None
                
        except Exception as e:
            logger.error(f"Ошибка получения игрока {user_id}: {e}")
            return None
    
    def save_game(self, user_id: int, tracker_name: str, 
                  game_state: Dict[str, Any], game_id: Optional[int] = None) -> int:
        """Сохранение состояния игры"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                game_state_json = json.dumps(game_state, default=str, ensure_ascii=False)
                
                if game_id:
                    cursor.execute('''
                        UPDATE games 
                        SET tracker_name = ?, game_state = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE game_id = ? AND user_id = ?
                    ''', (tracker_name, game_state_json, game_id, user_id))
                    conn.commit()
                    return game_id
                else:
                    cursor.execute('''
                        INSERT INTO games (user_id, tracker_name, game_state)
                        VALUES (?, ?, ?)
                    ''', (user_id, tracker_name, game_state_json))
                    game_id = cursor.lastrowid
                    
                    # Обновляем ссылку на текущую игру у игрока
                    cursor.execute('''
                        UPDATE players SET current_game_id = ? WHERE user_id = ?
                    ''', (game_id, user_id))
                    
                    conn.commit()
                    return game_id
                    
        except Exception as e:
            logger.error(f"Ошибка сохранения игры: {e}")
            raise
    
    def load_game(self, game_id: int) -> Optional[Dict[str, Any]]:
        """Загрузка состояния игры"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM games WHERE game_id = ?
                ''', (game_id,))
                row = cursor.fetchone()
                
                if row:
                    columns = [description[0] for description in cursor.description]
                    game_data = dict(zip(columns, row))
                    
                    # Декодируем JSON состояние игры
                    if game_data['game_state']:
                        game_data['game_state'] = json.loads(game_data['game_state'])
                    
                    return game_data
                return None
                
        except Exception as e:
            logger.error(f"Ошибка загрузки игры {game_id}: {e}")
            return None
    
    def load_active_game(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Загрузка активной игры игрока"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM games 
                    WHERE user_id = ? AND is_active = 1 
                    ORDER BY updated_at DESC 
                    LIMIT 1
                ''', (user_id,))
                row = cursor.fetchone()
                
                if row:
                    columns = [description[0] for description in cursor.description]
                    game_data = dict(zip(columns, row))
                    
                    if game_data['game_state']:
                        game_data['game_state'] = json.loads(game_data['game_state'])
                    
                    return game_data
                return None
                
        except Exception as e:
            logger.error(f"Ошибка загрузки активной игры для игрока {user_id}: {e}")
            return None
    
    def complete_game(self, game_id: int, user_id: int):
        """Завершение игры"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Получаем финальное состояние игры
                game_data = self.load_game(game_id)
                if game_data:
                    final_score = self._calculate_final_score(game_data['game_state'])
                    
                    # Обновляем статистику игрока
                    cursor.execute('''
                        UPDATE players 
                        SET total_games = total_games + 1,
                            best_score = MAX(best_score, ?),
                            last_played = CURRENT_TIMESTAMP,
                            current_game_id = NULL
                        WHERE user_id = ?
                    ''', (final_score, user_id))
                    
                    # Помечаем игру как завершенную
                    cursor.execute('''
                        UPDATE games 
                        SET is_active = 0, completed_at = CURRENT_TIMESTAMP
                        WHERE game_id = ?
                    ''', (game_id,))
                    
                    conn.commit()
                    
        except Exception as e:
            logger.error(f"Ошибка завершения игры {game_id}: {e}")
    
    def _calculate_final_score(self, game_state: Dict[str, Any]) -> int:
        """Расчет итогового счета игры"""
        try:
            # Базовый счет от активных пользователей
            base_score = game_state.get('active_users', 0)
            
            # Бонусы за метрики
            community_bonus = game_state.get('community', {}).get('active_users', 0) * 0.1
            revenue_bonus = game_state.get('revenue', {}).get('total_revenue', 0) * 0.001
            legal_bonus = (100 - game_state.get('legal', {}).get('risk_level', 50)) * 10
            nps_bonus = (game_state.get('marketing', {}).get('nps_score', 0) + 100) * 5
            
            final_score = int(base_score + community_bonus + revenue_bonus + legal_bonus + nps_bonus)
            return max(0, final_score)
            
        except Exception as e:
            logger.error(f"Ошибка расчета итогового счета: {e}")
            return 0
    
    def save_event(self, game_id: int, event_type: str, description: str, 
                   impact: int, choices: list = None) -> int:
        """Сохранение игрового события"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                choices_json = json.dumps(choices) if choices else None
                
                cursor.execute('''
                    INSERT INTO game_events (game_id, event_type, description, impact, choices)
                    VALUES (?, ?, ?, ?, ?)
                ''', (game_id, event_type, description, impact, choices_json))
                
                event_id = cursor.lastrowid
                conn.commit()
                return event_id
                
        except Exception as e:
            logger.error(f"Ошибка сохранения события: {e}")
            return 0
    
    def save_action(self, game_id: int, action_type: str, description: str, 
                   cost: int, turn_number: int) -> int:
        """Сохранение игрового действия"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO game_actions (game_id, action_type, description, cost, turn_number)
                    VALUES (?, ?, ?, ?, ?)
                ''', (game_id, action_type, description, cost, turn_number))
                
                action_id = cursor.lastrowid
                conn.commit()
                return action_id
                
        except Exception as e:
            logger.error(f"Ошибка сохранения действия: {e}")
            return 0
    
    def get_leaderboard(self, limit: int = 10) -> list:
        """Получение таблицы лидеров"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT username, first_name, best_score, total_games, last_played
                    FROM players 
                    WHERE best_score > 0
                    ORDER BY best_score DESC, total_games ASC
                    LIMIT ?
                ''', (limit,))
                
                rows = cursor.fetchall()
                return [dict(zip([desc[0] for desc in cursor.description], row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Ошибка получения таблицы лидеров: {e}")
            return []
    
    def get_player_stats(self, user_id: int) -> Dict[str, Any]:
        """Получение статистики игрока"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Основная статистика
                cursor.execute('''
                    SELECT total_games, best_score, last_played
                    FROM players WHERE user_id = ?
                ''', (user_id,))
                player_row = cursor.fetchone()
                
                if not player_row:
                    return {}
                
                # Статистика игр
                cursor.execute('''
                    SELECT COUNT(*) as completed_games, AVG(turn_number) as avg_turns
                    FROM game_actions ga
                    JOIN games g ON ga.game_id = g.game_id
                    WHERE g.user_id = ? AND g.completed_at IS NOT NULL
                ''', (user_id,))
                games_row = cursor.fetchone()
                
                return {
                    'total_games': player_row[0] or 0,
                    'best_score': player_row[1] or 0,
                    'last_played': player_row[2],
                    'completed_games': games_row[0] if games_row else 0,
                    'avg_turns': round(games_row[1], 1) if games_row and games_row[1] else 0
                }
                
        except Exception as e:
            logger.error(f"Ошибка получения статистики игрока {user_id}: {e}")
            return {}