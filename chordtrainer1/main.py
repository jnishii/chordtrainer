from kivy.properties import (
    NumericProperty, StringProperty, ObjectProperty
)
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.graphics import Color, Ellipse
from kivy.app import App, Widget
from kivy.clock import Clock
#from matplotlib import cm
import matplotlib.pyplot as plt
import numpy as np
import random as rnd
import time
import pygame.midi as m
import warnings
warnings.simplefilter('ignore')


midi_notes = range(132)
# note_name=["C","C[sup]#[/sup]","D","D[sup]#[/sup]","E","F","F[sup]#[/sup]","G","G[sup]#[/sup]","A","A[sup]#[/sup]","B"]*11
note_names = ["C", "C#", "D", "D#", "E",
              "F", "F#", "G", "G#", "A", "A#", "B"]*11
midi_names = dict(zip(midi_notes, note_names))
print(midi_names[10])

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
sus4 = (0, 5, 7)
names3 = {
    major: "", minor: "[sub]m[/sub]", aug: "[sup]-5[/sup]", dim: "[sub]dim[/sub]", sus4: "[sub]sus4[/sub]",
}

# 4 notes
mj7th = (0, 4, 7, 11)
d7th = (0, 4, 7, 10)
m7th = (0, 3, 7, 10)
dim7th = (0, 3, 6, 9)
names4 = {
    mj7th: "[sub]M7[/sub]", d7th: "[sub]7[/sub]",  m7th: "[sub]m7[/sub]",  dim7th: "[sub]dim7[/sub]"
}

#

names = names2 | names3 | names4

notes2 = [m2, mj2, m3, mj3, p4, tritone, p5, m6, mj6, m7, mj7]
notes22 = [m2, mj2]
notes27 = [m7, mj7]
notes3 = [major, minor, aug, dim, sus4]
notes4 = [mj7th, d7th]

chords = notes4
chords = [mj7th]
#chords = [d7th, mj7th]
#chords = notes4 + [aug, dim, m7, mj7]
#chords = notes22
#chords = [major, minor]
#chords =notes2

Window.size = (500, 500)

class playChords():
    def __init__(self, chords, print_root=True, note_range=[57, 81], arpeggio=False, delay=0.01) -> None:

        self.chords = chords
        self.print_root = print_root
        self.arpeggio = False
        self.delay = delay  # delay between notes for arpeggio

        # 110Hz: 45 (MIDI note)
        # 220Hz: 57
         # 440Hz: 69
        # 880Hz: 81
        self.note_range = note_range  # range of root note

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

    def chord_on(self, chord, root=0, vel=60, force_arpeggio=None):
        for n in chord:
            vel_n = vel
            if (force_arpeggio == None and self.arpeggio) or (force_arpeggio or self.arpeggio):
                time.sleep(self.delay)
            if n == chord[0]:
                vel_n = vel_n+35 if chord[-1]-chord[0]<12 else vel_n + 10
            if n == chord[-1]:
                vel_n += 20
            vel_n += rnd.randint(-15, 15)

            if vel_n > 127:
                vel_n = 127
            if vel_n < 0:
                vel_n = 0

            self.midiout.note_on(root + n,  vel_n)

    def chord_off(self, chord, root=0):
        for n in chord:
            self.midiout.note_off(root + n)

    def select_chord(self):
        root = rnd.randint(self.note_range[0], self.note_range[1])

        chord_id = rnd.randint(0, len(self.chords)-1)
        if len(self.chords[chord_id]) > 2:
            chord_name = "{}{}".format(
                midi_names[root], names[self.chords[chord_id]])
        else:
            chord_name = "{1}/{0}".format(
                midi_names[root], names[self.chords[chord_id]])

        return(chord_id, root, chord_name)

    def close(self):
        self.midiout.close()
        m.quit()

    def main(self):
        """
        Call this function for sound training without visual information.
        """
        duration = 3

        Transpose=True
        Random=False
        for i in range(20):
            chord, root, chord_name = self.select_chord()
            print(chord_name)
            notes=self.chords[chord]
            print(len(notes))
            if len(notes)==4 and Transpose:
                if (Random and rnd.randint(0,2)==0) or not Random:
                    notes=[notes[0]-24, notes[3]-12, notes[1], notes[2]]
                    print("transposed")

            self.chord_on(notes, root=root)
            time.sleep(duration)
            self.chord_off(notes, root=root)

        self.midiout.close()
        m.quit()


class LabelWidget(Widget):
    alpha = NumericProperty(1)
    fontsize = NumericProperty(60)
    chordname = StringProperty("Start!")

    def initialize(self, n_step):
        self.init_fontsize = 60  # text size
        self.init_alpha = 0  # transparancy
        self.dfontsize = 0
        self.dalpha = 1.2/n_step

        self.reset()

    def reset(self, chordname=""):
        #self.fontsize = self.init_fontsize
        self.alpha = self.init_alpha
        self.chordname = chordname

    def update(self):
        #self.fontsize += self.dfontsize
        self.alpha += self.dalpha

class ChordWidget(Widget):
    chord_label = ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        Widget.__init__(self, *args, **kwargs)
        self._keyboard = Window.request_keyboard(self.keyboard_closed, self)
        self._keyboard.bind(on_key_down=self.on_keyboard_down)

        self.chords = chords  # Todo: chords should be given by an arg or menu
        print_root = False if len(self.chords[0]) == 2 else True
        self.play_chords = playChords(
            chords=chords, print_root=print_root, delay=0.1)

        self.duration = 5  # duration of each chord
        self.t = 0  # time from new chord appearance
        self.dt = 0.01  # dt of animation update
        n_step = self.duration/self.dt  # total time step per chord

        self.chord_label.initialize(n_step)

        # object size parameters
        self.init_l = 0  # positional range of circles
        self.init_r = 0  # circle radius
        self.lmax = 500
        self.rmax = 80

        self.reset_canvas()

        self.dl = self.lmax/n_step
        self.dr = self.rmax/n_step

        self.event=Clock.schedule_interval(self.update, self.dt)
        
        self.flag_event = True
        print("initialize done!")

    def reset_canvas(self):
        self.l = self.init_l
        self.r = self.init_r      
            
    def pause_schedule(self):
        if self.flag_event == True:
            Clock.unschedule(self.event)
            self.flag_event = False
        else:
            self.event = Clock.schedule_interval(self.update, self.dt)
            self.flag_event = True
        return True

    def keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self.on_keyboard_down)
        self._keyboard = None

    def on_keyboard_down(self, keyboard, keycode, text, modifiers):
        print("keycode:", keyboard, keycode, text, modifiers)
        match keycode[1]:
            case 'spacebar':
                self.pause_schedule()
                return True
            case 'a':
                self.play_chords.chord_on(
                    self.notes, root=self.root, force_arpeggio=True)
            case 'h':
                self.play_chords.chord_on(
                    self.notes, root=self.root, force_arpeggio=False)
            case 'q' | 'escape':
                self.play_chords.chord_off(self.notes, root=self.root)
                self.play_chords.midiout.close()
                quit()
            case 't':
                self.play_chords.arpeggio = not self.play_chords.arpeggio
            case 'up':
                self.play_chords.delay += 0.01
                print(self.play_chords.delay)
            case 'down' | '-':
                self.play_chords.delay -= 0.01
                if self.play_chords.delay < 0:
                    self.play_chords.delay = 0
                print(self.play_chords.delay)
            case _:
                self.play_chords.chord_on(
                    self.chords[self.chord_id], root=self.root)
        return True

    def on_touch_down(self, position):
        self.pause_schedule()

        return True

    def update_canvas(self, notes, chord_id):
        # https://matplotlib.org/stable/tutorials/colors/colormaps.html
        #   self.rgb = plt.cm.Pastel1(self.chord) # get rgb of Pastel1        
        rgb = plt.cm.Accent(chord_id)  # get rgb of Accent
        #print(rgb)

        chord_vec = np.array(notes, dtype=np.float64)
        chord_vec -= np.mean(chord_vec)
        chord_vec /= 6  # normalized to [-1,1]

        self.center = (500, 500)  # Widget内の位置は%で指定
        pos = np.empty((len(chord_vec), 2))
        for i in range(len(chord_vec)):
            pos[i] = [self.center[0],
                      self.l*chord_vec[i] + self.center[1]] - np.array([self.r/2, self.r/2])

        # if you canvas.clear below, Label disappears!
        self.canvas.before.clear()
        with self.canvas.before:
            Color(rgb=rgb)
            for i in range(len(chord_vec)):
                Ellipse(pos=pos[i], size=(self.r, self.r))

        self.r += self.dr
        self.l += self.dl

    def transpose7th(self, notes):
        return notes[0]-24,  notes[3]-12, notes[1], notes[2]        

    def update(self, dt):
        Transpose=True
        Random=False
        if self.t == 0:
            self.chord_id, self.root, self.chord_name = self.play_chords.select_chord()

            self.notes=self.chords[self.chord_id]
            if len(self.notes)==4 and Transpose==True:
                if (Random and rnd.randint(0,2)==0) or not Random:
                    self.notes = self.transpose7th(self.notes)

            self.play_chords.chord_on(self.notes, root=self.root)
            self.reset_canvas()
            self.chord_label.reset(chordname=self.chord_name)

        self.update_canvas(self.notes, self.chord_id)
        self.chord_label.update()

        self.t += dt
        if self.t > self.duration:
            self.t = 0
            self.play_chords.chord_off(
                 self.notes, root=self.root)


class ChordApp(App):
    def build(self):
        chord = ChordWidget()
        #Clock.schedule_interval(chord.update, chord.dt)
        return chord


if __name__ == '__main__':
    # Run below if you want Visual info
    ChordApp().run()

    # If you don't need visual info, run below.
    # play_chords=playChords(chords=chords)
    # play_chords.main()

    exit()
