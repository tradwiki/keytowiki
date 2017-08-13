import pywikibot
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
import pyaudio
import wave

FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 3600
WAVE_OUTPUT_FILENAME = "file.wav"

def main():
	root = Tk()
	recordingGui = RecordingGui(root)
	root.mainloop()

class RecordingGui:
	def __init__(self, master):
		self.audio = pyaudio.PyAudio()

		self.master = master
		master.title("Record music!")

		self.greet_button = Button(master, text="Start recording", command=self.recordStart)
		self.greet_button.pack()

		self.greet_button = Button(master, text="End recording", command=self.recordEnd)
		self.greet_button.pack()

		#Chronometer - TODO
		# self.label = Label(master, text="Recording time: 00:00")
		# self.label.pack()

		self.close_button = Button(master, text="Close", command=master.quit)
		self.close_button.pack()

	def recordStart(self):
		print("Start recording")
		
		self.recordingNow = True 
		# start Recording
		self.stream = self.audio.open(format=FORMAT, channels=CHANNELS,rate=RATE, input=True,frames_per_buffer=CHUNK)
		self.frames = []

		for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
			if (recordingNow) :
		   	 	data = self.stream.read(CHUNK)
		    	self.frames.append(data)
		    else:
		    	print('Recording stopped')
		    	break

		print("Recording exceeded max time: " + RECORD_SECONDS/60 + " minutes")

	def recordEnd(self):
		print("end rec!")
		self.recordingNow = False
		# stop Recording
		self.stream.stop_stream()
		self.stream.close()
		self.audio.terminate()
		 
		#compute filepath - TODO: change to cl argument
		filepath = WAVE_OUTPUT_FILENAME
		waveFile = wave.open(filepath, 'wb')
		waveFile.setnchannels(CHANNELS)
		waveFile.setsampwidth(audio.get_sample_size(FORMAT))
		waveFile.setframerate(RATE)
		waveFile.writeframes(b''.join(frames))
		waveFile.close()


		#Open form window to input title and launch upload
		self.newWindow = Toplevel()
		self.formGui = FormGui(self.newWindow)


class FormGui:
	def __init__(self, master):
		self.master = master
		master.title("Formulaire d'import")

		#song field name
		self.label = Label(master, text="Morceau :")
		self.label.pack()

		#song field content
		self.titleString = StringVar()
		self.titleString.set("")
		self.titleField = Entry(master, textvariable=self.titleString)
		self.titleField.pack(side=LEFT)

		#artist field name
		self.label = Label(master, text="Artist :")
		self.label.pack()

		#artist field content
		self.artistString = StringVar()
		self.artistString.set("")
		self.artistString = Entry(master, textvariable=self.artistString)
		self.artistString.pack(side=LEFT)

		#button
		self.formbutton = Button(master, text="Ajouter au wiki", command=self.doneForm)
		self.formbutton.pack()
		

	def doneForm(self):
		print("Uploading info!")
		self.morceau = self.titleString.get()
		self.artist = self.artistString.get()
		self.pageTitle = self.title + ' par ' + self.artist

		#upload fichier .OGG
		#upload.main('-always','-filename:' + self.pageTitle + '.wav', '-ignorewarn', '-noverify', WAVE_OUTPUT_FILENAME,'-putthrottle:1','''{{Fichier|Concerne=''' + self.title +'''|Est un fichier du type=MIDI}}''')

		#Open page on wiki to input more info
		webbrowser.open("http://leviolondejos.wiki/index.php?title=Spécial:AjouterDonnées/Enregistrement/" + self.pageTitle)

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

