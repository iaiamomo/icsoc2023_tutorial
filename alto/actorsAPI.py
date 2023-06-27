import requests
import json
import urllib.parse
import grequests
import aiohttp

async def make_http_request(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response_text = await response.text()
            return response_text
        

async def make_post_http_request(url, data):
    async with aiohttp.ClientSession() as session:
        if data != None:
            async with session.post(url, data=data) as response:
                response_text = await response.text()
                return response_text
        else:
            async with session.post(url) as response:
                response_text = await response.text()
                return response_text


async def getService(serviceId):
    serviceId = urllib.parse.quote(serviceId, safe='')
    res = await make_http_request(f'http://localhost:8080/services/{serviceId}')
    return json.loads(res)


async def searchServices():
    url = f'http://localhost:8080/services'
    res = await make_http_request(url)
    return json.loads(res)


async def sendMessage(serviceId, body):
    print(serviceId)
    print(body)
    data = json.dumps(body)
    serviceId = urllib.parse.quote(serviceId, safe='')
    res = await make_post_http_request(f'http://localhost:8080/execute-service-action/{serviceId}', data=data)
    return json.loads(res)


async def breakService(serviceId):
    serviceId = urllib.parse.quote(serviceId, safe='')
    res = await make_post_http_request(f'http://localhost:8080/break-service/{serviceId}', None)
    return json.loads(res)
