import vk
from requests import *
from random import randint
import json


class VkApiHandler:
    class MsgHandlerNotSet(Exception):
        pass

    def __init__(self, token, api_v, group_id, msg_handler=None, debug=True):

        self.debug = debug
        self.msg_handler = msg_handler

        self.session = vk.Session(access_token=token)
        self.api = vk.API(self.session, v=api_v)

        # Первый запрос к LongPoll: получаем server и key
        self.longPoll = self.api.groups.getLongPollServer(group_id=group_id)
        self.server, self.key, self.ts = self.longPoll['server'], self.longPoll['key'], self.longPoll['ts']

        if self.debug:
            print(self.api)

            print(self.server)
            print(self.key)
            print(self.ts)

    # def send_msg(self, user_id, txt):
    #     # Send text only
    #     self.api.messages.send(user_id=user_id, random_id=randint(-2147483648, 2147483647),
    #                            message=txt)
    def send_msg(self, user_id, txt, attachment_str=None, json_kb=None):
        # Send text with attachments
        self.api.messages.send(user_id=user_id, random_id=randint(-2147483648, 2147483647),
                               message=txt, attachment=attachment_str, keyboard=json_kb)

    def get_name(self, user_id, short=False):
        # Return name of a person in VK
        # Отчество НЕ используется так как во ВКонтакте большинство пользователей его не выставляют.
        user = self.api.users.get(user_ids=f'id{user_id}')[0]
        first_name = user["first_name"]
        last_name = user["last_name"]
        if short:
            return f"{last_name} {first_name[0]}."  # Тампио И.
        else:
            return f"{last_name} {first_name}"  # Тампио Илья

    def setMsgHandler(self, msg_handler):
        self.msg_handler = msg_handler

    def main_loop(self):
        if not self.msg_handler:
            # use VkApiHandler.setMsgHandler()
            raise self.MsgHandlerNotSet()

        ticks_count = 0
        while True:
            ticks_count += 1
            if self.debug:
                print(str(ticks_count) + " iterations...")

            # Последующие запросы: меняется только ts
            longPoll = post('%s' % self.server, data={'act': 'a_check',
                                                      'key': self.key,
                                                      'ts': self.ts,
                                                      'wait': 12}).json()

            if self.debug:
                print(longPoll)

            if longPoll['updates'] and len(longPoll['updates']) != 0:
                for update in longPoll['updates']:
                    if update['type'] == 'message_new':
                        # Отправить в мессендж хендлер
                        # Там уже с дебагом писать что прилетело
                        # Помечаем сообщение от этого пользователя как прочитанное
                        self.api.messages.markAsRead(peer_id=update['object']['from_id'])
                        self.msg_handler.handle_message(update)
            # Меняем ts для следующего запроса
            self.ts = longPoll['ts']
