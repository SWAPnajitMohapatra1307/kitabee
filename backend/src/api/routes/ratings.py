"""API routes for the ratings feature.

Endpoints:
    POST   /api/v1/books/{book_id}/ratings      — create or update a rating
    GET    /api/v1/books/{book_id}/ratings/me   — get my rating for a book
    DELETE /api/v1/books/{book_id}/ratings/me   — delete my rating for a book
    GET    /api/v1/users/me/ratings              — get all my ratings (paginated)
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db
from src.api.response import error_envelope, success_envelope
from src.auth.dependencies import get_current_user
from src.database.models.user import User
from src.schemas.rating import MyRatingsResponse, RatingCreate, RatingResponse
from src.services.rating_service import RatingService

router = APIRouter(tags=["ratings"])


@router.post(
    "/api/v1/books/{book_id}/ratings",
    status_code=status.HTTP_200_OK,
)
async def rate_book(
    book_id: UUID,
    payload: RatingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create or update the current user's rating for a book."""
    service = RatingService(db)
    rating = await service.rate_book(
        user_id=current_user.id,
        book_id=book_id,
        payload=payload,
    )
    return success_envelope(RatingResponse.model_validate(rating).model_dump(mode="json"))


@router.get(
    "/api/v1/books/{book_id}/ratings/me",
    status_code=status.HTTP_200_OK,
)
async def get_my_book_rating(
    book_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the current user's rating for a specific book."""
    service = RatingService(db)
    rating = await service.get_my_rating(
        user_id=current_user.id,
        book_id=book_id,
    )
    if rating is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "RATING_NOT_FOUND", "message": "You have not rated this book."},
        )
    return success_envelope(RatingResponse.model_validate(rating).model_dump(mode="json"))


@router.delete(
    "/api/v1/books/{book_id}/ratings/me",
    status_code=status.HTTP_200_OK,
)
async def delete_my_book_rating(
    book_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete the current user's rating for a specific book."""
    service = RatingService(db)
    deleted = await service.delete_my_rating(
        user_id=current_user.id,
        book_id=book_id,
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "RATING_NOT_FOUND", "message": "You have not rated this book."},
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
    """Get all ratings submitted by the current user, paginated."""
    service = RatingService(db)
    ratings, total = await service.get_my_ratings(
        user_id=current_user.id,
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