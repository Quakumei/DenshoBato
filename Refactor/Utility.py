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

def groups_list_txt(group_ids, db_handler):
    txt = f"""-+-+-+-+-+- 📚 Группы 📚 -+-+-+-+-+-\n\n"""
    groups = [(x, db_handler.fetch_group_name(x)) for x in group_ids]
    for group in groups:
        group_id = group[0]
        group_name = group[1]

        txt += f"-- {group_name} (group_id: {group_id})\n"
    txt += "-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-"
    return txt

# Спасибо, из-за бага в вк API у меня нет возможности в payload кнопок запихивать кириллицу и я вынужден использовать эту коляску
# Спонсор транслитерации этот источник. Этот источник - спасибо, что не оверфлоу https://habr.com/ru/post/265455/)
ALPHABET_L2CYR = {
    'А': "A",
    'Б': "B",
    'В': "V",
    'Г': "G",
    'Д': "D",
    'Е': "E",
    'Ё': "JE",
    'Ж': "ZH",
    'З': "Z",
    'И': "I",
    'Й': "Y",
    'К': "K",
    'Л': "L",
    'М': "M",
    'Н': "N",
    'О': "O",
    'П': "P",
    'Р': "R",
    'С': "S",
    'Т': "T",
    'У': "U",
    'Ф': "F",
    'Х': "KH",
    'Ц': "C",
    'Ч': "CH",
    'Ш': "SH",
    'Щ': "JSH",
    'Ъ': "HH",
    'Ы': "IH",
    'Ь': "JH",
    'Э': "EH",
    'Ю': "JU",
    'Я': "JA",
    'а': "a",
    'б': "b",
    'в': "v",
    'г': "g",
    'д': "d",
    'е': "e",
    'ё': "je",
    'ж': "zh",
    'з': "z",
    'и': "i",
    'й': "y",
    'к': "k",
    'л': "l",
    'м': "m",
    'н': "n",
    'о': "o",
    'п': "p",
    'р': "r",
    'с': "s",
    'т': "t",
    'у': "u",
    'ф': "f",
    'х': "kh",
    'ц': "c",
    'ч': "ch",
    'ш': "sh",
    'щ': "jsh",
    'ъ': "hh",
    'ы': "ih",
    'ь': "jh",
    'э': "eh",
    'ю': "ju",
    'я': "ja"
}
ALPHABET_CYR2L = {}
for (key, value) in ALPHABET_CYR2L.items():
    ALPHABET_CYR2L[value] = key


def lat2cyr(s):
    ab = ALPHABET_L2CYR
    sb = ""
    i = 0
    while i < len(s):
        ch = s[i]
        if ch == 'J' or ch == 'j':
            i += 1

            # TODO: make it prettier
            ch = s[i]
            if ch == 'E':
                sb += 'Ё'
            elif ch == 'e':
                sb += 'ё'
            elif ch == 'S':
                sb += 'Щ'
                i += 1
                if (s[i] != 'H'): raise Exception
            elif ch == 's':
                sb += 'щ'
                i += 1
                if (s[i] != 'h'): raise Exception
            elif ch == 'H':
                sb += 'Ь'
            elif ch == 'U':
                sb += 'Ю'
            elif ch == 'A':
                sb += 'Я'
            elif ch == 'h':
                sb += 'ь'
            elif ch == 'u':
                sb += 'ю'
            elif ch == 'a':
                sb += 'я'
            else:
                raise Exception
        elif (i + 1 < len(s) and (s[i + 1] == 'H' or s[i + 1] == 'h') and not (
                i + 2 < len(s) and (s[i + 2] == 'H' or s[i + 2] == 'h'))):
            a = {'Z': 'Ж',
                 'K': 'Х',
                 'C': 'Ч',
                 'S': 'Ш',
                 'E': 'Э',
                 'H': 'Ъ',
                 'I': 'Ы',
                 'z': 'ж',
                 'k': 'х',
                 'c': 'ч',
                 's': 'ш',
                 'e': 'э',
                 'h': 'ъ',
                 'i': 'ы',
                 }
            if ch in a:
                sb += a[ch]
            else:
                raise Exception
        else:
            if ch in ab:
                sb += ab[ch]
            else:
                sb += ch


def cyr2lat(cyr):
    res = ""
    for letter in cyr:
        if letter in ALPHABET_L2CYR:
            res += ALPHABET_L2CYR[letter]
        else:
            res += letter
    return res
