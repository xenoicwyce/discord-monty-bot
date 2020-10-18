def replace(text, oldchars, newchars):
    """
    Utility function to replace characters in a string.

    If both oldchars and newchars are str, do the normal string.replace().

    If oldchars is a list and newchars is a str, replace all characters in
    oldchars by the character in newchars.

    If both oldchars and newchars are lists, replace by the map between the
    two lists (replace the character in oldchar by the character in newchar
    of the same index).
    """

    if type(oldchars) is str:
        return text.replace(oldchars, newchars)
    else:
        if type(newchars) is str:
            for oc in oldchars:
                text = text.replace(oc, newchars)
        else:
            for idx in range(len(oldchars)):
                text = text.replace(oldchars[idx], newchars[idx])

        return text