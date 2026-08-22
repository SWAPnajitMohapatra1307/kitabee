"""API routes for the ratings feature."""

from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_content_router, get_db
from src.api.response import success_envelope
from src.auth.dependencies import get_current_user
from src.database.models.user import User
from src.schemas.rating import MyRatingsResponse, RatingCreate, RatingResponse
from src.services.content_router import ContentRouter
from src.services.content_normalizer import parse_content_id
from src.services.rating_service import RatingService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["ratings"])


async def _resolve_to_book_uuid(
    content_id: str,
    content_router: ContentRouter,
    rating_service: RatingService,
    create_if_missing: bool = False,
) -> UUID | None:
    """Resolve a content_id to an internal book UUID.

    Strategy:
        1. Check DB for existing book record.
        2. If missing and create_if_missing is True:
           - Fetch item metadata via ContentRouter (or catalog)
           - Upsert book into Postgres DB and return new UUID.
        3. If missing and create_if_missing is False, return None.
    """
    # 1. Check existing DB
    book_uuid = await rating_service.resolve_content_id(content_id)
    if book_uuid is not None:
        return book_uuid

    # 2. If not in DB yet and creation requested (e.g. rate POST)
    if create_if_missing:
        item = await content_router.get_by_content_id(content_id)
        if item is not None:
            book_uuid = await rating_service.ensure_book_in_db(item)
            return book_uuid

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "CONTENT_NOT_FOUND",
                "message": f"No content found with id {content_id}.",
            },
        )

    return None


@router.post(
    "/api/v1/books/{content_id}/ratings",
    status_code=status.HTTP_200_OK,
)
async def rate_book(
    content_id: str,
    payload: RatingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    content_router: ContentRouter = Depends(get_content_router),
):
    user_id: UUID = current_user.id

    service = RatingService(db)
    book_uuid = await _resolve_to_book_uuid(
        content_id, content_router, service, create_if_missing=True
    )

    if book_uuid is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "CONTENT_NOT_FOUND",
                "message": f"Content {content_id} could not be resolved to a book record.",
            },
        )

    rating = await service.rate_book(
        user_id=user_id,
        book_id=book_uuid,
        payload=payload,
    )
    return success_envelope(RatingResponse.model_validate(rating).model_dump(mode="json"))


@router.get(
    "/api/v1/books/{content_id}/ratings/me",
    status_code=status.HTTP_200_OK,
)
async def get_my_book_rating(
    content_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    content_router: ContentRouter = Depends(get_content_router),
):
    user_id: UUID = current_user.id

    service = RatingService(db)
    book_uuid = await _resolve_to_book_uuid(
        content_id, content_router, service, create_if_missing=False
    )

    if book_uuid is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "RATING_NOT_FOUND",
                "message": "You have not rated this content.",
            },
        )

    rating = await service.get_my_rating(
        user_id=user_id,
        book_id=book_uuid,
    )
    if rating is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "RATING_NOT_FOUND",
                "message": "You have not rated this content.",
            },
        )
    return success_envelope(RatingResponse.model_validate(rating).model_dump(mode="json"))


@router.delete(
    "/api/v1/books/{content_id}/ratings/me",
    status_code=status.HTTP_200_OK,
)
async def delete_my_book_rating(
    content_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    content_router: ContentRouter = Depends(get_content_router),
):
    user_id: UUID = current_user.id

    service = RatingService(db)
    book_uuid = await _resolve_to_book_uuid(
        content_id, content_router, service, create_if_missing=False
    )

    if book_uuid is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "RATING_NOT_FOUND",
                "message": "You have not rated this content.",
            },
        )

    deleted = await service.delete_my_rating(
        user_id=user_id,
        book_id=book_uuid,
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "RATING_NOT_FOUND",
                "message": "You have not rated this content.",
            },
        )
    return success_envelope({"message": "Rating deleted successfully."})


@router.get(
    "/api/v1/users/me/ratings",
    status_code=status.HTTP_200_OK,
)
async def get_my_ratings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    user_id: UUID = current_user.id

    service = RatingService(db)
    ratings, total = await service.get_my_ratings(
        user_id=user_id,
        limit=limit,
        offset=offset,
    )
    response = MyRatingsResponse(
        total=total,
        limit=limit,
        offset=offset,
        results=[RatingResponse.model_validate(r) for r in ratings],
    )
    return success_envelope(response.model_dump(mode="json"))