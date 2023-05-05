from pydantic import BaseModel, Extra


class BaseResponseSchema(BaseModel):
    class Config:
        orm_mode = True


class BaseValidationSchema(BaseModel):
    class Config:
        extra = Extra.ignore
        allow_mutation = False
        anystr_strip_whitespace = True
