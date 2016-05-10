#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import signal
import sys
import json
from subprocess import Popen, PIPE, STDOUT
import ConfigParser

__author__ = "Jon Ander Besga"
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Jon Ander Besga"

class Bot(object):
    
    token = None
    update_id = None
        
    def __init__(self, token):
        print('Bot initialized!')
        self.token = str(token)
        
    def checkUpdates(self):
        """Check new messages received by the bot"""

        response = requests.post(
            url='https://api.telegram.org/bot{0}/{1}'.format(self.token, 'getUpdates'),
            data={'offset': self.update_id}
        ).json()
        
        if response['ok'] == True:
            if response['result']:
                if self.update_id == None:
                    self.update_id = response['result'][0]['update_id']
                    print('Update_id updated! (%s)' % str(self.update_id))
                
                if response['result'][0]['update_id'] == self.update_id:
                    message = response['result'][0]
                    self.update_id += 1
                    return message
        else:
            print('Unsuccessful request. Error code: %s. %s' % (response['error_code'], response['description']))
                
    def run(self):
        while True:
            message = self.checkUpdates()
            if message:
                if 'inline_query' in message:
                    if message['inline_query']['query']:
                        domain = message['inline_query']['query']
                        
                        whois_result = Popen(['whois', domain], stdout=PIPE, stderr=STDOUT).communicate()[0]
                        
                        if 'No match for' in whois_result:
                            status = 'El dominio %s esta DISPONIBLE!' % domain
                        else:
                            if 'Domain Name' in whois_result:
                                status = 'El dominio %s NO ESTA DISPONIBLE!' % domain
                            else:
                                status = 'No podemos comprobar el dominio %s' % domain
    
                        document = json.dumps([{'type': 'article',
                                                'id': '0',
                                                'input_message_content': {'message_text': status },
                                                'title': domain,
                                                'description': status,
                                                'thumb_url': 'https://cdn2.iconfinder.com/data/icons/windows-8-metro-style/512/domain.png',
                                                'thumb_width': 512,
                                                'thumb_height': 512}])
                                                
                        response = requests.post(
                            url='https://api.telegram.org/bot{0}/{1}'.format(self.token, 'answerInlineQuery'),
                            data={'inline_query_id': message['inline_query']['id'], 'results': document}
                        ).json()

  
def signal_handler(signal, frame):
    print('Bot stopped. Ctrl+C pressed!')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Get BOT_TOKEN from the settings.ini file
config = ConfigParser.RawConfigParser()
config.read('settings.ini')
BOT_TOKEN = config.get('Bot', 'token')
bot = Bot(BOT_TOKEN)
bot.run()