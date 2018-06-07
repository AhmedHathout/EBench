def directorize(path: str) -> str:
    return path if path.endswith("/") else path + "/"

def remove_file_name(path: str) -> str:
    return "/".join(path.split("/")[:-1])
