# OpenToken - A HTTP Token manager

This proxying solution provides URLs containing UUIDs. Each UUID-URL is mapped with a service. Each UUID-URL has a specified lifetime.
All data is stored in a SQLite database.

Run with

    FLASK_APP=test.py flask run


## Build With

  * Python
  * Flask
  * PeeWee

## ToDo

  * Performing the rerouted request
  * User Account management (so far the tokens and services have to be entered manually)
  * Database data in-memory buffering for faster access times (think WMTS)
