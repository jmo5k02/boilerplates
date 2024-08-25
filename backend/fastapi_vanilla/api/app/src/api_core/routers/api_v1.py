from fastapi import APIRouter

router = APIRouter(
    responses={404: {"description": "Not found"}},
)

