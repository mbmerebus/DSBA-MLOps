#Code for scoring logic
from pydantic import BaseModel, Field

#item classes

#Appartment class to be sent for scoring / with input fields
#per FastAPI documentation, Field is more robust.
class AppartmentItem(BaseModel):
    roomAmount: int = Field(placeholder=0, description="Number of rooms.", le=(3)) #number of rooms
    adress: str = Field(placeholder="", description="Adress of appartment.") #adress
    surface: float = Field(placeholder=0, description="Surface of appartment in square meters.") #surface in square meters




#functions for score

def score(apprt: AppartmentItem) -> int: #return an int for now but will change with implementation
    return 1 #return 1 for now but will change in further implementation