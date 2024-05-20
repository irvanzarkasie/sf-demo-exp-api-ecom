import sys
import json
from flask import Flask, request, jsonify, make_response, Response
from flask_restful import Api, Resource
import pprint
import logging
from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler
import uuid
import socket
from datetime import datetime, timedelta
import os
import urllib3
import redis
import uuid
from time import sleep
import logging
from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler
import jwt

app = Flask(__name__)
api = Api(app)

# CONSTANTS
api_host = socket.gethostname()
api_port = 37000
api_id = "ecom_exp_api"

CLIENT_ID = "8373854997-of44d9n5qupldqhlc5hh9h99d2q6rfk5.apps.googleusercontent.com"
CLIENT_SECRET = "a3b762f871cdb3bae0044c649622fc1396eda3e3"

# Work directory setup
script_dir = os.path.dirname(os.path.realpath(__file__))
home_dir = "/".join(script_dir.split("/")[:-1])
log_dir = "{home_dir}/logs".format(home_dir=home_dir)

# HTTP connection pool
http = urllib3.PoolManager()

# Initialize logger
logpath = "{log_dir}/{api_id}.log".format(log_dir=log_dir, api_id=api_id)
logger = logging.getLogger("{api_id}_logger".format(api_id=api_id))
logformatter = logging.Formatter("%(message)s")
logger.setLevel(logging.INFO)
handler = logging.FileHandler(logpath)
handler.setFormatter(logformatter)
logger.addHandler(handler)

def logRequest(request, rqid="", level="INFO"):
  rqtimestamp = datetime.now()
  logtype = "request"
  apiurl = request.url
  client_addr = request.remote_addr
  message = "Receive request"
  logpayload = {
    "host": api_host,
    "rqid": rqid,
    "level": level,
    "rqtimestamp": str(rqtimestamp),
    "logtype": logtype,
    "client_addr": client_addr,
    "logger_name": api_id,
    "message": message,
    "req_url": apiurl
  }
  logger.info(json.dumps(logpayload))
# end def

def logResponse(response, rqid="", message="Return response", duration=0, rqtimestamp="", request={}, level="INFO", status_code=""):
  rstimestamp = datetime.now()
  logtype = "response"
  logpayload = {
    "host": api_host,
    "rqid": rqid,
    "level": level,
    "rqtimestamp": str(rqtimestamp),
    "rstimestamp": str(rstimestamp),
    "logtype": logtype,
    "response": response,
    "status_code": status_code,
    "logger_name": api_id,
    "message": message
  }
  if duration != 0:
    logpayload["duration"] = duration
  # end if
  if len(str(rqtimestamp)) != 0:
    logpayload["rqtimestamp"] = str(rqtimestamp)
  # end if
  if len(request.remote_addr) != 0:
    logpayload["client_addr"] = request.remote_addr
  # end if
  if len(request.url) != 0:
    logpayload["req_url"] = request.url
  # end if

  logger.info(json.dumps(logpayload))
# end def

def auth():
    resp = http.request("GET", "http://168.119.225.15:34110/auth/exchange_token?client_id={CLIENT_ID}".format(CLIENT_ID=CLIENT_ID))
    resp_payload = json.loads(resp.data.decode("utf-8"))
    return resp_payload
# end def

def is_token_validated(token):
    decoded_token = jwt.decode(jwt=token, key=CLIENT_SECRET, algorithms=["HS256"])
    return decoded_token.get("expired_time", 0) > int(datetime.now().timestamp()) and decoded_token.get("client_id", "") == CLIENT_ID
# end def

class EcomExpApi(Resource):
    def get(self, transport_type):
      start_timestamp = datetime.now()

      token = auth().get("token", "")
      if not is_token_validated(token):
        return jsonify({"message": "Authentication failed"}, 401)
      # end if

      # Parse arguments
      args = request.args
      transport_type = transport_type
      departure_code = args.get("departureCode", "")
      destination_code = args.get("destinationCode", "")

      correlation_id = datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid.uuid4()).replace("-","")
      msg_ts = int(datetime.now().timestamp())

      logRequest(request, rqid=correlation_id)

      resp = http.request("GET", "http://168.119.225.15:36000/proc/booking/{transport_type}/routes?departureCode={departure_code}&destinationCode={destination_code}".format(transport_type=transport_type, departure_code=departure_code, destination_code=destination_code))
      resp_payload = json.loads(resp.data.decode("utf-8"))

      tmp_resp_list = []
      for resp in resp_payload:
        for r in resp.get("routes", []):
          tmp_resp_list.append(json.dumps(r))
        # end for
      # end for
      resp_list = set(tmp_resp_list)
      resp_list = [json.loads(r) for r in resp_list]

      end_timestamp = datetime.now()
      duration = int((end_timestamp - start_timestamp).total_seconds() * 1000)
      logResponse(json.dumps(resp_list), rqid=correlation_id, message="Return response", duration=duration, rqtimestamp=start_timestamp, request=request, level="INFO", status_code=200)
      return jsonify(resp_list)
    # end def
# end class

class MyCompProcApiDefault(Resource):
    def get(self):
      start_timestamp = datetime.now()

      token = auth().get("token", "")
      if not is_token_validated(token):
        return jsonify({"message": "Authentication failed"}, 401)
      # end if

      # Parse arguments
      args = request.args
      transport_type = transport_type
      departure_code = args.get("departureCode", "")
      destination_code = args.get("destinationCode", "")

      correlation_id = datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid.uuid4()).replace("-","")
      msg_ts = int(datetime.now().timestamp())

      logRequest(request, rqid=correlation_id)

      resp = http.request("GET", "http://168.119.225.15:36000/proc/booking/{transport_type}/routes?departureCode={departure_code}&destinationCode={destination_code}".format(transport_type=transport_type, departure_code=departure_code, destination_code=destination_code))
      resp_payload = json.loads(resp.data.decode("utf-8"))

      tmp_resp_list = []
      for resp in resp_payload:
        for r in resp.get("routes", []):
          tmp_resp_list.append(json.dumps(r))
        # end for
      # end for
      resp_list = set(tmp_resp_list)
      resp_list = [json.loads(r) for r in resp_list]

      end_timestamp = datetime.now()
      duration = int((end_timestamp - start_timestamp).total_seconds() * 1000)
      logResponse(json.dumps(resp_list), rqid=correlation_id, message="Return response", duration=duration, rqtimestamp=start_timestamp, request=request, level="INFO", status_code=200)
      return jsonify(resp_list)
    # end def
# end class

api.add_resource(EcomExpApi, '/ecom/exp/booking/<transport_type>/routes')
api.add_resource(MyCompProcApiDefault, '/ecom/exp/booking/routes')

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=api_port)
# end if