# This file is now in app/services/realtime_monitor.py
# Update all imports to use app.models, app.services, etc. as needed

# Place for database and monitoring logic

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List
from app.models.hate_speech_detector import HateSpeechResult

class DatabaseManager:
    """Manage SQLite database for storing results"""
    def __init__(self, db_path: str = "hate_speech_detections.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                is_hate_speech BOOLEAN NOT NULL,
                confidence REAL NOT NULL,
                detected_keywords TEXT,
                category TEXT,
                severity TEXT,
                explanation TEXT,
                timestamp DATETIME,
                user_id TEXT,
                platform TEXT,
                post_id TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE,
                total_processed INTEGER,
                hate_speech_detected INTEGER,
                platform TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def store_detection(self, result: HateSpeechResult, metadata: Dict = None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        if metadata is None:
            metadata = {}
        cursor.execute('''
            INSERT INTO detections 
            (text, is_hate_speech, confidence, detected_keywords, category, 
             severity, explanation, timestamp, user_id, platform, post_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            result.text,
            result.is_hate_speech,
            result.confidence,
            json.dumps(result.detected_keywords),
            result.category,
            result.severity,
            result.explanation,
            result.timestamp.isoformat(),
            metadata.get('user_id'),
            metadata.get('platform'),
            metadata.get('post_id')
        ))
        conn.commit()
        conn.close()

    def get_recent_detections(self, hours: int = 24, hate_only: bool = True) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()
        if hate_only:
            cursor.execute('''
                SELECT * FROM detections 
                WHERE timestamp > ? AND is_hate_speech = 1
                ORDER BY timestamp DESC
            ''', (cutoff_time,))
        else:
            cursor.execute('''
                SELECT * FROM detections 
                WHERE timestamp > ?
                ORDER BY timestamp DESC
            ''', (cutoff_time,))
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return results

    def get_statistics(self, days: int = 7) -> Dict:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cutoff_time = (datetime.now() - timedelta(days=days)).isoformat()
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN is_hate_speech = 1 THEN 1 ELSE 0 END) as hate_speech,
                category,
                platform
            FROM detections 
            WHERE timestamp > ?
            GROUP BY category, platform
        ''', (cutoff_time,))
        results = cursor.fetchall()
        conn.close()
        return {
            'period_days': days,
            'breakdown': [
                {
                    'total': row[0],
                    'hate_speech': row[1],
                    'category': row[2],
                    'platform': row[3]
                }
                for row in results
            ]
        }
