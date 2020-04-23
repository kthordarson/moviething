from defs import *
import unicodedata

def sanatized_string(input_string, whitelist=valid_input_string_chars, replace=''):
    # replace spaces
    for r in replace:
        input_string = input_string.replace(r, '_')

    # keep only valid ascii chars
    cleaned_input_string = unicodedata.normalize(
        'NFKD', input_string).encode('ASCII', 'ignore').decode()

    # keep only whitelisted chars
    cleaned_input_string = ''.join(
        c for c in cleaned_input_string if c in whitelist)
    # if len(cleaned_input_string) > char_limit:
    #    print("Warning, input_string truncated because it was over {}. input_strings may no longer be unique".format(char_limit))
    return cleaned_input_string[:char_limit]
