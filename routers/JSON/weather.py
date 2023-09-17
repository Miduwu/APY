import python_weather
from middleware.schemas import HTTPResponse
from fastapi.exceptions import HTTPException
from fastapi import APIRouter, Query
from main import APYManager
import pydash as _

router = APIRouter(prefix="/json", tags=["JSON"])

@router.get("/weather",
    description="Check the weather status in a specified location",
    response_model=HTTPResponse,
    responses=APYManager.get_responses()
)
async def weather(
    query: str = Query(description="The city to search", max_length=150, min_length=1, example="New York")
):
    async with python_weather.Client(format=python_weather.IMPERIAL) as client:
        try:
            weather = await client.get(query)
            return HTTPResponse.use(data={
                    "description": weather.current.description,
                    "feels_like": weather.current.feels_like,
                    "format": weather.current.format,
                    "humidity": weather.current.humidity,
                    "precipitation": weather.current.precipitation,
                    "pressure": weather.current.pressure,
                    "temperature": weather.current.temperature,
                    "type": {"name": weather.current.type.name, "value": weather.current.type.value},
                    "visibility": weather.current.visibility,
                    "wind_direction": weather.current.wind_direction,
                    "wind_speed": weather.current.wind_speed
                })
        except:
            raise HTTPException(404, { "error": "I was unable to find something related to that", "loc": "query", "param_type": "query"})
        