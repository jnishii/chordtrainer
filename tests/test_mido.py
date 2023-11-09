import mido
from mido import Message, MidiFile, MidiTrack, MetaMessage
from time import sleep

def note(note,velocity = 64, time = 0):
    return mido.Message('note_on',note=note,velocity = velocity, time=time)

def note_off(note,velocity = 64, time=0):
    return mido.Message('note_off', note=note, velocity = velocity, time=time)

outport = mido.open_output('IAC Driver pioneer', autoreset=True)
def majorChord(root, duration):
    outport.send(note(root))
    outport.send(note(root+4))
    outport.send(note(root+7))
    sleep(duration)
    outport.send(note_off(root))
    outport.send(note_off(root+4))
    outport.send(note_off(root+7))

def minorChord(root ,duration):
    outport.send(note(root))
    outport.send(note(root+3))
    outport.send(note(root+7))
    sleep(duration)
    outport.send(note_off(root))
    outport.send(note_off(root+3))
    outport.send(note_off(root+7))

C = 60 
G = 55 
A = 57 
F = 53 

majorChord(C,1)
majorChord(F,1)
#majorChord(G,1)
majorChord(C,2)
outport.close()