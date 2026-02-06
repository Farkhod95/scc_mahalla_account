
def enum_serialize(enum):
    result = []
    for e in enum:
        result.append({"id": e[0], "name": e[1]})
    return result
