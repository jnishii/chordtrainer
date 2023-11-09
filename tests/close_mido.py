import mido

outport = mido.open_output('IAC Driver pioneer', autoreset=True)
outport.close()
