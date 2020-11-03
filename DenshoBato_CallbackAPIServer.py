# DenshoBato bot
# VK API: v5.110+
from flask import Flask, request, json
from utility import *
import vk
import random

app = Flask(__name__)

# SENSITIVE DATA AHEAD
SENSITIVE_DATA_FILENAME = "sensitive.txt"
with open(SENSITIVE_DATA_FILENAME, "r") as f:
    # Sensitive data is stored in sensitive.txt
    # First line is confirmation token, second is access
    CONFIRMATION_TOKEN = f.readline().rstrip()
    ACCESS_TOKEN = f.readline().rstrip()

# log
console_log({"what": "Loaded tokens from file", "info": SENSITIVE_DATA_FILENAME})
console_log({"what": "CONFIRMATION TOKEN:", "info": CONFIRMATION_TOKEN})
console_log({"what": "ACCESS TOKEN:", "info": ACCESS_TOKEN})


@app.route('/')
def hello_world():
    return 'Hello from Flask! ^_^ Project is up and running...'


@app.route('/callback', methods=['POST'])
def processing():
    # Распаковываем json из пришедшего POST-запроса
    data = json.loads(request.data)
    # Вконтакте в своих запросах всегда отправляет поле типа
    if 'type' not in data.keys():
        return 'not vk'

    # log
    console_log({"what": "Got POST request: ", "info": data["type"]}, log_type="API")

    if data['type'] == 'confirmation':
        console_log({"what": "Sending confirmation token... TOKEN: ", "info": CONFIRMATION_TOKEN},
                    log_type="Important")
        return CONFIRMATION_TOKEN
    elif data['type'] == 'message_new':
        session = vk.Session()
        api = vk.API(session, v='5.110')
        msg = data['object']['message']
        user_id = msg['from_id']

        # log
        console_log({"what": "Got a message! Info below:", "info": format_msg_log(msg)}, log_type="Event")

        api.messages.send(access_token=ACCESS_TOKEN, user_id=str(user_id),
                          message='Привет, я Бато, цифровой почтовый голубь. А ты - @id' + str(user_id) + ', верно?',
                          random_id=random.getrandbits(64))
        # Сообщение о том, что обработка прошла успешно
        return 'ok'
