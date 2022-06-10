# TODO: Refactor, re-write and re-name
#  Currently just copied from the Bio-Logic API

def pp_plural(nb, label, num=True, nothing=''):
    """Return a user friendly version of an ordinal and a label.

       num is used to force a number version,
       nothing is what to say if there is nothing
    """
    if nb == 0:
        if nothing:
            en_clair = f"{nothing}"
        else:
            en_clair = f"{0 if num else 'no'} {label}"
    elif nb == 1:
        en_clair = f"{1 if num else 'one'} {label}"
    else:
        en_clair = f"{nb} {label}s"
    return en_clair