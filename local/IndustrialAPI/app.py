#!/usr/bin/env python3
import connexion
import json
from local.IndustrialAPI.actors_api_lmdp_ltlf.server import server


mode = "lmdp_ltlf"
app = connexion.AioHttpApp(__name__, only_one_api=True)
app.add_api(f'actors_api_{mode}/spec.yml')
# set the WSGI application callable to allow using uWSGI:
# uwsgi --http :8080 -w app
application = app.app


if __name__ == '__main__':
    server.run()
    