def parse_arg(cmd):
    """
    Вычленяет то, что идёт после команды в сообщении.
    Возвращает массив аргументов.
    :param cmd:
    :return:
    """
    # Get second word from split
    arg = cmd.split(' ', 1)[1]
    # Remove trailing backspaces
    while arg and arg[-1] == " ":
        arg = arg[:-1]
    args = arg.split(" ")
    if args == ['']:
        return False
    return args

# Some unit tests
# TODO: move unit tests to an other file.
assert (parse_arg("!создать_школу Лицей №86  ")==["Лицей","№86"]),"Wrong parse_arg result 1."
assert (parse_arg("!создать_школу       ") is False), "Wrong parse_arg result 2."