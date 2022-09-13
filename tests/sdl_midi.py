from kivy.app import App
from kivy.core.audio import SoundLoader
from kivy.uix.button import Button

class play_btn(Button):
    def __init__(self, **kwargs):
        super(Button, self).__init__(**kwargs)
        self.sound = SoundLoader.load('test.mid')

    def on_release(self):
        self.sound.play()
        return True

class myApp(App):
    def build(self):
        return play_btn()

myApp().run()