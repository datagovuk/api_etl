import string


ALLOWED = string.letters + string.digits + '_' + '-'

def slugify_name(name):
    newname = ""
    first = True
    for n in name.strip():
        if n.isupper() and not first:
            newname = "".join([newname, " ", n])
        else:
            newname = "".join([newname, n])
        first = False

    n = "".join(newname).replace(' ', '_').lower()
    n = "".join([c for c in n if c in ALLOWED])
    # Fix up common special cases ...
    return n.replace('_i_d', "_id")