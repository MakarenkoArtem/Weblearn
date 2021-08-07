from threading import Thread
import weblearn
import chat_bot

Thread(target=weblearn.main).start()
Thread(target=chat_bot.main).start()