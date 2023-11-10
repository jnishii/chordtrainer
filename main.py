from chordtrainer.chords import *

chords = [major, minor, dim]

Transpose=False
Random=False

play_chords = playChords(chords=progression, print_root=True, delay=0.1)
play_chords.main(interval=1.0)