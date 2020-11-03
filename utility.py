from colorama import Fore, Back, Style
from datetime import datetime
from time import gmtime, strftime


def format_msg_log(msg):
    """
    Formats data["object"]["message"] for
    log output
    :param msg:
    :return:
    """
    block_del = "-"
    lines = [
        block_del * 10,
        "profile_link:\thttps://vk.com/id" + str(msg["from_id"]),
        "date:\t" + str(datetime.utcfromtimestamp(msg["date"]).strftime('%H:%M:%S %Y-%m-%d')),
        "text:\n" + block_del * 10 + "\n" + str(msg["text"]) + "\n" + block_del * 10
    ]

    return "\n" + "\n".join([line for line in lines]) + "\n"


def console_log(data, log_type="General"):
    """
    :param log_type: - type of the log
    :param data: dictionary passed with it.
    :return: prints beautiful console log
    """
    font_color = {"red": Fore.RED,
                  "blue": Fore.BLUE,
                  "green": Fore.GREEN,
                  "yellow": Fore.YELLOW,
                  "pink": Fore.MAGENTA,
                  "cyan": Fore.CYAN,
                  "white": Fore.WHITE,
                  "black": Fore.BLACK,
                  "magenta": Fore.MAGENTA}
    style_reset = Style.RESET_ALL
    log_type_color = style_reset
    if log_type == "General":
        log_type_color = font_color["white"]
    if log_type == "Event":
        log_type_color = font_color["yellow"]
    if log_type == "Important":
        log_type_color = font_color["magenta"]
    if log_type == "API":
        log_type_color = font_color["white"]

    time_string = strftime("%d/%m/%Y %H:%M:%S", gmtime())
    log_string = "[" + time_string + "]"
    log_string += "[" + log_type_color + log_type + style_reset + "] "
    log_string += str(data["what"]) + ' ' + str(data["info"])

    print(log_string)
    return
