from base64 import b64decode

__BASE_PATH = "L1ZvbHVtZXMvRWxlbWVudHMvUGVsaWN1bGFzLy5IaWRlL01ORw=="
__BASE_URL = "aHR0cHM6Ly9kb3VqaW5zLm1lL21hbmdhLw=="
__WP_URL = "aHR0cHM6Ly9kb3VqaW5zLm1lL3dwLWFkbWluL2FkbWluLWFqYXgucGhw"


def __decode(symbol):
    return b64decode(symbol.encode('ascii')).decode('ascii')


def get_base_path():
    return __decode(__BASE_PATH)


def get_base_url():
    return __decode(__BASE_URL)


def get_wp_url():
    return __decode(__WP_URL)
