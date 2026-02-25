from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.database import get_session
from app.models.schemas import (
    DailyMealInput,
    HealthCheckResponse,
    MealInput,
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
