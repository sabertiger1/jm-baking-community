from fastapi import APIRouter

from . import baking_records, classes, points, ratings, votes

router = APIRouter()

router.include_router(baking_records.router, prefix="/baking", tags=["Baking: Records"])
router.include_router(ratings.router, prefix="/recipes", tags=["Baking: Ratings"])
router.include_router(points.router, prefix="/points", tags=["Baking: Points"])
router.include_router(votes.router, prefix="/votes", tags=["Baking: Votes"])
router.include_router(classes.router, prefix="/classes", tags=["Baking: Classes"])
