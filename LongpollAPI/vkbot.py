import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

# for random_id
import random


def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id':random.getrandbits(64)})


# API-token for working with messages
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
            request = event.text
            if request == 'привет':
                write_msg(event.user_id, "Хай")
            elif request == 'пока':
                write_msg(event.user_id, 'Пока((')
            else:
                write_msg(event.user_id, "Не поняла вашего ответа...")
