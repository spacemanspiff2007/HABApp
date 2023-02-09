"""Load the json in json of openHAB and print it as a proper json"""

from json import dumps, loads

INCLUDE_CHANNELS = False


to_prettify = ''


def load_str(in_str):
    if not isinstance(in_str, str):
        return in_str

    if in_str.startswith('[') and in_str.endswith(']') or in_str.startswith('{') and in_str.endswith('}'):
        return loads(in_str)
    return in_str


def load_obj(obj):
    new_obj = load_str(obj)
    if isinstance(new_obj, list):
        for i, obj in enumerate(new_obj):
            new_obj[i] = load_obj(obj)
    elif isinstance(new_obj, dict):
        for key, obj in new_obj.items():
            new_obj[key] = load_obj(obj)

        # replace channel with an empty list
        if not INCLUDE_CHANNELS and (channels := new_obj.get('channels')) is not None:
            channels.clear()
            channels.append('...')

    return new_obj


pretty_obj = load_obj(to_prettify)
print(dumps(pretty_obj, indent=4))
