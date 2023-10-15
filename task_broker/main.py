from celery.exceptions import TimeoutError
from tasks import say_hello
from time import sleep

result = [] 
for x in range(100):
    result.append(say_hello.delay(f"i am {x}"))
for x in result:
    print(x.get(timeout=10))
