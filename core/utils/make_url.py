
def url_by_dict(url_config: dict, path_name: str) -> str:
    return f"{url_config['scheme']}://{url_config['host']}:{url_config['port']}/{path_name}"