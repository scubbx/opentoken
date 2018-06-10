#!/usr/bin/python3

from peewee import *
from flask import Flask
from flask import request
import time

db = SqliteDatabase('token.db')

'''
class BaseModel(Model):
    class Meta:
        database = db
'''

db.connect()

class Tokens(Model):
    class Meta:
        database = db

    token_uuid = TextField(column_name = 'token_uuid', unique=True, primary_key = True)
    mapped_service = IntegerField(column_name = 'mapped_service')
    valid_until = IntegerField(column_name = 'valid_until')

class Services(Model):
    class Meta:
        database =db

    serviceid = IntegerField(unique=True, primary_key = True)
    url = TextField()
    layer = TextField()

def createUUID():
    return uuid.uuid4()

app = Flask(__name__)

@app.route("/")
def hello():
    return "This is a reimplementaion of a commonly token based URL-Interceptor for HTTP services."

@app.route("/<uuid:urltoken>/<path:restofquery>")
def tokenrequest(urltoken,restofquery):
    # lets query the information about the token from the database
    try:
        queryparameters = request.query_string.decode("utf-8")
        tokendata = Tokens.get(Tokens.token_uuid == urltoken)
        isvalid = 'valid'
        servicedata = Services.get(Services.serviceid == tokendata.mapped_service)
        internalquery = ''.join([servicedata.url,queryparameters])
        response = "<h1>OpenToken Interceptor</h1>This is the response to a tokenrequest. The token used was <b>{}</b>.</br> The tokendata according to the internal Interceptor-database is <b>{}</b>.</br><b>This token is {}</b>.</br>The timestamp is <b>{}</b>. This token is still valid for <b>{} seconds</b>.</br>The internal URL to which this request will be reroutet is <b>{}</b>".format(urltoken,tokendata,isvalid,tokendata.valid_until,round(tokendata.valid_until - time.time()),internalquery)

    except DoesNotExist:
        isvalid = 'invalid'
        response = "<h1>OpenToken Interceptor</h1>The token <b>{}</b> was not found in the database. The request is <b>{}</b>".format(urltoken,isvalid)
    return response


