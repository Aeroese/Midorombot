#coding:utf-8
import threading
import telebot
import configparser
import urllib3
import re
import json
import time
config = configparser.ConfigParser()
config.read('Config.ini')
chatid = config.get('Config','chatid').split(',')
hello = config.get('Config','hello').replace(r'\n','\n')
time = int(config.get('Config','time'))
bot = telebot.TeleBot(config.get('Config','token'))
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
http = urllib3.PoolManager()
def checkupdate(messagechatid=''):
    rom = json.loads(config.get('Config','roms'))
    if isinstance(rom,dict) :
        for i in rom.keys() :
            request = http.request('GET',rom.get(i)[0])
            result = re.search('.*?' + rom.get(i)[1], str(request.data)).groups()
            if len(result) >= 1 :
                download = rom.get(i)[2] + result[0] + rom.get(i)[3]
            if len(result) >= 2 :
                filename = result[1].replace('.zip','',1)
            else:
                filename = result[0].replace('.zip','',1)
            if len(result) >= 3 :
                filesize = result[2]
            if len(result) >= 4 :
                md5sum = result[3]
            else:
                md5sum = 'None'
            list = config.sections()
            section = filename.split('-',1)[0]
            if section not in list :
                config.add_section(section)
                config.set(section,'filename','')
            if config.get(section,'filename') != filename :
                if messagechatid != '' :
                    chatid2 = [messagechatid]
                else:
                    chatid2 = chatid
                for id in chatid2 :
                    if id == '' :
                        break
                    bot.send_message(chat_id=id, text='Hello , ' + i + ' has been updated\n' + 'Filename : ' + filename + '\nDownload : ' + download + '\nFile size : '+ filesize + '\nMd5sum : ' + md5sum)
                config.set(section,'filename',filename)
                config.set(section,'download',download)
                config.write(open("Config.ini", "w"))
            else:
                if messagechatid != '' :
                    chatid2 = [messagechatid]
                else:
                    chatid2 = chatid
                for id in chatid2 :
                    if id == '' :
                        break
                    bot.send_message(chat_id=id, text= i + ' no update.')
    timer = threading.Timer(time, checkupdate)
    timer.start()
@bot.message_handler(commands=['start'])
def send_welcome(message):
    if str(message.chat.id) in chatid:
        bot.send_message(reply_to_message_id=message.message_id, chat_id=message.chat.id, text='Sorry, You have been added. ')
        return
    chatid.append(str(message.chat.id))
    chatid1 = ''
    for id in chatid :
        if id == '' :
            continue
        chatid1 = chatid1 + id + ','
    config.set('Config', 'chatid', chatid1)
    config.write(open("Config.ini", "w"))
    bot.send_message(reply_to_message_id=message.message_id, chat_id=message.chat.id, text=hello)
@bot.message_handler(commands=['get','check','find'])
def send_roms(message):
    print(message)
    #bot.send_message(reply_to_message_id=message.message_id, chat_id=message.chat.id, text=message)
@bot.message_handler(commands=['update'])
def send_update(message):
    print(message.chat.id)
    bot.send_message(reply_to_message_id=message.message_id, chat_id=message.chat.id, text='Checking...')
    checkupdate(str(message.chat.id))
    #bot.send_message(reply_to_message_id=message.message_id, chat_id=message.chat.id, text='test')
@bot.message_handler(commands=['test'])
def send_test(message):
    bot.send_message(reply_to_message_id=message.message_id, chat_id=message.chat.id, text='test')
if __name__ == '__main__':
    timer = threading.Timer(time, checkupdate)
    timer.start()
    bot.polling()