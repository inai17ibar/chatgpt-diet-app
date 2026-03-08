from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.database import MealLog, get_session
from app.models.schemas import (
    DailyMealInput,
    DailySummaryResponse,
    HealthCheckResponse,
    MealInput,
    MealLogResponse,
    MealType,
    PostResult,
)
from app.services.meal_processor import create_and_post, process_single_meal

router = APIRouter()


async def verify_api_key(x_api_key: Annotated[str | None, Header()] = None):
    """APIキー認証"""
    if x_api_key != settings.secret_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """ヘルスチェック"""
    return HealthCheckResponse(status="ok")


@router.post("/meal/analyze", response_model=PostResult)
async def analyze_meal(
    meal: MealInput,
    session: AsyncSession = Depends(get_session),
    _: None = Depends(verify_api_key),
):
    """単一の食事を分析（投稿なし）"""
    pfc = await process_single_meal(meal)
    return PostResult(success=True, pfc=pfc)


@router.post("/meal/post", response_model=PostResult)
async def post_meal(
    daily_input: DailyMealInput,
    auto_post: bool = True,
    session: AsyncSession = Depends(get_session),
    _: None = Depends(verify_api_key),
):
    """食事を処理してInstagramに投稿"""
    result = await create_and_post(daily_input, session, auto_post=auto_post)
    return result


@router.post("/meal/quick", response_model=PostResult)
async def quick_post(
    description: str,
    auto_post: bool = True,
    session: AsyncSession = Depends(get_session),
    _: None = Depends(verify_api_key),
):
    """
    簡易モード：テキストだけで投稿

    例: "昼：サラダチキン、夜：豚しゃぶ"
    """
    daily_input = DailyMealInput(
        date=datetime.now(),
        total_description=description,
    )
    result = await create_and_post(daily_input, session, auto_post=auto_post)
    return result


@router.post("/shortcut/meal", response_model=PostResult)
async def shortcut_endpoint(
    meal_type: MealType = MealType.LUNCH,
    description: str | None = None,
    image_base64: str | None = None,
    auto_post: bool = True,
    session: AsyncSession = Depends(get_session),
    _: None = Depends(verify_api_key),
):
    """
    iPhoneショートカット用エンドポイント

    - meal_type: breakfast/lunch/dinner/snack
    - description: 食事の説明（任意）
    - image_base64: 写真のBase64（任意）
    - auto_post: 自動投稿するか（デフォルト: true）
    """
    meal = MealInput(
        meal_type=meal_type,
        description=description,
        image_base64=image_base64,
    )
    daily_input = DailyMealInput(
        date=datetime.now(),
        meals=[meal],
    )
    result = await create_and_post(daily_input, session, auto_post=auto_post)
    return result


@router.get("/meal/history", response_model=list[MealLogResponse])
async def get_meal_history(
    start_date: str | None = Query(None, description="開始日 (YYYY-MM-DD)"),
    end_date: str | None = Query(None, description="終了日 (YYYY-MM-DD)"),
    session: AsyncSession = Depends(get_session),
    _: None = Depends(verify_api_key),
):
    """食事ログの履歴を取得"""
    query = select(MealLog).order_by(MealLog.date.desc())

    if start_date:
        query = query.where(MealLog.date >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.where(
            MealLog.date <= datetime.fromisoformat(end_date + "T23:59:59")
        )

    result = await session.execute(query)
    logs = result.scalars().all()

    return [
        MealLogResponse(
            id=log.id,
            date=log.date.strftime("%Y-%m-%d"),
            protein=log.protein,
            fat=log.fat,
            carbs=log.carbs,
            calories=log.calories,
            meal_description=log.meal_description,
            ai_comment=log.ai_comment,
            mode=log.mode or "text_only",
        )
        for log in logs
    ]


@router.get("/meal/daily-summary", response_model=list[DailySummaryResponse])
async def get_daily_summary(
    days: int = Query(30, description="取得する日数"),
    session: AsyncSession = Depends(get_session),
    _: None = Depends(verify_api_key),
):
    """日別のPFCサマリーを取得"""
    query = (
        select(
            func.date(MealLog.date).label("date"),
            func.sum(MealLog.protein).label("total_protein"),
            func.sum(MealLog.fat).label("total_fat"),
            func.sum(MealLog.carbs).label("total_carbs"),
            func.sum(MealLog.calories).label("total_calories"),
            func.count(MealLog.id).label("meal_count"),
        )
        .group_by(func.date(MealLog.date))
        .order_by(func.date(MealLog.date).desc())
        .limit(days)
    )

    result = await session.execute(query)
    rows = result.all()

    return [
        DailySummaryResponse(
            date=str(row.date),
            total_protein=row.total_protein or 0,
            total_fat=row.total_fat or 0,
            total_carbs=row.total_carbs or 0,
            total_calories=row.total_calories or 0,
            meal_count=row.meal_count,
        )
        for row in rows
    ]
