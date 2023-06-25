import requests
import json
import urllib.parse


def getService(serviceId):
    serviceId = urllib.parse.quote(serviceId, safe='')
    response = requests.get(f'http://localhost:8080/services/{serviceId}')
    return json.loads(response.content)


def searchServices():
    response = requests.get(f'http://localhost:8080/services')
    return json.loads(response.content)


def sendMessage(serviceId, body):
    data = body
    serviceId = urllib.parse.quote(serviceId, safe='')
    response = requests.post(f'http://localhost:8080/execute-service-action/{serviceId}', data=data)
    return (response) 
