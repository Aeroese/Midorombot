#coding:utf-8
import threading
import telebot
import configparser
import telepot
import urllib3
import re
import json
import datetime
import time
from telebot import types
config = configparser.ConfigParser()
config.read('Config.ini')
chatid = config.get('Config','chatid').split(',')
hello = config.get('Config','hello').replace(r'\n','\n')
checktime = config.get('Config','time').split(',')
proxy_url = "http://proxy.server:3128"
telepot.api._pools = {
    'default': urllib3.ProxyManager(proxy_url=proxy_url, num_pools=3, maxsize=10, retries=False, timeout=30),}
telepot.api._onetime_pool_spec = (urllib3.ProxyManager, dict(proxy_url=proxy_url, num_pools=1, maxsize=1, retries=False, timeout=30))
bot = telebot.TeleBot(config.get('Config','token'))
#urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
http = urllib3.PoolManager()
def checkupdate(messagechatid='') :
    rom = json.loads(config.get('Config','roms'))
    if isinstance(rom,dict) :
        for i in rom.keys() :
            request = http.request('GET',rom.get(i)[0])
            a = re.search('.*?' + rom.get(i)[1], str(request.data))
            if a is None:
                break
                if messagechatid != '' :
                    bot.send_message(chat_id=int(messagechatid), text= i + ' no update.')
            result = a.groups()
            if len(result) >= 1 :
                download = rom.get(i)[2] + result[0] + rom.get(i)[3]
            if len(result) >= 2 :
                filename = result[1].replace('.zip','',1)
            else:
                filename = result[0].replace('.zip','',1)
            if len(result) >= 3 :
                if result[2].replace(' ','') == '' :
                    filesize = 'None'
                else :
                    filesize = result[2]
            if len(result) >= 4 :
                md5sum = result[3]
            else:
                md5sum = 'None'
            list = config.sections()
            if i not in list :
                config.add_section(i)
                config.set(i,'filename','')
            if filename == '' :
                break
            if config.get(i,'filename') != filename :
                if messagechatid != '' :
                    chatid2 = [messagechatid]
                else:
                    chatid2 = chatid
                for id in chatid2 :
                    if id == '' :
                        break
                    bot.send_message(chat_id=int(id), text='Hello , ' + i + ' has been updated\n' + 'Filename : ' + filename + '\nDownload : ' + download + '\nFilesize : '+ filesize + '\nMd5sum : ' + md5sum)
                    config.set(i,'filename',filename)
                    config.set(i,'download',download)
                    config.set(i,'filesize',filesize)
                    config.set(i,'md5sum',md5sum)
                    config.write(open("Config.ini", "w"))
            else:
                if messagechatid != '' :
                    bot.send_message(chat_id=int(messagechatid), text= i + ' no update.')
def task() : 
    print('Midorombot started.')
    while True:
        for ckt in checktime :
            ckt2=ckt.split(':')
            now = datetime.datetime.now()
            if now.hour==int(ckt2[0]) and now.minute==int(ckt2[1]):
                t = threading.Thread(target=checkupdate)
                t.start()
                time.sleep(60)
        time.sleep(10)
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
    print('Total use : '+str(len(chatid)))
@bot.message_handler(commands=['get'])
def send_roms(message):
    rom = json.loads(config.get('Config','roms'))
    markup = types.InlineKeyboardMarkup()
    if isinstance(rom,dict) :
        for i in rom.keys() :
            itembtn = types.InlineKeyboardButton(i, callback_data=i)
            markup.add(itembtn)
        bot.send_message(message.chat.id, "Choose one rom:", reply_markup=markup)
@bot.callback_query_handler(func=lambda call: True)
def callback_handle(call):
    #bot.send_message(call.message.chat.id, 'You Choosed %s' % call.data)
    filename = config.get(call.data,'filename')
    download = config.get(call.data,'download')
    filesize = config.get(call.data,'filesize')
    md5sum = config.get(call.data,'md5sum')
    bot.send_message(call.message.chat.id, text='Hello , This is the latest ' + call.data + '\nFilename : ' + filename + '\nDownload : ' + download + '\nFilesize : '+ filesize + '\nMd5sum : ' + md5sum)
@bot.message_handler(commands=['update'])
def send_update(message):
    bot.send_message(reply_to_message_id=message.message_id, chat_id=message.chat.id, text='Checking...')
    t = threading.Thread(target=checkupdate,args=(str(message.chat.id),))
    t.start()
@bot.message_handler(commands=['test'])
def send_test(message):
    bot.send_message(reply_to_message_id=message.message_id, chat_id=message.chat.id, text='test')
if __name__ == '__main__':
    timer = threading.Timer(1, task)
    timer.start()
    bot.polling()
