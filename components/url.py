from urllib.parse import urlparse
from os.path import basename as osp_basename
from re import sub as re_sub

def sanitize_filename(filename: str) -> str:
    return re_sub(r'[\\/*?:"<>|]', "", filename)

def url_get_filename(url: str) -> str:
    parsed_url = urlparse(url)
    filename = osp_basename(parsed_url.path)
    return sanitize_filename(filename)

def url_is_valid(url: str) -> bool:
    parsed_url = urlparse(url)
    return parsed_url.scheme in ["http", "https"] and bool(parsed_url.netloc)
