# 智能旅行规划系统 🌍✈️

基于 LLM 与多智能体架构的智能旅行规划系统，实现景点推荐、天气查询、酒店推荐与行程自动规划等功能，通过 Agent 协作自动生成完整旅行方案。

## ✨ 功能特点

- 🤖 **Multi-Agent 协作架构**: 拆分景点搜索、天气查询、酒店推荐与行程规划 4 类智能体，通过任务分解与协作提升复杂任务处理能力
- 🗺️ **高德地图集成**: 通过 MCP 协议接入高德地图 API，实现 POI 搜索、天气查询等外部工具调用
- 🧠 **智能工具调用**: Agent 自动调用高德地图 MCP 工具，获取实时 POI、路线和天气信息
- 🎨 **现代化前端**: Vue3 + TypeScript + Vite，响应式设计，流畅的用户体验
- 📱 **完整功能**: 包含住宿、交通、餐饮和景点游览时间推荐
- 💰 **预算估算**: 自动计算景点门票、酒店、餐饮、交通等费用
- 📄 **PDF导出**: 支持将旅行计划导出为 PDF 文档
- 🗺️ **地图可视化**: 高德地图展示景点位置和游览路线

## 🏗️ 技术栈

### 后端
- **框架**: FastAPI + HelloAgents
- **架构**: Multi-Agent 协作架构
- **MCP工具**: amap-mcp-server (高德地图)
- **数据模型**: Pydantic 结构化数据验证
- **LLM**: 支持多种 LLM 提供商 (OpenAI, DeepSeek 等)
- **异步处理**: asyncio 并行任务执行

### 前端
- **框架**: Vue 3 + TypeScript
- **构建工具**: Vite
- **UI组件库**: Ant Design Vue
- **地图服务**: 高德地图 JavaScript API
- **HTTP客户端**: Axios
- **PDF导出**: html2canvas + jsPDF

## 📁 项目结构

```
helloagents-trip-planner/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── agents/            # 多智能体系统
│   │   │   ├── base.py        # Agent 基类与注册表
│   │   │   ├── attraction_agent.py    # 景点搜索 Agent
│   │   │   ├── weather_agent.py       # 天气查询 Agent
│   │   │   ├── hotel_agent.py         # 酒店推荐 Agent
│   │   │   ├── planner_agent.py       # 行程规划 Agent
│   │   │   └── trip_planner_agent.py  # 主控制器
│   │   ├── api/               # FastAPI 路由
│   │   │   ├── main.py
│   │   │   └── routes/
│   │   │       ├── trip.py    # 旅行规划 API
│   │   │       ├── poi.py     # POI 搜索 API
│   │   │       └── map.py     # 地图服务 API
│   │   ├── services/          # 服务层
│   │   │   ├── amap_service.py
│   │   │   ├── llm_service.py
│   │   │   └── unsplash_service.py
│   │   ├── models/            # Pydantic 数据模型
│   │   │   └── schemas.py
│   │   └── config.py          # 配置管理
│   ├── requirements.txt
│   ├── .env.example
│   └── run.py
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── views/
│   │   │   ├── Home.vue       # 首页表单
│   │   │   └── Result.vue     # 结果展示（地图、PDF导出）
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── types/
│   │   │   └── index.ts
│   │   ├── App.vue
│   │   └── main.ts
│   ├── package.json
│   ├── vite.config.ts
│   └── .env.example
└── README.md
```

## 🚀 快速开始

### 前提条件

- Python 3.10+
- Node.js 16+
- 高德地图 API 密钥 (Web 服务 API 和 Web 端 JS API)
- LLM API 密钥 (OpenAI/DeepSeek 等)

### 后端安装

1. 进入后端目录
```bash
cd backend
```

2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 API 密钥
```

5. 启动后端服务
```bash
python run.py
# 或
uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端安装

1. 进入前端目录
```bash
cd frontend
```

2. 安装依赖
```bash
npm install
```

3. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，填入高德地图 Web API Key 和 Web 端 JS API Key
```

4. 启动开发服务器
```bash
npm run dev
```

5. 打开浏览器访问 `http://localhost:5173`

## 📝 使用指南

1. **填写旅行信息**:
   - 目的地城市
   - 旅行日期和天数
   - 交通方式偏好
   - 住宿偏好
   - 旅行风格标签

2. **生成旅行计划**:
   - 点击"生成旅行计划"按钮
   - 系统通过 Multi-Agent 协作自动生成方案

3. **查看结果**:
   - 📅 每日详细行程
   - 🗺️ 景点地图标记与路线
   - 🌤️ 天气预报
   - 🏨 酒店推荐
   - 🍽️ 餐饮安排
   - 💰 预算明细

4. **编辑与导出**:
   - ✏️ 编辑行程内容
   - 📷 导出为图片
   - 📄 导出为 PDF

## 🔧 核心实现

### Multi-Agent 协作架构

```python
# 主控制器协调多个 Agent 协作
class MultiAgentTripPlanner:
    def __init__(self):
        self.attraction_agent = AttractionAgent()  # 景点搜索
        self.weather_agent = WeatherAgent()        # 天气查询
        self.hotel_agent = HotelAgent()            # 酒店推荐
        self.planner_agent = PlannerAgent()        # 行程规划
    
    async def plan_trip(self, request: TripRequest) -> TripPlan:
        # Step 1: 并行执行景点搜索和天气查询
        attractions, weather = await asyncio.gather(
            self.attraction_agent.execute(...),
            self.weather_agent.execute(...)
        )
        
        # Step 2: 酒店推荐
        hotels = await self.hotel_agent.execute(...)
        
        # Step 3: 整合生成完整行程
        trip_plan = await self.planner_agent.execute(...)
        
        return trip_plan
```

### MCP 工具调用

```python
from hello_agents.tools import MCPTool

# 创建高德地图 MCP 工具（单例模式）
amap_tool = MCPTool(
    name="amap",
    server_command=["uvx", "amap-mcp-server"],
    env={"AMAP_MAPS_API_KEY": "your_api_key"},
    auto_expand=True
)

# Agent 自动调用工具
# - maps_text_search: 搜索景点 POI
# - maps_weather: 查询天气
# - maps_direction_*: 路线规划
```

### 结构化数据模型

```python
from pydantic import BaseModel, Field

class TripPlan(BaseModel):
    """旅行计划"""
    city: str
    start_date: str
    end_date: str
    days: List[DayPlan]
    weather_info: List[WeatherInfo]
    overall_suggestions: str
    budget: Budget

class Budget(BaseModel):
    """预算信息"""
    total_attractions: int      # 景点门票总费用
    total_hotels: int           # 酒店总费用
    total_meals: int            # 餐饮总费用
    total_transportation: int   # 交通总费用
    total: int                  # 总费用
```

## 📄 API 文档

启动后端服务后，访问 `http://localhost:8000/docs` 查看完整的 API 文档。

### 主要端点

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/api/trip/plan` | 生成旅行计划 |
| GET | `/api/trip/agents/status` | 获取 Agent 状态 |
| GET | `/api/trip/health` | 健康检查 |
| GET | `/api/poi/search` | 搜索 POI |
| GET | `/api/map/weather` | 查询天气 |

## 🎯 项目成果

- ✅ 实现完整 AI Agent 应用系统，支持自动生成多天个性化旅行计划
- ✅ 系统可自动整合景点 / 酒店 / 天气 / 预算多维信息
- ✅ 前端支持地图可视化、行程编辑与导出功能
- ✅ 引入异步请求与 API 复用机制，优化系统响应效率

## 🤝 贡献指南

欢迎提交 Pull Request 或 Issue！

## 📜 开源协议

CC BY-NC-SA 4.0

## 🙏 致谢

- [HelloAgents](https://github.com/datawhalechina/hello-agents) - 智能体框架
- [高德地图开放平台](https://lbs.amap.com/) - 地图服务
- [amap-mcp-server](https://github.com/modelcontextprotocol/servers) - 高德地图 MCP 服务器
