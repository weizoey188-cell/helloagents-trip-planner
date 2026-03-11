"""多智能体旅行规划系统 - 主控制器"""

import asyncio
from typing import Dict, Any, List
from ..models.schemas import TripRequest, TripPlan
from .base import agent_registry
from .attraction_agent import AttractionAgent
from .weather_agent import WeatherAgent
from .hotel_agent import HotelAgent
from .planner_agent import PlannerAgent


class MultiAgentTripPlanner:
    """多智能体旅行规划系统主控制器"""
    
    def __init__(self):
        """初始化多智能体系统"""
        print("🔄 初始化多智能体旅行规划系统...")
        
        # 初始化各个Agent
        self.attraction_agent = AttractionAgent()
        self.weather_agent = WeatherAgent()
        self.hotel_agent = HotelAgent()
        self.planner_agent = PlannerAgent()
        
        print("✅ 多智能体系统初始化完成")
        print(f"   - 景点搜索Agent: {self.attraction_agent.name}")
        print(f"   - 天气查询Agent: {self.weather_agent.name}")
        print(f"   - 酒店推荐Agent: {self.hotel_agent.name}")
        print(f"   - 行程规划Agent: {self.planner_agent.name}")
    
    async def plan_trip(self, request: TripRequest) -> TripPlan:
        """
        生成旅行计划 - 多Agent协作
        
        Args:
            request: 旅行请求
            
        Returns:
            旅行计划
        """
        print(f"\n{'='*60}")
        print(f"🎯 开始多Agent协作规划旅行")
        print(f"   城市: {request.city}")
        print(f"   日期: {request.start_date} - {request.end_date}")
        print(f"   天数: {request.travel_days}")
        print(f"{'='*60}\n")
        
        # Step 1: 并行执行景点搜索和天气查询
        print("🔄 Step 1: 并行获取景点和天气信息...")
        attraction_task = self.attraction_agent.execute(
            city=request.city,
            preferences=request.preferences,
            days=request.travel_days
        )
        weather_task = self.weather_agent.execute(
            city=request.city,
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        # 等待并行任务完成
        attractions, (weather_info, weather_suggestions) = await asyncio.gather(
            attraction_task, weather_task
        )
        print(f"   ✅ 获取到 {len(attractions)} 个景点")
        print(f"   ✅ 获取到 {len(weather_info)} 天天气信息")
        
        # Step 2: 酒店推荐（依赖景点位置信息）
        print("🔄 Step 2: 获取酒店推荐...")
        hotels = await self.hotel_agent.execute(
            city=request.city,
            accommodation_type=request.accommodation,
            attractions=[{"name": a.name, "location": a.location} for a in attractions[:3]]
        )
        print(f"   ✅ 获取到 {len(hotels)} 个酒店推荐")
        
        # Step 3: 行程规划（整合所有信息）
        print("🔄 Step 3: 生成完整行程规划...")
        trip_plan = await self.planner_agent.execute(
            city=request.city,
            start_date=request.start_date,
            end_date=request.end_date,
            travel_days=request.travel_days,
            transportation=request.transportation,
            accommodation=request.accommodation,
            preferences=request.preferences,
            attractions=attractions,
            hotels=hotels,
            weather_info=weather_info,
            weather_suggestions=weather_suggestions
        )
        print(f"   ✅ 行程规划完成")
        
        print(f"\n{'='*60}")
        print(f"✅ 旅行计划生成成功!")
        print(f"   总预算: ¥{trip_plan.budget.total}")
        print(f"   景点: ¥{trip_plan.budget.total_attractions}")
        print(f"   酒店: ¥{trip_plan.budget.total_hotels}")
        print(f"   餐饮: ¥{trip_plan.budget.total_meals}")
        print(f"   交通: ¥{trip_plan.budget.total_transportation}")
        print(f"{'='*60}\n")
        
        return trip_plan
    
    def get_agent_status(self) -> Dict[str, Any]:
        """获取Agent状态"""
        return {
            "attraction_agent": {
                "name": self.attraction_agent.name,
                "tools_count": len(self.attraction_agent.get_tools()),
                "status": "active"
            },
            "weather_agent": {
                "name": self.weather_agent.name,
                "tools_count": len(self.weather_agent.get_tools()),
                "status": "active"
            },
            "hotel_agent": {
                "name": self.hotel_agent.name,
                "tools_count": len(self.hotel_agent.get_tools()),
                "status": "active"
            },
            "planner_agent": {
                "name": self.planner_agent.name,
                "tools_count": len(self.planner_agent.get_tools()),
                "status": "active"
            }
        }


# 全局单例实例
_trip_planner_instance: MultiAgentTripPlanner = None


def get_trip_planner_agent() -> MultiAgentTripPlanner:
    """获取旅行规划Agent实例（单例模式）"""
    global _trip_planner_instance
    if _trip_planner_instance is None:
        _trip_planner_instance = MultiAgentTripPlanner()
    return _trip_planner_instance
