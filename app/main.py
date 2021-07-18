import fastapi
import aiohttp
import os
from aiohttp import client_exceptions

host = os.environ.get('REDIS_HOST')

app = fastapi.FastAPI()


@app.get("/")
async def root():
    return {"report": "Major is ready"}

@app.get("/graphic")
async def serve_graphic_root():
	try:
		async with aiohttp.ClientSession() as client:
			async with client.get(host) as resp:
				return await resp.json()
	except client_exceptions.ContentTypeError:
		raise fastapi.HTTPException(404)

@app.get("/graphic/{key}")
async def serve_graphic(key):
	try:
		async with aiohttp.ClientSession() as client:
			async with client.get(host + key) as resp:
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
		print(host + key)
		async with aiohttp.ClientSession() as client:
			async with client.get(host + key) as resp:
				response = await resp.json()
				if response == None:
					raise fastapi.HTTPException(404)
				return response
	except client_exceptions.ContentTypeError:
		raise fastapi.HTTPException(404)
