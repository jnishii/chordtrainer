import numpy as np
import re
import random as rnd
import re
import time
import pygame.midi as m
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

note3_basic = [major, minor, dim]
note3_var = [dim, aug, sus4]

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

# for chord progression
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

p_1251 = [1,2,5,1] # roman numeral

# basic definition
Transpose=False
Random=False
scale = "major"
chords = p_1251

class playChords():
    def __init__(self, chords, progression=[1,2,5,1], scale="major", mode="chords", 
                 print_root=True, note_range=NOTE_RANGE, arpeggio=False, delay=0.01) -> None:
        """
        ARGS:
            mode: "chords" or "progression"
        """

        self.chords = chords
        self.print_root = print_root
        self.arpeggio = False
        self.delay = delay  # delay between notes for arpeggio

        self.note_range = note_range  # range of root note

        # for chord progression
        self.scale = scale
        self.progression = progression
        self.mode = mode
        self.n_progression = 0 # progression counter

        m.init()            # MIDIデバイスを初期化
        self.get_midi_devices()
        #device_id = 2
        device_id = 3

        print("device_id:", device_id)
        self.midiout = m.Output(device_id)

    def get_midi_devices(self) -> None:
        n_midi = m.get_count()  # MIDIデバイスの数
        print("# of devices: ", n_midi)
        for i in range(n_midi):
            print("{}: {}".format(i, m.get_device_info(i)))  # MIDIデバイスの情報を表示

    def chord_on(self, chord, root=0, vel=60, force_arpeggio=None):
        for n in chord:
            vel_n = vel
            if (force_arpeggio == None and self.arpeggio) or (force_arpeggio or self.arpeggio):
                time.sleep(self.delay)

            if n == chord[0]:
                vel_n = vel_n+35 if chord[-1]-chord[0] < 12 else vel_n + 10
            if n == chord[-1]:
                vel_n += 25
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
        notes = self.chords[chord_id]

        if len(self.chords[chord_id]) == 2:
            chord_name = "{1}/{0}".format(
                midi_names[root], names[self.chords[chord_id]])
        else:
            chord_name = "{}{}".format(
                midi_names[root], names[self.chords[chord_id]])

        return(notes, root, chord_name)

    def select_progression(self):
        progression_root = 69
        if self.n_progression == 0:
            # select root note
            progression_root = rnd.randint(self.note_range[0], self.note_range[1])

        chord_degree = self.progression[self.n_progression] # roman numeral
        root = progression_root + diatonic_scale_midi[self.scale][chord_degree] # midi note of root
        notes = diatonic_chords[self.scale][chord_degree]
        
        self.n_progression += 1
        if self.n_progression == len(self.progression):
            self.n_progression = 0

        chord_name = "{}{}".format(
            midi_names[root], degree_names[self.scale][chord_degree])

        return(notes, root, chord_name)

    def close(self):
        self.midiout.close()
        m.quit()

    def main(self):
        """
        Call this function for sound training without visual information.
        """
        duration = 3

        for i in range(20):
            if self.mode == "chord":
                notes, root, chord_name = self.select_chord()
                print(notes,root,chord_name)
                print(re.sub('[.*]','',chord_name))
                #notes = self.chords[chord]                
            else:
                notes, root, chord_name = self.select_progression()
                print(notes,root,chord_name)

            print(len(notes))
            if len(notes) == 4 and Transpose:
                if (Random and rnd.randint(0, 2) == 0) or not Random:
                    notes = [notes[0]-24, notes[3]-12, notes[1], notes[2]]
                    print("transposed")

            self.chord_on(notes, root=root)
            time.sleep(duration)
            self.chord_off(notes, root=root)

        self.midiout.close()
        m.quit()

