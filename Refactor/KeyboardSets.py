import json
import Utility
from CodeList import *

# sample_keyboard = {"one_time": False, "buttons": [
#     [
#     ]
# ]
#                    }
# sample_json = json.dumps(sample_keyboard)

COLORS = {"RED": 'negative',
          "BLUE": 'primary',
          "WHITE": 'secondary',
          "GREEN": 'positive'}


def text_button(label, color, payload=''):
    # returns button dict with given parameters

    # Note on colors:
    # Green - positive
    # Blue - primary
    # White - secondary
    # Red - negative

    color = COLORS[color]
    return {
        "action": {
            "type": "text",
            "payload": payload,
            "label": label
        },
        "color": color
    }


def create_kb(one_time, buttons, inline=False):
    # return kb json object
    # pay attention to buttons obj:
    # you put all buttons in an array,
    # and than in array for each of the lines.
    return json.dumps({"one_time": one_time, "buttons": buttons, "inline": inline})


def get_register_buttons(name):
    return create_kb(False, [[text_button(f"{COMMAND_SYMBOL}{REGISTER_WORD} {name}", "BLUE")],
                             [text_button("- Потом", "WHITE")]], True)
