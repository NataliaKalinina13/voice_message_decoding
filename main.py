import telebot
import requests
# import openai
import os
import subprocess
import ffmpeg


class VoiceToTextBot:
    def __init__(self, api_token, ogg_file):
        self.API_token = api_token
        self.bot = telebot.TeleBot(self.API_token)
        # self.openai_key = openai_key
        self.mp3_file = self.convert_ogg_to_mp3(input_file=ogg_file)

        @self.bot.message_handler(commands=['start'])
        def start(message):
            '''output a greeting after /start'''
            message_with_user_name = f'Привет, <b>{message.from_user.first_name}</b>. Я бот для расшифровки твоих голосовых сообщений. Отправь мне любую голосовуху.'
            self.bot.send_message(message.chat.id, message_with_user_name, parse_mode='html')

        @self.bot.message_handler(content_types=['voice'])
        def get_audio_file(message):
            '''get an audio file from a user and save it as a temp.file'''
            file_info = self.bot.get_file(message.voice.file_id)
            file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(api_token, file_info.file_path))

            with open('v_message.ogg', 'wb') as file_object:
                file_object.write(file.content)

    def convert_ogg_to_mp3(self, input_file):
        '''convert an ogg-file to mp3 with ffmpeg'''
        process = subprocess.run(['ffmpeg', '-i',
                              'input_file', '-c:a',
                              'libmp3lame', '-q:a', '2', 'output_file'])
   

def run_bot(self):
    '''launch a bot'''
    self.bot.polling(none_stop=True)


if __name__ == '__main__':
    API_token = 'text_token'
    ogg_file = 'file_path'
    bot = VoiceToTextBot(API_token, ogg_file)
    bot.run_bot()

