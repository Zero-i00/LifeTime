from typing import Final
from pydantic import BaseModel


class ModelConstants(BaseModel):
    max_char_field: Final[int] = 256
    max_text_field: Final[int] = 5_000

class Constants(BaseModel):
    model: ModelConstants = ModelConstants()


constants = Constants()
