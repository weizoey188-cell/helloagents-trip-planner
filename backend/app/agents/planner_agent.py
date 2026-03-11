"""行程规划Agent"""

from typing import List, Dict, Any
from datetime import datetime, timedelta
from .base import BaseAgent, agent_registry
from ..models.schemas import (
    TripPlan, DayPlan, Attraction, Meal, Hotel, 
    WeatherInfo, Budget, Location
)
import json
import re


PLANNER_AGENT_PROMPT = """你是专业的旅行规划专家。你的任务是根据景点、酒店和天气信息，生成详细的旅行计划。

你需要:
1. 合理安排每天的行程
2. 考虑景点之间的距离和游览时间
3. 安排合适的餐饮
4. 根据天气调整行程
5. 计算预算

返回格式必须是JSON:
{
  "city": "城市名称",
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD",
  "days": [
    {
      "date": "YYYY-MM-DD",
      "day_index": 0,
      "description": "第1天行程概述",
      "transportation": "交通方式",
      "accommodation": "住宿类型",
      "hotel": {
        "name": "酒店名称",
        "address": "酒店地址",
        "location": {"longitude": 经度, "latitude": 纬度},
        "price_range": "价格范围",
        "rating": "评分",
        "distance": "距离景点距离",
        "type": "酒店类型",
        "estimated_cost": 预估费用
      },
      "attractions": [
        {
          "name": "景点名称",
          "address": "详细地址",
          "location": {"longitude": 经度, "latitude": 纬度},
          "visit_duration": 游览时间(分钟),
          "description": "景点描述",
          "category": "景点类别",
          "ticket_price": 门票价格
        }
      ],
      "meals": [
        {
          "type": "breakfast/lunch/dinner/snack",
          "name": "餐饮名称",
          "address": "地址",
          "location": {"longitude": 经度, "latitude": 纬度},
          "description": "描述",
          "estimated_cost": 预估费用
        }
      ]
    }
  ],
  "weather_info": [
    {
      "date": "YYYY-MM-DD",
      "day_weather": "白天天气",
      "night_weather": "夜间天气",
      "day_temp": 白天温度(数字),
      "night_temp": 夜间温度(数字),
      "wind_direction": "风向",
      "wind_power": "风力"
    }
  ],
  "overall_suggestions": "总体建议",
  "budget": {
    "total_attractions": 景点门票总费用,
    "total_hotels": 酒店总费用,
    "total_meals": 餐饮总费用,
    "total_transportation": 交通总费用,
    "total": 总费用
  }
}

注意:
- 每天安排2-3个景点
- 考虑景点间的地理位置，合理安排路线
- 每天必须包含早中晚三餐
- 提供实用的旅行建议
- 预算要详细准确
"""


class PlannerAgent(BaseAgent):
    """行程规划Agent"""
    
    def __init__(self):
        super().__init__(
            name="行程规划专家",
            system_prompt=PLANNER_AGENT_PROMPT
        )
    
    async def execute(
        self,
        city: str,
        start_date: str,
        end_date: str,
        travel_days: int,
        transportation: str,
        accommodation: str,
        preferences: List[str],
        attractions: List[Attraction],
        hotels: List[Hotel],
        weather_info: List[WeatherInfo],
        weather_suggestions: str
    ) -> TripPlan:
        """
        生成旅行计划
        
        Args:
            city: 城市
            start_date: 开始日期
            end_date: 结束日期
            travel_days: 旅行天数
            transportation: 交通方式
            accommodation: 住宿偏好
            preferences: 用户偏好
            attractions: 景点列表
            hotels: 酒店列表
            weather_info: 天气信息
            weather_suggestions: 天气建议
            
        Returns:
            旅行计划
        """
        try:
            # 构建规划提示
            prompt = self._build_planning_prompt(
                city, start_date, end_date, travel_days,
                transportation, accommodation, preferences,
                attractions, hotels, weather_info
            )
            
            # 调用Agent生成计划
            response = self.agent.run(prompt)
            
            # 解析响应
            trip_plan = self._parse_trip_plan(
                response, city, start_date, end_date, 
                travel_days, weather_info
            )
            
            # 补充天气建议
            trip_plan.overall_suggestions = weather_suggestions or trip_plan.overall_suggestions
            
            return trip_plan
            
        except Exception as e:
            print(f"行程规划失败: {e}")
            return self._generate_default_plan(
                city, start_date, end_date, travel_days,
                transportation, accommodation, attractions, 
                hotels, weather_info
            )
    
    def _build_planning_prompt(
        self,
        city: str,
        start_date: str,
        end_date: str,
        travel_days: int,
        transportation: str,
        accommodation: str,
        preferences: List[str],
        attractions: List[Attraction],
        hotels: List[Hotel],
        weather_info: List[WeatherInfo]
    ) -> str:
        """构建规划提示"""
        
        # 景点信息
        attractions_str = "\n".join([
            f"- {a.name}: {a.description}, 游览时间{a.visit_duration}分钟, 门票{a.ticket_price}元"
            for a in attractions[:8]
        ])
        
        # 酒店信息
        hotels_str = "\n".join([
            f"- {h.name}: {h.type}, {h.price_range}, 评分{h.rating}"
            for h in hotels[:3]
        ])
        
        # 天气信息
        weather_str = "\n".join([
            f"- {w.date}: 白天{w.day_weather} {w.day_temp}°C, 夜间{w.night_weather} {w.night_temp}°C"
            for w in weather_info
        ])
        
        prompt = f"""请为以下旅行需求生成详细的旅行计划:

**基本信息:**
- 城市: {city}
- 日期: {start_date} 至 {end_date} ({travel_days}天)
- 交通方式: {transportation}
- 住宿偏好: {accommodation}
- 旅行偏好: {', '.join(preferences)}

**可选景点:**
{attractions_str}

**推荐酒店:**
{hotels_str}

**天气预报:**
{weather_str}

请生成完整的旅行计划，包括每天的行程安排、餐饮推荐和预算。"""
        
        return prompt
    
    def _parse_trip_plan(
        self,
        response: str,
        city: str,
        start_date: str,
        end_date: str,
        travel_days: int,
        weather_info: List[WeatherInfo]
    ) -> TripPlan:
        """解析旅行计划"""
        
        try:
            # 查找JSON代码块
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(1))
            else:
                data = json.loads(response)
            
            # 解析每日行程
            days = []
            for day_data in data.get("days", []):
                # 解析景点
                attractions = []
                for attr_data in day_data.get("attractions", []):
                    attraction = Attraction(
                        name=attr_data.get("name", ""),
                        address=attr_data.get("address", ""),
                        location=Location(
                            longitude=attr_data.get("location", {}).get("longitude", 0),
                            latitude=attr_data.get("location", {}).get("latitude", 0)
                        ),
                        visit_duration=attr_data.get("visit_duration", 120),
                        description=attr_data.get("description", ""),
                        category=attr_data.get("category", "景点"),
                        ticket_price=attr_data.get("ticket_price", 0)
                    )
                    attractions.append(attraction)
                
                # 解析餐饮
                meals = []
                for meal_data in day_data.get("meals", []):
                    meal = Meal(
                        type=meal_data.get("type", "lunch"),
                        name=meal_data.get("name", ""),
                        address=meal_data.get("address"),
                        location=Location(
                            longitude=meal_data.get("location", {}).get("longitude", 0),
                            latitude=meal_data.get("location", {}).get("latitude", 0)
                        ) if meal_data.get("location") else None,
                        description=meal_data.get("description"),
                        estimated_cost=meal_data.get("estimated_cost", 50)
                    )
                    meals.append(meal)
                
                # 解析酒店
                hotel_data = day_data.get("hotel", {})
                hotel = Hotel(
                    name=hotel_data.get("name", ""),
                    address=hotel_data.get("address", ""),
                    location=Location(
                        longitude=hotel_data.get("location", {}).get("longitude", 0),
                        latitude=hotel_data.get("location", {}).get("latitude", 0)
                    ) if hotel_data.get("location") else None,
                    price_range=hotel_data.get("price_range", ""),
                    rating=hotel_data.get("rating", ""),
                    distance=hotel_data.get("distance", ""),
                    type=hotel_data.get("type", ""),
                    estimated_cost=hotel_data.get("estimated_cost", 300)
                ) if hotel_data else None
                
                day_plan = DayPlan(
                    date=day_data.get("date", ""),
                    day_index=day_data.get("day_index", 0),
                    description=day_data.get("description", ""),
                    transportation=day_data.get("transportation", ""),
                    accommodation=day_data.get("accommodation", ""),
                    hotel=hotel,
                    attractions=attractions,
                    meals=meals
                )
                days.append(day_plan)
            
            # 解析预算
            budget_data = data.get("budget", {})
            budget = Budget(
                total_attractions=budget_data.get("total_attractions", 0),
                total_hotels=budget_data.get("total_hotels", 0),
                total_meals=budget_data.get("total_meals", 0),
                total_transportation=budget_data.get("total_transportation", 0),
                total=budget_data.get("total", 0)
            )
            
            # 如果没有预算数据，计算一个
            if budget.total == 0:
                budget = self._calculate_budget(days, travel_days)
            
            trip_plan = TripPlan(
                city=city,
                start_date=start_date,
                end_date=end_date,
                days=days,
                weather_info=weather_info,
                overall_suggestions=data.get("overall_suggestions", ""),
                budget=budget
            )
            
            return trip_plan
            
        except Exception as e:
            print(f"解析旅行计划失败: {e}")
            raise
    
    def _generate_default_plan(
        self,
        city: str,
        start_date: str,
        end_date: str,
        travel_days: int,
        transportation: str,
        accommodation: str,
        attractions: List[Attraction],
        hotels: List[Hotel],
        weather_info: List[WeatherInfo]
    ) -> TripPlan:
        """生成默认旅行计划"""
        
        days = []
        start = datetime.strptime(start_date, "%Y-%m-%d")
        
        # 分配景点到每天
        attractions_per_day = 2
        hotel = hotels[0] if hotels else None
        
        for day_idx in range(travel_days):
            current_date = start + timedelta(days=day_idx)
            date_str = current_date.strftime("%Y-%m-%d")
            
            # 获取当天的景点
            start_idx = day_idx * attractions_per_day
            end_idx = start_idx + attractions_per_day
            day_attractions = attractions[start_idx:end_idx] if start_idx < len(attractions) else []
            
            # 如果没有足够的景点，重复使用
            if len(day_attractions) < attractions_per_day and attractions:
                day_attractions = attractions[:attractions_per_day]
            
            # 生成餐饮
            meals = [
                Meal(type="breakfast", name="酒店早餐", estimated_cost=30),
                Meal(type="lunch", name="当地特色餐厅", estimated_cost=60),
                Meal(type="dinner", name="推荐餐厅", estimated_cost=80)
            ]
            
            day_plan = DayPlan(
                date=date_str,
                day_index=day_idx,
                description=f"第{day_idx + 1}天行程安排",
                transportation=transportation,
                accommodation=accommodation,
                hotel=hotel,
                attractions=day_attractions,
                meals=meals
            )
            days.append(day_plan)
        
        # 计算预算
        budget = self._calculate_budget(days, travel_days)
        
        return TripPlan(
            city=city,
            start_date=start_date,
            end_date=end_date,
            days=days,
            weather_info=weather_info,
            overall_suggestions=f"欢迎来到{city}！建议提前预订酒店和热门景点门票。",
            budget=budget
        )
    
    def _calculate_budget(self, days: List[DayPlan], travel_days: int) -> Budget:
        """计算预算"""
        total_attractions = sum(
            sum(a.ticket_price for a in day.attractions)
            for day in days
        )
        
        total_hotels = sum(
            day.hotel.estimated_cost if day.hotel else 300
            for day in days
        )
        
        total_meals = sum(
            sum(m.estimated_cost for m in day.meals)
            for day in days
        )
        
        total_transportation = travel_days * 50  # 每天交通费估算
        
        return Budget(
            total_attractions=total_attractions,
            total_hotels=total_hotels,
            total_meals=total_meals,
            total_transportation=total_transportation,
            total=total_attractions + total_hotels + total_meals + total_transportation
        )


# 注册Agent
agent_registry.register("planner", PlannerAgent())
