def parse_arg(cmd):
    """
    Вычленяет то, что идёт после команды в сообщении.
    Возвращает массив аргументов.
    Если аргументов нет, возвращает False
    :param cmd:
    :return:
    """
    # Get second word from split
    try:
        arg = cmd.split(' ', 1)[1]
    except IndexError:
        return False

    # Remove trailing backspaces
    while arg and arg[-1] == " ":
        arg = arg[:-1]
    args = arg.split(" ")
    if args == ['']:
        return False
    return args


# Some unit tests
# TODO: move unit tests to an other file.
assert (parse_arg("!создать_школу Лицей №86  ") == ["Лицей", "№86"]), "Wrong parse_arg result 1."
assert (parse_arg("!создать_школу       ") is False), "Wrong parse_arg result 2."


def parse_attachments2str(attachments):
    # Some code I wrote two months ago I don't remember how it works now
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
        return "", ""
    return res[:-1], urls


