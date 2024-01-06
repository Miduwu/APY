from middle.schemas import HTTPResponse
from fastapi import APIRouter, Query
from fastapi.exceptions import HTTPException
from main import APYManager

def text_to_bits(text, encoding="utf-8", errors="surrogatepass"):
    bits = bin(int.from_bytes(text.encode(encoding, errors), "big"))[2:]
    return bits.zfill(8 * ((len(bits) + 7) // 8))


def text_from_bits(bits, encoding="utf-8", errors="surrogatepass"):
    n = int(bits, 2)
    return n.to_bytes((n.bit_length() + 7) // 8, "big").decode(encoding, errors) or "\0"

router = APIRouter(prefix="/json", tags=["JSON"])

@router.get("/binary",
    description="Encode or decode a binary text",
    response_model=HTTPResponse,
    responses=APYManager.get_responses()
)
async def binary(
    body: str = Query(description="The body to encode/decode", min_length=2, max_length=1000),
):
    try:
        return HTTPResponse.use(data={
            "original": body,
            "converted": text_from_bits(body) if body.isdigit() else text_to_bits(body)
        })
    except:
        raise HTTPException(400 ,detail={"error": "Your body was unable to be decoded", "loc": "query", "param_type": "query"})