from random import randint
from requests import *
import vk
import db
import beautify

# Всякие вкусности букв
GROUPSEND_WORD = 'групрас'
DEBUG_WORD = 'дебаг'
CREATE_SCHOOL_WORD = 'сш'
HELP_WORD = 'помощь'
ADD_WORD = 'доб'
WHOIN_WORD = 'кто в'

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


def send_text(update, msg):
    api.messages.send(user_id=update['object']['from_id'], random_id=randint(-2147483648, 2147483647),
                      message=msg)
    return


def begins_with(a, b):
    return a[:len(b)] == b


def help_response(update):
    #
    msg = """
Привет! Я цифровой голубь-почтальон Бато. Моя работа - вовремя доставлять тебе информацию от учителей. 😉

~~~~ Команды ~~~~
%s - выводит это сообщение
%s - кое-что проверяет
%s - создать новую школу
%s [кому_id] [школа] [роль] - добавить роль человеку с кому_id
%s [школа] - выводит состав школы
%s [школа] - отправляет сообщение всем в школе
~~~~~~~~~~~~~~~~



Бот разработан в рамках школьного проекта ГОУ ЯО "Лицей №86"

Если найдёте ошибки/баги, сообщите мне!
Разработчик: @id388032588(Тампио Илья), ученик 11Б класса.
Github: github.com/Quakumei Telegram: @yasumi404
""" % (HELP_WORD, DEBUG_WORD, CREATE_SCHOOL_WORD, ADD_WORD, WHOIN_WORD, GROUPSEND_WORD)
    # загрузить фото на сервервы вк
    pfile = post(api.photos.getMessagesUploadServer(peer_id=update['object']['from_id'])['upload_url'],
                 files={'photo': open('bato.jpg', 'rb')}).json()
    photo = api.photos.saveMessagesPhoto(server=pfile['server'], photo=pfile['photo'], hash=pfile['hash'])[0]

    # соо
    api.messages.send(user_id=update['object']['from_id'], random_id=randint(-2147483648, 2147483647),
                      message=msg,
                      attachment='photo%s_%s' % (photo['owner_id'], photo['id']))
    return


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


def who_in_school(school_name):
    status, response = db.fetch_pupils(school_name)
    return status, response


def parse_attachments2str(attachments):
    res = ""
    urls = []
    for a in attachments:
        # url
        if a['type'] in ["doc", "audio"]:
            urls.append(a[a['type']]['url'])
        else:
            if a['type'] == 'photo':
                max_height = 0
                for i in a[a['type']]['sizes']:
                    if i['height'] > max_height:
                        max_height = i['height']
                for i in a[a['type']]['sizes']:
                    print(i)
                    if i['height'] == max_height:
                        urls.append(i['url'])
                        print(i['url'])
                        break
            elif a[a['type']] == 'video':
                urls.append(a['type'] + str(a[a['type']]['owner_id']) + "_" + str(a[a['type']]['id']))

        res += a['type'] + str(a[a['type']]['owner_id']) + "_" + str(a[a['type']]['id']) + ","

    # print(attachments)
    # print(res[:-1])

    if res == "":
        return ""
    return res[:-1], urls


def send_to_person(update, person_id):
    # TODO: Дописать сообщение от (роли в группе в которую написали) --- СДЕЛАНО
    # TODO: РАССЫЛКА С ВЛОЖЕНИЯМИ !!!!!!! --- СДЕЛАНО

    # TODO: ЗАМЕТКА: ПРИ ОТПРАВКЕ ВИДОСОВ С ЮТУБА НЕОБХОДИМО ДОБАВИТЬ ИХ ПО ССЫЛКЕ ЧЕРЕЗ ИНТЕРФЕЙС ВК ИНАЧЕ НИЧЕГО НЕ СРАБОТАЕТ (ИЛИ ПРОСТО ОСТАВЬТЕ ССЫЛКУ)
    # TODO: ЭТО ПОХОДУ ИЗ ЗА ТОГО ЧТО ОНО ДЕЛАЕТСЯ ПРИВАТНЫМ И ПОЧЕМУ ТО ВООБЩЕ ССЫЛКУ НЕЛЬЗЯ ЭКСТРАДИРОВАТЬ ЕСЛИ ЕЁ ЯВНО НЕ СКИНУТЬ
    # TODO: СКОРЕЕ ВСЕГО СВЯЗАНО С НАСТРОЙКАМИ ПРИВАТНОСТИ ДЛЯ НОВОДОБАВЛЕННЫХ ВИДОСОВ ИЛИ ЧТО ТО ТАКОЕ
    # TODO: ВСЁ ОСТАЛЬНОЕ +- РАБОТАЕТ

    # TODO: пересылка карты местности (для презенташки клёво будет)
    # По идее во вложениях ссылки на всё кроме видоса

    # Берём значит список того что нам прислали
    attachment_str, urls = parse_attachments2str(update['object']['attachments'])
    # print(attachment_str)
    print(urls)

    # очень плохой код
    msg = "Рассылка от @id" + str(update['object']['from_id']) + ":\n\n" + update['object']['text']
    if attachment_str:
        msg = msg + "\n\nВложения:\n" + str("\n".join(urls))

    api.messages.send(user_id=person_id, random_id=randint(-2147483648, 2147483647),
                      message=msg,
                      attachment=attachment_str)


def send_to_recipients(update, recipients):
    for r in recipients:
        send_to_person(update, r)


def send_to_group(update, group_id):
    # Fetch getters
    status1, response = who_in_school(group_id)

    # Parse and get ids of people in the group
    recipients = []
    for r in response:
        # id vkid school role
        recipients.append(r[1])
    recipients = list(dict.fromkeys(recipients))
    # Send messages
    send_to_recipients(update, recipients)

    return status1


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
                                         'wait': 12}).json()
    print(longPoll)
    if longPoll['updates'] and len(longPoll['updates']) != 0:
        for update in longPoll['updates']:
            if update['type'] == 'message_new':
                # print(update)

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

                # TODO: HELP RESPONSE
                # TODO: REMOVE ATTRIBUTE
                # TODO: SEND MESSAGE TO THE GROUP_ID --- DONE!
                # TODO: SEND MESSAGE TO THE GROUP_ID - ROLE_TAG
                # TODO: FIX FUCKING ADDING ATTRIBUTE --- DONE!
                # TODO: VK INTERFACE BUTTONS ???

                # GROUP SEND

                elif begins_with(msg, GROUPSEND_WORD):
                    check = beautify.check_cmd(msg, GROUPSEND_WORD, 1, True)
                    if check == -1:
                        simple_response(update, "Неверная команда!")
                    else:
                        # групрас [груп] дальше соо
                        status = send_to_group(update, check[0])
                        status_response(update, status)


                # WHO IN
                elif begins_with(msg, WHOIN_WORD):
                    check = beautify.check_cmd(msg, WHOIN_WORD, 1)
                    if check == -1:
                        simple_response(update, "Неверная команда!")
                    else:
                        # кто в [Название школы]
                        status, users_roles = who_in_school(*check)
                        status_response(update, status)
                        send_text(update, beautify.userRoles2Str(users_roles))
                        # simple_response(update, str(users_roles))


                # ADD ATTRIBUTE
                elif begins_with(msg, ADD_WORD):
                    check = beautify.check_cmd(msg, ADD_WORD, 3)
                    if check == -1:
                        simple_response(update, "Неверная команда!")
                    else:
                        # доб [id] [Название школы] [роль]
                        status = add_attribute(*check)
                        status_response(update, status)


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
