from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty
)
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.graphics import Color, Ellipse
from kivy.app import App, Widget
from kivy.clock import Clock
from kivy.core.window import Window
from matplotlib import cm
import matplotlib.pyplot as plt
import numpy as np
import random as rnd
import time
import pygame.midi as m
import warnings
warnings.simplefilter('ignore')

class LabelWidget(Widget):
    pass

class TestWidget(Widget):
    test_label=ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        Widget.__init__(self, *args, **kwargs)
        Window.size = (500, 500)
        self.center = (50, 50)  # Widget内の位置は%で指定


class TestApp(App):
    def build(self):
        test=TestWidget()
        return test


if __name__ == '__main__':
    # Run below if you want Visual info
    TestApp().run()

    # If you don't need visual info, run below.
    # play_chords=playChords(chords=chords)
    # play_chords.main()

    exit()
