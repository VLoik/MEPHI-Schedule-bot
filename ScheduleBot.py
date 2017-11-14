# coding=UTF-8

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import requests
import time, datetime
import config
from commands import run_msg, morning_messages
from multiprocessing import Process

def posting():
    vk_session = vk_api.VkApi(config.login, config.password, scope="messages,offline")
    try:
        vk_session.auth()
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return
     
    vk = vk_session.get_api()
    print("Morning messages ready!")
    while(True):
        try:
            now = datetime.datetime.now()
            if(now.hour == config.sending_time.hour and now.minute == config.sending_time.minute):
                morning_messages(96494615,vk)
                time.sleep(23*3600)
        except Exception as err:
            print(err)



def main():

    vk_session = vk_api.VkApi(config.login, config.password, scope="messages,offline")
    try:
        vk_session.auth()
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return
     
    vk = vk_session.get_api()
    print("Main bot ready!")

    p = Process(target=posting)
    p.start()


    longpoll = VkLongPoll(vk_session)
    while True:
        try:
            

            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    if(event.from_chat):
                        run_msg(vk, event.chat_id, event.text, True)
                    else:
                        run_msg(vk, event.user_id, event.text, False)
        except Exception as error:
                text = "Произошла ошибка: " + str(error)
                vk.messages.send(user_id=96494615, message=text)
                print(error)
                time.sleep(5)


if __name__ == '__main__':
    main()
