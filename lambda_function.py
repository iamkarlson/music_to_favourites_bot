import json
from botocore.vendored import requests
import datetime
import re
import os

"""
https://api.telegram.org/botBOT_TOKEN/setWebHook?url=API_GATEWAY_URL
"""
BOT_TOKEN = os.environ['bot_token']
URL = "https://api.telegram.org/bot{}/".format(BOT_TOKEN)
IFTTT_TOKEN = os.environ['ifttt_token']
IFTTT_EVENT_NAME = os.environ['ifttt_event_name']
LINK_PREVIEW_KEY = os.environ['link_preview_key']

def lambda_handler(event, context):
    event_body = event['body']
    body = json.loads(event_body)
    print(body)
    chat_id = body['message']['chat']['id']
    try:
        text = body['message']['text']
        if "spotify.com" in text or "youtube.com" in text:
            what = (re.search("(?P<url>https?://[^\s]+)", text).group("url"))
            message_date = datetime.datetime.now()
            whom = "%s %s"%(body['message']['from']['first_name'],body['message']['from']['last_name'])
            description = get_description(what)
            ifttt_alert(what, whom, description)
            reply = "Added!"
            send_message(reply, chat_id)

    except:
        pass
    
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('OK')
    }    
def get_description(what):
    try:
        link_preview = requests.get("http://api.linkpreview.net/?key={}&q={}".format(LINK_PREVIEW_KEY,what))
        text = link_preview.json()
        if "youtube" in what:
            return text['title']
        else:
            return text['description']
    except:
        return ""
    
def send_message(text, chat_id):
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    requests.get(url)

def ifttt_alert(what, whom, description):
    row_data = {}
    row_data["value1"] = what
    row_data["value2"] = whom
    row_data["value3"] = description
    requests.post("https://maker.ifttt.com/trigger/{}/with/key/{}".format(IFTTT_EVENT_NAME,IFTTT_TOKEN), data=row_data)
