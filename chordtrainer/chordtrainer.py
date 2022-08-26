from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty
)
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.graphics import Color, Ellipse
from kivy.app import App, Widget
from kivy.clock import Clock
from matplotlib import cm
import matplotlib.pyplot as plt
import numpy as np
import random as rnd
import time
import pygame.midi as m
from turtle import position
import warnings
warnings.simplefilter('ignore')


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
notes27= [m7,mj7, m3, p5, p4]
notes3 = [major, minor, aug, dim]
notes4 = [m7th, d7th]

chords = [major, minor]
chords = notes27
#chords=[major, d7th]


class playChords():
    def __init__(self, print_root=True) -> None:

        self.print_root = print_root
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

    def chord_on(self, chord, root=0, vel=60):
        for n in chord:
            vel_n=vel
            if n == chord[0]:
                 vel_n+= 30
            if n == chord[-1]:
                 vel_n += 20
            vel_n += rnd.randint(-15, 15)

            if  vel_n > 127: vel_n = 127 
            if  vel_n < 0:   vel_n = 0

            self.midiout.note_on(root + n,  vel_n)

    def chord_off(self, chord, root=0):
        for n in chord:
            self.midiout.note_off(root + n)

    def select_chord(self):
        # 110Hz: 45 (MIDI note)
        # 220Hz: 57
        # 440Hz: 69
        # 880Hz: 81
        # 48(C)から72(C)の間の24音からランダムに選んでベース音にする
        root = rnd.randint(48, 72)
        chord_id = rnd.randint(0, len(chords)-1)
        if self.print_root:
            chord_name = "{}{}".format(
                midi_name[root], names[chords[chord_id]])
        else:
            chord_name = "{1}/{0}".format(
                midi_name[root], names[chords[chord_id]])

        return(chord_id, root, chord_name)

    def main(self):
        duration = 3

        chord, root, chord_name = self.select_chord()
        for i in range(20):
            self.chord_on(chords[chord], root=root)
            time.sleep(duration)
            self.chord_off(chords[chord], root=root)

        self.midiout.close()
        m.quit()


class lightLabel(Label):
    def __init__(self, *args, **kws):
        Label.__init__(self, *args, **kws)


class ChordWidget(Widget):
    evn = None

    def __init__(self, *args, **kwargs):
        Widget.__init__(self, *args, **kwargs)

        print_root = False if len(chords[0]) == 2 else True
        self.play_chords = playChords(print_root=print_root)

        self.duration = 3  # duration of each chord
        self.t = 0  # time from new chord appearance
        self.dt = 0.01  # dt of animation update
        n_step = self.duration/self.dt

        # object size parameters
        self.init_l = 0  # positional range of circles
        self.init_r = 0  # circle radius
        self.init_fontsize = 60  # text size
        self.init_alpha = 0  # circle transparancy

        lmax=500
        rmax=80
        self.dl = lmax/n_step
        self.dr = rmax/n_step
        #self.dfontsize = 70/n_step
        self.dfontsize = 0
        self.dalpha = 1.2/n_step

        self.l = self.init_l
        self.r = self.init_r
        self.fontsize = self.init_fontsize
        self.alpha = self.init_alpha

        Window.size = (500, 500)
        self.center = [50, 50] # Widget内の位置は%で指定

        self.evn = Clock.schedule_interval(self.update, self.dt)

    def update_circle(self, chord_id, chord_name):
        #self.ellipse_size = [self.r*2, self.r*2]
        #self.ellipse_pos = self.center-self.r
        rgb = plt.cm.Accent(chord_id)  # get rgb of Pastel1

        chord_vec = np.array(chords[chord_id], dtype=np.float64)
        chord_vec -= np.mean(chord_vec)
        chord_vec /= 6  # normalized to [-1,1]

        pos = np.empty((len(chord_vec), 2))
        for i in range(len(chord_vec)):
            pos[i] = [self.center[0], 
                self.l*chord_vec[i] + self.center[1]] - np.array([self.r/2, self.r/2])

        label_width = 100
        self.canvas.clear()
        with self.canvas:
            Color(rgb=rgb)
            #Ellipse(pos=self.ellipse_pos, size=self.ellipse_size)
            for i in range(len(chord_vec)):
                Ellipse(pos=pos[i], size=(self.r, self.r))

            #L=np.array([pos[-1][1],pos[-1][1]])-self.center
            #Ellipse(pos=self.center-L[0], size=L*2, fill=None)

            Label(pos=[self.center[0]-label_width/2, 22], 
                text=chord_name, font_size=str(int(self.fontsize)), 
                markup=True, halign="center", size_hint_x=None, width= label_width, 
                color=[1, 1, 1, self.alpha]
                )

        self.r += self.dr
        self.l += self.dl
        self.fontsize += self.dfontsize
        self.alpha += self.dalpha

    def update(self, dt):

        if self.t == 0:
            self.chord_id, self.root, self.chord_name = self.play_chords.select_chord()
            self.play_chords.chord_on(chords[self.chord_id], root=self.root)
            self.l = self.init_l
            self.r = self.init_r
            self.fontsize = self.init_fontsize
            self.alpha = self.init_alpha

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
