from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
import tkinter as tk

root = tk.Tk()
root.title("Audio Controller v0.03")
root.geometry("280x200+300+300")
#root.configure(background = "white")

#######################TODO###############################
#Finalize variable names, and AudioController object
#Separate GUI from audiocontroller
#Correct "getvolume" from interface/slider
#test opening multiple programs of the same kind (i.e. 2 itunes.exe)
#Make muteButton logic more readable
#Make list of controllers and sessions a list of 2-tuples containing the names?

class AudioController:
	audioControllers = list()
	audioSessionNames = list()

	def __init__(self, session):
		self.session = session
		self.name = self.session.Process.name()
		self.interface = self.session.SimpleAudioVolume
		#GUI elements associated
		self.elements = self.addController(self)
		#Add itself to list of all controllers
		AudioController.audioControllers.append(self)
		AudioController.audioSessionNames.append(self.name)

	def getVolume(self):
		#Returns volume as a percentage
		return self.interface.GetMasterVolume() * 100

	def getSliderVolume(self):
		return self.elements["volumeSlider"].get()

	def setVolume(self, volume):
		#Volume is passed in as a percentage
		self.interface.SetMasterVolume(volume / 100, None)

	def mute(self):
		#Checks whether it was previously muted and sets the new status to the opposite
		newStatus = not self.interface.GetMute()
		self.interface.SetMute(newStatus, None)
		self.elements["muteButton"].configure(relief = (tk.RAISED if newStatus is False else tk.SUNKEN), text = ("Mute" if newStatus is False else "Unmute"))

	def addController(self, session):
		#Add label
		label = tk.Label(root, text = self.name)
		label.grid(row = 0, column = len(AudioController.audioSessionNames), padx = 15)
		#Create associated slider
		slider = tk.Scale(root, from_ = 100, to = 0)
		slider.grid(row = 1, column = len(AudioController.audioSessionNames), padx = 15, rowspan = 2)
		#Set the slider
		slider.set(self.getVolume())
		
		mute = tk.Button(root, text = "Mute", command = self.mute)
		mute.grid(row = 4, column = len(AudioController.audioSessionNames), padx = 15)

		return {"label":label, "volumeSlider":slider, "muteButton":mute}

	def removeController(self):
		for element in self.elements:
			element.destroy()

		AudioController.audioControllers.remove(self)
		AudioController.audioSessionNames.remove(self.name)


#Main logic loop
def update():
	sessions = AudioUtilities.GetAllSessions()
	sessionNames = list()

	for session in sessions:
		#You have a volume, add yourself to list
		if session.Process:
			sessionNames.append(session.Process.name())

		#Skip over "null" sessions
		if not session.Process or session.Process.name() in AudioController.audioSessionNames:
			#Don't do anything
			#You're either a session without a volume, or you're already in the list
			continue

		#You're have a volume, you're not already on the list, so add yourself to the list
		AudioController(session)

	for audioController in AudioController.audioControllers:
		#Check to see whether the program with a previously made slider has been closed
		if audioController.name not in sessionNames:
			audioController.removeController()
			root.update()
			continue
		#You're still open, and you're an audiocontroller
		audioController.setVolume(audioController.getSliderVolume())

	#Roughly "60FPS", 1000/60 ~ 17ms
	root.after(20, update)




def main():
	tk.Button(root, text = "Exit", command = close).grid(row = 5, column = 0, pady = 15)

	update()
	root.mainloop()

def close():
	exit()

main()