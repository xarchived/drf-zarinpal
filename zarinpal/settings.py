from django.conf import settings

MERCHANT = settings.ZARINPAL['MERCHANT']
CALLBACK = settings.ZARINPAL['CALLBACK']
SUCCESS_REDIRECT = settings.ZARINPAL['SUCCESS_REDIRECT']
FAIL_REDIRECT = settings.ZARINPAL['FAIL_REDIRECT']
REDIS_DB = settings.ZARINPAL['REDIS_DB']
