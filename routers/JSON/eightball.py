from middle.schemas import HTTPResponse
from fastapi import APIRouter, Query
from main import APYManager
from typing import Literal
from random import choice

router = APIRouter(prefix="/json", tags=["JSON"])

RESPONSES = {
    "en": ["Yes.", "No.", "Maybe.", "Probably.", "Probably no.", "I don't know.", "Sure.", "Obviously no.", "I doubt it."],
    "es": ["Si.", "No.", "Tal vez.", "Probablemente.", "Probablemente no.", "No sé.", "Obvio si.", "Obvio no.", "Lo dudo."],
    "pt": ["Sim.", "Não.", "Talvez.", "Provavelmente.", "Provavelmente não.", "Não sei.", "Óbvio.", "Óbvio não.", "Duvido."],
    "fr": ["Oui", "Non.", "Peut-être.", "Probablement.", "Probablement non.", "Je ne sais pas.", "De toute évidence.", "Évidemment pas.", "J'en doute."]
}

@router.get("/8ball",
    description="Get a random 8ball response",
    response_model=HTTPResponse,
    responses=APYManager.get_responses()
)
async def magic_ball(
    text: str = Query(description="The question to do to the magic ball", min_length=2, max_length=1000),
    idiom: Literal["en", "es", "pt", "fr"] = Query("en", description="The idiom for the response")
):
    return HTTPResponse.use(data={
        "question": text,
        "idiom": idiom,
        "response": choice(RESPONSES.get(idiom))
    })