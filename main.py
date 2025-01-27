from threading import Thread
from os import environ
import pip

if 'HEROKU' not in environ:
    with open("requirements.txt") as file:
        for module in file.readlines():
            pip.main(['install', module])
import weblearn

Thread(target=weblearn.main).start()
