# Here comes everything I didn't know where to put

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


# Few unit tests
assert (parse_arg("!создать_школу Лицей №86  ") == ["Лицей", "№86"]), "Wrong parse_arg result 1."
assert (parse_arg("!создать_школу       ") is False), "Wrong parse_arg result 2."


def parse_attachments2str(attachments):
    # Used in sending messages with attachments via VkApiHandler.py
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


def arrange_buttons(buttons, columns_count):
    # Arranges given text_buttons
    # Text button: ["label"],["color"]
    res = []
    i = 0
    while i + columns_count - 1 < len(buttons):
        line = []
        j = 0
        while j < columns_count:
            line.append(buttons[i + j])
            j += 1
        i += columns_count
        res.append(line)
    line = []
    j = 0
    while i + j < len(buttons):
        line.append(buttons[i + j])
        j += 1
    if line:
        res.append(line)

    return res


def groups2txt(groups):
    # Return groups list for message
    # groups: (id, school_id, name)
    txt = """======== 📚 Группы 📚 ========\n\n"""
    for group_id, school_id, group_name in groups:
        txt += f"-- \"{group_name}\" (group_id: {group_id})\n"
    return txt


def schools2txt(schools):
    # Return schools list for message
    # schools: (school_id, creator_id, school_name)
    txt = """======== 🏫 Школы 🏫 ========\n\n"""
    for school_id, creator_id, school_name in schools:
        txt += f"-- \"{school_name}\" (school_id: {school_id})\n"
    return txt


def members2txt(members):
    # Return group members in a message
    # members: (vk_id, nickname)
    txt = f"======== 👩‍🦱 Участники группы 🧓 ========\n\n"
    for vk_id, nickname in members:
        txt += f"-- \"{nickname}\" (@id{vk_id}(@id{vk_id}))\n"
    return txt


def roles2txt(roles):
    # Return roles in a message
    # roles: (role_id, permissions, role_name)
    txt = f"======== 🆓 Доступные роли 🆓 ========\n\n"
    for role_id, permissions, role_name in roles:
        txt += f"-- \"{role_name}\" (role_id: {role_id})\n"
    return txt
