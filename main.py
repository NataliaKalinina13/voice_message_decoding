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

        # @self.bot.message_handler(content_types=['#text'])
        # def start(message):
        #     '''output a greeting'''
        #     message_with_user_name = f'Привет, <b>{message.from_user.first_name}</b>. Я бот для расшифровки ' \
        #                              f'твоих голосовых сообщений. Отправь мне любую голосовуху.'
        #     self.bot.send_message(message.chat.id, message_with_user_name, parse_mode='html')

        @self.bot.message_handler(content_types=['voice', 'video_note'])
        def get_audio_file(message):
            '''get an audio file from a user and save it as a temp.file,
            convert it into wav-format, get a transcription and send it back'''
            if message.content_type == 'voice':
                file_info = self.bot.get_file(message.voice.file_id)
                file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(api_token, file_info.file_path))

                with open('v_message.ogg', 'wb') as file_object:
                    file_object.write(file.content)
                new_file = self.convert_ogg_to_mp3()
                open_file_voice = open('v_message.wav', "rb")
                transcript = openai.Audio.transcribe("whisper-1", open_file_voice)

                os.remove('/Users/nataliakalinina/voice_message_decoding/v_message.wav')

                self.bot.reply_to(message, transcript['text'])

                # return text

            elif message.content_type == 'video_note':
                file_info = self.bot.get_file(message.video_note.file_id)
                file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(api_token, file_info.file_path))

                with open('video_message.mp4', 'wb') as file_object:
                    file_object.write(file.content)

                new_file = self.convert_mp4_to_mp3()
                open_file_video = open('video_message.wav', "rb")

                transcript = openai.Audio.transcribe("whisper-1", open_file_video)

                os.remove('/Users/nataliakalinina/voice_message_decoding/video_message.wav')

                self.bot.reply_to(message, transcript['text'])

                # return text

    def convert_ogg_to_mp3(self, input_file='v_message.ogg', output_file='v_message.wav'):
        '''convert an ogg-file to wav-format with ffmpeg'''
        process = subprocess.run(['ffmpeg', '-i', input_file, output_file])

        return os.remove('/Users/nataliakalinina/voice_message_decoding/v_message.ogg')

    def convert_mp4_to_mp3(self, input_file='video_message.mp4', output_file='video_message.wav'):
        '''convert an ogg-file to wav-format with ffmpeg'''
        process = subprocess.run(['ffmpeg', '-i', input_file, output_file])

        return os.remove('/Users/nataliakalinina/voice_message_decoding/video_message.mp4')

    def run_bot(self):
        '''launch a bot'''
        self.bot.polling(none_stop=True)


if __name__ == '__main__':
    API_token = '6106303194:AAExMxe7GqUM1IdDE25PAU6SdTSagF4o3K4'
    openai.api_key = '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'

    bot = VoiceToTextBot(API_token, openai.api_key)
    bot.run_bot()
