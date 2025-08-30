"""Agent Registry - промежуточный модуль для подключения агентов к letsgo.py

Этот модуль изолирует ядро letsgo.py от прямых зависимостей агентов,
позволяя легко добавлять новых агентов без изменения базовой системы.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Dict, Callable, Awaitable, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Тип для функции чата агента
AgentChatFunction = Callable[[str], Awaitable[str]]

class AgentRegistry:
    """Реестр агентов для letsgo.py"""
    
    def __init__(self):
        self._agents: Dict[str, AgentChatFunction] = {}
        self._fallback_agent: Optional[str] = None
        
    def register_agent(self, name: str, chat_func: AgentChatFunction, is_fallback: bool = False) -> None:
        """Регистрирует агента в системе.
        
        Args:
            name: Имя агента (tommy, lizzie, monday, etc.)
            chat_func: Async функция для чата с агентом
            is_fallback: Если True, этот агент будет использоваться по умолчанию
        """
        self._agents[name] = chat_func
        if is_fallback:
            self._fallback_agent = name
        logger.info(f"Registered agent: {name} (fallback: {is_fallback})")
    
    def unregister_agent(self, name: str) -> None:
        """Удаляет агента из системы."""
        if name in self._agents:
            del self._agents[name]
            if self._fallback_agent == name:
                self._fallback_agent = None
            logger.info(f"Unregistered agent: {name}")
    
    async def chat(self, message: str, agent_name: Optional[str] = None) -> str:
        """Отправляет сообщение агенту.
        
        Args:
            message: Сообщение для агента
            agent_name: Имя конкретного агента или None для fallback
            
        Returns:
            Ответ агента или сообщение об ошибке
        """
        target_agent = agent_name or self._fallback_agent
        
        if not target_agent:
            return "No agents available. The void echoes back your words."
        
        if target_agent not in self._agents:
            available = ", ".join(self._agents.keys()) if self._agents else "none"
            return f"Agent '{target_agent}' not found. Available: {available}"
        
        try:
            chat_func = self._agents[target_agent]
            response = await chat_func(message)
            return response
        except Exception as e:
            logger.error(f"Agent {target_agent} error: {e}")
            return f"Agent {target_agent} encountered an error: {str(e)}"
    
    def list_agents(self) -> Dict[str, str]:
        """Возвращает список доступных агентов."""
        return {
            name: "fallback" if name == self._fallback_agent else "active"
            for name in self._agents.keys()
        }
    
    def is_agent_available(self, name: str) -> bool:
        """Проверяет доступность агента."""
        return name in self._agents


# Глобальный реестр агентов
_global_registry = AgentRegistry()


def get_registry() -> AgentRegistry:
    """Возвращает глобальный реестр агентов."""
    return _global_registry


# Функции для автоматической регистрации агентов
def auto_register_agents() -> None:
    """Автоматически регистрирует доступных агентов."""
    
    # Пытаемся зарегистрировать Tommy
    try:
        from tommy import tommy
        _global_registry.register_agent("tommy", tommy.chat, is_fallback=True)
        logger.info("Tommy registered as fallback agent")
    except ImportError as e:
        logger.warning(f"Tommy not available: {e}")
    except Exception as e:
        logger.error(f"Failed to register Tommy: {e}")
    
    # Пытаемся зарегистрировать других агентов
    # В будущем здесь будут Lizzie, Monday, Lilith, Lisette...
    
    agents_to_try = [
        ("lizzie", "lizzie.lizzie"),
        ("monday", "nomonday.monday"),
    ]
    
    for agent_name, module_path in agents_to_try:
        try:
            # Динамический импорт агентов
            import importlib
            module = importlib.import_module(module_path)
            if hasattr(module, 'chat'):
                _global_registry.register_agent(agent_name, module.chat)
                logger.info(f"{agent_name.title()} registered successfully")
        except ImportError:
            logger.debug(f"{agent_name.title()} not available (module not found)")
        except Exception as e:
            logger.warning(f"Failed to register {agent_name}: {e}")


# Функция для letsgo.py
async def chat_with_agent(message: str, agent_name: Optional[str] = None) -> str:
    """Упрощенная функция для использования в letsgo.py"""
    return await _global_registry.chat(message, agent_name)


# Функция для получения списка агентов (для /help команды)
def get_available_agents() -> str:
    """Возвращает список доступных агентов для отображения."""
    agents = _global_registry.list_agents()
    if not agents:
        return "No agents registered."
    
    lines = []
    for name, status in agents.items():
        marker = " (default)" if status == "fallback" else ""
        lines.append(f"  {name}{marker}")
    
    return "Available agents:\n" + "\n".join(lines)


# Инициализация при импорте
auto_register_agents()
