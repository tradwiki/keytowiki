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
laptop = False
bpm = 90

def main():
	root = Tk()
	recordingGui = RecordingGui(root)
	root.mainloop()

class RecordingGui:
	def __init__(self, master):

		#time.clock()
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
		#self.previousTime = time.clock()

		self.mid = music21.midi.MidiFile()
		self.mid.ticksPerQuarterNote = 2048

		#initialize track with tempo marking
		self.track = music21.midi.MidiTrack(0)
		mm = music21.tempo.MetronomeMark(number=bpm)
		events = music21.midi.translate.tempoToMidiEvents(mm)

		self.microSecondsPerQuarterNote = music21.midi.getNumber(events[1].data, len(events[1].data))[0]

		self.track.events.extend(events)

		self.mid.tracks.append(self.track)


		self.first=True

		#open ports
		self.inport = mido.open_input()
		self.inport.callback = self.saveMyMessage
		print('saving message')

	def saveMyMessage(self, msg):
		#currentTime = time.clock()
		#print(currentTime)

		if (msg.type == 'note_on' or msg.type =='note_off') :
			#EXPERIMENTAL VERSION WITH TIMING
			if (experimental) :

				#convert time difference to ticks using tempo information
				delta = int( mido.second2tick(time.perf_counter(), self.mid.ticksPerQuarterNote , self.microSecondsPerQuarterNote))

				#limit to whole note
				if (delta > self.mid.ticksPerQuarterNote*4) :
					delta =  int(self.mid.ticksPerQuarterNote*4)

				#round
				delta = int (RecordingGui.roundToMultiples(delta,  self.mid.ticksPerQuarterNote/4))

				#SPECIAL CASES
				#set first time to 1 beat
				if (self.first) :
					delta =  int(self.mid.ticksPerQuarterNote)
					self.first = False

				#if note_off msg of a very short message, set min duration of 16th note
				#skip first one because prevnote will be null
				#note_on msg seem to be delayed automatically by 16th note from eachother by music21, so no need to do that
				else :
					if ((msg.type == 'note_off') and (msg.note == self.prevnote) and (delta == 0)) : 
						delta =  int(self.mid.ticksPerQuarterNote/4)
						#print(msg.type)

				#update prevnote for checking for short notes
				self.prevnote = msg.note

				#for debug
				#print(delta)

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
			m21msg = music21.midi.MidiEvent(self.track)
			m21msg.type = msg.type.upper()
			m21msg.time = None
			m21msg.pitch = msg.note
			m21msg.velocity = msg.velocity
			m21msg.channel = 1
			self.track.events.append(m21msg)

		#update previousTime
		#self.previousTime = currentTime

		#for debug
		#print(m21msg)
		

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

		#Create MIDI file  from mystream
		self.mid.open('new_song.mid', 'wb')
		self.mid.write()
		self.mid.close()
		mystream = music21.midi.translate.midiFileToStream(self.mid)
		
		print("Plain :\n")
		mystream.show('text', addEndTimes=True)

		print("Flat :\n")
		flatstream =  mystream.flat
		flatstream.show('text', addEndTimes=True)

		print("Just notes:\n")
		justnotes = flatstream.notesAndRests.stream()
		justnotes.show('text', addEndTimes=True)

		print("Just notes with chords:\n")
		justnoteswithchords = justnotes.chordify()
		justnoteswithchords.show('text', addEndTimes=True)


		print("Just notes with chords and rests:\n")
		justnoteswithchords.makeRests()
		justnoteswithchords.show('text', addEndTimes=True)


		#go through list of events and set end time of events to  whevener another event starts
		#if two notes start at same time, then they must end at same time
		firstNote = True
		prevnotewaschord = False
		for mynote in justnoteswithchords:
			if firstNote :
				firstNote = False
				prevnote = mynote
			else:
				#if two notes start at same time, then they must end at same time
				if prevnote.offset == mynote.offset :
					#take the duration of previous note in chords, ie chords will cut off when their first note is unpressed
					mynote.duration = prevnote.duration
					prevnotewaschord = True
				else:	
					if prevnotewaschord :
						mynote.offset = prevnote.offset + prevnote.duration.quarterLength
						prevnotewaschord = False

					else :
						prevnote.duration = music21.duration.Duration(mynote.offset - prevnote.offset)
				
				prevnote = mynote
		
		print("No overlap:\n")
		justnoteswithchords.show('text', addEndTimes=True)

		mystream = justnoteswithchords

		print("Fixed mystream:\n")
		mmystream = mystream.makeMeasures()
		fmmystream = mmystream.makeNotation()
		fmmystream.show('text', addEndTimes=True)


		#compute filepath - TODO: change to cl argument
		scorename = 'new_score'
		if (laptop) :
			filepath ='C:/Users/yoann/pywikibot/core/' + scorename
		else :
			filepath ='D:/Apps/pywikibot/core/' + scorename

		#Create score PNG file
		conv =  music21.converter.subConverters.ConverterLilypond()
		conv.write(fmmystream, fmt = 'lilypond', fp=filepath, subformats = ['png'])

		#Open form window to input title and launch upload
		self.newWindow = Toplevel()
		self.formGui = FormGui(self.newWindow)

	#Helper function to round ticks to closest 1/16 note
	def roundToMultiples(toRound, increment) :
		if (toRound%increment >= increment/2) : 
			rounded = toRound + (increment-(toRound%increment))
		else :
			rounded = toRound - (toRound%increment)

		#print ('rounding {} to {}'.format(toRound, rounded))
		return rounded


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
		upload.main('-always','-filename:' + self.title + '.mid', '-ignorewarn', '-noverify','new_song.mid','-putthrottle:1','''{{Fichier|Concerne=''' + self.title +'''|Est un fichier du type=MIDI}}''')

		#upload fichier score
		upload.main('-always','-filename:' + self.title + '.png', '-ignorewarn', '-noverify','new_score.png','-putthrottle:1','''{{Fichier|Concerne=''' + self.title +'''|Est un fichier du type=Score}}''')

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

