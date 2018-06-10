#!/usr/bin/python3

from peewee import *

from flask import Flask
from flask import request
from flask import Response
from flask import stream_with_context

import time
import requests
import hashlib

ownUrl = "http://localhost:5000"

db = SqliteDatabase('token.db')

db.connect()

class Services(Model):
    class Meta:
        database = db

    serviceid = IntegerField(unique=True, primary_key = True)
    url = TextField()
    layer = TextField()
    servicename = TextField()

class Users(Model):
    class Meta:
        database = db

    userid = IntegerField(unique=True, primary_key = True)
    username = TextField()
    pwhash = TextField()
    userlevel = IntegerField()

class Tokens(Model):
    class Meta:
        database = db

    token_uuid = TextField(column_name = 'token_uuid', unique=True, primary_key = True)
    mapped_service = IntegerField()
    #mapped_service = ForeignKeyField(Services, column_name='serviceid')
    valid_until = IntegerField(column_name = 'valid_until')
    assigneduserid = IntegerField()
    #assigneduserid = ForeignKeyField(model=Users, field='userid')

def createUUID():
    return uuid.uuid4()

def createUserHash(username,password):
    h = hashlib.sha1()
    h.update(':'.join(username,password).decode())
    return h.digest()

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
    return "This is a reimplementaion of a commonly token based URL-Interceptor for HTTP services. See <a href='{}'>Config Page</a> for the configuration interface.".format('/'.join([ownUrl,'config']))


@app.route("/config")
def configure():
    allTokens = Tokens.select()
    allServices = Services.select()
    responsetext = "<h1>OpenToken Interceptor</h1></br>List of available Tokens and their mapping:</br><ul>"
    for token in allTokens:
        selectedService = Services.get(Services.serviceid == token.mapped_service)
        responsetext += '    '.join(['<li>',token.token_uuid, selectedService.url, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(token.valid_until)),'</li>'])
    responsetext += "</ul>"
    return responsetext


@app.route("/ows/<uuid:urltoken>/<path:restofquery>")
def tokenrequest(urltoken,restofquery):
    print("Request to interceptor received.\nToken: {}\nQuery: {}".format(urltoken,restofquery))
    # lets query the information about the token from the database
    try:
        queryparameters = request.query_string.decode("utf-8")
        tokendata = Tokens.get(Tokens.token_uuid == urltoken)
        isvalid = 'valid'
        servicedata = Services.get(Services.serviceid == tokendata.mapped_service)
        internalquery = ''.join([servicedata.url,queryparameters])
        tokenvalidseconds = round(tokendata.valid_until - time.time())
        response = "<h1>OpenToken Interceptor</h1>This is the response to a tokenrequest. The token used was <b>{}</b>.</br> The tokendata according to the internal Interceptor-database is <b>{}</b>.</br><b>This token is {}</b>.</br>The timestamp is <b>{}</b>. This token is still valid for <b>{} seconds</b>.</br>The internal URL to which this request will be reroutet is <b>{}</b></br>".format(urltoken,tokendata,isvalid,tokendata.valid_until,tokenvalidseconds,internalquery)

        if restofquery == "info":
            print("-> this is an INFO query")
            return response
        
        if tokenvalidseconds < 0:
            print("-> token age is too old")
            return "<h1>OpenToken Interceptor</h1></br>This token was only valid until {}.".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(tokendata.valid_until)))
        
        internal_response = performInternalQuery(internalquery)
        if request.args.get('request') or request.args.get('REQUEST'):
            print("-> Queryparameters: {}".format(queryparameters))
            if 'getcapabilities' in queryparameters.lower():
                textToReplace = str(servicedata.url.replace('?',''))
                newText = '/'.join([ownUrl,"ows",str(urltoken),restofquery])
                response = alterInternalResponse(internal_response,textToReplace,newText)
            else:
                print("-> directly passing through the response")
                response = internal_response
        
    except DoesNotExist:
        isvalid = 'invalid'
        response = "<h1>OpenToken Interceptor</h1>The token <b>{}</b> was not found in the database. The request is <b>{}</b>".format(urltoken,isvalid)
    return response


