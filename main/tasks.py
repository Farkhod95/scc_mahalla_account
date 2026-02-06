# app/tasks.py

from celery import shared_task
from time import sleep

# Oddiy vazifa: salom berish
@shared_task
def say_hello():
    print("Hello, world!")
    return "Hello, world!"

# Sekin ishlaydigan vazifa: kutish
@shared_task
def long_task():
    sleep(10)
    print("Task finished!")
    return "Task finished!"
