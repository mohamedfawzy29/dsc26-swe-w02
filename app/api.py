from dataclasses import asdict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.domain import EventType, InvalidTransition, Parcel, ParcelState, apply_event  # noqa: F401
import secrets
from typing import Annotated
from fastapi import FastAPI, HTTPException, Query

class ParcelCreate(BaseModel):
    merchant_ref: str = Field(min_length=1, max_length=64, strict=True)
    cod_amount_piastres: int = Field(ge=0, le=5_000_000, strict=True)
    address_text: str = Field(min_length=1, max_length=500, strict=True)


class EventIn(BaseModel):
    type: EventType

def problem(status: int, title: str, **extra) -> JSONResponse:
    body = {"type": "about:blank", "title": title, "status": status, **extra}
    return JSONResponse(body, status_code=status, media_type="application/problem+json")

def create_app() -> FastAPI:
    app = FastAPI()
    parcel_store: dict[str, Parcel] = {}

    cursors: dict[str, int] = {}     # توكن -> مكان آخر شحنة اتعرضت
    
    @app.exception_handler(StarletteHTTPException)
    async def http_problem(request, exc):
        return problem(exc.status_code, str(exc.detail))

    @app.exception_handler(RequestValidationError)
    async def validation_problem(request, exc):
        seen = set()
        errors = []
        for e in exc.errors():
            loc = tuple(e["loc"])
            if loc in seen:
                continue
            seen.add(loc)
            errors.append({"loc": list(loc), "msg": e["msg"]})
        return problem(422, "Validation error", errors=errors)

    @app.post("/v1/parcels", operation_id="createParcel", status_code=201, responses={409: {"description": "Duplicate merchant_ref"}, 422: {"description": "Invalid body"}})
    def create_parcel(body: ParcelCreate):
        if any(p.merchant_ref == body.merchant_ref for p in parcel_store.values()):
            raise HTTPException(status_code=409, detail="merchant_ref already exists")
        new_id = f"pcl_{len(parcel_store) + 1}"
        parcel = Parcel(
            id=new_id,
            merchant_ref=body.merchant_ref,
            cod_amount_piastres=body.cod_amount_piastres,
            address_text=body.address_text
        )
        parcel_store[new_id] = parcel
        return asdict(parcel)

    @app.get("/v1/parcels/{parcel_id}", operation_id="getParcel",responses={404: {"description": "Parcel not found"}})
    def get_parcel(parcel_id: str):
        if parcel_id not in parcel_store:
            raise HTTPException(status_code=404, detail="not found")
        return asdict(parcel_store[parcel_id])

    @app.post("/v1/parcels/{parcel_id}/events", operation_id="recordParcelEvent", responses={404: {"description": "Parcel not found"}, 409: {"description": "Invalid transition"}, 422: {"description": "Unknown or missing event type"}})
    def record_event(parcel_id: str, body: EventIn):
        if parcel_id not in parcel_store:
            raise HTTPException(status_code=404, detail="not found")
        try:
            updated = apply_event(parcel_store[parcel_id], body.type)
        except InvalidTransition as exc:
            raise HTTPException(status_code=409, detail=str(exc))
        parcel_store[parcel_id] = updated
        return asdict(updated)

    @app.get("/v1/parcels", operation_id="listParcels", responses={400: {"description": "Invalid cursor"}, 422: {"description": "Invalid state or limit"}})
    def list_parcels(
        state: ParcelState | None = None,
        limit: Annotated[int, Query(ge=1, le=100)] = 20,
        cursor: str | None = None,
    ):
        start = 0
        if cursor is not None:
            if cursor not in cursors:
                raise HTTPException(status_code=400, detail="invalid cursor")
            start = cursors[cursor] + 1

        everything = list(parcel_store.values())
        items = []
        last_pos = -1
        has_more = False
        for pos in range(start, len(everything)):
            p = everything[pos]
            if state is not None and p.state != state:
                continue
            if len(items) == limit:
                has_more = True
                break
            items.append(p)
            last_pos = pos

        next_cursor = None
        if has_more:
            next_cursor = secrets.token_urlsafe(8)
            cursors[next_cursor] = last_pos

        return {"items": [asdict(p) for p in items], "next_cursor": next_cursor}

    return app


app = create_app()