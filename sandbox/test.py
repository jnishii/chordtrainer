from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty, StringProperty
)
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.app import App, Widget
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse

from matplotlib import cm
import matplotlib.pyplot as plt
import numpy as np
import random as rnd
import time
import pygame.midi as m
import warnings
warnings.simplefilter('ignore')

class LabelWidget(Widget):
    i=NumericProperty(0)
    text=StringProperty("test")

    def update(self):
        self.text=str(self.i)
        self.i+=1

class TestWidget(Widget):
    test_label=ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        Widget.__init__(self, *args, **kwargs)
        Window.size = (500, 500)
        self.center = (50, 50)  # Widget内の位置は%で指定

    def update(self,dt):
        #self.canvas.clear
        Ellipse(pos=(250,250), size=(50,50))
        self.test_label.update()



class TestApp(App):
    def build(self):
        test=TestWidget()
        Clock.schedule_interval(test.update, 1)

        return test

if __name__ == '__main__':
    # Run below if you want Visual info
    TestApp().run()

    # If you don't need visual info, run below.
    # play_chords=playChords(chords=chords)
    # play_chords.main()

    exit()
