
def get_data(path):
    content = ""
    with open(path, 'r', encoding="utf-8") as file:
        content = file.read()
    return content