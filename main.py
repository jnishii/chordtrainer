from chordtrainer.chords import *

chords = [major, minor, dim]

Transpose=False
Random=False
scale = "major"
progression = p_1251

play_chords = playChords(mode="chords", chords=chords, print_root=True, delay=0.1)
play_chords.main()