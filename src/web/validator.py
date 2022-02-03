from re import match

with open('database/codigos_postais.txt', encoding='utf8') as f:
    valid_postal_codes = f.read().split('\n')

def name_validator(Name):
    if len(Name) > 64:
        return False
    group = match(r"^[a-zA-Z\-]{1,64}$", Name)
    return group is not None

def postal_code_validator(postal_code):
    return postal_code in valid_postal_codes

def email_validator(email):
    if len(email) > 320:
        return False
    group = match(r"^[\w\"!#$%&'*+\/=?^_`{|}~-]+(?:\.[\w!#$%&'*+\/=?^_`{|}~-]+)*@(?:[\[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9\]])?$", email)
    return group is not None

def password_validator(password):
    if len(password) > 64:
        return False
    group = match(r"(?=^.{8,}$)((?=.*\d)|(?=.*\W+))(?![.\n])(?=.*[A-Z])(?=.*[a-z]).*$", password)
    return group is not None

def address_validator(address):
    if len(address) > 512:
        return False
    group = match(r"^[\w\ ºª/.-:]*$", address)
    return group is not None

#add birthday validator? (frontend is already done)

def cellphone_validator(cellphone):
    if len(cellphone) > 9 or len(cellphone)  < 9:
        return False
    group = match(r"^9[1236]{1}[0-9]{7}$", cellphone)
    return group is not None