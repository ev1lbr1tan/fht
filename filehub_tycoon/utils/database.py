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

                # Таблица игр - хранит состояние игры для каждого пользователя
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS games (
                        user_id INTEGER PRIMARY KEY,
                        tracker_name TEXT,
                        game_state TEXT,  -- JSON
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                conn.commit()
                logger.info("База данных успешно инициализирована")

        except Exception as e:
            logger.error(f"Ошибка инициализации базы данных: {e}")
            raise
    
    def save_game(self, user_id: int, tracker_name: str, game_state: Dict[str, Any]) -> bool:
        """Сохранение состояния игры для пользователя"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                game_state_json = json.dumps(game_state, default=str, ensure_ascii=False)

                cursor.execute('''
                    INSERT OR REPLACE INTO games
                    (user_id, tracker_name, game_state, updated_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ''', (user_id, tracker_name, game_state_json))

                conn.commit()
                return True

        except Exception as e:
            logger.error(f"Ошибка сохранения игры для пользователя {user_id}: {e}")
            return False
    
    def load_game(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Загрузка состояния игры для пользователя"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT user_id, tracker_name, game_state, created_at, updated_at
                    FROM games WHERE user_id = ?
                ''', (user_id,))
                row = cursor.fetchone()

                if row:
                    game_data = {
                        'user_id': row[0],
                        'tracker_name': row[1],
                        'game_state': json.loads(row[2]) if row[2] else None,
                        'created_at': row[3],
                        'updated_at': row[4]
                    }
                    return game_data
                return None

        except Exception as e:
            logger.error(f"Ошибка загрузки игры для пользователя {user_id}: {e}")
            return None
    