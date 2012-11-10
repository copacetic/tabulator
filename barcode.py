PREFIX='**'
SUFFIX='**'
PREFIX_LENGTH=len(PREFIX)
SUFFIX_LENGTH=len(SUFFIX)

def scan():
    while True:
        code = input()
        if code[0:PREFIX_LENGTH] == PREFIX and code[-1*SUFFIX_LENGTH:] == SUFFIX:
            code = code[PREFIX_LENGTH:-SUFFIX_LENGTH]
            break
    return code

