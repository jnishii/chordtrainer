from turtle import position
import warnings
warnings.simplefilter('ignore')
import pygame.midi as m
import time
import random as rnd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm


from kivy.clock import Clock
from kivy.app import App, Widget
from kivy.graphics import Color, Ellipse
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.config import Config
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty
)

midi_note = range(132)
# note_name=["C","C[sup]#[/sup]","D","D[sup]#[/sup]","E","F","F[sup]#[/sup]","G","G[sup]#[/sup]","A","A[sup]#[/sup]","B"]*11
note_name = ["C", "C#", "D", "D#", "E",
             "F", "F#", "G", "G#", "A", "A#", "B"]*11
midi_name = dict(zip(midi_note, note_name))
print(midi_name[10])

# 2 notes
m2 = (0, 1)
mj2 = (0, 2)
m3 = (0, 3)
mj3 = (0, 4)
p4 = (0, 5)
tritone = (0, 6)
p5 = (0, 7)
m6 = (0, 8)
mj6 = (0, 9)
m7 = (0, 10)
mj7 = (0, 11)

names2 = {
    m2: "minor 2nd",
    mj2: "major 2nd",
    m3: "minor 3rd",
    mj3: "major 3rd",
    p4: "perfect 4th",
    tritone: "tritone",
    p5: "perfect 5th",
    m6: "minor 6th",
    mj6: "major 6th",
    m7: "minor 7th",
    mj7: "major 7th",
}


# 3 notes
major = (0, 4, 7)
minor = (0, 3, 7)
aug = (0, 4, 8)
dim = (0, 3, 6)
names3 = {
    major: "", minor: "[sub]m[/sub]", aug: "[sup]-5[/sup]", dim: "[sub]dim[/sub]"
}
# 4 notes
m7th = (0, 4, 7, 11)
d7th = (0, 4, 7, 10)

names4 = {
    m7th: "[sub]M7[/sub]", d7th: "[sub]7[/sub]"
}

names = names2 | names3 | names4

notes2 = [m2, mj2, m3, mj3, p4, tritone, p5, m6, mj6, m7, mj7]
notes3 = [major, minor, aug, dim]
notes4 = [m7th, d7th]

chords = [major, minor]
chords = notes2


class playChords():
    def __init__(self, print_root=True) -> None:

        self.print_root=print_root
        m.init()            # MIDIデバイスを初期化
        self.get_midi_devices()
        device_id = 2
        print("device_id:", device_id)
        self.midiout = m.Output(device_id)

    def get_midi_devices(self):
        n_midi = m.get_count()  # MIDIデバイスの数
        print("# of devices: ", n_midi)
        for i in range(n_midi):
            print(m.get_device_info(i))  # MIDIデバイスの情報を表示

    def chord_on(self, chord, root=0, vel=80):
        for n in chord:
            self.midiout.note_on(root + n, vel)

    def chord_off(self, chord, root=0):
        for n in chord:
            self.midiout.note_off(root + n)

    def select_chord(self):
        # 220Hz: 57 (MIDI note)
        # 440Hz: 69
        # 880Hz: 81
        # 57から81の間の24音からランダムに選んでベース音にする
        root = rnd.randint(57, 81)
        chord_id = rnd.randint(0, len(chords)-1)
        if self.print_root:
           chord_name = "{}{}".format(midi_name[root], names[chords[chord_id]])
        else:
           chord_name = names[chords[chord_id]]


        return(chord_id, root, chord_name)

    def main(self):
        duration = 0.5

        chord, root, chord_name = self.select_chord()
        for i in range(20):
            self.chord_on(chords[chord], root=root)
            time.sleep(duration)
            self.chord_off(chords[chord], root=root)

        self.midiout.close()
        m.quit()


class ChordWidget(Widget):
    evn = None

    def __init__(self, *args, **kwargs):
        Widget.__init__(self, *args, **kwargs)

        print_root=False if len(chords[0])==2 else True
        self.play_chords = playChords(print_root=print_root)

        self.duration = 2.0  # duration of each chord
        self.t = 0
        self.dt = 0.01  # dt of animation update
        n_step = self.duration/self.dt
        self.dl = 500/n_step # positional range of circles
        self.dr = 80/n_step # circle radius
        self.init_l = 0
        self.init_r = 0
        self.l = self.init_l
        self.r = self.init_r

        Window.size = (500, 500)
        self.center = [50, 50]

        self.evn = Clock.schedule_interval(self.update, self.dt)

    def update_circle(self, chord_id, chord_name):
        #self.ellipse_size = [self.r*2, self.r*2]
        #self.ellipse_pos = self.center-self.r
        rgb = plt.cm.Accent(chord_id)  # get rgb of Pastel1

        chord_vec=np.array(chords[chord_id], dtype=np.float64)
        chord_vec-=np.mean(chord_vec)
        chord_vec/=6 # normalized to [-1,1]
 
        pos=np.empty((len(chord_vec),2))
        for i in range(len(chord_vec)):
            pos[i] = [self.center[0], self.l*chord_vec[i]+self.center[1]]
            
       
        self.canvas.clear()
        with self.canvas:
            Color(rgb=rgb)
            #Ellipse(pos=self.ellipse_pos, size=self.ellipse_size)
            for i in range(len(chord_vec)):
                Ellipse(pos=pos[i].tolist(), size=(self.r,self.r))
            
            Label(pos=[self.center[0], 20], 
                    text=chord_name,
                  font_size='50sp', markup=True)

        self.r += self.dr
        self.l += self.dl

    def update(self, dt):

        if self.t == 0:
            self.chord_id, self.root, self.chord_name = self.play_chords.select_chord()
            self.play_chords.chord_on(chords[self.chord_id], root=self.root)
            self.l = self.init_l
            self.r = self.init_r

        # https://matplotlib.org/stable/tutorials/colors/colormaps.html
        #   self.rgb = plt.cm.Pastel1(self.chord) # get rgb of Pastel1

        self.update_circle(self.chord_id, self.chord_name)

        self.t += dt
        if(self.t > self.duration):
            self.t = 0

        if self.t == 0:
            self.play_chords.chord_off(chords[self.chord_id], root=self.root)


class ChordApp(App):
    def build(self):
        return ChordWidget()


ChordApp().run()

# play_chords=playChords()
# play_chords.main()


exit()
