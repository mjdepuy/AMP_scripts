import logging, logging.handlers
import sys
import os
import requests
import json
import splunk
from datetime import datetime
from base64 import encodestring
#from urllib.parse import quote_plus

TIME_FILE = "/opt/splunk/etc/amp_events/local/time.txt"

def setup_logging():
        logger = logging.getLogger('amp_getevents.py')
        SPLUNK_HOME = os.environ['SPLUNK_HOME']

        LOGGING_DEFAULT_CONFIG_FILE = os.path.join(SPLUNK_HOME,'etc','log.cfg')
        LOGGING_LOCAL_CONFIG_FILE = os.path.join(SPLUNK_HOME,'etc','log-local.cfg')
        LOGGING_STANZA_NAME = "python"
        LOGGING_FILE_NAME = "amp_getevents.log"
        BASE_LOG_PATH = os.path.join('var','log','splunk')
        LOGGING_FORMAT = "%(asctime)s %(levelname)-s\t%(module)s:%(lineno)d - %(message)s"
        splunk_log_handler = logging.handlers.RotatingFileHandler(os.path.join(SPLUNK_HOME, BASE_LOG_PATH, LOGGING_FILE_NAME), mode='a')
        splunk_log_handler.setFormatter(logging.Formatter(LOGGING_FORMAT))
        logger.addHandler(splunk_log_handler)
        splunk.setupSplunkLogger(logger, LOGGING_DEFAULT_CONFIG_FILE, LOGGING_LOCAL_CONFIG_FILE, LOGGING_STANZA_NAME)
        return logger

def main():

        # Setup logging
        logger = setup_logging()
        logger.info("Script starting...")
        
        # Base URL and auth
        base_url = "https://api.amp.cisco.com/v1/"
        client_id_apik = ''
        auth = encodestring(client_id_apik)
        auth = auth.decode("utf-8")
        amp_h = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0", "Authorization": "Basic %s" % auth.replace('\n','')}

        # List of event IDs
        eid_list = ["1090519054","553648166","1005","553648147","553648168","1090524040","1090524041","1090519084","1107296257","1107296258","1107296261","1107296262","1107296263","1107296264","1107296266","1107296267","1107296268","1107296269","1107296270","1107296271","1107296272","1107296273","1107296274","1107296275","1107296276","1107296277","1107296278","1107296280","1107296281","1107296282","1107296284","1107296283","1090519103","1090519081","1090519105","1090519102","553648199","1090519112"]

        # Build query
        url = base_url + "events?"
        for id in eid_list:
                url = url + "event_type[]=" + id + "&"
        
        f = open(TIME_FILE,"r")
        datetimestamp = f.read()
        #datetimestamp = quote_plus(datetimestamp+"-07:00")
        f.close()
        url = url + "start_date=" + datetimestamp

        logger.info("Querying! url=%s, time=%s",url,datetimestamp)
        
        # Begin query
        res = requests.get(url,headers=amp_h)
        for e in res.json()["data"]:
                print(json.dumps(e))

        # Get current time and write to file so we can pull from correct time on next run
        f = open(TIME_FILE,"w")
        f.write(datetime.strftime(datetime.now(),"%Y-%m-%dT%H:%M:%S")+"-07:00")
        f.close()

if __name__ == "__main__":
        main()
