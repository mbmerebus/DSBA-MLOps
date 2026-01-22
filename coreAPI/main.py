#Per FastAPI Documentation:

#Some imports are for later if needed.
from fastapi import FastAPI, Path
from typing import Optional

#import from scripts
from scoring import score,AppartmentItem #scoring algo import

# Beginning of APP
app = FastAPI(title="Let's Score your Appartment !")


#Root of app
@app.post("/score")
#NOTE: request optional for debug purposes (so it scores "1" for now). TODO change that when request system is made
#NOTE 2: ChatGPT used for debug
async def root(reqst: Optional[AppartmentItem] = None): 
    if reqst is None:
        #TEST REQUEST
        reqst= AppartmentItem(
            adress="Rue des Mariniers",
            roomAmount=2,
            surface=14.8
        )

    #score function call
    _scored = score(reqst)
    return _scored