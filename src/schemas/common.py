from typing import Annotated

from pydantic import Field

Age = Annotated[int, Field(gt=1, lt=150)]
Name = Annotated[str, Field(min_length=2)]
Rating = Annotated[float, Field(gt=0, le=10)]
