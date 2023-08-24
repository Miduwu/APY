import pydantic, json, typing
from fastapi.responses import JSONResponse

class PrettyJSONResponse(JSONResponse):
    def render(self, content: typing.Any) -> bytes:
        return json.dumps(content, ensure_ascii=False, allow_nan=False, indent=4, separators=(", ", ": ")).encode("utf-8")

class HTTPResponse(pydantic.BaseModel):
    status: int
    data: typing.Any
    success: bool

    @staticmethod
    def use(*,
        status: int = 200, data: str | int | float | dict | list, headers: typing.Dict[str, str] | None = None
    ):
        return PrettyJSONResponse(
            content={
                "status": status,
                "data": data,
                "success": status == 200 or status == 201,
            },
            status_code=status,
            headers=headers,
        )

class HTTPBadResponseData(pydantic.BaseModel):
    error: str
    metadata: typing.Dict[str, typing.Any] | None
    loc: str | None
    param_type: str | None

class HTTPBadResponse(pydantic.BaseModel):
    status: int
    data: HTTPBadResponseData
    success: bool = False

    @staticmethod
    def use(*, status: int = 400, data: HTTPBadResponseData, headers: typing.Dict[str, str] | None = None):
        return HTTPResponse.use(status=status, data=data, headers=headers)

