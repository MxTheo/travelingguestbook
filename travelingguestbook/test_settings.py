from travelingguestbook.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = []

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]