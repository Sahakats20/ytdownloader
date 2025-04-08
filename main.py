from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
import threading
import os
from pytube import Playlist, YouTube, exceptions
from android.storage import primary_external_storage_path
from android.permissions import request_permissions, Permission
from android import api_version

Builder.load_string('''
<DownloadScreen>:
    orientation: 'vertical'
    padding: '10dp'
    spacing: '10dp'
    
    ScrollView:
        size_hint: (1, 1)
        bar_width: '6dp'
        scroll_type: ['bars', 'content']
        
        GridLayout:
            cols: 1
            size_hint_y: None
            height: self.minimum_height
            spacing: '10dp'
            padding: '5dp'
            
            Label:
                text: 'YouTube Downloader'
                font_size: '20sp'
                size_hint_y: None
                height: '50dp'
                bold: True
                halign: 'center'
                color: 0.2, 0.6, 1, 1
                
            Label:
                text: 'Ссылка на плейлист:'
                size_hint_y: None
                height: '30dp'
                color: 0.9, 0.9, 0.9, 1
                
            TextInput:
                id: url_input
                multiline: False
                size_hint_y: None
                height: '50dp'
                hint_text: 'https://www.youtube.com/playlist?list=...'
                background_color: 0.1, 0.1, 0.1, 1
                foreground_color: 1, 1, 1, 1
                cursor_color: 0.2, 0.6, 1, 1
                
            Label:
                text: 'Папка для сохранения:'
                size_hint_y: None
                height: '30dp'
                color: 0.9, 0.9, 0.9, 1
                
            BoxLayout:
                size_hint_y: None
                height: '50dp'
                spacing: '5dp'
                
                TextInput:
                    id: path_input
                    multiline: False
                    readonly: True
                    background_color: 0.1, 0.1, 0.1, 1
                    foreground_color: 1, 1, 1, 1
                    
                Button:
                    text: 'Выбрать'
                    size_hint_x: 0.3
                    background_color: 0.2, 0.6, 1, 1
                    on_press: root.choose_folder()
                    
            Label:
                text: 'Текущий статус:'
                size_hint_y: None
                height: '30dp'
                color: 0.9, 0.9, 0.9, 1
                
            Label:
                text: root.status_text
                size_hint_y: None
                height: '40dp'
                text_size: self.width, None
                color: 0.9, 0.9, 0.9, 1
                
            ProgressBar:
                value: root.progress_value
                max: 100
                size_hint_y: None
                height: '30dp'
                
            Label:
                text: f'Загружено: {root.success_count} | Ошибок: {root.error_count}'
                size_hint_y: None
                height: '30dp'
                color: 0.9, 0.9, 0.9, 1
                
            BoxLayout:
                size_hint_y: None
                height: '60dp'
                spacing: '10dp'
                
                Button:
                    id: download_btn
                    text: 'Загрузить'
                    disabled: False
                    background_color: 0.2, 0.8, 0.2, 1
                    on_press: root.start_download()
                    
                Button:
                    id: stop_btn
                    text: 'Остановить'
                    disabled: True
                    background_color: 0.8, 0.2, 0.2, 1
                    on_press: root.stop_download()
                    
            ScrollView:
                size_hint_y: None
                height: '200dp'
                bar_width: '6dp'
                
                Label:
                    id: log_label
                    text: root.log_text
                    size_hint_y: None
                    height: max(self.texture_size[1], self.parent.height)
                    text_size: self.width, None
                    halign: 'left'
                    valign: 'top'
                    color: 0.8, 0.8, 0.8, 1
                    font_size: '12sp'
''')

class DownloadScreen(BoxLayout):
    status_text = StringProperty("Ожидание начала загрузки...")
    progress_value = NumericProperty(0)
    success_count = NumericProperty(0)
    error_count = NumericProperty(0)
    log_text = StringProperty("")
    is_downloading = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.download_thread = None
        self.stop_flag = False
        self.current_video = None
        
        # Определение пути для сохранения
        if api_version >= 30:
            self.download_path = os.path.join(
                primary_external_storage_path(), 
                "Download", 
                "YTDownloads"
            )
        else:
            self.download_path = os.path.join(
                primary_external_storage_path(), 
                "YTDownloads"
            )
            
        # Запрос разрешений
        request_permissions([
            Permission.INTERNET,
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE
        ])
        
        self.ids.path_input.text = self.download_path
        
    def choose_folder(self):
        self.log_message(f"Текущая папка: {self.download_path}")
        
    def log_message(self, message):
        self.log_text += f"{message}\n"
        Clock.schedule_once(lambda dt: self.ids.log_label.parent.scroll_to(
            self.ids.log_label.get_last_line_pos()
        ))
        
    def update_progress(self, percent):
        self.progress_value = percent
        
    def start_download(self):
        if self.is_downloading:
            return
            
        playlist_url = self.ids.url_input.text.strip()
        if not playlist_url:
            self.show_error("Введите ссылку на плейлист!")
            return
            
        if not playlist_url.startswith(('http://', 'https://')):
            self.show_error("Неверный формат ссылки!")
            return
            
        self._reset_state()
        self._start_download_thread(playlist_url)
        
    def _reset_state(self):
        self.is_downloading = True
        self.stop_flag = False
        self.success_count = 0
        self.error_count = 0
        self.log_text = ""
        self.progress_value = 0
        self.status_text = "Подготовка..."
        self.ids.download_btn.disabled = True
        self.ids.stop_btn.disabled = False
        
    def _start_download_thread(self, playlist_url):
        self.download_thread = threading.Thread(
            target=self.download_playlist,
            args=(playlist_url,)
        )
        self.download_thread.start()
        
    def stop_download(self):
        if self.is_downloading:
            self.stop_flag = True
            self.is_downloading = False
            self.status_text = "Остановка..."
            self.log_message("Загрузка остановлена")
            self.ids.download_btn.disabled = False
            self.ids.stop_btn.disabled = True
            
    def download_playlist(self, playlist_url):
        try:
            self._prepare_directory()
            playlist = Playlist(playlist_url)
            videos = playlist.videos[:50]  # Лимит 50 видео
            
            total = len(videos)
            self.log_message(f"Найдено видео: {total}")
            
            for idx, video in enumerate(videos):
                if self.stop_flag:
                    break
                
                self.current_video = video
                self._update_video_status(idx, total)
                
                try:
                    stream = self._get_best_stream(video)
                    if not stream:
                        raise Exception("Нет подходящего потока")
                        
                    self._download_stream(stream)
                    self._handle_success(video.title)
                    
                except Exception as e:
                    self._handle_error(video.title, str(e))
                
                self._update_progress(idx, total)
                
        except exceptions.RegexMatchError:
            self.show_error("Неверная ссылка на плейлист!")
        except Exception as e:
            self.log_message(f"Ошибка: {str(e)}")
        finally:
            self._finish_download()
            
    def _prepare_directory(self):
        if not os.path.exists(self.download_path):
            os.makedirs(self.download_path)
            self.log_message(f"Создана папка: {self.download_path}")
            
    def _get_best_stream(self, video):
        return video.streams.filter(
            progressive=True,
            file_extension='mp4'
        ).order_by('resolution').desc().first()
        
    def _download_stream(self, stream):
        stream.download(output_path=self.download_path)
        
    def _update_video_status(self, idx, total):
        Clock.schedule_once(lambda dt: setattr(
            self, 'status_text',
            f"Загрузка {idx+1}/{total}\n{self.current_video.title[:30]}..."
        ))
        
    def _handle_success(self, title):
        Clock.schedule_once(lambda dt: setattr(
            self, 'success_count', self.success_count + 1
        ))
        self.log_message(f"Успешно: {title[:40]}")
        
    def _handle_error(self, title, error):
        Clock.schedule_once(lambda dt: setattr(
            self, 'error_count', self.error_count + 1
        ))
        self.log_message(f"Ошибка: {title[:40]} - {error}")
        
    def _update_progress(self, idx, total):
        progress = ((idx + 1) / total) * 100
        Clock.schedule_once(lambda dt: self.update_progress(progress))
        
    def _finish_download(self):
        self.is_downloading = False
        Clock.schedule_once(lambda dt: setattr(
            self.ids.download_btn, 'disabled', False
        ))
        Clock.schedule_once(lambda dt: setattr(
            self.ids.stop_btn, 'disabled', True
        ))
        
        status = "Остановлено" if self.stop_flag else "Завершено"
        self.status_text = f"{status}! Успешно: {self.success_count}, Ошибок: {self.error_count}"
        
    def show_error(self, message):
        content = BoxLayout(orientation='vertical', spacing='10dp', padding='10dp')
        content.add_widget(Label(text=message, color=(1, 1, 1, 1)))
        btn = Button(text='OK', size_hint_y=None, height='50dp', background_color=(0.2, 0.6, 1, 1))
        content.add_widget(btn)
        
        popup = Popup(
            title='Ошибка',
            content=content,
            size_hint=(0.8, 0.4),
            background_color=(0.1, 0.1, 0.1, 1)
        )
        btn.bind(on_press=popup.dismiss)
        popup.open()

class YTDownloaderApp(App):
    def build(self):
        self.title = 'YouTube Downloader'
        return DownloadScreen()

if __name__ == '__main__':
    YTDownloaderApp().run()
