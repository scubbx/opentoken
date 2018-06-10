# OpenToken - A HTTP Token manager

This proxying solution provides URLs containing UUIDs. Each UUID-URL is mapped with a service. Each UUID-URL has a specified lifetime.
All data is stored in a SQLite database.

To get information about a specific token, just replace "data" in the URL with "info".

Run with

    FLASK_APP=test.py flask run

## Test with

### DORIS OOE WMS

http://srv.doris.at/arcgis/services/Basisdaten/INSPIRE/MapServer/WMSServer?version=1.3.0&SERVICE=WMS&REQUEST=GetCapabilities
http://localhost:5000/ows/e19ad42a-6c21-4151-ba94-4baedceb78a8/data?version=1.3.0&SERVICE=WMS&REQUEST=GetCapabilities

### Vienna OGD WMS

https://data.wien.gv.at/daten/geo?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&BBOX=48.12827736546119439,16.21330318908830037,48.28881917402753032,16.49841758269718284&CRS=EPSG:4326&WIDTH=1020&HEIGHT=574&LAYERS=ogdwien:ABWARMEPOTOGD&STYLES=point&FORMAT=image/png&DPI=96&MAP_RESOLUTION=96&FORMAT_OPTIONS=dpi:96&TRANSPARENT=TRUE
http://localhost:5000/ows/e1493f45-8856-412e-99fd-d834f9ac5e6a/data?version=1.3.0&SERVICE=WMS&REQUEST=GetCapabilities

## Build With

  * Python
  * Flask
  * PeeWee

## ToDo

  * User Account management (so far the tokens and services have to be entered manually)
  * Database data in-memory buffering for faster access times (think WMTS)
