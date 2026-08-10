"""API routes for the ratings feature.

Endpoints:
    POST   /api/v1/books/{content_id}/ratings    — create or update a rating
    GET    /api/v1/books/{content_id}/ratings/me — get my rating for a book
    DELETE /api/v1/books/{content_id}/ratings/me — delete my rating
    GET    /api/v1/users/me/ratings               — get all my ratings (paginated)

content_id uses the prefixed convention: gb:{id}, cv:{id}, ia:{id}.
The route layer resolves content_id to an internal book UUID before
passing to the service layer. The DB schema is unchanged.
"""

from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db, get_content_router
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
) -> UUID:
    """Resolve a content_id to an internal book UUID.

    Fetch-and-persist strategy:
        1. Parse and validate the content_id format.
        2. Check DB for existing book record.
        3. If not in DB, fetch from external API (persists as side-effect).
        4. Return internal UUID.

    Args:
        content_id: Prefixed content identifier.
        content_router: For fetching from external APIs if needed.
        rating_service: For DB resolution.

    Returns:
        Internal book UUID.

    Raises:
        HTTPException 400: When content_id format is invalid.
        HTTPException 404: When content cannot be found in any source.
    """
    if parse_content_id(content_id) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_CONTENT_ID",
                "message": f"Invalid content_id format: '{content_id}'.",
            },
        )

    book_uuid = await rating_service.resolve_content_id(content_id)

    if book_uuid is None:
        item = await content_router.get_by_content_id(content_id)
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "CONTENT_NOT_FOUND",
                    "message": f"No content found with id {content_id}.",
                },
            )
        book_uuid = await rating_service.resolve_content_id(content_id)

    if book_uuid is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "CONTENT_NOT_FOUND",
                "message": f"Content {content_id} could not be resolved to a book record.",
            },
        )

    return book_uuid


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
    """Create or update the current user's rating for a content item.

    Args:
        content_id: Prefixed content identifier (gb:, cv:, ia:).
        payload: Rating data including star rating and optional review.
        current_user: Authenticated user.
        db: Database session.
        content_router: For resolving unknown content_ids via external APIs.

    Returns:
        Success envelope wrapping RatingResponse.

    Raises:
        HTTPException 400: When content_id format is invalid.
        HTTPException 404: When content is not found.
        HTTPException 401: When user is not authenticated.
    """
    service = RatingService(db)
    book_uuid = await _resolve_to_book_uuid(content_id, content_router, service)

    rating = await service.rate_book(
        user_id=current_user.id,
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
    """Get the current user's rating for a specific content item.

    Args:
        content_id: Prefixed content identifier.
        current_user: Authenticated user.
        db: Database session.
        content_router: For resolving unknown content_ids.

    Returns:
        Success envelope wrapping RatingResponse.

    Raises:
        HTTPException 404: When rating or content is not found.
    """
    service = RatingService(db)
    book_uuid = await _resolve_to_book_uuid(content_id, content_router, service)

    rating = await service.get_my_rating(
        user_id=current_user.id,
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
    """Delete the current user's rating for a specific content item.

    Args:
        content_id: Prefixed content identifier.
        current_user: Authenticated user.
        db: Database session.
        content_router: For resolving unknown content_ids.

    Returns:
        Success envelope with confirmation message.

    Raises:
        HTTPException 404: When rating or content is not found.
    """
    service = RatingService(db)
    book_uuid = await _resolve_to_book_uuid(content_id, content_router, service)

    deleted = await service.delete_my_rating(
        user_id=current_user.id,
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
    """Get all ratings submitted by the current user, paginated.

    Args:
        current_user: Authenticated user.
        db: Database session.
        limit: Page size (1-100, default 20).
        offset: Results to skip (default 0).

    Returns:
        Success envelope wrapping MyRatingsResponse.
    """
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
