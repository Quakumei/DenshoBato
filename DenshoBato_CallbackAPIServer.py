# A very simple Flask Hello World app for you to get started with...
from flask import Flask, request, json
import vk
import random

app = Flask(__name__)

# SENSITIVE DATA AHEAD
with open("sensitive.txt", "r") as f:
    # Sensitive data is stored in sensitive.txt
    # First line is confirmation token, second is access
    CONFIRMATION_TOKEN = f.readline().rstrip()
    ACCESS_TOKEN = f.readline().rstrip()
print(CONFIRMATION_TOKEN)
print(ACCESS_TOKEN)


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
    if data['type'] == 'confirmation':
        print("MINUS TRI WOOOOOHOOOOOOOOo")
        return CONFIRMATION_TOKEN
    elif data['type'] == 'message_new':
        session = vk.Session()
        api = vk.API(session, v='5.110')
        user_id = data['object']['message']['from_id']
        print("Gotcha! [Message], Access_token = ", ACCESS_TOKEN)
        api.messages.send(access_token=ACCESS_TOKEN, user_id=str(user_id),
                          message='Привет, я Бато, цифровой почтовый голубь. А ты - @id' + str(user_id) + ', верно?',
                          random_id=random.getrandbits(64))
        # Сообщение о том, что обработка прошла успешно
        return 'ok'
