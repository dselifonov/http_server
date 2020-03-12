import os
import urllib

from src.http import HTTPError
from src.http.body import Body


def check_perms(root_dir, doc_path):
    parent_path = os.path.abspath(root_dir)
    child_path = os.path.abspath(doc_path)
    return os.path.commonpath([parent_path]) == os.path.commonpath([parent_path, child_path])


def get_response_file(root_dir, path):
    decoded_path = urllib.parse.unquote(path)
    doc_path = os.path.join(root_dir, decoded_path.lstrip('/'))
    if decoded_path.endswith('/'):
        doc_path = os.path.join(doc_path, 'index.html')

    if not os.path.exists(doc_path):
        raise HTTPError(404, 'Not Found')

    if not check_perms(root_dir, doc_path):
        raise HTTPError(403, 'Permission Denied')

    return Body(doc_path, open(doc_path, 'rb'))
