from schedule_parser import get_schedule
from dateutil import parser
import datetime
from config import mmessage, OW_API_key
from pyowm import OWM
import sqlite3

conn = sqlite3.connect('users.db')

def get_group(vk_id):
    with conn:
        cur = conn.cursor()    
        cur.execute('SELECT user_Group FROM users WHERE vk_ID=?',(vk_id,))
        user = cur.fetchone()
        if (user == None):
            return 0
        else: return user[0]

def set_mode(vk_id, mode):
    with conn:
        cur = conn.cursor()    
        cur.execute('SELECT vk_ID FROM users WHERE vk_ID=?',(vk_id,))
        user = cur.fetchone()
        if (user == None):
            return 0
        cur.execute('UPDATE users SET mode=? WHERE vk_ID=?', (int(mode), vk_id,))
        conn.commit()
        return 1

def send_mesg(vk, vk_id, chat_flag, text):
    if(chat_flag):
        vk.messages.send(chat_id=vk_id, message=text)
    else:
        vk.messages.send(user_id=vk_id, message=text)

def send_schedule(vk_id, vk, chat_flag, msg):
    send_mesg(vk, vk_id, chat_flag, "Расписание подготавливается...")
    config = msg.split()
    if(len(config)>1):
        date = config[0]
        group = config[1]
    else:
        date=config[0]
        group = get_group(vk_id)
        if(group == 0):
            text = "Необходимо указать группу. Напишите команду в формате !расписание <дата> <группа>, или используйте команду !группа для внесения информации о вашей группе в базу."
            send_mesg(vk, vk_id, chat_flag, text)
            return
    try:
        date=parser.parse(date, dayfirst=True)
        schedule = get_schedule(group, date.strftime("%Y-%m-%d"))
    except ValueError as error:
        text = "⚠ Произошла ошибка, вероятно вы ввели неправильную дату. Соблюдайте следующий формат: ДД.ММ.ГГ (ДД/ММ/ГГ)"
        send_mesg(vk, vk_id, chat_flag, text)
        return
    except Exception as error:
        text = "Произошла ошибка: " + str(error)
        send_mesg(vk, vk_id, chat_flag, text)
        return
    text = ""
    for subj in schedule:
        text=text+"[%s] [%s] %s {%s} |%s|\n"%(subj['time'], subj['type'], subj['name'], subj['room'], subj['lecturers'])
    send_mesg(vk, vk_id, chat_flag, text)

def send_today(vk_id, vk, chat_flag, msg):
    send_mesg(vk, vk_id, chat_flag, "Расписание подготавливается...")
    if msg is not None:
        group=msg
    else:
        group = get_group(vk_id)
        if(group == 0):
            text = "Необходимо указать группу. Напишите команду в формате !сегодня <группа>, или используйте команду !группа для внесения информации о вашей группе в базу."
            send_mesg(vk, vk_id, chat_flag, text)
            return
    try:
        date=datetime.date.today()
        schedule = get_schedule(group, date.strftime("%Y-%m-%d"))
    except Exception as error:
        text = "Произошла ошибка: " + str(error)
        send_mesg(vk, vk_id, chat_flag, text)
        return
    text = ""
    for subj in schedule:
        text=text+"[%s] [%s] %s {%s} |%s|\n"%(subj['time'], subj['type'], subj['name'], subj['room'], subj['lecturers'])
    send_mesg(vk, vk_id, chat_flag, text)

def send_tomorrow(vk_id, vk, chat_flag, msg):
    send_mesg(vk, vk_id, chat_flag, "Расписание подготавливается...")
    if msg is not None:
        group=msg
    else:
        group = get_group(vk_id)
        if(group == 0):
            text = "Необходимо указать группу. Напишите команду в формате !завтра <группа>, или используйте команду !группа для внесения информации о вашей группе в базу."
            send_mesg(vk, vk_id, chat_flag, text)
            return
    try:
        date=datetime.date.today()+ datetime.timedelta(days=1)
        schedule = get_schedule(group, date.strftime("%Y-%m-%d"))
    except Exception as error:
        text = "Произошла ошибка: " + str(error)
        send_mesg(vk, vk_id, chat_flag, text)
        return
    text = ""
    for subj in schedule:
        text=text+"[%s] [%s] %s {%s} |%s|\n"%(subj['time'], subj['type'], subj['name'], subj['room'], subj['lecturers'])
    send_mesg(vk, vk_id, chat_flag, text)

def morning_messages(vk_id, vk, chat_flag=0, group=0):
    owm = OWM(OW_API_key, language='ru')
    obs = owm.weather_at_place('Moscow,RU') 
    weather = obs.get_weather()
    temp = weather.get_temperature(unit='celsius')['temp']
    status = weather.get_detailed_status()
    fc = owm.three_hours_forecast('Moscow,RU')
    f = fc.get_forecast()
    forecast = ""
    i=0
    for w in f:
          if(i>3): break
          ttime=w.get_reference_time('iso')[:-6]
          ttemp = int(w.get_temperature(unit='celsius')['temp'])
          tstatus = w.get_detailed_status()
          forecast = forecast + "%s, %d градусов, %s\n"%(ttime, ttemp, tstatus)
          i+=1

    with conn:
        cur = conn.cursor()    
        cur.execute('SELECT * FROM users WHERE mode=?',(1,))
        users = cur.fetchall()
    for user in users:
        schedule = get_schedule(user[1])
        sc_text = ""
        for subj in schedule:
            sc_text=sc_text+"[%s] [%s] %s {%s} |%s|\n"%(subj['time'], subj['type'], subj['name'], subj['room'], subj['lecturers'])
        text = mmessage%(sc_text, temp, status, forecast)
        if(user[0]<1000):
            chat_flag=True
        else: chat_flag=False
        send_mesg(vk, user[0], chat_flag, text)

def save_group(vk_id, vk, chat_flag, msg):
    if msg is not None:
        
        group=msg
    else:
        text="Необходимо написать вашу группу после команды. \nПример: !группа Б14-501"
        send_mesg(vk, vk_id, chat_flag, text)
        return

    with conn:
        cur = conn.cursor()    
        cur.execute('SELECT vk_id FROM users WHERE vk_ID=?',(vk_id,))
        user = cur.fetchall()
        if (len(user) != 0):
            text="Вы уже были зарегестрированы ранее! Для удаления информации о себе используйте команду !забыть"
            send_mesg(vk, vk_id, chat_flag, text)
            return
        cur.execute('INSERT INTO users (vk_ID, user_Group, mode) VALUES(?, ?, ?)', (vk_id, group, 0))
        conn.commit()
        text="Я тебя запомнил..."
        send_mesg(vk, vk_id, chat_flag, text)

def delete_user(vk_id, vk, chat_flag, msg):
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute('SELECT vk_ID FROM users WHERE vk_ID=?', (vk_id,))
    user = cur.fetchall()
    if (len(user) == 0):
        text='Вы не были зарегестрированы ранее!'
        send_mesg(vk, vk_id, chat_flag, text)
        return
    cur.execute("DELETE FROM users WHERE vk_ID=?", (vk_id,))
    conn.commit()
    text='Ваш id удален из базы!'
    send_mesg(vk, vk_id, chat_flag, text)

def update_mode(vk_id, vk, chat_flag, msg):
    if msg is not None and msg in ('0','1'):
        mode=msg
    else:
        text="Необходимо указать режим: \n1 - включить напоминания\n0 - выключить напоминания.\nИспользуйте команду в формате: !напоминания {0|1}"
        send_mesg(vk, vk_id, chat_flag, text)
        return
    if(set_mode(vk_id, mode) == 0):
        text="Для начала необходимо указать совю группу. Используйте команду !группа <группа>"
        send_mesg(vk, vk_id, chat_flag, text)
    else:
        text="Информация обновлена"
        send_mesg(vk, vk_id, chat_flag, text)

commands = ((u'!расписание',send_schedule),
            (u'!сегодня',send_today),
            (u'!завтра',send_tomorrow),
            (u'!пост',morning_messages),
            (u'!группа', save_group),
            (u'!забыть', delete_user),
            (u'!напоминания', update_mode),)

def parse_message(msg):
    #msg = msg.lower()
    if msg[0] == '!':
        return msg.split(" ", 1)
    else:
        return [u'***', '']

def run_msg(vk, vk_id, message, chat_flag):
    res = parse_message(message)
    for command in commands:
        if (res[0] == command[0]):
            try:
                command[1](vk_id, vk, chat_flag, res[1] if len(res)>1 else None)
                return

            except Exception as error:
                err_m = u'Что то пошло не так. Попробуйте повторить запрос или свяжитесь с администратором'
                send_mesg(vk, vk_id, chat_flag, err_m)
                print(error)