from typing import List

import pandas as pd
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

from challenge.model import DelayModel, InputDataException

app = FastAPI()
model = DelayModel()

class FlightData(BaseModel):
    OPERA: str
    TIPOVUELO: str
    MES: int

class PredictRequest(BaseModel):
    flights: List[FlightData]

class PredictResponse(BaseModel):
    predict: List[int]

@app.get("/health", status_code=status.HTTP_200_OK)
async def get_health() -> dict:
    return {
        "status": "OK"
    }

@app.post("/predict", status_code=status.HTTP_200_OK)
async def post_predict(request: PredictRequest) -> dict:
    try:
        data_list = [flight.dict() for flight in request.flights]
        data = pd.DataFrame(data_list)
        
        # Perform preprocessing
        features = model.preprocess(data)
        
        # Use the model to make a prediction (you may need to adapt depending on how your model works)
        predictions  = model._model.predict(features)

        return {"predict": predictions.tolist()}
    except InputDataException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))