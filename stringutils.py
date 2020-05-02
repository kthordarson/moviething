import unicodedata

from defs import CHAR_LIMIT, VALID_INPUT_STRING_CHARS, VALID_TAG_CHARS


def sanatized_string(input_string, whitelist=VALID_INPUT_STRING_CHARS, replace='', s_format='NFKD'):
    # replace spaces
    #  ‘NFC’, ‘NFKC’, ‘NFD’, and ‘NFKD’.
    for r in replace:
        input_string = input_string.replace(r, '_')
    # keep only valid ascii chars
    cleaned_input_string = unicodedata.normalize(s_format, input_string).encode('ASCII', 'ignore').decode()
    # keep only whitelisted chars
    cleaned_input_string = ''.join(c for c in cleaned_input_string if c in whitelist)
    # if len(cleaned_input_string) > CHAR_LIMIT:
    #    print("Warning, input_string truncated because it was over {}. input_strings may no longer be unique".format(CHAR_LIMIT))
    return cleaned_input_string[:CHAR_LIMIT]
