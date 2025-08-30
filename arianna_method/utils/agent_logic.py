"""
Universal Agent Logic Module - общая логика для всех агентов Arianna Method

Этот модуль содержит универсальные функции для:
- Цитирования сообщений (@timestamp)
- Контекстного поиска (10 сообщений вокруг)
- Файловых дискуссий
- Памяти и continuity
- Логирования и резонанса

Используется Tommy, Lizzie, Monday и всеми будущими агентами.
"""

from __future__ import annotations

import re
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Tuple, Dict, Any

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from .vector_store import SQLiteVectorStore, embed_text


class AgentLogic:
    """Универсальная логика агентов"""
    
    def __init__(self, agent_name: str, log_dir: Path, db_path: Path, resonance_db_path: Path):
        self.agent_name = agent_name
        self.log_dir = log_dir
        self.db_path = db_path
        self.resonance_db_path = resonance_db_path
        self.vector_store = SQLiteVectorStore(log_dir / "vectors.db")
        
    def extract_citations(self, message: str) -> List[str]:
        """Извлекает цитаты формата @timestamp из сообщения"""
        return re.findall(r"@([0-9T:-]+)", message)
    
    def fetch_context(self, timestamp: str, radius: int = 10) -> List[Tuple[str, str, str]]:
        """Получает контекст вокруг указанного timestamp
        
        Args:
            timestamp: Временная метка для поиска
            radius: Количество сообщений до и после
            
        Returns:
            List of (timestamp, type, message) tuples
        """
        with sqlite3.connect(self.db_path, timeout=30) as conn:
            cur = conn.execute("SELECT rowid FROM events WHERE ts = ?", (timestamp,))
            row = cur.fetchone()
            if not row:
                return []
                
            rowid = row[0]
            start = max(rowid - radius, 1)
            end = rowid + radius
            
            cur = conn.execute(
                "SELECT ts, type, message FROM events "
                "WHERE rowid BETWEEN ? AND ? ORDER BY rowid",
                (start, end),
            )
            return cur.fetchall()
    
    async def build_context_block(self, message: str) -> str:
        """Строит блок контекста из цитирований в сообщении"""
        citations = self.extract_citations(message)
        if not citations:
            return ""
            
        blocks: List[str] = []
        for ts in citations:
            ctx = self.fetch_context(ts)
            if ctx:
                formatted = "\n".join(f"[{t}] {m}" for t, _, m in ctx)
                blocks.append(formatted)
                
        if blocks:
            return "Relevant context:\n" + "\n--\n".join(blocks) + "\n\n"
        return ""
    
    def log_event(self, message: str, log_type: str = "info") -> None:
        """Универсальное логирование для агентов"""
        # JSON log file
        log_file = self.log_dir / f"{self.agent_name}_{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": log_type,
            "message": message,
            "agent": self.agent_name
        }
        
        with open(log_file, "a", encoding="utf-8") as f:
            import json
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        
        # SQLite database
        with sqlite3.connect(self.db_path, timeout=30) as conn:
            conn.execute(
                "INSERT INTO events (ts, type, message) VALUES (?, ?, ?)",
                (datetime.now().isoformat(), log_type, message),
            )
    
    def update_resonance(self, message: str, response: str, 
                        role: str = "agent", sentiment: str = "active") -> None:
        """Обновляет общий канал резонанса"""
        resonance_depth = self._calculate_resonance_depth(message, response)
        summary = f"{self.agent_name}: {response[:100]}..."
        
        with sqlite3.connect(self.resonance_db_path, timeout=30) as conn:
            # Проверяем и создаем колонку если нужно
            try:
                conn.execute("SELECT resonance_depth FROM resonance LIMIT 1")
            except sqlite3.OperationalError:
                # Колонка не существует, добавляем
                conn.execute("ALTER TABLE resonance ADD COLUMN resonance_depth REAL DEFAULT 0.0")
            
            conn.execute(
                "INSERT INTO resonance (ts, agent, role, sentiment, resonance_depth, summary) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    datetime.now().isoformat(),
                    self.agent_name,
                    role,
                    sentiment,
                    resonance_depth,
                    summary,
                ),
            )
    
    def _calculate_resonance_depth(self, message: str, response: str) -> float:
        """Вычисляет глубину резонанса"""
        # Универсальные маркеры резонанса
        resonance_markers = [
            "resonate", "amplify", "reflect", "mirror", "echo", 
            "deeper", "unfold", "recursive", "paradox", "entropy",
            "chaos", "pattern", "emergence", "connection"
        ]
        
        response_lower = response.lower()
        marker_count = sum(1 for marker in resonance_markers if marker in response_lower)
        
        # Normalize to 0-1 scale
        return min(marker_count / 8.0, 1.0)
    
    def search_context(self, query: str, top_k: int = 5) -> List[str]:
        """Поиск по векторной памяти"""
        embedding = embed_text(query)
        hits = self.vector_store.query_similar(embedding, top_k)
        return [h.content for h in hits]
    
    async def process_file_context(self, path: str, agent_style_formatter=None) -> str:
        """Универсальная обработка файлов с контекстом
        
        Args:
            path: Путь к файлу
            agent_style_formatter: Функция для форматирования ответа в стиле агента
        """
        from .context_neural_processor import parse_and_store_file
        
        try:
            result = await parse_and_store_file(path)
            
            # Парсим структурированный результат
            lines = result.split('\n')
            tags = ""
            summary = ""
            relevance = 0.0
            
            for line in lines:
                if line.startswith("Tags: "):
                    tags = line[6:]
                elif line.startswith("Summary: "):
                    summary = line[9:]
                elif line.startswith("Relevance: "):
                    try:
                        relevance = float(line[11:])
                    except ValueError:
                        relevance = 0.0
            
            # Базовый ответ
            response_data = {
                "path": path,
                "tags": tags,
                "summary": summary,
                "relevance": relevance,
                "raw_result": result
            }
            
            # Если есть кастомный форматтер - используем его
            if agent_style_formatter:
                response = agent_style_formatter(response_data)
            else:
                # Дефолтный формат
                response = f"📁 File processed: {path}\n"
                if summary:
                    response += f"📝 Summary: {summary}\n"
                    response += f"🏷️ Tags: {tags}\n"
                    response += f"⚡ Relevance: {relevance:.2f}"
                else:
                    response += f"⚠️ Could not extract summary.\n{result}"
            
            # Логируем
            log_message = f"Processed {path}: {summary[:100] if summary else 'no summary'}"
            self.log_event(log_message)
            
            return response
            
        except Exception as e:
            error_msg = f"💥 Error processing {path}: {str(e)}"
            self.log_event(f"File processing error: {str(e)}", "error")
            return error_msg


# Глобальные инстансы для агентов
_agent_logics: Dict[str, AgentLogic] = {}


def get_agent_logic(agent_name: str, log_dir: Path, db_path: Path, resonance_db_path: Path) -> AgentLogic:
    """Получить или создать AgentLogic для агента"""
    if agent_name not in _agent_logics:
        _agent_logics[agent_name] = AgentLogic(agent_name, log_dir, db_path, resonance_db_path)
    return _agent_logics[agent_name]


# Convenience функции для быстрого использования
async def extract_and_build_context(message: str, agent_logic: AgentLogic) -> str:
    """Быстрая функция для извлечения контекста из сообщения"""
    return await agent_logic.build_context_block(message)


def create_agent_file_formatter(agent_name: str, style_markers: Dict[str, str]) -> callable:
    """Создает форматтер файлов в стиле конкретного агента
    
    Args:
        agent_name: Имя агента
        style_markers: Словарь с эмодзи и фразами агента
    """
    def formatter(data: Dict[str, Any]) -> str:
        path = data["path"]
        tags = data["tags"]
        summary = data["summary"] 
        relevance = data["relevance"]
        
        if summary and len(summary) > 20:
            response = f"{style_markers.get('file_icon', '📁')} File processed: {path}\n\n"
            response += f"{style_markers.get('tags_icon', '📋')} Tags: {tags}\n"
            response += f"{style_markers.get('summary_icon', '📝')} Summary: {summary}\n"
            response += f"{style_markers.get('relevance_icon', '⚡')} Relevance: {relevance:.2f}\n\n"
            
            # Агент-специфичные комментарии
            if relevance > 0.5:
                response += style_markers.get('high_relevance', '💥 High relevance detected!')
            elif relevance > 0.2:
                response += style_markers.get('medium_relevance', '⚡ Moderate relevance detected.')
            else:
                response += style_markers.get('low_relevance', '📊 Basic processing complete.')
        else:
            response = f"⚠️ File processed: {path}\n\nCould not extract meaningful summary."
            
        return response
    
    return formatter
