#Per FastAPI Documentation:

#Some imports are for later if needed.
from typing import Annotated
from fastapi import Body,FastAPI, Path
from pydantic import BaseModel, Field

# Beginning of APP
app = FastAPI()

#Root
@app.get("/")
async def root():
    return 1