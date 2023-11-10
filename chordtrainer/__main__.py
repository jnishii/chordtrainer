from .chords import *

from matplotlib import pyplot as plt
from kivy.properties import (
    NumericProperty, StringProperty, ObjectProperty
)
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.graphics import Color, Ellipse
from kivy.app import App, Widget
from kivy.clock import Clock

chords = note3_basic
chords = note3_var
chords = notes4
#chords = [minor7th]

#chords = [dominant7th, major7th]
#chords = notes4 + [aug, dim, m7, mj7]
#chords = notes22
#chords = [major, minor]
#chords =notes2
#chords=notes26 + notes27

chords = p_56451

Window.size = (500, 500)

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
        print("args",*args, **kwargs)
        self._keyboard = Window.request_keyboard(self.keyboard_closed, self)
        self._keyboard.bind(on_key_down=self.on_keyboard_down)

        self.chords = chords  # Todo: chords should be given by an arg or menu

        print_root = True
        if type(chords) is list:
            self.mode = "chord"
            self.interval = 6  # interval between chords
            if len(self.chords[0]) == 2:
                print_root = False
        else:
            self.mode = "progression"
            self.interval = 2  # interval between chords
        
        #####
        self.play_chords = playChords(
            chords=chords, print_root=print_root, delay=0.1)

        self.t = 0  # time from new chord appearance
        self.dt = 0.01  # dt of animation update
        n_step = self.interval/self.dt  # total time step per chord

        self.chord_label.initialize(n_step)

        # object size parameters
        self.init_l = 0  # positional range of circles
        self.init_r = 0  # circle radius
        self.lmax = 500
        self.rmax = 80

        self.reset_canvas()

        self.dl = self.lmax/n_step
        self.dr = self.rmax/n_step

        self.event = Clock.schedule_interval(self.update, self.dt)

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
                self.play_chords.close()
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
                self.play_chords.chord_on(self.notes, root=self.root)
        return True

    def on_touch_down(self, position):
        self.pause_schedule()

        return True

    def update_canvas(self, notes):
        # https://matplotlib.org/stable/tutorials/colors/colormaps.html
        #   self.rgb = plt.cm.Pastel1(self.chord) # get rgb of Pastel1
        if notes in chords:
            rgb = plt.cm.Accent(self.chords.index(notes))  # get rgb of Accent
        else:
            rgb = plt.cm.Accent(note3_all.index(compress_chord(notes)))
  
        # print(rgb)

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
        if self.t == 0:
            if self.mode == "chord":
                self.notes, self.root, chord_name = self.play_chords.select_chord()
                if len(self.notes) == 4 and Transpose == True:
                    if (Random and rnd.randint(0, 2) == 0) or not Random:
                        self.notes = self.transpose7th(self.notes)

            else:
                self.notes, self.root, chord_name, terminal = self.play_chords.select_progression()

            self.play_chords.chord_on(self.notes, root=self.root)
            self.reset_canvas()
            self.chord_label.reset(chordname=chord_name)
            print(re.sub('\[[a-zA-Z0-9=/]*\]|\.','', chord_name))

        self.update_canvas(self.notes)
        self.chord_label.update()

        self.t += dt
        if self.t > self.interval:
            self.t = 0
            self.play_chords.chord_off(
                self.notes, root=self.root)


class ChordApp(App):
    def build(self):
        chord = ChordWidget()
        #Clock.schedule_interval(chord.update, chord.dt)
        return chord

def main():
    # Run below if you want Visual info
    ChordApp().run()

    # If you don't need visual info, run below.
    # play_chords=playChords(chords=chords)
    # play_chords.main()

if __name__ == '__main__':
    main()
