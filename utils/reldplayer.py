
from functools import cache

@cache
def ldplayer():
    from reldplayer.quick import Global, Console
    x = Global()
    assert x
    return Console.auto()



    
