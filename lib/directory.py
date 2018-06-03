def directorize(path: str, remove_slash=True) -> str:
    if not path.endswith("/"):
        path += "/"
    if path.startswith("/") and remove_slash:
        path = path[1:]
    return path

def remove_file_name(path: str) -> str:
    return "/".join(path.split("/")[:-1])
