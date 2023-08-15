import telebot
import requests
import openai
import os
import subprocess


class VoiceToTextBot:
    def __init__(self, api_token, openai_key):
        self.API_token = api_token
        self.bot = telebot.TeleBot(self.API_token)
        self.openai_key = openai_key

        @self.bot.message_handler(content_types=['text'])
        def start(message):
            '''output a greeting'''
            message_with_user_name = f'Привет, <b>{message.from_user.first_name}</b>. Я бот для расшифровки ' \
                                     f'твоих голосовых сообщений. Отправь мне любую голосовуху.'
            self.bot.send_message(message.chat.id, message_with_user_name, parse_mode='html')

        @self.bot.message_handler(content_types=['voice'])
        def get_audio_file(message):
            '''get an audio file from a user and save it as a temp.file,
            convert it into wav-format, get a transcription and send it back'''
            file_info = self.bot.get_file(message.voice.file_id)
            file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(api_token, file_info.file_path))

            with open('v_message.ogg', 'wb') as file_object:
                file_object.write(file.content)

            text = self.transcribe_file(message)

            return text

    def convert_ogg_to_mp3(self, input_file='v_message.ogg', output_file='v_message.wav'):
        '''convert an ogg-file to wav-format with ffmpeg'''
        process = subprocess.run(['ffmpeg', '-i', input_file, output_file])

        return os.remove(input_file)

    def transcribe_file(self, message):
        '''get a file transcription with the help of Whisper'''
        wav_file = self.convert_ogg_to_mp3()
        audio_file = open('v_message.wav', "rb")
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        os.remove('v_message.wav')

        self.bot.reply_to(message, transcript['text'])

    def run_bot(self):
        '''launch a bot'''
        self.bot.polling(none_stop=True)


if __name__ == '__main__':
    API_token = 'token_text'
    openai.api_key = 'key_text'

    bot = VoiceToTextBot(API_token, openai.api_key)
    bot.run_bot()
