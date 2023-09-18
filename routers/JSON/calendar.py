from middleware.schemas import HTTPResponse
from fastapi import APIRouter, Query
from main import APYManager
from calendar import month as M
from datetime import datetime

router = APIRouter(prefix="/json", tags=["JSON"])

@router.get("/calendar",
    description="Check the calendar of a month",
    response_model=HTTPResponse,
    responses=APYManager.get_responses()
)
async def calendar(
    year: int = Query(2023, description="The year calendar", le=2100, ge=1000),
    month: int = Query(datetime.now().month, description="The month calendar", le=12, ge=1)
):
    return HTTPResponse.use(data=M(year, month))