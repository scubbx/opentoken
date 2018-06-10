#!/usr/bin/python3

from peewee import *

from flask import Flask
from flask import request
from flask import Response
from flask import stream_with_context

import time
import requests

ownUrl = "http://localhost:5000"

db = SqliteDatabase('token.db')

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

def performInternalQuery(url):
    print("-> performing query: {}".format(url))
    internal_request = requests.get(url, stream = True)
    return Response(stream_with_context(internal_request.iter_content()), content_type = internal_request.headers['content-type'])

def alterInternalResponse(internal_response,textToReplace,newText):
    internal_bodyXML = internal_response.get_data().decode()
    #print(internal_bodyXML)
    print("-> replace {} with {}.".format(textToReplace,newText))
    modified_bodyXML = internal_bodyXML.replace(textToReplace,newText)
    #print(internal_bodyXML)
    internal_response.set_data(modified_bodyXML)
    return internal_response

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

        internal_response = performInternalQuery(internalquery)
        if request.args.get('request'):
            if request.args.get('request').lower() == "getcapabilities":
                textToReplace = str(servicedata.url.replace('?',''))
                newText = '/'.join([ownUrl,str(urltoken),restofquery])
                response = alterInternalResponse(internal_response,textToReplace,newText)
        else:
            response = internal_response

    except DoesNotExist:
        isvalid = 'invalid'
        response = "<h1>OpenToken Interceptor</h1>The token <b>{}</b> was not found in the database. The request is <b>{}</b>".format(urltoken,isvalid)
    return response


