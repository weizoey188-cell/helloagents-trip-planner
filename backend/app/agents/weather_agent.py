"""天气查询Agent"""

from typing import List, Dict, Any
from datetime import datetime, timedelta
from .base import BaseAgent, agent_registry
from ..models.schemas import WeatherInfo
import json
import re


WEATHER_AGENT_PROMPT = """你是专业的天气查询专家。你的任务是查询指定城市的天气信息。

你需要:
1. 查询指定日期范围内的天气
2. 提供每天的详细天气信息
3. 根据天气给出旅行建议

返回格式必须是JSON:
{
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
  "suggestions": "根据天气给出的旅行建议"
}

注意:
- 温度必须是纯数字，不要带单位
- 覆盖所有请求的日期
- 给出实用的穿衣和出行建议
"""


class WeatherAgent(BaseAgent):
    """天气查询Agent"""
    
    def __init__(self):
        super().__init__(
            name="天气查询专家",
            system_prompt=WEATHER_AGENT_PROMPT
        )
        self.add_tool(agent_registry.get_shared_mcp_tool())
        # 缓存天气数据，避免重复查询
        self._weather_cache: Dict[str, List[WeatherInfo]] = {}
    
    async def execute(self, city: str, start_date: str, end_date: str) -> tuple[List[WeatherInfo], str]:
        """
        查询天气
        
        Args:
            city: 城市
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            (天气列表, 建议)
        """
        cache_key = f"{city}_{start_date}_{end_date}"
        
        # 检查缓存
        if cache_key in self._weather_cache:
            print(f"使用缓存的天气数据: {cache_key}")
            return self._weather_cache[cache_key], "天气数据来自缓存"
        
        try:
            weather_list, suggestions = await self._fetch_weather(city, start_date, end_date)
            # 缓存结果
            self._weather_cache[cache_key] = weather_list
            return weather_list, suggestions
        except Exception as e:
            print(f"天气查询失败: {e}")
            return self._get_default_weather(city, start_date, end_date), "使用默认天气数据"
    
    async def _fetch_weather(self, city: str, start_date: str, end_date: str) -> tuple[List[WeatherInfo], str]:
        """获取天气数据"""
        prompt = f"请查询{city}从{start_date}到{end_date}的天气预报"
        
        response = self.agent.run(prompt)
        
        return self._parse_weather(response)
    
    def _parse_weather(self, response: str) -> tuple[List[WeatherInfo], str]:
        """解析天气信息"""
        weather_list = []
        suggestions = ""
        
        try:
            # 查找JSON代码块
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(1))
            else:
                data = json.loads(response)
            
            weather_data = data.get("weather_info", [])
            suggestions = data.get("suggestions", "")
            
            for weather in weather_data:
                weather_info = WeatherInfo(
                    date=weather.get("date", ""),
                    day_weather=weather.get("day_weather", ""),
                    night_weather=weather.get("night_weather", ""),
                    day_temp=weather.get("day_temp", 0),
                    night_temp=weather.get("night_temp", 0),
                    wind_direction=weather.get("wind_direction", ""),
                    wind_power=weather.get("wind_power", "")
                )
                weather_list.append(weather_info)
                
        except Exception as e:
            print(f"解析天气信息失败: {e}")
            return [], ""
        
        return weather_list, suggestions
    
    def _get_default_weather(self, city: str, start_date: str, end_date: str) -> List[WeatherInfo]:
        """获取默认天气数据"""
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        weather_list = []
        current = start
        
        weather_types = ["晴", "多云", "晴", "晴", "多云", "阴", "晴"]
        
        day = 0
        while current <= end:
            weather = WeatherInfo(
                date=current.strftime("%Y-%m-%d"),
                day_weather=weather_types[day % len(weather_types)],
                night_weather="晴",
                day_temp=22 + (day % 5),
                night_temp=15 + (day % 3),
                wind_direction="南风",
                wind_power="1-3级"
            )
            weather_list.append(weather)
            current += timedelta(days=1)
            day += 1
        
        return weather_list


# 注册Agent
agent_registry.register("weather", WeatherAgent())
