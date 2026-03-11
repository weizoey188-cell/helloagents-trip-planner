"""景点搜索Agent"""

from typing import List, Dict, Any
from .base import BaseAgent, agent_registry
from ..models.schemas import Attraction, Location
import json
import re


ATTRACTION_AGENT_PROMPT = """你是专业的景点搜索专家。你的任务是根据城市、用户偏好和旅行天数搜索合适的景点。

你需要:
1. 根据用户偏好筛选景点类型
2. 考虑旅行天数合理安排景点数量
3. 提供景点的详细信息

返回格式必须是JSON:
{
  "attractions": [
    {
      "name": "景点名称",
      "address": "详细地址",
      "location": {"longitude": 经度, "latitude": 纬度},
      "visit_duration": 建议游览时间(分钟),
      "description": "景点描述",
      "category": "景点类别",
      "rating": 评分,
      "ticket_price": 门票价格(元)
    }
  ]
}

注意:
- 每天安排2-3个景点
- 考虑景点之间的距离
- 包含不同类型的景点(自然、人文、历史等)
"""


class AttractionAgent(BaseAgent):
    """景点搜索Agent"""
    
    def __init__(self):
        super().__init__(
            name="景点搜索专家",
            system_prompt=ATTRACTION_AGENT_PROMPT
        )
        # 添加共享MCP工具
        self.add_tool(agent_registry.get_shared_mcp_tool())
    
    async def execute(self, city: str, preferences: List[str], days: int) -> List[Attraction]:
        """
        搜索景点
        
        Args:
            city: 城市
            preferences: 用户偏好
            days: 旅行天数
            
        Returns:
            景点列表
        """
        # 构建搜索关键词
        keywords = self._build_search_keywords(preferences)
        
        # 调用MCP工具搜索景点
        try:
            result = await self._search_attractions(city, keywords)
            return result
        except Exception as e:
            print(f"景点搜索失败: {e}")
            return self._get_default_attractions(city)
    
    def _build_search_keywords(self, preferences: List[str]) -> str:
        """构建搜索关键词"""
        base_keywords = ["景点", "旅游"]
        if preferences:
            pref_str = "、".join(preferences[:3])
            return f"{pref_str}景点"
        return "热门景点"
    
    async def _search_attractions(self, city: str, keywords: str) -> List[Attraction]:
        """搜索景点"""
        # 使用Agent调用工具
        prompt = f"请搜索{city}的{keywords}，返回至少6个热门景点"
        
        response = self.agent.run(prompt)
        
        # 解析响应
        return self._parse_attractions(response, city)
    
    def _parse_attractions(self, response: str, city: str) -> List[Attraction]:
        """解析景点信息"""
        attractions = []
        
        # 尝试从响应中提取JSON
        try:
            # 查找JSON代码块
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(1))
                attractions_data = data.get("attractions", [])
            else:
                # 尝试直接解析JSON
                data = json.loads(response)
                attractions_data = data.get("attractions", [])
            
            for attr_data in attractions_data:
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
                    rating=attr_data.get("rating"),
                    ticket_price=attr_data.get("ticket_price", 0)
                )
                attractions.append(attraction)
                
        except Exception as e:
            print(f"解析景点信息失败: {e}")
            return self._get_default_attractions(city)
        
        return attractions
    
    def _get_default_attractions(self, city: str) -> List[Attraction]:
        """获取默认景点列表"""
        defaults = {
            "北京": [
                Attraction(name="故宫博物院", address="北京市东城区景山前街4号", 
                          location=Location(longitude=116.397128, latitude=39.916527),
                          visit_duration=180, description="中国明清两代的皇家宫殿", category="历史文化", ticket_price=60),
                Attraction(name="天安门广场", address="北京市东城区东长安街",
                          location=Location(longitude=116.397477, latitude=39.903738),
                          visit_duration=60, description="世界上最大的城市广场", category="地标建筑", ticket_price=0),
                Attraction(name="颐和园", address="北京市海淀区新建宫门路19号",
                          location=Location(longitude=116.275467, latitude=39.999982),
                          visit_duration=240, description="中国清朝时期皇家园林", category="园林", ticket_price=30),
            ],
            "上海": [
                Attraction(name="外滩", address="上海市黄浦区中山东一路",
                          location=Location(longitude=121.490317, latitude=31.239703),
                          visit_duration=120, description="上海的标志性景点", category="地标建筑", ticket_price=0),
                Attraction(name="东方明珠", address="上海市浦东新区世纪大道1号",
                          location=Location(longitude=121.495619, latitude=31.239703),
                          visit_duration=180, description="上海标志性文化景观之一", category="地标建筑", ticket_price=199),
                Attraction(name="豫园", address="上海市黄浦区安仁街137号",
                          location=Location(longitude=121.492231, latitude=31.227152),
                          visit_duration=120, description="江南古典园林", category="园林", ticket_price=40),
            ]
        }
        return defaults.get(city, [
            Attraction(name=f"{city}热门景点1", address=f"{city}市中心",
                      location=Location(longitude=116.397128, latitude=39.916527),
                      visit_duration=120, description="热门旅游景点", category="景点", ticket_price=50),
            Attraction(name=f"{city}热门景点2", address=f"{city}市郊区",
                      location=Location(longitude=116.397128, latitude=39.916527),
                      visit_duration=120, description="热门旅游景点", category="景点", ticket_price=50),
        ])


# 注册Agent
agent_registry.register("attraction", AttractionAgent())
