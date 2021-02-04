import os
from random import randint
from requests import *
import vk
import db
import beautify
import sys

# Всякие вкусности букв
DEBUG_WORD = 'дебаг'
CREATE_SCHOOL_WORD = 'сш'
HELP_WORD = 'помоги'
ADD_WORD = 'доб'

# Указываем ключи доступа, id группы и версию API
VK_API_ACCESS_TOKEN = '0405278c1d9aa5b5962e158cfc6e036ebb3703d671d5042df8d9d807e1a6cbbb577effb424664c474efe6'
VK_API_VERSION = '5.95'
GROUP_ID = 199935063

session = vk.Session(access_token=VK_API_ACCESS_TOKEN)
api = vk.API(session, v=VK_API_VERSION)

# Первый запрос к LongPoll: получаем server и key
longPoll = api.groups.getLongPollServer(group_id=GROUP_ID)
server, key, ts = longPoll['server'], longPoll['key'], longPoll['ts']


def debug_response(update):
    # Запрашиваем имя пользователя
    name = api.users.get(user_ids=update['object']['from_id'])[0]['first_name']

    # Загружаем картинку на сервера ВК
    pfile = post(api.photos.getMessagesUploadServer(peer_id=update['object']['from_id'])['upload_url'],
                 files={'photo': open('shnek.jpg', 'rb')}).json()
    photo = api.photos.saveMessagesPhoto(server=pfile['server'], photo=pfile['photo'], hash=pfile['hash'])[0]
    print("sasu")

    # Получаем роли
    roles_list = db.fetch_roles(update['object']['from_id'])
    roles_str = beautify.roles_list2str(roles_list)

    # Получаем школы
    schools_list = db.fetch_all_schools()
    schools_str = beautify.schools_list2str(schools_list)

    # Формируем сообщение
    msg = ""
    msg = msg + 'Привет, %s &#128521;\n' % name
    msg = msg + '\n' + "Вот твои роли:\n" + roles_str
    msg = msg + "\n\nА вот все школы в сети:\n" + schools_str

    # Отправляем сообщение
    api.messages.send(user_id=update['object']['from_id'], random_id=randint(-2147483648, 2147483647),
                      message=msg,
                      attachment='photo%s_%s' % (photo['owner_id'], photo['id']))
    return


def simple_response(update, msg):
    name = api.users.get(user_ids=update['object']['from_id'])[0]['first_name']
    api.messages.send(user_id=update['object']['from_id'], random_id=randint(-2147483648, 2147483647),
                      message=('%s, привет!  &#128521;\n' % name) + msg + '\n')
    return


def begins_with(a, b):
    return a[:len(b)] == b


def help_response(update):
    pass


def create_school(update, school_name):
    status = db.create_school(school_name, update['object']['from_id'])
    return status


def status_response(update, status):
    if status == 0:
        simple_response(update, "Успех!")
    elif status == -1:
        simple_response(update, "Что-то пошло не так...")
    else:
        simple_response(update, "Всё *очень* плохо.")
    return


def add_attribute(user_id, group_id, role):
    return db.user_add_attribute(user_id, group_id, role)


ticks_count = False
user_string_flag = False
school_dialogue_flag = False
user_string = ""
while True:
    ticks_count += 1
    print(str(ticks_count) + " cycles...")
    # Последующие запросы: меняется только ts
    longPoll = post('%s' % server, data={'act': 'a_check',
                                         'key': key,
                                         'ts': ts,
                                         'wait': 5}).json()
    print(longPoll)
    if longPoll['updates'] and len(longPoll['updates']) != 0:
        for update in longPoll['updates']:
            if update['type'] == 'message_new':
                print(update)

                # Помечаем сообщение от этого пользователя как прочитанное
                api.messages.markAsRead(peer_id=update['object']['from_id'])

                ### Отвечаем ###
                msg = update['object']['text']
                user_id = update['object']['from_id']

                if user_string_flag:
                    user_string = msg

                # DEBUG
                if begins_with(msg, DEBUG_WORD):
                    debug_response(update)

                # HELP
                elif begins_with(msg, HELP_WORD):
                    help_response(update)

                # ADD ATTRIBUTE
                elif begins_with(msg, ADD_WORD):
                    words_list = msg.split(" [")
                    if len(words_list) != 4:
                        simple_response(update, "Неверная команда!")
                    else:
                        arr = []
                        for w in words_list:
                            if w != ADD_WORD:
                                arr.append(w[1:-2])
                        # доб [id] [Название школы] [роль]
                        status = add_attribute(arr[0], arr[1], arr[2])
                        status_response(update, status)


                # TODO: HELP RESPONSE
                # TODO: REMOVE ATTRIBUTE
                # TODO: SEND MESSAGE TO THE GROUP_ID
                # TODO: 

                # CREATE SCHOOL
                elif begins_with(msg, CREATE_SCHOOL_WORD) or school_dialogue_flag:
                    if not school_dialogue_flag:
                        simple_response(update, "Давай помогу создать школу!\nНапиши, как она будет называться:")
                        school_dialogue_flag = True
                        user_string_flag = True
                        break
                    else:
                        school_dialogue_flag = False
                        user_string_flag = False
                        status1 = create_school(update, user_string)
                        status2 = add_attribute(user_id, user_string, "Владелец")
                        status_response(update, status1 + status2)


                # FINALLY
                else:
                    simple_response(update, "Ты попался в else.")

    # Меняем ts для следующего запроса
    ts = longPoll['ts']
