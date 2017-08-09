import  pywikibot
import music21
import pagefromfile
import os
import mido
import time
from tkinter import Tk, Label, Button, Toplevel
from mido import Message, MidiFile, MidiTrack
from music21 import converter
from music21.ext.six import StringIO
import webbrowser
import upload
from tkinter import *

experimental = True


def main():
	root = Tk()
	recordingGui = RecordingGui(root)
	root.mainloop()

class RecordingGui:
	def __init__(self, master):
		time.clock()
		self.master = master
		master.title("Record music!")

		self.greet_button = Button(master, text="Start recording", command=self.recordStart)
		self.greet_button.pack()

		self.greet_button = Button(master, text="End recording", command=self.recordEnd)
		self.greet_button.pack()

		#Chronometer - TODO
		# self.label = Label(master, text="Recording time: 00:00")
		# self.label.pack()

		#Seperate button for upload
		# self.greet_button = Button(master, text="Upload", command=self.openForm)
		# self.greet_button.pack()

		self.close_button = Button(master, text="Close", command=master.quit)
		self.close_button.pack()

	def recordStart(self):
		print("start rec!")

		#initialize structures used to record
		self.previousTime = time.clock()

		self.mid = music21.midi.MidiFile()
		self.mid.ticksPerQuarterNote = 1024

		#initialize track with tempo marking
		self.track = music21.midi.MidiTrack(0)
		mm = music21.tempo.MetronomeMark(number=90)
		events = music21.midi.translate.tempoToMidiEvents(mm)

		self.microSecondsPerQuarterNote = music21.midi.getNumber(events[1].data, len(events[1].data))[0]

		self.track.events.extend(events)

		self.mid.tracks.append(self.track)


		self.first=True

		#open ports
		self.inport = mido.open_input()
		self.inport.callback =self.saveMyMessage

	def saveMyMessage(self, msg):
		currentTime = time.clock()


		#EXPERIMENTAL VERSION WITH TIMING
		if (experimental) :

			#7500 000 = 90bpm in musescore
			delta = int( mido.second2tick(currentTime - self.previousTime, self.mid.ticksPerQuarterNote , self.microSecondsPerQuarterNote))
			if (self.first) :
				delta = 2048
				self.first = False
			if (delta >3078) :
				delta = 3078
			# #rounding to 0, 256, and multiples of 128 thereafter
			# if delta < 8 :
			# 	delta = 0
			# else :
			# 	if delta < 256 :
			# 		delta = 256
			# 	else:
			# 		if (delta%128 >=64) : 
			# 			delta = delta + (128-(delta%128))
			# 		else :
			# 			delta = delta - (delta%128)

			# 		if delta > 4096 :
			# 			delta = 4096

			#for debug
			print(delta)

		#FIXED TIMING VERSION
		else :
			if msg.type == 'note_on' : 
				delta = 0
			else :
				delta = 1024

		#DELTA TIME MSG
		dt = music21.midi.DeltaTime(self.track)
		dt.time = delta

		self.track.events.append(dt)

		#NOTE MSG
		me1 = music21.midi.MidiEvent(self.track)
		me1.type = msg.type.upper()
		me1.time = None
		me1.pitch = msg.note
		me1.velocity = msg.velocity
		me1.channel = 1
		self.track.events.append(me1)

		#update previousTime
		self.previousTime = currentTime

		#for debug
		print(me1)
		

	def recordEnd(self):
		print("end rec!")

		#END OF TRACK
		dt = music21.midi.DeltaTime(self.track)
		dt.time = 0
		self.track.events.append(dt)
		me = music21.midi.MidiEvent(self.track)
		me.type = "END_OF_TRACK"
		me.channel = 1
		me.data = '' # must set data to empty string
		self.track.events.append(me)
		print(self.mid)

		#close port
		self.inport.callback = None
		self.inport.close()

		#Create MIDI file  from stream
		self.mid.open('new_song.mid', 'wb')
		self.mid.write()
		self.mid.close()
		stream = music21.midi.translate.midiFileToStream(self.mid)
		#stream.show()

		#Create score PNG file
		conv =  music21.converter.subConverters.ConverterLilypond()
		scorename = 'new_score'
		filepath = 'D:/Apps/pywikibot/core/' + scorename
		conv.write(stream, fmt = 'lilypond', fp=filepath, subformats = ['png'])

		#Open form window to input title and launch upload
		self.newWindow = Toplevel()
		self.formGui = FormGui(self.newWindow)


class FormGui:
	def __init__(self, master):
		self.master = master
		master.title("Formulaire d'import")

		#field name
		self.label = Label(master, text="Donnez un titre à la page")
		self.label.pack()

		#field content
		self.titleString = StringVar()
		self.titleString.set("")
		self.titleField = Entry(master, textvariable=self.titleString)
		self.titleField.pack()

		#button
		self.formbutton = Button(master, text="Ajouter au wiki", command=self.doneForm)
		self.formbutton.pack()
		

	def doneForm(self):
		print("Uploading info!")
		self.title = self.titleString.get()

		#upload fichier MIDI
		upload.main('-always','-filename:' + self.title + '.mid', '-ignorewarn', '-noverify','new_song.mid','''{{Fichier|Concerne=''' + self.title +'''|Est un fichier du type=MIDI}}''')

		#upload fichier score
		upload.main('-always','-filename:' + self.title + '.png', '-ignorewarn', '-noverify','new_score.png','''{{Fichier|Concerne=''' + self.title +'''|Est un fichier du type=Score}}''')

		#Open page on wiki to input more info
		webbrowser.open("http://leviolondejos.wiki/index.php?title=Spécial:AjouterDonnées/Enregistrement/" + self.title)

		#close
		self.master.destroy()

if __name__ == '__main__':
	main()


#FOR ALTERNATIVE METHOD
# def uploadToWiki():
# 	path = os.path.abspath('../scripts/dict.txt')
# 	f = open(path, 'w')
# 	f.write(
# 		"""xxxx
# 		'''Upload test page'''
# 		{{Interprétation
# 		|A la partition -> Nom du fichier PDF/PNG du score uploadé
# 		|A le fichier midi -> Nom du fichier MID uploadé
# 		|A la description de l interprétation -> "Enregistré pendant WikiMania 2017"
# 		}}
# 		{{Interprète d une interprétation
# 		|A l interprète -> GUI:Interprète
# 		|Joue de l instrument -> GUI:Instrument
# 		}}
# 		{{Interprétation B}}
# 		{{Morceau d une interprétation
# 		|A le morceau interprété -> GUI:Morceau
# 		|Est joué dans la tonalité -> Tonalité de music21
# 		|A la métrique musicale -> Time signa9ture de music21
# 		|A le bpm -> BPM moyen de music21(?)
# 		}}
# 		{{Interprétation C}}

# 		<score lang="ABC">
# 		X:1
# 		M:C
# 		L:1/4
# 		K:C
# 		C, D, E, F,|G, A, B, C|D E F G|A B c d|
# 		e f g a|b c' d' e'|f' g' a' b'|]
# 		</score>
# 		yyyy"""
# 		)
# 	f.close()

# 	pagefromfile.main('-begin:xxxx','-end:yyyy', '-notitle', '-force') #REMOVE FORCE AFTER TESTING

