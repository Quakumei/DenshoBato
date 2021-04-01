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


def school_info(school, school_groups, members, db_handler):
    # Based on data given (school is a tuple (id,school_name))
    # Return text message for the user
    members = sorted(members, key=lambda x: int(x[0]))

    res = ""
    res = res + f"Школа '{school[1]}' - [school_id: {school[0]}]\n"
    res = res + f"\nШкольные группы:\n"
    for group_id, group_name in school_groups:
        res = res + f"{group_name} - [group_id: {group_id}]\n"
    res = res + f"\nУчастники:\n"

    prev_role = 0
    cur_role = 0
    for m in members:
        cur_role = m[0]
        if cur_role != prev_role:
            res = res + f"\n{db_handler.fetch_role_name(cur_role)}:\n"
            prev_role = cur_role
        res += f'{m[1]} ({", ".join(m[2])}) [id{m[3]}]\n'
    res += '\n' + "-"*20 + '\n'
    res += f'Итого: {len(members)} участников.\n'
    return res

