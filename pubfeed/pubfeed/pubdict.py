from collections import defaultdict
from typing import Any

class SubVal(object):
    pass


class SubKey(object):
    pass


class AllSubKeys(object):
    pass


class PubDictException(Exception):
    pass


class PubDictSub(object):

    def __init__(self, func, args: tuple = None, kwargs: dict = None, call_order: int = None, ):
        pass 

    
class PubDict(dict):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)