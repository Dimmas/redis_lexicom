import aioredis
from exceptions import *
from pydantic import BaseModel
from fastapi import FastAPI, Query
from fastapi.exceptions import HTTPException
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"])

redis = aioredis.from_url("redis://redis", encoding="utf8", decode_responses=True)


class Data(BaseModel):
    phone: int
    address: str


@app.get("/check_data", response_class=PlainTextResponse)
async def check_data(
        phone: int = Query()
):
    """
        Ручка ищет в redis по ключу phone и возвращает соответствующий адрес.<br>
        Если в базе отсутствует запись с указанным ключом ручка возвращает HTTP - 404,
        HTTP - 500 - для внутренних ошибок
    :param data: содержит phone - номер телефона, интерпретируемый как ключ для записи в redis<br>
    address - адрес пользователя, интерпретируемыый как значение<br>
    """
    try:
        async with redis.client() as conn:
            address = await conn.get(phone)
    except Exception as e:
        # тут можно записать ошибку в лог, но пока просто выведем ее в stdout
        print(str(e))
        raise HTTPException(status_code=500, detail='redis get error')
    if not address:
        raise HTTPException(status_code=404, detail='record not found')
    return address


@app.post("/write_data", status_code=201)
async def write_data(
        data: Data
):
    """
        Ручка записи пары ключ-значения в redis.<br>
        В случае успешной записи возвращает HTTP 200,
        если в базе отсутствует запись с указанным ключом - 404,
        иначе - 500
    :param data: содержит phone - номер телефона, интерпретируемый как ключ для записи в redis<br>
    address - адрес пользователя, интерпретируемыый как значение<br>
    """
    try:
        async with redis.client() as conn:
            if await conn.get(data.phone):
                raise RecordIsExistsException
            await conn.set(data.phone, data.address)
    except RecordIsExistsException:
        raise HTTPException(status_code=RecordIsExistsException.code, detail=RecordIsExistsException.message)
    except Exception as e:
        # тут можно записать ошибку в лог, но пока просто выведем ее в stdout
        print(str(e))
        raise HTTPException(status_code=500, detail='redis set error')


@app.put("/write_data", status_code=202)
async def write_data(
        data: Data
):
    """
        Ручка  изменения записи в redis. <br>
        В случае успешной записи возвращает HTTP 200, <br>
        если записи с таким ключом не содержится в базе, то вернет HTTP - 404, <br>
        иначе - 500
    :param data: содержит phone - номер телефона, интерпретируемый как ключ для записи в redis<br>
    address - адрес пользователя, интерпретируемыый как значение<br>
    """
    try:
        async with redis.client() as conn:
            if not await conn.get(data.phone):
                raise NotFoundRecordException
            await conn.set(data.phone, data.address)
    except NotFoundRecordException:
        raise HTTPException(status_code=NotFoundRecordException.code, detail=NotFoundRecordException.message)
    except Exception as e:
        # тут можно записать ошибку в лог, но пока просто выведем ее в stdout
        print(str(e))
        raise HTTPException(status_code=500, detail='redis set error')

