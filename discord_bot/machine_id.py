import base64

caesar_string = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

def caesar_encrypt(s:str, k:int=0, p:int=3):
    shift = k
    new_str = ''
    for i,char in enumerate([char for char in s if char in caesar_string]):
        shift += p
        c_i = caesar_string.index(char)
        c_i += shift
        c_i %= len(caesar_string)
        new_str += caesar_string[c_i]
    return new_str

def caesar_decrypt(s:str, k:int=0, p:int=3):
    shift = k
    new_str = ''
    for i,char in enumerate([char for char in s if char in caesar_string]):
        shift += p
        c_i = caesar_string.index(char)
        c_i -= shift
        c_i %= len(caesar_string)
        new_str += caesar_string[c_i]
    return new_str

base64_pad = lambda L: 2-(L+2)%3

def decrypt(encrypted:str):
    c_decrypt = caesar_decrypt(encrypted)
    if len(c_decrypt) != len(encrypted):
        return None
    try:
        padding = '='*base64_pad(len(c_decrypt))
        b64_padded = c_decrypt+padding
        decoded_machine_id = base64.b64decode(b64_padded).decode()
        return decoded_machine_id
    except:
        return None