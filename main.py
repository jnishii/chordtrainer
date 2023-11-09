from chordtrainer.chords import *

chords = [major, minor, dim]

Transpose=False
Random=False
scale = "major"
#mode = "chord"
mode = "progression"
interval = 1 # seconds
progression = p_1251

play_chords = playChords(mode=mode, chords=chords, print_root=True, delay=0.1)
play_chords.main(interval=1.0)