"""多智能体旅行规划系统

包含以下Agent:
- AttractionAgent: 景点搜索Agent
- WeatherAgent: 天气查询Agent
- HotelAgent: 酒店推荐Agent
- PlannerAgent: 行程规划Agent
- MultiAgentTripPlanner: 主控制器
"""

from .base import BaseAgent, agent_registry
from .attraction_agent import AttractionAgent
from .weather_agent import WeatherAgent
from .hotel_agent import HotelAgent
from .planner_agent import PlannerAgent
from .trip_planner_agent import MultiAgentTripPlanner, get_trip_planner_agent

__all__ = [
    "BaseAgent",
    "agent_registry",
    "AttractionAgent",
    "WeatherAgent",
    "HotelAgent",
    "PlannerAgent",
    "MultiAgentTripPlanner",
    "get_trip_planner_agent"
]
