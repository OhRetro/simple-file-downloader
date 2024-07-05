from urllib.parse import urlparse
from os.path import basename as osp_basename
from re import sub as re_sub, search as re_search

def sanitize_filename(filename: str) -> str:
    return re_sub(r'[\\/*?:"<>|]', "", filename)

def get_filename_from_content_disposition(content_disposition: str):
    if not content_disposition:
        return None

    filename_match = re_search(r'filename\*?="?([^;"]+)"?', content_disposition)
    if filename_match:
        return sanitize_filename(filename_match.group(1))
    
    return None

def url_get_filename(url: str) -> str:
    parsed_url = urlparse(url)
    filename = osp_basename(parsed_url.path)
    return sanitize_filename(filename)

def url_is_valid(url: str) -> bool:
    parsed_url = urlparse(url)
    return parsed_url.scheme in ["http", "https"] and bool(parsed_url.netloc)
