"""酒店推荐Agent"""

from typing import List, Dict, Any, Optional
from .base import BaseAgent, agent_registry
from ..models.schemas import Hotel, Location
import json
import re


HOTEL_AGENT_PROMPT = """你是专业的酒店推荐专家。你的任务是根据城市、景点位置和住宿偏好推荐合适的酒店。

你需要:
1. 根据住宿偏好筛选酒店类型
2. 考虑酒店与景点的距离
3. 提供酒店的详细信息

返回格式必须是JSON:
{
  "hotels": [
    {
      "name": "酒店名称",
      "address": "详细地址",
      "location": {"longitude": 经度, "latitude": 纬度},
      "price_range": "价格范围(如: 300-500元)",
      "rating": "评分(如: 4.5)",
      "distance": "距离景点距离",
      "type": "酒店类型",
      "estimated_cost": 预估每晚费用(数字)
    }
  ],
  "recommendation": "推荐理由"
}

注意:
- 推荐2-3个不同价位的酒店
- 考虑交通便利性
- 包含酒店特色和优势
"""


class HotelAgent(BaseAgent):
    """酒店推荐Agent"""
    
    def __init__(self):
        super().__init__(
            name="酒店推荐专家",
            system_prompt=HOTEL_AGENT_PROMPT
        )
        self.add_tool(agent_registry.get_shared_mcp_tool())
        # 缓存酒店数据
        self._hotel_cache: Dict[str, List[Hotel]] = {}
    
    async def execute(
        self, 
        city: str, 
        accommodation_type: str, 
        attractions: List[Dict[str, Any]] = None
    ) -> List[Hotel]:
        """
        搜索酒店
        
        Args:
            city: 城市
            accommodation_type: 住宿类型偏好
            attractions: 景点列表（用于计算距离）
            
        Returns:
            酒店列表
        """
        cache_key = f"{city}_{accommodation_type}"
        
        # 检查缓存
        if cache_key in self._hotel_cache:
            print(f"使用缓存的酒店数据: {cache_key}")
            return self._hotel_cache[cache_key]
        
        try:
            hotels = await self._search_hotels(city, accommodation_type)
            # 缓存结果
            self._hotel_cache[cache_key] = hotels
            return hotels
        except Exception as e:
            print(f"酒店搜索失败: {e}")
            return self._get_default_hotels(city, accommodation_type)
    
    async def _search_hotels(self, city: str, accommodation_type: str) -> List[Hotel]:
        """搜索酒店"""
        keywords = self._build_search_keywords(accommodation_type)
        prompt = f"请搜索{city}的{keywords}，返回至少3个推荐酒店"
        
        response = self.agent.run(prompt)
        
        return self._parse_hotels(response)
    
    def _build_search_keywords(self, accommodation_type: str) -> str:
        """构建搜索关键词"""
        type_mapping = {
            "经济型": "经济型酒店",
            "舒适型": "舒适型酒店",
            "豪华型": "豪华酒店",
            "民宿": "民宿",
            "青旅": "青年旅舍"
        }
        return type_mapping.get(accommodation_type, "酒店")
    
    def _parse_hotels(self, response: str) -> List[Hotel]:
        """解析酒店信息"""
        hotels = []
        
        try:
            # 查找JSON代码块
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(1))
            else:
                data = json.loads(response)
            
            hotels_data = data.get("hotels", [])
            
            for hotel_data in hotels_data:
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
                )
                hotels.append(hotel)
                
        except Exception as e:
            print(f"解析酒店信息失败: {e}")
            return []
        
        return hotels
    
    def _get_default_hotels(self, city: str, accommodation_type: str) -> List[Hotel]:
        """获取默认酒店列表"""
        defaults = {
            "北京": [
                Hotel(name="北京饭店", address="北京市东城区东长安街33号",
                     location=Location(longitude=116.407526, latitude=39.90403),
                     price_range="800-1200元", rating="4.8", distance="市中心",
                     type="豪华型", estimated_cost=1000),
                Hotel(name="如家快捷酒店", address="北京市朝阳区建国路88号",
                     location=Location(longitude=116.407526, latitude=39.90403),
                     price_range="200-300元", rating="4.2", distance="交通便利",
                     type="经济型", estimated_cost=250),
            ],
            "上海": [
                Hotel(name="和平饭店", address="上海市黄浦区南京东路20号",
                     location=Location(longitude=121.473701, latitude=31.230416),
                     price_range="1500-2500元", rating="4.9", distance="外滩核心区",
                     type="豪华型", estimated_cost=2000),
                Hotel(name="汉庭酒店", address="上海市浦东新区陆家嘴环路",
                     location=Location(longitude=121.473701, latitude=31.230416),
                     price_range="300-500元", rating="4.3", distance="地铁沿线",
                     type="舒适型", estimated_cost=400),
            ]
        }
        
        city_hotels = defaults.get(city, [
            Hotel(name=f"{city}大酒店", address=f"{city}市中心",
                 location=Location(longitude=116.407526, latitude=39.90403),
                 price_range="400-600元", rating="4.5", distance="市中心",
                 type="舒适型", estimated_cost=500),
        ])
        
        # 根据住宿类型筛选
        if accommodation_type == "经济型":
            return [h for h in city_hotels if "经济" in h.type or h.estimated_cost < 300] or city_hotels
        elif accommodation_type == "豪华型":
            return [h for h in city_hotels if "豪华" in h.type or h.estimated_cost > 800] or city_hotels
        
        return city_hotels


# 注册Agent
agent_registry.register("hotel", HotelAgent())
