def roles_list2str(roles):
    res = ""
    for role in roles:
        res += "В \"" + role[-2] + "\" ты " + "[" + role[-1] + "];\n"
    return res[:-2:] + "."


def schools_list2str(schools):
    res = ""
    # schoolname(id), ...
    for school in schools:
        res += str(school[1]) + "(" + str(school[0]) + ")\n"
    return res


def begins_with(a, b):
    return a[:len(b)] == b


def check_cmd(prompt, cmd_alias, n_args, more_allowed=False):
    a = begins_with(prompt, cmd_alias)
    left = 0
    right = 0
    all = 0
    flag = False
    args = []
    arg = ""
    for letter in prompt:

        if letter == '[' and not flag:
            arg = ""
            left += 1
            flag = True
        elif letter == ']' and flag:
            args.append(arg)
            right += 1
            flag = False
        if letter == '[' or letter == ']':
            all += 1
        if letter != '[' and letter != ']':
            arg = arg + letter

        # print(all, left, right, letter)
    # print(flag)
    # print(all/2==n_args)
    # print(a)
    if a and left == right and left + right == all and (flag is False) and all / 2 == n_args:
        return args
    elif more_allowed and all / 2 >= n_args:
        return args
    else:
        return -1




def userRoles2Str(roles_list):
    # идет сначала группа потом люди
    if not roles_list:
        return "Ничего не надйено!"
    res = "Состав " + roles_list[0][2] + ":\n\n"

    for entry in roles_list:
        id_string = entry[1]
        role_string = entry[-1]

        res += "@id" + id_string + " - '" + role_string + "'\n"
    return res
