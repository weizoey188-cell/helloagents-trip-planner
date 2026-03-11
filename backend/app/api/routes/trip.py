"""旅行规划API路由"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional
import asyncio
from ...models.schemas import (
    TripRequest,
    TripPlanResponse,
    TripPlan,
    ErrorResponse
)
from ...agents.trip_planner_agent import get_trip_planner_agent

router = APIRouter(prefix="/trip", tags=["旅行规划"])


@router.post(
    "/plan",
    response_model=TripPlanResponse,
    summary="生成旅行计划",
    description="根据用户输入的旅行需求，使用多Agent协作生成详细的旅行计划"
)
async def plan_trip(request: TripRequest):
    """
    生成旅行计划
    
    Args:
        request: 旅行请求参数
        
    Returns:
        旅行计划响应
    """
    try:
        print(f"\n{'='*60}")
        print(f"📥 收到旅行规划请求:")
        print(f"   城市: {request.city}")
        print(f"   日期: {request.start_date} - {request.end_date}")
        print(f"   天数: {request.travel_days}")
        print(f"   交通: {request.transportation}")
        print(f"   住宿: {request.accommodation}")
        print(f"   偏好: {', '.join(request.preferences) if request.preferences else '无'}")
        print(f"{'='*60}\n")
        
        # 获取Agent实例
        print("🔄 获取多智能体系统实例...")
        agent = get_trip_planner_agent()
        
        # 生成旅行计划（异步）
        print("🚀 开始生成旅行计划...")
        trip_plan = await agent.plan_trip(request)
        
        print("✅ 旅行计划生成成功，准备返回响应\n")
        
        return TripPlanResponse(
            success=True,
            message="旅行计划生成成功",
            data=trip_plan
        )
        
    except Exception as e:
        print(f"❌ 生成旅行计划失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"生成旅行计划失败: {str(e)}"
        )


@router.get(
    "/plan/{plan_id}",
    response_model=TripPlanResponse,
    summary="获取旅行计划",
    description="根据计划ID获取已生成的旅行计划"
)
async def get_trip_plan(plan_id: str):
    """
    获取旅行计划
    
    Args:
        plan_id: 计划ID
        
    Returns:
        旅行计划响应
    """
    # TODO: 实现计划缓存和查询
    return TripPlanResponse(
        success=False,
        message="功能开发中",
        data=None
    )


@router.post(
    "/plan/{plan_id}/optimize",
    response_model=TripPlanResponse,
    summary="优化旅行计划",
    description="根据用户反馈优化已生成的旅行计划"
)
async def optimize_trip_plan(plan_id: str, feedback: str):
    """
    优化旅行计划
    
    Args:
        plan_id: 计划ID
        feedback: 用户反馈
        
    Returns:
        优化后的旅行计划
    """
    # TODO: 实现计划优化
    return TripPlanResponse(
        success=False,
        message="功能开发中",
        data=None
    )


@router.get(
    "/agents/status",
    summary="获取Agent状态",
    description="获取多智能体系统中各Agent的状态信息"
)
async def get_agents_status():
    """
    获取Agent状态
    
    Returns:
        Agent状态信息
    """
    try:
        agent = get_trip_planner_agent()
        status = agent.get_agent_status()
        
        return {
            "success": True,
            "message": "Agent状态获取成功",
            "data": status
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取Agent状态失败: {str(e)}"
        )


@router.get(
    "/health",
    summary="健康检查",
    description="检查旅行规划服务是否正常"
)
async def health_check():
    """健康检查"""
    try:
        # 检查Agent是否可用
        agent = get_trip_planner_agent()
        status = agent.get_agent_status()
        
        # 检查所有Agent是否都处于active状态
        all_active = all(
            agent_info.get("status") == "active"
            for agent_info in status.values()
        )
        
        if all_active:
            return {
                "status": "healthy",
                "service": "trip-planner",
                "agents": {
                    "total": len(status),
                    "active": sum(1 for s in status.values() if s.get("status") == "active")
                }
            }
        else:
            raise HTTPException(
                status_code=503,
                detail="部分Agent服务异常"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"服务不可用: {str(e)}"
        )
