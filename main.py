#This file is part of Sight Read.

#Sight Read is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#Sight Read is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with Sight Read.  If not, see <https://www.gnu.org/licenses/>.

from kivy.utils import platform
if(platform == 'android'):
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
import kivy.uix.button as kb
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty
)
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
#import time
from kivy.graphics import Color, Ellipse, Rectangle
from enum import Enum
import random
from decimal import Decimal as D
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.animation import Animation
from kivy.uix.image import Image
import math
if(platform == 'android'):
    from jnius import autoclass 
import os
from time import sleep
import glob
from functools import partial
import re

class MainMenu(Screen):
    pass

class SongSelect(Screen):
    musicDIR = ''
    def on_enter(self):
        #Check platform to get directory for music
        if(platform == 'android'):
            self.musicDIR = '/sdcard/Music'
        else:
            fileDIR = os.path.dirname(os.path.realpath('__file__'))
            self.musicDIR = str(fileDIR) + "/Music"
        entries = os.listdir(self.musicDIR)
        print(entries)
        for i in range(len(entries)):
            if(entries[i] != 'SidecarFiles'):
                btn = Button(text=str(entries[i]))  
                btn.size = (Window.width / 2, Window.height / 8)
                btn.size_hint = (None, None)
                btn.center_x = Window.width / 2
                btn.center_y = (Window.height - (Window.height / 8 * i)) - Window.height / 8
                buttoncallback = partial(self.switch_screen, btn.text)
                btn.bind(on_press=buttoncallback)
                self.add_widget(btn)
    
    def switch_screen(self, *args):
        self.manager.current = "game"
        self.manager.musicDIR = self.musicDIR
        self.manager.songName = args[0]
        self.manager.transition.direction = "right"


class GameScreen(Screen):
    #Loads the widget for the game itself
    def on_enter(self):
        self.clear_widgets()
        print(self.manager.mode)
        if(self.manager.mode == "SongPlay"):
            self.game = SongMode()
        else:
            self.game = RandomMode()

        self.game.setup_game(self.manager)
        self.add_widget(self.game)
        Clock.schedule_interval(self.game.update, 1.0 / 60.0)

        #self.game.start_song()
#    def call_hit(self, hasHit):
#        self.game.hit_note(hasHit)

class ScreenManager(ScreenManager):
    songName = ""
    mode = ""
        

#calculate these values based on the time sig later
#trouble with python decimal addition is causing problems with smaller beats
class NoteType(Enum):
    fullNote = 1
    halfNote = 2
    quarterNote = 4
    eigthNote = 8
    sixteethNote = 16
    fullNoteTriplet = "1t"
    halfNoteTriplet  = "2t"
    quarterNoteTriplet  = "4t"
    eigthNoteTriplet  = "8t"
    sixteethNoteTriplet  = "16t"
    fullNoteRest = "1r"
    halfNoteRest = "2r"
    quarterNoteRest = "4r"
    eigthNoteRest = "8r"
    sixteethNoteRest = "16r"
    

class MissType(Enum):
    missDecrease = 0#4
    missClick = 0#6
    sucessfulHit = -8

class Bars:  
        
    beatPositions = []  #Holds beat times for entire song
    randomBarPositions = [] #Holds bars for random bar choices
    curBarPositions = []   #Holds beat times for a bar of a song
    nextBarPositions = [] # Holds beat times for next bar of song
    curBarNoteTypes = []  #Holds the type of note parallel to the cur bar 
    nextBarNoteTypes = []   #Holds the type of note parallel to the next bar

    gameType = ""

    meter = 4
            
    time = 0  #How long in seconds is a bar based on BPM and time sig

    clock = 0           #Overall game time
    barClock = 0
    lastBarTime = 0     #What time in seconds did the last bar run until
    barNumber = 1
    
    beatsPassed = 0
    
    missMargin = 0.1

    
    def calc_bar_time(self, BPM):
        bps = float(60/float(BPM))
        self.time = bps * self.meter 

    #Creates a random bar for testing
    def create_random(self):
        totalBar = 0
        bar = []

        canContinue = 0 
        
        while totalBar <= 1:
            beat = random.choice(list(NoteType))
            
            for x in list(NoteType):
                if(x.value + totalBar <= 1):
                    canContinue += 1
            
            if(canContinue > 0):
                if(totalBar + beat.value > 1):
                    continue
                bar.append(beat)
                totalBar += beat.value
                canContinue = 0
            else:
                break
                        
        totalBar = 0
        return bar
    
    #Checks to see when the next bar needs to be constructed
    def bar_setup(self, dt):
        self.clock = self.clock + dt
        self.barClock += dt
        if(self.clock >= self.lastBarTime + self.time):
            print(self.nextBarNoteTypes)
            self.lastBarTime += self.time
            self.barClock = 0
            
            del self.curBarPositions[:]
            del self.curBarNoteTypes[:]

            if(self.gameType == "SongPlay"):
                self.curBarPositions = self.calculate_bars_song(self.lastBarTime)
                
                del self.nextBarPositions[:]
                self.nextBarPositions = self.calculate_bars_song((self.lastBarTime + self.time))
            else:
                #self.curBarPositions, self.curBarNoteTypes = self.calculate_bars_random(self.lastBarTime)
                for i in range(len(self.nextBarNoteTypes)):
                    self.curBarPositions.append(self.nextBarPositions[i])
                    self.curBarNoteTypes.append(self.nextBarNoteTypes[i])
                
                del self.nextBarPositions[:]
                del self.nextBarNoteTypes[:]
                self.nextBarPositions, self.nextBarNoteTypes = self.calculate_bars_random((self.lastBarTime + self.time))
            print(self.curBarPositions)
            #self.construct_bar()
            return True
        return False
          
    #Calculates the bar for read in beat files and assigns it
    def calculate_bars_song(self, lastTime):
        self.beatsPassed = 0
        beatHolder = []
        del beatHolder[:]
        for i in range(len(self.beatPositions)):
            if self.beatPositions[i] <= (lastTime + self.time) and self.beatPositions[i] > lastTime:
                #self.curBarPositions.append((self.beatPositions[i] - self.lastBarTime))
                beatHolder.append((self.beatPositions[i] - lastTime))
        return beatHolder
    
    def calculate_bars_random(self, lastTime):
        self.beatsPassed = 0
        beatHolder = []
        beatTypes = []
        del beatHolder[:]
        del beatTypes[:]

        randomBar = random.randint(0, len(self.randomBarPositions) - 1)
        lastBeatTime = 0

        for i in range(len(self.randomBarPositions[randomBar])):
            
            #Sets the first note to 0 distance on the staff so other notes can be positioned accordingly 
            if(i != 0):
                #split the number out from the note type (4t/ 4r etc.)
                #This number is used to divide the length of the staff for proper note positioning
                #Gets the value of the last note so can space the current note the correct distance away on the staff 
                number = re.findall('\d+', self.randomBarPositions[randomBar][i - 1])

                #If not triplet set beat timing
                #If triplet run through 3 times and append
                if(str(self.randomBarPositions[randomBar][i]) != str(NoteType.fullNoteTriplet.value) and str(self.randomBarPositions[randomBar][i]) != str(NoteType.halfNoteTriplet.value) and str(self.randomBarPositions[randomBar][i]) != str(NoteType.quarterNoteTriplet.value) and str(self.randomBarPositions[randomBar][i]) != str(NoteType.eigthNoteTriplet.value) and str(self.randomBarPositions[randomBar][i]) != str(NoteType.sixteethNoteTriplet.value)):
                    #Checks to see if the last note was a triplet and if so reduces the spacing as otherwise would result in an entire quarter note gap after a triplet
                    if(str(self.randomBarPositions[randomBar][i - 1]) == str(NoteType.fullNoteTriplet.value) or str(self.randomBarPositions[randomBar][i - 1]) == str(NoteType.halfNoteTriplet.value) or str(self.randomBarPositions[randomBar][i - 1]) == str(NoteType.quarterNoteTriplet.value) or str(self.randomBarPositions[randomBar][i]) == str(NoteType.eigthNoteTriplet.value) or str(self.randomBarPositions[randomBar][i - 1]) == str(NoteType.sixteethNoteTriplet.value)):
                        beatTiming = self.time / (float(number[0]) * 3)
                    else:
                        beatTiming = self.time / float(number[0])
                    beatHolder.append(beatTiming + lastBeatTime)
                    lastBeatTime += beatTiming 
                else:
                    for j in range(0, 3):
                        #To get proper spacing between notes the first note of a triplet is spaced according to the type of note (eg 1/4 note, 1/8 etc)
                        if(j == 0):
                            beatTiming = (self.time / (float(number[0])))
                        #The rest of the notes in the triplet are then spaced 3rd of the total note duration (eg 1/4 note triplet) apart (meaning the length of the staff is divided by 12 for a 1/4 note)
                        else:
                            beatTiming = (self.time / (float(number[0]) * 3))
                        beatHolder.append(beatTiming + lastBeatTime)
                        lastBeatTime += beatTiming
            else:
                #Does the same as above but starting the first note at 0 rather than, for example a 1/4 of the way down the staff for a quarter note
                if(str(self.randomBarPositions[randomBar][i]) != str(NoteType.fullNoteTriplet.value) and str(self.randomBarPositions[randomBar][i]) != str(NoteType.halfNoteTriplet.value) and str(self.randomBarPositions[randomBar][i]) != str(NoteType.quarterNoteTriplet.value) and str(self.randomBarPositions[randomBar][i]) != str(NoteType.eigthNoteTriplet.value) and str(self.randomBarPositions[randomBar][i]) != str(NoteType.sixteethNoteTriplet.value)):
                    beatTiming = 0 
                    beatHolder.append(beatTiming + lastBeatTime)
                    lastBeatTime += beatTiming 
                else:
                    number = re.findall('\d+', self.randomBarPositions[randomBar][i])
                    for j in range(0, 3):
                        if(j == 0):
                            beatTiming = 0
                        else:
                            beatTiming = (self.time / (float(number[0]) * 3))
                        beatHolder.append(beatTiming + lastBeatTime)
                        lastBeatTime += beatTiming
            #Assigns what type of note it is to an arrray so it can be used to decide what to draw to the screen later in the application
            for noteType in NoteType:
                if(str(self.randomBarPositions[randomBar][i]) == str(noteType.value)):
                    if(str(self.randomBarPositions[randomBar][i]) != str(NoteType.fullNoteTriplet.value) and str(self.randomBarPositions[randomBar][i]) != str(NoteType.halfNoteTriplet.value) and str(self.randomBarPositions[randomBar][i]) != str(NoteType.quarterNoteTriplet.value) and str(self.randomBarPositions[randomBar][i]) != str(NoteType.eigthNoteTriplet.value) and str(self.randomBarPositions[randomBar][i]) != str(NoteType.sixteethNoteTriplet.value)):
                        beatTypes.append(noteType)
                    else:
                        for j in range(0,3):
                            beatTypes.append(noteType)

        return beatHolder, beatTypes


    def calculate_song_length(self):
        return math.ceil(self.beatPositions[-1] / self.time)

    #Constructs a bar randomly and assigns it         
    def construct_bar(self):
        self.beatsPassed = 0
        del self.curBarPositions[:]
        bar = self.create_random()
        for x in range(len(bar)):
            if (x == 0):
                self.curBarPositions.append(bar[x].value)
            else:
                self.curBarPositions.append(bar[x].value + bar[x - 1].value)
    
    def miss_beat(self, notesHit):
        for i in range(self.beatsPassed, len(self.curBarPositions)):
            #Used for generated random bars
            
            if (self.clock > (self.curBarPositions[i] + self.lastBarTime) + 0.1):
                self.beatsPassed += 1
                if(i not in notesHit):
                    if(self.check_if_rest(self.curBarNoteTypes[i]) == False):
                        return True
                    else:
                        return False
        return False
        
    def check_if_rest(self, note):
        if(note == NoteType.fullNoteRest or note == NoteType.halfNoteRest or note == NoteType.quarterNoteRest or note == NoteType.eigthNoteRest or note == NoteType.sixteethNoteRest):
            return True
        return False
        
    #Clears out attributes ready to start again
    def end_game(self):
        del self.curBarPositions[:]
        del self.beatPositions[:]
        self.clock = 0
        self.lastBarTime = 0
    
class Player(Widget):
    
    notesHitTotal = NumericProperty(0)
    curScore = NumericProperty(0)
  
    #Score attributes
    baseIncreaseScore = 100
    baseScoreMultiplier = 1
    currentScoreMultipler = 1
    maxMultiplier = 4
    notesToIncMultipler = 5
    concurrentNotes = 0
    maxConcurrentNotes = 0
    
    #Player success meter
    initSuccessMeter = 50
    maxSuccessMeter = 100
    curSuccess = initSuccessMeter
    
    #is called when player touches screen to see if correctly hit a note
    def check_touch(self, barPositions, lastBarTime, time, clock, noteTypes):
        recordTimes = open("RecordTimes.txt", "a")
        recordTimes.write(str(clock) + "\n")
        hasHit = False
        noteHit = -1
        for i in range(len(barPositions)):
            #Just used for random generated bars 
            #accNum = lastBarTime + (time * barPositions[i])
            #Replace barPos with acc num for random bars
            #if (clock > (barPositions[i] + lastBarTime) - 0.1) and (clock < (barPositions[i] + lastBarTime) + 0.1):
            if (clock > (barPositions[i]) - 0.12) and (clock < (barPositions[i]) + 0.12):
                if(self.check_if_rest(noteTypes[i]) == True):
                    break
                self.hit_note(True)
                self.success_meter(MissType.sucessfulHit)
                noteHit = i
                hasHit = True
                break
            
        if(hasHit == False):    
            self.hit_note(False)
            self.success_meter(MissType.missClick)
        #self.touch_feedback(hasHit)
        return hasHit, noteHit
    
    #Calculates score with multipliers 
    def hit_note(self, noteHit):
        if (noteHit):
            self.notesHitTotal += 1
            self.concurrentNotes += 1

            if(self.concurrentNotes > self.maxConcurrentNotes):
                self.maxConcurrentNotes = self.concurrentNotes

            if(self.concurrentNotes % (self.notesToIncMultipler * self.currentScoreMultipler) == 0):
                if(self.currentScoreMultipler < self.maxMultiplier):
                    self.currentScoreMultipler += 1
                    
            self.curScore += (self.baseIncreaseScore * self.currentScoreMultipler)
        else:
            self.currentScoreMultipler = self.baseScoreMultiplier
            self.concurrentNotes = 0
    
    def check_if_rest(self, note):
        if(note == NoteType.fullNoteRest or note == NoteType.halfNoteRest or note == NoteType.quarterNoteRest or note == NoteType.eigthNoteRest or note == NoteType.sixteethNoteRest):
            return True
        return False

    def restart_game(self):
        self.curScore = 0
        self.notesHitTotal = 0 
        self.maxConcurrentNotes = 0
        self.concurrentNotes = 0
        self.curSuccess = self.initSuccessMeter 
        
        
    def success_meter(self, missType):
        self.curSuccess -= missType.value
        if(self.curSuccess > self.maxSuccessMeter):
            self.curSuccess = self.maxSuccessMeter
        

#Will control the game state (WIP)
#Will calculate performance metrics
class GameManager:    
    maxBars = 0
    totalNotes = 0
    
    def check_for_end(self, curBar):
        if(self.maxBars == curBar):
            return True
        return False
        
    def restart_game(self):
        self.totalNotes = 0

class MusicGame(Widget):
    
    barGenerator = Bars()
    gameManager = GameManager()
    player1 = ObjectProperty(None)

    sound = None
    
    curBar = 0
    
    #Notes Labels
    notesHit = None
    score = None
    multiplier = None
    conCurNotes = None

    #TiminghelpLabel
    timingHelp = None
    
    #gameEnding
    gameEnded = False
    gameStarted = False

    performanceMeter = None
    
    notesHitInBar = []

    #Performance meter boundaries
    performanceStartX = 0
    performanceSizeX = 0
    performanceStartY = 0
    performanceSizeY = 0
    performanceMaxMoveX = 0
    peformanceCurPos = 0
    distanceBetweenStaffLines = 0

    #bar display boundaries 
    barOneStartX = 0
    barOneSizeX = 0
    barOneStartY = 0
    barOneSizeY = 0
    barTwoStartX = 0
    barTwoSizeX = 0
    barTwoStartY = 0
    barTwoSizeY = 0
    barTwoPosOffset = 0

    passedSong = False

    songName = ""
    mamager = None
    gameMode = ""

    bpm = 0

    gameStartOffset = 0
    gameStartTimer = barGenerator.meter
    desktopAudio = None

    def setup_game(self, screenManager):
        self.manager = screenManager
        self.songName = self.manager.songName
        self.gameMode = self.manager.mode
        self.gameEnded = False
        self.calculate_boundaries()
        self.load_beats()
        if(platform == 'android'):
            self.load_song_android()
        else:
            self.load_song_desktop()
        self.barGenerator.gameType = self.gameMode
        self.barGenerator.calc_bar_time(self.bpm)

    def prepare_game(self, dt):
        self.gameStartTimer -= dt
        with self.canvas:
            Label(text=str(int(self.gameStartTimer)), font_size = 50, pos = (50,50))

        if(self.gameStartTimer <= 0):
            self.gameStartOffset -= dt
            self.start_game()
            self.gameStarted = True

    def start_game(self):
        self.draw_background()
        self.bar_setup_type()
        if(platform == 'android'):
            self.play_audio_android()
        else:
            self.play_audio_desktop()

    def calculate_boundaries(self):
        self.performanceStartX = (Window.width/4 + Window.width / 16)
        self.performanceSizeX = (Window.width / 4 + (Window.width / 8))
        self.performanceStartY = 80
        self.performanceSizeY = 2
        self.performanceMaxMoveX = self.performanceStartX + self.performanceSizeX

        heightOffset = Window.height / 4
        barWidth = heightOffset * 5

        self.barOneStartY = Window.height - heightOffset
        self.barOneSizeY = heightOffset
        self.barTwoStartY = heightOffset * 2
        self.barTwoSizeY = heightOffset

        self.barOneStartX = (Window.width / 2) - (barWidth / 2)
        self.barTwoStartX = (Window.width / 2) - (barWidth / 2)
        self.barOneSizeX = barWidth
        self.barTwoSizeX = barWidth

        self.barTwoPosOffset = 30

    def end_game(self):
        if(platform == 'android'):
            self.mPlayer.release()
        file = open("Timings.txt", "a")
        if file.mode == 'a':
            file.writelines(("\n",str(self.player1.curScore)))
            file.close()
        self.draw_final_screen()
    
    def restart_game(self):
        self.curBar = 0
        self.player1.restart_game()
        self.barGenerator.end_game()
        self.gameManager.restart_game()
        #self.start_game(self.songName)
        self.manager.current = "song"
        self.manager.transition.direction = "right"
    
    #Kivy touch event, try and cut down on parameters sent        
    def on_touch_down(self, touch):
        succesfulHit, noteID = self.player1.check_touch(self.barGenerator.curBarPositions, self.barGenerator.lastBarTime, self.barGenerator.time, self.barGenerator.barClock, self.barGenerator.curBarNoteTypes) 
        #self.touch_feedback(succesfulHit)
        if(succesfulHit):
            self.note_hit_animation(noteID)
        self.notesHitInBar.append(noteID)
        if(self.gameEnded == True):
            self.restart_game()
    
    #Visual animation to see where hit
    def touch_feedback(self, hasHit):
        with self.canvas:
                if(hasHit):
                    Color(0.06,1,0.06,0.3)
                else:
                    Color(1,1,1,0.1)
                visualHit = Rectangle(pos=(self.timingHelp.center_x, (self.barOneStartY - (self.barOneSizeY / 2))), size=(2, 0))
        self.animate_touch_feedback(visualHit, self.timingHelp.center_x)    
    
    #Maybe change animation to fade? Still need to make notes pulse    
    def animate_touch_feedback(self, visual, posX):
        anim = Animation(pos = (posX, (self.barOneStartY - self.barOneSizeY)), size = (2,self.barOneSizeY - (self.barOneSizeY / 5)), duration = 0.1)
        anim.start(visual)

    def note_hit_animation(self, noteID):
        anim = Animation(pos = (self.notesAdded[noteID].pos[0] - 12, self.notesAdded[noteID].pos[1] - 12), size = (74, self.notesAdded[noteID].height + 24), color = (1,0.82,0.26,1), duration =0.03)
        anim.start(self.notesAdded[noteID])
         
    #Kivy function called by clock      
    def update(self, dt):

        if(self.gameStarted == False):
            self.prepare_game(dt)

        if(self.gameEnded == False and self.gameStarted == True):
            if(self.barGenerator.bar_setup(dt)):
                self.bar_updated()
            
            if(self.barGenerator.miss_beat(self.notesHitInBar)):                        
                self.player1.hit_note(False)
                self.player1.success_meter(MissType.missDecrease)                                                    

            if(self.player1.curSuccess <= 0):                               
                self.gameEnded = True                                       
                self.passedSong = False                                     
                self.end_game()                                                 

            #THIS IS CAUSING THE BAD FRAMERATE I BELIEVE
            #self.timingHelp.center_x = float(self.timingHelp.center_x) + (float(self.barOneSizeX) / float(self.barGenerator.time) / Clock.get_rfps())
            
            self.performanceMeter.center_x = self.performanceStartX + ((float(self.player1.curSuccess) / 100) * self.performanceSizeX)
            self.draw_labels()
            #self.animate_timing_icon(dt)

    def bar_updated(self):
        self.draw_background()
        del self.notesHitInBar[:]
        self.curBar += 1 
        self.gameEnded = self.gameManager.check_for_end(self.curBar)

        if(self.gameEnded == True):
            self.passedSong = True
            self.end_game()

    def timing_icon_animate(self, timingIcon):
        #anim = Animation(pos = (posX, (self.barOneStartY - self.barOneSizeY)), size = (2,self.barOneSizeY - (self.barOneSizeY / 5)), duration = 0.1)
        anim = Animation(pos = (self.barOneStartX + self.barOneSizeX, self.barOneStartY + 50), duration = self.barGenerator.time)
        anim.start(timingIcon)

    def load_song_android(self):
        print("loading song")
        songsDIR = str(self.manager.musicDIR)
        songSource = (songsDIR, '/', str(self.songName))
        #self.sound = SoundLoader.load('song.mp3')
        #self.sound.play()
        MediaPlayer = autoclass('android.media.MediaPlayer')
        AudioManager = autoclass('android.media.AudioManager')
        self.mPlayer = MediaPlayer()
        self.mPlayer.setDataSource(songsDIR + '/' + self.songName)
        self.mPlayer.setAudioStreamType(AudioManager.STREAM_NOTIFICATION)
        self.mPlayer.prepare()
        #self.mPlayer.start()

    def load_song_desktop(self):
        songDIR = (self.manager.musicDIR + '/' + str(self.songName))
        self.desktopAudio = SoundLoader.load(songDIR)
        

    def play_audio_android(self):
        self.mPlayer.start()   

    def play_audio_desktop(self):
        self.desktopAudio.play()
                
    #Split into draw class
    def draw_background(self):
        self.canvas.clear()
        #Window.clearcolor = (0, 0.5, 0.5, 1)
        #backgroundImage = Image(source="Background.jpg")
        #backgroundImage.allow_stretch = False
        #backgroundImage.keep_ration = True
        self.draw_notes()
        with self.canvas:
            timingIconTest = Rectangle(pos=(self.barOneStartX, self.barOneStartY + 50), size=(2, 20))
            self.timing_icon_animate(timingIconTest)
            self.distanceBetweenStaffLines = self.barOneSizeY / 5

            for i in range(1,6):  
                Rectangle(pos=(self.barOneStartX, self.barOneStartY - (i * self.distanceBetweenStaffLines)), size=(self.barOneSizeX, 2))
                Rectangle(pos=(self.barTwoStartX, (self.barTwoStartY - (i * self.distanceBetweenStaffLines) - self.barTwoPosOffset)), size=(self.barTwoSizeX, 2))
   
            Rectangle(pos=(self.performanceStartX, self.performanceStartY), size = (self.performanceSizeX, self.performanceSizeY))
            Rectangle(pos=(0, Window.height - 105), size=(Window.width, 1))
            Color(1,1,1,0.5)
            Ellipse(pos=(self.width / 2 - 35, self.height / 2 - 35 - self.distanceBetweenStaffLines), size=(70,70))
            Color(1,1,1,1)
        
        self.assign_labels()    
    
    def draw_labels(self):
        self.score.text= ("Score: " + str(self.player1.curScore) + " fps" + str(Clock.get_rfps()))
        self.multiplier.text= (str(self.player1.currentScoreMultipler) + "x")
        self.conCurNotes.text= ("Streak: " + str(self.player1.concurrentNotes))

    def assign_labels(self):
            with self.canvas:
                self.score = Label(text= ("Score: " + str(self.player1.curScore)), font_size=50)
                self.multiplier = Label(text= (str(self.player1.currentScoreMultipler)), font_size=50)
                self.conCurNotes = Label(text= ("Streak: " + str(self.player1.concurrentNotes)), font_size=50)
                self.timingHelp = Label(text= ("|"), font_size=20)
                self.performanceMeter = Label(text=("|"), font_size=20)
                
                self.score.center_x = 150
                self.score.center_y = Window.height - 55
                
                self.multiplier.center_x = Window.width / 2
                self.multiplier.center_y = Window.height / 2  - self.distanceBetweenStaffLines
                
                self.conCurNotes.center_x = Window.width - 115
                self.conCurNotes.center_y = Window.height - 55
                
                self.timingHelp.center_x = self.barOneStartX
                self.timingHelp.center_y = self.barOneStartY
       
                self.performanceMeter.pos = (20,20)  
        
    #Split into draw class            

    notesAdded = []

    def draw_notes(self):
        distBetween = self.barOneSizeY / 5
        self.clear_notes()
        #Current Bar
        for i in range(len(self.barGenerator.curBarPositions)):
            #This offset for loaded in bars
            #self.performanceMeter.center_x = self.performanceStartX + ((float(self.player1.curSuccess) / 100) * self.performanceSizeX)
            offset = (self.barGenerator.curBarPositions[i] / self.barGenerator.time)
            #offset = (self.barGenerator.curBarPositions[i] * 100)
            draw = ((self.barOneSizeX) * offset) + self.barOneStartX
            if(len(self.barGenerator.curBarNoteTypes) > 0):
                if(self.barGenerator.curBarNoteTypes[i] == NoteType.fullNoteRest):
                    fullRest = Image(source = "Assets/Rest semibreve.png", keep_ratio = False, allow_stretch = True)
                    self.add_widget(fullRest)
                    self.notesAdded.append(fullRest)
                    fullRest.pos = (draw - (fullRest.width / 4), (self.barOneStartY - (distBetween * 2)))
                    fullRest.size = (50, distBetween / 2)
                elif(self.barGenerator.curBarNoteTypes[i] == NoteType.halfNoteRest):
                    halfRest = Image(source = "Assets/Rest minim.png", keep_ratio = False, allow_stretch = True)
                    self.add_widget(halfRest)
                    self.notesAdded.append(halfRest)
                    halfRest.pos = (draw - (halfRest.width / 4), self.barOneStartY- self.barOneSizeY)
                    halfRest.size = (50,  distBetween / 2)
                elif(self.barGenerator.curBarNoteTypes[i] == NoteType.quarterNoteRest):
                    quarterRest = Image(source = "Assets/Rest crotchet.png", keep_ratio = False, allow_stretch = True)
                    self.add_widget(quarterRest)
                    self.notesAdded.append(quarterRest)
                    quarterRest.size = (50, distBetween * 3)
                    quarterRest.pos = (draw - (quarterRest.width / 4), (self.barOneStartY- self.barOneSizeY) + distBetween)
                elif(self.barGenerator.curBarNoteTypes[i] == NoteType.eigthNoteRest):
                    eighthRest = Image(source = "Assets/Rest quaver.png", keep_ratio = False, allow_stretch = True)
                    self.add_widget(eighthRest)
                    self.notesAdded.append(eighthRest)
                    eighthRest.pos = (draw - (eighthRest.width / 4), (self.barOneStartY- self.barOneSizeY) + distBetween)
                    eighthRest.size = (50, distBetween * 2)
                elif(self.barGenerator.curBarNoteTypes[i] == NoteType.sixteethNoteRest):
                    sixteenthRest = Image(source = "Assets/Rest semiquaver.png", keep_ratio = False, allow_stretch = True)
                    self.add_widget(sixteenthRest)
                    self.notesAdded.append(sixteenthRest)
                    sixteenthRest.pos = (draw - sixteenthRest.width / 4, self.barOneStartY- self.barOneSizeY)
                    sixteenthRest.size = (50, self.barOneSizeY - (distBetween * 2))
                elif(self.barGenerator.curBarNoteTypes[i] == NoteType.fullNote):
                    full = Image(source = "Assets/Semibreve.png", keep_ratio = False, allow_stretch = True)
                    self.add_widget(full)
                    self.notesAdded.append(full)
                    full.pos = (draw - full.width / 4, self.barOneStartY- self.barOneSizeY)
                    full.size = (50, self.barOneSizeY - distBetween)
                elif(self.barGenerator.curBarNoteTypes[i] == NoteType.halfNote):
                    half = Image(source = "Assets/Minim.png", keep_ratio = False, allow_stretch = True)
                    self.add_widget(half)
                    self.notesAdded.append(half)
                    half.pos = (draw - half.width / 4, self.barOneStartY- self.barOneSizeY)
                    half.size = (50, self.barOneSizeY - distBetween)
                elif(self.barGenerator.curBarNoteTypes[i] == NoteType.quarterNote):
                    quarter = Image(source = "Assets/Crotchet.png", keep_ratio = False, allow_stretch = True)
                    self.add_widget(quarter)
                    self.notesAdded.append(quarter)
                    quarter.pos = (draw - quarter.width / 4, self.barOneStartY- self.barOneSizeY)
                    quarter.size = (50, self.barOneSizeY - distBetween)
                elif(self.barGenerator.curBarNoteTypes[i] == NoteType.eigthNote):
                    eighth = Image(source = "Assets/Quaver single.png", keep_ratio = False, allow_stretch = True)
                    self.add_widget(eighth)
                    self.notesAdded.append(eighth)
                    eighth.pos = (draw - eighth.width / 4, self.barOneStartY- self.barOneSizeY)
                    eighth.size = (50, self.barOneSizeY - distBetween)
                elif(self.barGenerator.curBarNoteTypes[i] == NoteType.sixteethNote):
                    sixteenth = Image(source = "Assets/Semiquaver.png", keep_ratio = False, allow_stretch = True)
                    self.add_widget(sixteenth)
                    self.notesAdded.append(sixteenth)
                    sixteenth.pos = (draw - sixteenth.width / 4, self.barOneStartY- self.barOneSizeY)
                    sixteenth.size = (50, self.barOneSizeY - distBetween)
                else:
                    Rectangle(pos=(draw, self.barOneStartY- self.barOneSizeY), size=(2, self.barOneSizeY - distBetween))
                    Ellipse(pos=(draw - distBetween, self.barOneStartY - self.barOneSizeY), size=(distBetween, distBetween))
            else:
                pass
                        #Rectangle(pos=(draw, self.barOneStartY- self.barOneSizeY), size=(2, self.barOneSizeY - distBetween))
                        #Ellipse(pos=(draw - distBetween, self.barOneStartY - self.barOneSizeY), size=(distBetween, distBetween))

        #Next Bar
        for i in range(len(self.barGenerator.nextBarPositions)):
            #This offset for loaded in bars
            
            #self.performanceMeter.center_x = self.performanceStartX + ((float(self.player1.curSuccess) / 100) * self.performanceSizeX)
            offset = (self.barGenerator.nextBarPositions[i] / self.barGenerator.time)
            #offset = (self.barGenerator.curBarPositions[i] * 100)
            draw = ((self.barTwoSizeX) * offset) + self.barTwoStartX
            if(len(self.barGenerator.nextBarNoteTypes) > 0):
                if(self.barGenerator.nextBarNoteTypes[i] == NoteType.fullNoteRest):
                    fullRest = Image(source = "Assets/Rest semibreve.png", keep_ratio = False, allow_stretch = True)
                    self.add_widget(fullRest)
                    fullRest.pos = (draw - (fullRest.width / 4), (self.barTwoStartY - (distBetween * 2)) - self.barTwoPosOffset)
                    fullRest.size = (50, distBetween / 2)
                elif(self.barGenerator.nextBarNoteTypes[i] == NoteType.halfNoteRest):
                    halfRest = Image(source = "Assets/Rest minim.png", keep_ratio = False, allow_stretch = True)
                    self.add_widget(halfRest)
                    halfRest.pos = (draw - (halfRest.width / 4), self.barTwoStartY- self.barOneSizeY - self.barTwoPosOffset)
                    halfRest.size = (50,  distBetween / 2)
                elif(self.barGenerator.nextBarNoteTypes[i] == NoteType.quarterNoteRest):
                    quarterRest = Image(source = "Assets/Rest crotchet.png", keep_ratio = False, allow_stretch = True)
                    self.add_widget(quarterRest)
                    quarterRest.size = (50, distBetween * 3)
                    quarterRest.pos = (draw - (quarterRest.width / 4), (self.barTwoStartY- self.barOneSizeY) + distBetween - self.barTwoPosOffset)
                elif(self.barGenerator.nextBarNoteTypes[i] == NoteType.eigthNoteRest):
                    eighthRest = Image(source = "Assets/Rest quaver.png", keep_ratio = False, allow_stretch = True)
                    self.add_widget(eighthRest)
                    eighthRest.pos = (draw - (eighthRest.width / 4), (self.barTwoStartY- self.barOneSizeY) + distBetween - self.barTwoPosOffset)
                    eighthRest.size = (50, distBetween * 2)
                elif(self.barGenerator.nextBarNoteTypes[i] == NoteType.sixteethNoteRest):
                    sixteenthRest = Image(source = "Assets/Rest semiquaver.png", keep_ratio = False, allow_stretch = True)
                    self.add_widget(sixteenthRest)
                    sixteenthRest.pos = (draw - sixteenthRest.width / 4, self.barTwoStartY- self.barOneSizeY - self.barTwoPosOffset)
                    sixteenthRest.size = (50, self.barOneSizeY - (distBetween * 2))
                elif(self.barGenerator.nextBarNoteTypes[i] == NoteType.fullNote):
                    full = Image(source = "Assets/Semibreve.png", keep_ratio = False, allow_stretch = True)
                    self.add_widget(full)
                    full.pos = (draw - full.width / 4, self.barTwoStartY- self.barOneSizeY - self.barTwoPosOffset)
                    full.size = (50, self.barOneSizeY - distBetween)
                elif(self.barGenerator.nextBarNoteTypes[i] == NoteType.halfNote):
                    half = Image(source = "Assets/Minim.png", keep_ratio = False, allow_stretch = True)
                    self.add_widget(half)
                    half.pos = (draw - half.width / 4, self.barTwoStartY- self.barOneSizeY - self.barTwoPosOffset)
                    half.size = (50, self.barOneSizeY - distBetween)
                elif(self.barGenerator.nextBarNoteTypes[i] == NoteType.quarterNote):
                    quarter = Image(source = "Assets/Crotchet.png", keep_ratio = False, allow_stretch = True)
                    self.add_widget(quarter)
                    quarter.pos = (draw - quarter.width / 4, self.barTwoStartY -  self.barOneSizeY - self.barTwoPosOffset)
                    quarter.size = (50, self.barOneSizeY - distBetween)
                elif(self.barGenerator.nextBarNoteTypes[i] == NoteType.eigthNote):
                    eighth = Image(source = "Assets/Quaver single.png", keep_ratio = False, allow_stretch = True)
                    self.add_widget(eighth)
                    eighth.pos = (draw - eighth.width / 4, self.barTwoStartY- self.barOneSizeY- self.barTwoPosOffset)
                    eighth.size = (50, self.barOneSizeY - distBetween)
                elif(self.barGenerator.nextBarNoteTypes[i] == NoteType.sixteethNote):
                    sixteenth = Image(source = "Assets/Semiquaver.png", keep_ratio = False, allow_stretch = True)
                    self.add_widget(sixteenth)
                    sixteenth.pos = (draw - sixteenth.width / 4, self.barTwoStartY- self.barOneSizeY - self.barTwoPosOffset)
                    sixteenth.size = (50, self.barOneSizeY - distBetween)
                else:
                    Rectangle(pos=(draw, self.barOneStartY- self.barOneSizeY), size=(2, self.barOneSizeY - distBetween))
                    Ellipse(pos=(draw - distBetween, self.barOneStartY - self.barOneSizeY), size=(distBetween, distBetween))
            else:
                pass

    def clear_notes(self):
        for note in self.notesAdded:
            self.remove_widget(note)
        del self.notesAdded[:] 

    
    def draw_final_screen(self):
        self.canvas.clear()
        Window.clearcolor = (0, 0.5, 0.5, 1)
        results = False
        previousResults = []

        with self.canvas:
                title = Label(text="Results", font_size = 60)
                notes = Label(text= ("Total Notes Hit: " + str(self.player1.notesHitTotal) + "/" + str(self.gameManager.totalNotes - 1)), font_size=40)
                scoreFInal = Label(text= ("Score: " + str(self.player1.curScore)), font_size=40)
                maxNotes = Label(text= ("Max Streak: " + str(self.player1.maxConcurrentNotes)), font_size=40)
            
                if(self.passedSong):
                    title.text = "Result: Pass"
                else:
                    title.text = "Result: Failed"
            
                title.center_x = Window.width / 2
                title.center_y = Window.height / 2 + 60
            
                notes.center_x = Window.width / 2
                notes.center_y = Window.height / 2 - 40
                
                scoreFInal.center_x = Window.width / 2
                scoreFInal.center_y = Window.height / 2

                maxNotes.center_x = Window.width / 2
                maxNotes.center_y = Window.height / 2 - 80

                #Read in and display results
                file = open("Timings.txt", "r")
                if file.mode == 'r':
                    contents = file.read().splitlines()
                    for i in contents:
                        if(results == True):
                            try:
                                previousResults.append(int(i))
                            except:
                                print("not int")

                        if(i == "Results"):
                            results = True

                    file.close()

                previousResults.sort()
                previousResults.reverse()

                numOfPreviousResults = len(previousResults)
                
                #Print previous results
                if(numOfPreviousResults >= 3):
                    for i in range(0,3):
                        note = Label(text= ("Leaderboard: " + str(i+1) + " " + str(previousResults[i])), font_size=20)
                        note.center_x = Window.width / 2
                        note.center_y = Window.height / 2 - 140 - (i * 20)
                else:
                    for i in range(numOfPreviousResults):
                        note = Label(text= ("Leaderboard: " + str(i+1) + " " + str(previousResults[i])), font_size=20)
                        note.center_x = Window.width / 2
                        note.center_y = Window.height / 2 - 140 - (i * 20)

                
#        restartButton = kb.Button(text="Restart")
#        restartButton.bind(on_press=self.start_game)
#        self.add_widget(restartButton)

class SongMode(MusicGame):
    def bar_setup_type(self):
        self.barGenerator.curBarPositions = self.barGenerator.calculate_bars_song(0)
        self.barGenerator.nextBarPositions = self.barGenerator.calculate_bars_song(self.barGenerator.time)

        #Return how many bars the song contains
        self.gameManager.maxBars = self.barGenerator.calculate_song_length()
        self.gameManager.totalNotes = len(self.barGenerator.beatPositions)
        self.draw_notes()

    def load_beats(self):
        cleanpath = os.path.abspath(self.manager.musicDIR + "/SidecarFiles/" + self.songName + ".txt")
        file = open(cleanpath, 'r')

        contents = file.read().splitlines()

        for i in range (len(contents)):
            try:
                if(i != 0):
                    self.barGenerator.beatPositions.append(float(contents[i]))
            except:
                print("error")

        self.bpm = contents[0]

class RandomMode(MusicGame):

    def bar_setup_type(self):
        self.barGenerator.curBarPositions, self.barGenerator.curBarNoteTypes = self.barGenerator.calculate_bars_random(0)
        self.barGenerator.nextBarPositions, self.barGenerator.nextBarNoteTypes = self.barGenerator.calculate_bars_random(self.barGenerator.time)

        #Return how many bars the song contains
        self.gameManager.maxBars = 16
        self.gameManager.totalNotes = len(self.barGenerator.beatPositions)
        self.draw_notes()

    def load_beats(self):
        #Get BPM for chosen song
        cleanpath = os.path.abspath(self.manager.musicDIR + "/SidecarFiles/" + self.songName + ".txt")
        file = open(cleanpath, 'r')
        contents = file.read().splitlines()
        self.bpm = contents[0]  

        cleanpath = os.path.abspath(self.manager.musicDIR + "/SidecarFiles/" + "RandomBeats.txt")
        file = open(cleanpath, 'r')  
        contents = file.read().splitlines()       

        for i in range (len(contents)):
            fields = contents[i].split(" ")
            self.barGenerator.randomBarPositions.append(fields)

        
#TestCommit
menu = Builder.load_file("Menu.kv")

class MusicApp(App):
    def build(self):
#        game = MusicGame()
#        game.draw_background()
#        game.load_beats()
#        game.calculate_bars()
#        game.draw_notes()
#        Clock.schedule_interval(game.update, 0.001)
#        game.start_song()
#        return game
        return menu


if __name__ == '__main__':
    MusicApp().run()
