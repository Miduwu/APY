from middle.schemas import HTTPResponse
from fastapi.exceptions import HTTPException
from fastapi import APIRouter, Query
from deep_translator import GoogleTranslator
from main import APYManager

router = APIRouter(prefix="/json", tags=["JSON"])

convert = lambda x: x.replace("ch", "zh-CN").replace("zh-tw", "zh-TW").replace("zh-cn", "zh-CN") if x else None

@router.get("/translate",
    description="Translate a text",
    response_model=HTTPResponse,
    responses=APYManager.get_responses()
)
async def translator(
    text: str = Query(description="The text to translate", min_length=2, max_length=1500),
    source: str = Query("auto", description="The source idiom", min_length=2, max_length=8),
    target: str = Query(description="The target idiom", min_length=2, max_length=8)
):
    source, target = convert(source.lower()), convert(target.lower())
    Translator = GoogleTranslator(source="auto", target="en")
    LANGUAGES = list(Translator.get_supported_languages(as_dict=True).values())
    if source not in LANGUAGES and source != "auto" or target not in LANGUAGES:
        raise HTTPException(400, { "error": "The provided language is not supported", "metadata": {"languages": LANGUAGES}, "loc": "target" if target not in LANGUAGES else "source", "param_type": "query"})
    Translator.source = source
    Translator.target = target
    translation = Translator.translate(text)
    if not translation:
         raise HTTPException(400, { "error": "The provided translation is invalid", "loc": None, "param_type": None})
    return HTTPResponse.use(data=translation)