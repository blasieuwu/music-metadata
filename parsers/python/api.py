from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import tempfile
import os
from mdata import validate_mdata, _track_identify

app = FastAPI(title="mdata API", version="1.0.0")

class RawMDataRequest(BaseModel):
    content: str

@app.post("/parse/file")
async def parse_file(file: UploadFile = File(...)):
    if not file.filename.endswith(".mdata"):
        raise HTTPException(status_code=400, detail="File must have a .mdata extension")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mdata") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        result = validate_mdata(tmp_path, silent=True)
        if result is None:
            raise HTTPException(status_code=422, detail="Invalid .mdata file content or syntax")
        return {"status": "success", "data": result}
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

@app.post("/parse/raw")
async def parse_raw(payload: RawMDataRequest):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mdata", mode="w", encoding="utf-8") as tmp:
        tmp.write(payload.content)
        tmp_path = tmp.name

    try:
        result = validate_mdata(tmp_path, silent=True)
        if result is None:
            raise HTTPException(status_code=422, detail="Invalid .mdata content or syntax")
        return {"status": "success", "data": result}
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

@app.post("/identify/file")
async def identify_file(file: UploadFile = File(...)):
    if not file.filename.endswith(".mdata"):
        raise HTTPException(status_code=400, detail="File must have a .mdata extension")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mdata") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        identity = _track_identify(tmp_path)
        if not identity:
            raise HTTPException(status_code=422, detail="Unable to extract track identity")
        return {"status": "success", "identity": identity}
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)