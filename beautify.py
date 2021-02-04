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
