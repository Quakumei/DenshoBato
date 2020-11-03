import vkapi


def get_answer(body, user_id):
    message = "Привет, я Бато 🕊️, цифровой почтовый голубь! А ты, должно быть, @id" + str(user_id) + ", верно?\n" + \
              "\n Ты мне сказал следующее:\n" + "-" * 10 + "\n" + str(
        body) + "\n" + "-" * 10 + "\n\n Я верно тебя расслышал?"
    return message


def create_answer(data, token):
    user_id = data['from_id']
    message = get_answer(data['text'].lower(), user_id)
    vkapi.send_message(user_id, token, message)
