import fastapi
import aiohttp
import os
from aiohttp import client_exceptions
from datetime import datetime
import time

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
	raise fastapi.HTTPException(404)
	# try:
	# 	key = "parse_moex/" + sec + "/" + time
	# 	async with aiohttp.ClientSession() as client:
	# 		async with client.get(moex_host + key) as resp:
	# 			return await resp.json()
	# except client_exceptions.ContentTypeError:
	# 	raise fastapi.HTTPException(404)

@app.get("/db/stock")
async def serve_stock(date: str = None):
	try:
		async with aiohttp.ClientSession() as client:
			async with client.get(db_host + "tickers") as resp:
				response = await resp.json()
				if date == None:
					date = datetime.now()
					unix_date = int(time.mktime(date.timetuple()))
					current_date = str(unix_date // (60*60*24*7))
				else:
					current_date = date
				new_resp = []
				for ticker in response:
					quote = ticker["sec_id"]
					key = "top/" + current_date + "/" + quote
					async with client.get(redis_host + key) as resp:
						ticker_data = await resp.json()
						ticker["bos"] = ticker_data["bos_negative"] + ticker_data["bos_positive"]
					new_resp.append(ticker)
				return new_resp
	except client_exceptions.ContentTypeError:
		raise fastapi.HTTPException(404)


@app.get("/db/stock/{secid}")
async def serve_stock_by_secid(secid: str):
	try:
		async with aiohttp.ClientSession() as client:
			async with client.get(db_host + "stock" + "/" + secid) as resp:
				response = await resp.json()
				new_resp = []
				for item in response:
					raw_date = datetime.strptime(item["date"], "%Y-%m-%dT%H:%M:%S")
					unix_date = int(time.mktime(raw_date.timetuple()))
					date = str(unix_date // (60*60*24*7))
					key = "top/" + date + "/" + secid
					try:
						async with client.get(redis_host + key) as resp:
							ticker_data = await resp.json()
							item["bos"] = ticker_data["bos_negative"] + ticker_data["bos_positive"]
					except client_exceptions.ContentTypeError:
						item["bos"] = 0
					new_resp.append(item)
				return new_resp
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


@app.get("/db/topics")
async def serve_topics():
	try:
		async with aiohttp.ClientSession() as client:
			async with client.get(db_host + "topics") as resp:
				return await resp.json()
	except client_exceptions.ContentTypeError:
		raise fastapi.HTTPException(404)


@app.get("/db/entities")
async def serve_entities():
	try:
		async with aiohttp.ClientSession() as client:
			async with client.get(db_host + "entities") as resp:
				return await resp.json()
	except client_exceptions.ContentTypeError:
		raise fastapi.HTTPException(404)


@app.get("/db/news")
async def serve_news(id: int = None, rubric: str = None, page: int = None, secid: str = None, date: str = None):
	try:
		async with aiohttp.ClientSession() as client:
			if secid != None and date != None:
				key = "top/" + date + "/" + secid
				async with client.get(redis_host + key) as resp:
					response = await resp.json()
					data = []
					for item in response["news"]:
						async with client.get(db_host + "news?id=" + str(item)) as resp:
							news_data = await resp.json()
							data.append(news_data)
					glass = {
						"bos": response["bos_negative"] + response["bos_positive"],
						"bos_positive": response["bos_positive"],
						"bos_negative": response["bos_negative"],
						"num_positive": response["num_positive"],
						"num_negative": response["num_negative"],
					}
					return {"news":data, "sent":glass}
			elif page != None:
				async with client.get(db_host + "news?page=" + str(page)) as resp:
					return await resp.json()
			elif id != None and secid != None:
				async with client.get(db_host + "news?id=" + str(id) + "&secid=" + secid) as resp:
					return await resp.json()
			elif id != None:
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
