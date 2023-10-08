from middle.schemas import HTTPResponse
from fastapi.exceptions import HTTPException
from fastapi import APIRouter, Body
from main import APYManager

router = APIRouter(prefix="/json", tags=["JSON"])

@router.post("/runcode",
    description="Run a code",
    response_model=HTTPResponse,
    responses=APYManager.get_responses()
)
async def run_code(
    language: str = Body(description="The programming language", min_length=1, max_length=30, example="js"),
    code: str = Body(description="The code to run", max_length=3000)
):
    print(language, "LANGUAGE")
    print(APYManager.languages, "SSSS") 
    lang = next((x for x in APYManager.languages if x["language"] == language or language in x["aliases"]), None)
    if not lang:
        raise HTTPException(400, { "error": "The provided programming language is invalid", "metadata": {"languages": APYManager.languages}, "loc": "language", "param_type": "query"})
    d = {
        "language": lang["language"],
        "version": lang["version"],
        "files": [{"content": code}],
        "args": None,
        "stdin": "",
        "log": 0,
    }
    res = await APYManager.request(method="POST", url="https://emkc.org/api/v2/piston/execute", json=d)
    return HTTPResponse.use(data=res)