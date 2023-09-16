import telebot
import requests
import openai
import os
import time


class VoiceToTextBot:
    TEMP_FILE_DIR = "/var/cache/voice_message_decoding/"
    MAX_REQUEST = 3

    def __init__(self, api_token, openai_key):
        self.API_token = api_token
        self.bot = telebot.TeleBot(self.API_token)
        self.openai_key = openai_key
        self.last_request_time = 0
        self.request_amount = 0

        try:
            os.mkdir("/var/cache/voice_message_decoding")
        except FileExistsError:
            pass

        @self.bot.message_handler(content_types=['voice', 'video_note'])
        def get_audio_file(message):
            start = time.time()

            if start - self.last_request_time <= 60:
                self.request_amount = 0
            else:
                self.request_amount += 1
                if self.request_amount >= self.MAX_REQUEST:
                    time_to_sleep = int(self.last_request_time + 60 - start)
                    if time_to_sleep > 0:
                        time.sleep(time_to_sleep)
                    else:
                        self.request_amount = 0
                        self.last_request_time = start

            if message.content_type == 'voice':
                file_info = self.bot.get_file(message.voice.file_id)
            else:
                file_info = self.bot.get_file(message.video_note.file_id)
            filename = f'{message.content_type}_{start}'
            new_filename = f'{filename}.wav'
            file = self.request_to_api(api_token, file_info.file_path, 5)
            if file == False:
                return file

            with open(f'{self.TEMP_FILE_DIR}{filename}', 'wb') as file_object:
                file_object.write(file.content)

            if self.convert_to_mp3(filename, new_filename) != 0:
                return False

            with open(f'{self.TEMP_FILE_DIR}{new_filename}', "rb") as open_file:
                transcript = openai.Audio.transcribe("whisper-1", open_file)
            os.remove(f'{self.TEMP_FILE_DIR}{new_filename}')

            self.bot.reply_to(message, transcript['text'])
            self.request_count += 1
            self.last_request_time = time.time()

    def convert_to_mp3(self, input_file, output_file):
        res = os.system(f"ffmpeg -y -i {self.TEMP_FILE_DIR}{input_file} {self.TEMP_FILE_DIR}{output_file} 2>/dev/null")
        if res != 0:
            print(f"ERROR: ffmpeg exited with code [{res}]. \n Input file: {input_file} \n Output file {output_file}")
        os.remove(f'{self.TEMP_FILE_DIR}{input_file}')
        return res

    def run_bot(self):
        '''launch a bot'''
        self.bot.polling(none_stop=True)

    def request_to_api(self, token, file_path, count=5):
        for _ in range(0, count):
            file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(token, file_path))
            if file.status_code == 200:
                return file
            time.sleep(0.2)
        return False


if __name__ == '__main__':
    API_token = '6106303194:AAExMxe7GqUM1IdDE25PAU6SdTSagF4o3K4'
    openai.api_key = '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'

    bot = VoiceToTextBot(API_token, openai.api_key)
    bot.run_bot()


