from datetime import datetime

from fastapi import HTTPException
from typing import List
import logging
import utils
from httpx import AsyncClient, HTTPStatusError


from fastapi import FastAPI, Depends, File, UploadFile, Request
from fastapi.responses import StreamingResponse


from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

import models
import schemas
from database2 import Session, engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()

@app.get("/customers", response_model=List[schemas.Customer])
def get_customers(db: Session = Depends(get_db)):
    try:
        return utils.export_customers(db)
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error :c")

@app.get("/customers/csv")
def export_customers_to_csv(db: Session = Depends(get_db)):
    csv_file = utils.export_customers_to_csv(utils.export_customers(db))
    return StreamingResponse(csv_file, media_type="text/csv")

@app.post("/customers")
def import_customers(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        customers = utils.import_customers_from_csv(file.file)
        utils.upsert_customers(db, customers)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"message": "Your file was processed successfully :)"}

@app.post("/salesforce_sync")
@limiter.limit("5/minute")
async def sync():
    data = await call_sf_api()
    return data

async def call_sf_api():
    sf_url = 'https://jsonplaceholder.typicode.com/users'
    async with AsyncClient() as client:
        try:
            response = await client.get(sf_url)
            response.raise_for_status()
            return response.json()
        except HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail=str(exc))
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

@app.get("/analytics", response_model=schemas.AnalyticsResponse)
def get_analytics(start_date: datetime, end_date: datetime, db: Session = Depends(get_db)):
    response = utils.get_customers_analytics(db, start_date, end_date)
    return response