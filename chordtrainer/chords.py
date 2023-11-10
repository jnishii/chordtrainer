import numpy as np
import re
import random as rnd
import re
import time
import mido
# import pygame.midi as m
import warnings
warnings.simplefilter('ignore')

flat="[size=90][sup]\u266d[/sup][/size][size=0].[/size]"
sharp="[size=90][sup]\u266f[/sup][/size][size=0].[/size]"

midi_notes = range(132)

# note_name=["C","C[sup]#[/sup]","D","D[sup]#[/sup]","E","F","F[sup]#[/sup]","G","G[sup]#[/sup]","A","A[sup]#[/sup]","B"]*11

note_names = ["C", "C"+sharp, "D", "E"+flat, "E",
              "F", "F"+sharp, "G", "A"+flat, "A", "B"+flat, "B"]
midi_names = dict(zip(midi_notes, note_names*11))

# 110Hz: 45 (MIDI note)
# 220Hz: 57
# 440Hz: 69
# 880Hz: 81
NOTE_RANGE=[52, 77]

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

note3_basic = [major, minor]
note3_var = [dim, aug, sus4]
note3_all = note3_basic + note3_var

# 4 notes
major7th = (0, 4, 7, 11) # base + minor
dominant7th = (0, 4, 7, 10) # base + dim
minor7th = (0, 3, 7, 10) # base + major
m7b5 = (0, 3, 6, 10) # base + minor
dim7th = (0, 3, 6, 9) # base + dim
names4 = {
    major7th: "[sub]M7[/sub]", dominant7th: "[sub]7[/sub]",  minor7th: "[sub]m7[/sub]",
    m7b5: "[sub]m7[/sub][size=0].[/size][sup]-5[/sup]", 
    #m7b5: "[sup][i]\u00D8[/i][/sup]",
    dim7th: "[sub]dim7[/sub]"
}

names = names2 | names3 | names4

notes2 = [m2, mj2, m3, mj3, p4, tritone, p5, m6, mj6, m7, mj7]
notes22 = [m2, mj2]
notes26 = [m6, mj6]
notes27 = [m7, mj7]
notes2long= notes26 + notes27
notes3 = [major, minor, aug, dim, sus4]
notes4 = [major7th, dominant7th, minor7th]

######## for chord progression
diatonic_scale_midi = {
    "major": [0, 2, 4, 5, 7, 9, 11], 
    "minor": [0, 2, 3, 5, 7, 8, 10]
    }
diatonic_chords = {
    "major": [major, minor, minor, major, major, minor, dim],
    "minor": [minor, dim, major, minor, minor, major, major],
    "harmonic_minor": [minor, dim, aug, minor, major, major, dim],
    }
degree_names = {
    "major": ["I", "ii", "iii", "IV", "V", "vi", "vii\u00B0"],
    "minor": ["i", "ii\u00B0", "III", "iv", "v", "VI", "VII"],
    "harmonic_minor": ["i", "ii\u00B0", "III+", "iv", "V", "VI", "vii\u00B0"],
    }

M1={"degree":1, "notes":(-12,4,7,12)} # C|EGC
M1_2={"degree":1, "notes":(0,4,7,12)} # |CEGC
m1_2={"degree":1, "notes":(0,3,7,12)} # |CEbGC
m2={"degree":2, "notes":(-10,2,5,9)}  # D|DFA
M4={"degree":4, "notes":(-7,5,9,12)}  # F|FAC
m4={"degree":4, "notes":(-7,5,8,12)}  # F|FAbC
M5={"degree":5, "notes":(-5,2,7,11)}  # G|DGB
m6={"degree":6, "notes":(-3,0,4,12)}  #A|CEC
M6b={"degree":6, "notes":(-4,0,3,12)}  #Ab|CEbC


p_1251 = {
    "scale" : "major",
    "progression":(M1, m2, M5, M1)
}
p_56451 = {
    "scale" : "major",
    "progression": (M5, m6, M4, M5, M1_2)
}
pm_56451 = {
    "scale" : "harmonic_minor",
    "progression": (M5, M6b, m4, M5, m1_2)
}

progression = pm_56451
# basic definition
Transpose=False
Random=False
scale = "major"

def compress_chord(chord):
    """
    Compress chord to 1 octave on the base note
    """
    chord = list(chord)
    base = min(chord)
    for i in range(len(chord)):
        chord[i] = chord[i] - base
        chord[i] = chord[i] % 12

    return tuple(set(chord))

class playChords():
    def __init__(self, chords, 
                 print_root=True, note_range=NOTE_RANGE, arpeggio=False, delay=0.01) -> None:
        """
        ARGS:
            mode: "chords" or "progression"
        """

        self.chords = chords
        self.print_root = print_root
        self.arpeggio = arpeggio
        self.delay = delay  # delay between notes for arpeggio

        self.note_range = note_range  # range of root note

        # for chord progression
        if type(chords) is list:
            self.mode = "chord"
            self.interval = 6  # interval between chords
        else:
            self.mode = "progression"
            self.interval = 1  # interval between chords
            self.n_progression = 0 # progression counter

        self.player = mido.open_output('IAC Driver pioneer')

        # m.init()            # MIDIデバイスを初期化
        # self.get_midi_devices()
        # #device_id = 2
        # device_id = 3

        # print("device_id:", device_id)
        # self.midiout = m.Output(device_id)

    def get_midi_devices(self) -> None:
        n_midi = m.get_count()  # MIDIデバイスの数
        print("# of devices: ", n_midi)
        for i in range(n_midi):
            print("{}: {}".format(i, m.get_device_info(i)))  # MIDIデバイスの情報を表示

    def note_on(self, note, vel=60, time=5):
        self.player.send(mido.Message('note_on', note=note, velocity = vel, time=time))

    def note_off(self, note, vel=60, time=5):
        self.player.send(mido.Message('note_off', note=note, velocity = vel, time=time))

    def chord_on(self, chord, root=0, vel=60, force_arpeggio=None):
        for n in chord:
            vel_n = vel
            if (force_arpeggio == None and self.arpeggio) or (force_arpeggio or self.arpeggio):
                time.sleep(self.delay)

            if n == chord[0]:
                vel_n = vel_n + 15 if chord[-1]-chord[0] < 12 else vel_n + 10
            if n == chord[0]:
                vel_n += 20
            vel_n += rnd.randint(-3, 3)

            if vel_n > 127:
                vel_n = 127
            if vel_n < 0:
                vel_n = 0

            self.note_on(root + n,  vel_n)

    def chord_off(self, chord, root=0):
        for n in chord:
            self.note_off(root + n)

    def select_chord(self):
        root = rnd.randint(self.note_range[0], self.note_range[1])

        chord_id = rnd.randint(0, len(self.chords)-1)
        notes = self.chords[chord_id]

        if len(self.chords[chord_id]) == 2:
            chord_name = "{1}/{0}".format(
                midi_names[root], names[self.chords[chord_id]])
        else:
            chord_name = "{}{}".format(
                midi_names[root], names[self.chords[chord_id]])

        return(notes, root, chord_name)

    def select_progression(self):

        terminal = False # True if the progression is finished
        # select root for new progression
        if self.n_progression == 0:
            self.root = rnd.randint(self.note_range[0], self.note_range[1])
            print("[on {}]----------".format(
                re.sub('\[[a-zA-Z0-9=/]*\]|\.','', midi_names[self.root%12])))

        scale = self.chords["scale"]
        progression = self.chords["progression"]
        chord_degree = progression[self.n_progression]["degree"] # roman numeral
        notes = progression[self.n_progression]["notes"]

        self.n_progression += 1
        if self.n_progression == len(progression):
            self.n_progression = 0
            terminal = True

        # for i in range(len(notes)):
        #     print(note_names[notes[i]%12], end=" ")

        chord_name = "{}{}, {}".format(
            midi_names[self.root + notes[0]], names[diatonic_chords[scale][chord_degree-1]], degree_names[scale][chord_degree-1])

        return(notes, self.root, chord_name, terminal)

    def close(self):
        self.player.close()

    def main(self, interval=3):
        """
        Call this function for ear training without visual information.
        """

        while True:
            try:
                if self.mode == "chord":
                    notes, root, chord_name = self.select_chord()
                    terminal = False
                    #print(notes,root,chord_name)
                    #notes = self.chords[chord]

                    if len(notes) == 4 and Transpose:
                        if (Random and rnd.randint(0, 2) == 0) or not Random:
                            notes = [notes[0]-24, notes[3]-12, notes[1], notes[2]]
                            print("transposed")

                else:
                    notes, root, chord_name, terminal = self.select_progression()

    #            print(re.sub('[.*]','',chord_name))
                print(re.sub('\[[a-zA-Z0-9=/]*\]|\.','', chord_name))


                self.chord_on(notes, root=root)
                time.sleep(interval)
                if terminal:
                    time.sleep(interval*2)
                self.chord_off(notes, root=root)
            
            except KeyboardInterrupt:
                break

        print("bye")
        self.close()

