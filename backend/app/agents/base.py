"""Agent基类定义"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from hello_agents import SimpleAgent
from hello_agents.tools import MCPTool
from ..services.llm_service import get_llm
from ..config import get_settings
import asyncio
from functools import lru_cache


class BaseAgent(ABC):
    """Agent基类"""
    
    def __init__(self, name: str, system_prompt: str):
        """
        初始化Agent
        
        Args:
            name: Agent名称
            system_prompt: 系统提示词
        """
        self.name = name
        self.system_prompt = system_prompt
        self.llm = get_llm()
        self.agent = SimpleAgent(
            name=name,
            llm=self.llm,
            system_prompt=system_prompt
        )
        self._tools: List[MCPTool] = []
        
    def add_tool(self, tool: MCPTool):
        """添加工具"""
        self._tools.append(tool)
        self.agent.add_tool(tool)
        
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """执行Agent任务"""
        pass
    
    def get_tools(self) -> List[str]:
        """获取可用工具列表"""
        return self.agent.list_tools()


class AgentRegistry:
    """Agent注册表 - 用于管理所有Agent实例"""
    
    _instance = None
    _agents: Dict[str, BaseAgent] = {}
    _mcp_tool: Optional[MCPTool] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def get_shared_mcp_tool(cls) -> MCPTool:
        """获取共享的MCP工具实例（单例模式）"""
        if cls._mcp_tool is None:
            settings = get_settings()
            if not settings.amap_api_key:
                raise ValueError("高德地图API Key未配置")
            
            cls._mcp_tool = MCPTool(
                name="amap",
                description="高德地图服务",
                server_command=["uvx", "amap-mcp-server"],
                env={"AMAP_MAPS_API_KEY": settings.amap_api_key},
                auto_expand=True
            )
        return cls._mcp_tool
    
    def register(self, name: str, agent: BaseAgent):
        """注册Agent"""
        self._agents[name] = agent
        
    def get(self, name: str) -> Optional[BaseAgent]:
        """获取Agent"""
        return self._agents.get(name)
    
    def list_agents(self) -> List[str]:
        """列出所有Agent"""
        return list(self._agents.keys())


# 全局Agent注册表实例
agent_registry = AgentRegistry()
