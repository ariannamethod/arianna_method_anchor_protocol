"""
Agent Bridge - промежуточный модуль для подключения агентов к arianna_utils и letsgo.py

Этот модуль решает проблему доступа агентов в отдельных папках к корневым утилитам.
Каждый агент может импортировать этот модуль и получить доступ к:
- arianna_utils (логика, процессор, векторы)
- letsgo.py (терминал, команды)
- Общему каналу резонанса
"""

from pathlib import Path
import sys

# Убеждаемся что корень проекта в sys.path
_project_root = Path(__file__).parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# Импортируем через letsgo.py как центральный хаб
try:
    import letsgo
    # letsgo.py уже импортирует все arianna_utils модули
    from arianna_utils.agent_logic import get_agent_logic, create_agent_file_formatter
    from arianna_utils.context_neural_processor import parse_and_store_file
    from arianna_utils.vector_store import SQLiteVectorStore, embed_text
    UTILS_AVAILABLE = True
    TERMINAL_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import utilities: {e}")
    UTILS_AVAILABLE = False
    TERMINAL_AVAILABLE = False


def get_agent_utils(agent_name: str, log_dir: Path, db_path: Path, resonance_db_path: Path):
    """Получить утилиты для агента"""
    if not UTILS_AVAILABLE:
        raise ImportError("arianna_utils not available through letsgo.py")
    return get_agent_logic(agent_name, log_dir, db_path, resonance_db_path)


def get_terminal_access():
    """Получить доступ к терминалу letsgo.py"""
    if not TERMINAL_AVAILABLE:
        return None
    return letsgo


def create_file_formatter(agent_name: str, style_config: dict):
    """Создать форматтер файлов для агента"""
    return create_agent_file_formatter(agent_name, style_config)


async def process_file(path: str, formatter=None):
    """Обработать файл через neural processor"""
    return await parse_and_store_file(path, formatter)


def get_vector_store(db_path: Path):
    """Получить векторное хранилище"""
    return SQLiteVectorStore(db_path)


# Экспорт основных функций
__all__ = [
    "get_agent_utils",
    "get_terminal_access", 
    "create_file_formatter",
    "process_file",
    "get_vector_store",
    "embed_text"
]
