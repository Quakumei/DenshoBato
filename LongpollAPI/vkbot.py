import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from datetime import datetime
from time import gmtime, strftime
import DenshoBatoAPI

# for random_id
import random


def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': random.getrandbits(64)})


# API-token for working with messages
# TODO: Вынести токен отсюда нафиг
token = '1db3d674ad5402cc10dc136734302e1ea6268510cce9842a0ee9c75124f4c955ea1aeea1d33528cdf9589'

# Authorize as community
vk = vk_api.VkApi(token=token)

# Stuff with msgs
longpoll = VkLongPoll(vk)

# Main cycle
for event in longpoll.listen():
    # If new message:
    if event.type == VkEventType.MESSAGE_NEW:

        if event.to_me:
            # Message from user

            # Логируем...
            print("\nGot Event!")
            print(str(datetime.utcfromtimestamp(event.timestamp).strftime('%H:%M:%S %Y-%m-%d')))
            print(event.type)
            print("@id" + str(event.user_id) + ":")
            print(event.text)

            # Отвечаем...
            # TODO: Сделать диалог с пользователем
            # TODO: Добавить кнопки (способности)
            request = event.text
            if request == 'привет':
                response = "Хай"
            elif request == 'пока':
                response = 'Пока(('
            else:
                response = "Не поняла вашего ответа..."

            # Fun happening
            response = "Эхо отразилось от стен..."

            # Ещё немного логов...
            print("=" * 15)
            print(response)

            # И, собственно ответ.
            write_msg(event.user_id, response)
            DenshoBatoAPI.mass_mailing(DenshoBatoAPI.TEST_SCHOOL, (DenshoBatoAPI.GROUP_NAME,), request)

