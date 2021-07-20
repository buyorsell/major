import fastapi
import aiohttp
import os
from aiohttp import client_exceptions

redis_host = os.environ.get('REDIS_HOST')
moex_host = os.environ.get('MOEX_HOST')
db_host = os.environ.get('DB_HOST')

app = fastapi.FastAPI()


@app.get("/")
async def root():
    return {"report": "Major is ready"}

@app.get("/graphic")
async def serve_graphic_root():
	try:
		async with aiohttp.ClientSession() as client:
			async with client.get(redis_host) as resp:
				return await resp.json()
	except client_exceptions.ContentTypeError:
		raise fastapi.HTTPException(404)

@app.get("/graphic/{key}")
async def serve_graphic(key):
	try:
		async with aiohttp.ClientSession() as client:
			async with client.get(redis_host + key) as resp:
				response = await resp.json()
				if response == None:
					raise fastapi.HTTPException(404)
				return response
	except client_exceptions.ContentTypeError:
		raise fastapi.HTTPException(404)

@app.get("/top/{datetime}/{quote}")
async def serve_top(datetime, quote):
	try:
		key = "top/" + datetime + "/" + quote
		async with aiohttp.ClientSession() as client:
			async with client.get(redis_host + key) as resp:
				response = await resp.json()
				if response == None:
					raise fastapi.HTTPException(404)
				return response
	except client_exceptions.ContentTypeError:
		raise fastapi.HTTPException(404)

@app.get("/parse_moex/{sec}/{time}")
async def serve_moex(sec, time):
	try:
		key = "parse_moex/" + sec + "/" + time
		async with aiohttp.ClientSession() as client:
			async with client.get(moex_host + key) as resp:
				return await resp.json()
	except client_exceptions.ContentTypeError:
		raise fastapi.HTTPException(404)

@app.get("/db/tickers")
async def serve_db():
	try:
		async with aiohttp.ClientSession() as client:
			async with client.get(db_host + "tickers") as resp:
				return await resp.json()
	except client_exceptions.ContentTypeError:
		raise fastapi.HTTPException(404)


@app.get("/db/")
async def serve_db():
	try:
		async with aiohttp.ClientSession() as client:
			async with client.get(db_host) as resp:
				return await resp.json()
	except client_exceptions.ContentTypeError:
		raise fastapi.HTTPException(404)


@app.get("/db/news")
async def serve_news(d: int = None, rubric: str = None):
	try:
		async with aiohttp.ClientSession() as client:
			if id != None:
				async with client.get(db_host + "news?id=" + str(id)) as resp:
					return await resp.json()
			elif rubric != None:
				async with client.get(db_host + "news?rubric=" + rubric) as resp:
					return await resp.json()
			else:
				async with client.get(db_host + "news") as resp:
					return await resp.json()
	except client_exceptions.ContentTypeError:
		raise fastapi.HTTPException(404)
