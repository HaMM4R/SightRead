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
from kivy.uix.checkbox import CheckBox
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
    numOfSongs = 0
    minSongList = 0
    maxSongList = 4
    songs = None
    lastChange = 0

    songButtons = []

    difficulty = "Easy"
    difficultyLabel = None

    def on_enter(self):
        self.clear_widgets()
        #Check platform to get directory for music
        if(platform == 'android'):
            self.musicDIR = '/sdcard/Music'
        else:
            fileDIR = os.path.dirname(os.path.realpath('__file__'))
            self.musicDIR = str(fileDIR) + "/Music"
        self.songs = os.listdir(self.musicDIR)
        self.numOfSongs = len(self.songs)
        self.manager.difficulty = "Easy"

        #Creates buttons for difficulties and changing songs in list
        btnDown = Button(text="Previous Songs")
        btnDown.size_hint = (None, None)
        btnDown.size = (Window.width / 4, Window.height / 10)
        btnDown.center_x = Window.width - Window.width / 8
        btnDown.center_y = Window.height - Window.height / 20
        btnDown.bind(on_press=self.moveSongsDown)
        self.add_widget(btnDown)

        btnUp = Button(text="Next Songs")
        btnUp.size_hint = (None, None)
        btnUp.size = (Window.width / 4, Window.height / 10)
        btnUp.center_x = Window.width - Window.width / 8
        btnUp.center_y = 0 + Window.height / 20
        btnUp.bind(on_press=self.moveSongsUp)
        self.add_widget(btnUp)

        btnNoFail = Button(text="No Fail")
        btnNoFail.size_hint = (None, None)
        btnNoFail.size = (Window.width / 8, Window.height / 10)
        btnNoFail.center_x = Window.width / 16
        btnNoFail.center_y = Window.height / 2
        btnNoFailCall = partial(self.set_difficulty, btnNoFail.text)
        btnNoFail.bind(on_press=btnNoFailCall)
        self.add_widget(btnNoFail)

        btnEasy = Button(text="Easy")
        btnEasy.size_hint = (None, None)
        btnEasy.size = (Window.width / 8, Window.height / 10)
        btnEasy.center_x = Window.width / 16 + Window.width / 8
        btnEasy.center_y = Window.height / 2
        btnEasyCall = partial(self.set_difficulty, btnEasy.text)
        btnEasy.bind(on_press=btnEasyCall)
        self.add_widget(btnEasy)

        btnMedium = Button(text="Medium")
        btnMedium.size_hint = (None, None)
        btnMedium.size = (Window.width / 8, Window.height / 10)
        btnMedium.center_x = Window.width / 16 + (Window.width / 8 * 2)
        btnMedium.center_y = Window.height / 2
        btnMidCall = partial(self.set_difficulty, btnMedium.text)
        btnMedium.bind(on_press=btnMidCall)
        self.add_widget(btnMedium)

        btnHard = Button(text="Hard")
        btnHard.size_hint = (None, None)
        btnHard.size = (Window.width / 8, Window.height / 10)
        btnHard.center_x = Window.width / 16 + (Window.width / 8 * 3)
        btnHard.center_y = Window.height / 2
        btnHardCall = partial(self.set_difficulty, btnHard.text)
        btnHard.bind(on_press=btnHardCall)
        self.add_widget(btnHard)

        btnBack = Button(text="Back")
        btnBack.size_hint = (None, None)
        btnBack.size = (Window.width / 2, Window.height / 10)
        btnBack.center_x = 0 + Window.width / 4
        btnBack.center_y = Window.height / 2 - Window.height / 10
        btnBack.bind(on_press=self.back)
        self.add_widget(btnBack)

        self.difficultyLabel = Label(text=("Difficulty: Easy"), font_size = 50)
        self.difficultyLabel.center_x = 0 - Window.width / 6
        self.difficultyLabel.center_y = Window.height / 4
        self.add_widget(self.difficultyLabel)

        self.displaySongList()

    def back(self, *args):
        self.manager.current = "main"


    def set_difficulty(self, *args):
        self.manager.difficulty = args[0]
        self.difficultyLabel.text = ("Difficulty: " + args[0])

    #Moves songs in the list up    
    def moveSongsUp(self, *args):
        for button in self.songButtons:
            self.remove_widget(button)

        if(self.maxSongList + 4 <= len(self.songs)):
            self.minSongList += 4
            self.maxSongList += 4
            self.lastChange = 4
        else:
            if(len(self.songs) != self.maxSongList):
                self.lastChange = len(self.songs) - self.maxSongList
            self.maxSongList = len(self.songs)
            if(self.minSongList + 4 < self.maxSongList):
                self.minSongList += 4

        self.displaySongList()

    #Moves songs in the list down
    def moveSongsDown(self, *args):
        for button in self.songButtons:
            self.remove_widget(button)

        if(self.minSongList - 4 >= 0):
            self.minSongList -= 4
            self.maxSongList -= self.lastChange
            self.lastChange = 4
        else:
            self.minSongList = 0

        self.displaySongList()
    
    def switch_screen(self, *args):
        self.manager.current = "game"
        self.manager.musicDIR = self.musicDIR
        self.manager.songName = args[0]
        self.manager.transition.direction = "right"

    #Displays the list of songs
    def displaySongList(self):
        if(self.maxSongList >= len(self.songs)):
            self.maxSongList = len(self.songs)
        print(self.maxSongList)
        for i in range(self.minSongList, self.maxSongList):
            path = os.path.join(self.musicDIR, self.songs[i])
            if(os.path.isdir(path)):
                continue
            btn = Button(text=str(self.songs[i]))  
            btn.size = (Window.width / 4, Window.height / 5)
            btn.size_hint = (None, None)
            btn.center_x = Window.width - Window.width / 8
            if(i == 0):
                btn.center_y = ((Window.height / 5 * i + Window.height / 5))
            else:
                if(self.minSongList >= 4):
                    btn.center_y = ((Window.height / 5 * (i - self.minSongList) + Window.height / 5))
                else:
                    btn.center_y = ((Window.height / 5 * i))

            buttoncallback = partial(self.switch_screen, btn.text)
            btn.bind(on_press=buttoncallback)
            self.songButtons.append(btn)
            self.add_widget(btn)


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

#Is used to pass data between different screens
class ScreenManager(ScreenManager):
    songName = ""
    mode = ""
    difficulty = ""
        

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
    
class Bars:  
        
    beatPositions = []  #Holds beat times for entire song
    randomBarPositions = [] #Holds bars for random bar choices
    curBarPositions = []   #Holds beat times for a bar of a song
    nextBarPositions = [] # Holds beat times for next bar of song
    curBarNoteTypes = []  #Holds the type of note parallel to the cur bar 
    nextBarNoteTypes = []   #Holds the type of note parallel to the next bar

    gameType = ""

    meter = 4
            
    time = 0            #How long in seconds is a bar based on BPM and time sig

    clock = 0           #Overall game time
    barClock = 0        #Time within one bar, gets reset to 0 every time bar changes
    lastBarTime = 0     #What time in seconds did the last bar run until
    barNumber = 1
    
    beatsPassed = 0
    
    missMargin = 0.1

    #Calculates how long a bar lasts
    def calc_bar_time(self, BPM):
        bps = float(60/float(BPM))
        self.time = bps * self.meter 
    
    #Returns how many notes in a bar
    def return_notes_in_bar(self):
        return len(self.curBarPositions)

    #Checks when the next bar needs to be constructed
    def bar_setup(self, dt, currentBar,maxBar):
        self.clock = self.clock + dt
        self.barClock += dt
        if(self.clock >= self.lastBarTime + self.time):
            self.lastBarTime += self.time
            self.barClock = 0
            
            del self.curBarPositions[:]
            del self.curBarNoteTypes[:]

            #Constructs the bars differently depending on the mode as the random bar mode pulls in bars at random so must pull the previous bar to current bar
            if(self.gameType == "SongPlay"):
                self.curBarPositions, self.curBarNoteTypes = self.calculate_bars_song(self.lastBarTime)
                
                del self.nextBarPositions[:]
                del self.nextBarNoteTypes[:]
                self.nextBarPositions, self.nextBarNoteTypes = self.calculate_bars_song((self.lastBarTime + self.time))
            else:
                for i in range(len(self.nextBarNoteTypes)):
                    self.curBarPositions.append(self.nextBarPositions[i])
                    self.curBarNoteTypes.append(self.nextBarNoteTypes[i])
                
                del self.nextBarPositions[:]
                del self.nextBarNoteTypes[:]
                if(currentBar < maxBar - 2):
                    self.nextBarPositions, self.nextBarNoteTypes = self.calculate_bars_random((self.lastBarTime + self.time))
            return True
        return False
          
    #Calculates the bar for read in beat files and assigns it
    def calculate_bars_song(self, lastTime):
        self.beatsPassed = 0
        beatHolder = []
        beatTypes = []
        del beatTypes[:]
        del beatHolder[:]
        for i in range(len(self.beatPositions)):
            if self.beatPositions[i] <= (lastTime + self.time) and self.beatPositions[i] > lastTime:
                beatHolder.append((self.beatPositions[i] - lastTime))
                beatTypes.append(NoteType.quarterNote)
        return beatHolder, beatTypes
    
    #Calculates bars for RandomBeats.txt
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

    #Returns song length
    def calculate_song_length(self, length):
        return math.ceil(length / self.time)

    #Checks to see if the player has gone passed a beat and missed it  
    def miss_beat(self, notesHit):
        for i in range(self.beatsPassed, len(self.curBarPositions)):
            #Used for generated random bars
            
            if (self.clock > (self.curBarPositions[i] + self.lastBarTime) + 0.4):
                self.beatsPassed += 1
                if(i not in notesHit):
                    if(self.check_if_rest(self.curBarNoteTypes[i]) == False):
                        return True
                    else:
                        return False
        return False
        
    #Checks if the note is a rest
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
    
    missDecrease = 0#4
    missClick = 0#6
    sucessfulHit = -8

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
    def check_touch(self, barPositions, lastBarTime, time, clock, noteTypes, notesPlayed):
        hasHit = False
        isRest = False
        noteHit = -1
        for i in range(len(barPositions)):
            if (clock > (barPositions[i]) - 0.04) and (clock < (barPositions[i]) + 0.28):
                if(i in notesPlayed):
                    break
                if(self.check_if_rest(noteTypes[i]) == True):
                    isRest = True
                    noteHit = i
                    break
                self.hit_note(True)
                self.success_meter(self.sucessfulHit)
                noteHit = i
                hasHit = True
                break
            
        if(hasHit == False):    
            self.hit_note(False)
            self.success_meter(self.missClick)
        return hasHit, noteHit, isRest
    
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
        self.curSuccess -= missType
        if(self.curSuccess > self.maxSuccessMeter):
            self.curSuccess = self.maxSuccessMeter
        

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
    songLength = 0
    songStart = 0

    gameStartOffset = 0
    gameStartTimer = float(barGenerator.meter)
    desktopAudio = None

    failLabel = None
    epicLabel = None

    gameReadyToStart = False
    songStarted = False

    gameStartLabel = None

    #Sets up the game and begins loading in audio and other files ready for when the game starts
    def setup_game(self, screenManager):
        self.manager = screenManager
        print(self.gameStartTimer)
        self.songName = self.manager.songName
        self.gameMode = self.manager.mode
        self.set_difficulty_parameters()
        self.gameEnded = False
        self.calculate_boundaries()
        self.load_beats()
        if(platform == 'android'):
            self.load_song_android()
        else:
            self.load_song_desktop()
        self.gameStartTimer += float(self.songStart)
        self.barGenerator.gameType = self.gameMode
        self.barGenerator.calc_bar_time(self.bpm)
        self.gameReadyToStart = True
        self.gameStartLabel = Label(text="", font_size=60)
        self.gameStartLabel.center_x = Window.width / 2
        self.gameStartLabel.center_y = Window.height / 2
        self.add_widget(self.gameStartLabel)

    #Sets the different values for different difficulties
    def set_difficulty_parameters(self):
        if(self.manager.difficulty == "No Fail"):
            self.player1.missDecrease = 0#4
            self.player1.missClick = 0#6
            self.player1.sucessfulHit = 0
        elif(self.manager.difficulty == "Easy"):
            self.player1.missDecrease = 3
            self.player1.missClick = 6
            self.player1.sucessfulHit = -12
        elif(self.manager.difficulty == "Medium"):
            self.player1.missDecrease = 6
            self.player1.missClick = 8
            self.player1.sucessfulHit = -12
        else:
            self.player1.missDecrease = 8
            self.player1.missClick = 10
            self.player1.sucessfulHit = -8

    #Has a timer to allow the audio to load before the game starts
    def prepare_game(self, dt):
        self.gameStartTimer -= dt
        self.gameStartLabel.text = str(int(self.gameStartTimer))

        if(self.gameStartTimer <= self.songStart and self.songStarted == False):
            if(platform == 'android'):
                self.play_audio_android()
            else:
                self.play_audio_desktop()
            self.songStarted = True

        if(self.gameStartTimer <= 0):
            self.start_game()
            self.gameStarted = True

    def start_game(self):
        self.draw_background()
        self.bar_setup_type()
        
    #Calculates how long the staff and other screen elements need to be relative to the screen size
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
        file = open("Results.txt", "a")
        if file.mode == 'a':
            file.writelines(("\n",str((float(self.player1.notesHitTotal) / float(self.gameManager.totalNotes - 1)) * 100)))
            file.close()
        self.draw_final_screen()
    
    def restart_game(self):
        self.curBar = 0
        self.player1.restart_game()
        self.barGenerator.end_game()
        self.gameManager.restart_game()

        self.manager.current = "song"
        self.manager.transition.direction = "right"
    
    #Kivy touch event, try and cut down on parameters sent        
    def on_touch_down(self, touch):
        succesfulHit, noteID, isRest = self.player1.check_touch(self.barGenerator.curBarPositions, self.barGenerator.lastBarTime, self.barGenerator.time, self.barGenerator.barClock, self.barGenerator.curBarNoteTypes, self.notesHitInBar) 

        if(succesfulHit or isRest):
            self.note_hit_animation(noteID, isRest)
        self.notesHitInBar.append(noteID)
        if(self.gameEnded == True):
            self.restart_game()
 

    def note_hit_animation(self, noteID, isRest):
        if(isRest):
            anim = Animation(color = (1,0.2,0.2,1), duration =0.03)
        else:
            anim = Animation(pos = (self.notesAdded[noteID].pos[0] - 12, self.notesAdded[noteID].pos[1] - 12), size = (74, self.notesAdded[noteID].height + 24), color = (0,0.6,0.8,1), duration =0.03)
        anim.start(self.notesAdded[noteID])
         
    #Kivy function called by clock      
    def update(self, dt):

        if(self.gameStarted == False and self.gameReadyToStart == True):
            self.prepare_game(dt)

        if(self.gameEnded == False and self.gameStarted == True):
            #Checks to see when the bar is being updated
            if(self.barGenerator.bar_setup(dt, self.curBar, self.gameManager.maxBars)):
                self.gameManager.totalNotes += self.barGenerator.return_notes_in_bar()
                self.bar_updated()
            
            if(self.barGenerator.miss_beat(self.notesHitInBar)):                        
                self.player1.hit_note(False)
                self.player1.success_meter(self.player1.missDecrease)                                                    

            if(self.player1.curSuccess <= 0):                               
                self.gameEnded = True                                       
                self.passedSong = False                                     
                self.end_game()                                                 

            
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

    #Moves the timing icon across the screen
    def timing_icon_animate(self, timingIcon):
        anim = Animation(pos = (self.barOneStartX + self.barOneSizeX, self.barOneStartY + 50), duration = self.barGenerator.time)
        anim.start(timingIcon)

    def load_song_android(self):
        print("loading song")
        songsDIR = str(self.manager.musicDIR)
        songSource = (songsDIR, '/', str(self.songName))
        MediaPlayer = autoclass('android.media.MediaPlayer')
        AudioManager = autoclass('android.media.AudioManager')
        self.mPlayer = MediaPlayer()
        self.mPlayer.setDataSource(songsDIR + '/' + self.songName)
        self.mPlayer.setAudioStreamType(AudioManager.STREAM_NOTIFICATION)
        self.mPlayer.prepare()

    def load_song_desktop(self):
        songDIR = (self.manager.musicDIR + '/' + str(self.songName))
        self.desktopAudio = SoundLoader.load(songDIR)
        
    def play_audio_android(self):
        self.mPlayer.start()   

    def play_audio_desktop(self):
        self.desktopAudio.play()
                
    #Draws the background with staff 
    def draw_background(self):
        self.canvas.clear()
        self.remove_widget(self.failLabel)
        self.remove_widget(self.epicLabel)

        self.draw_notes()
        with self.canvas:
            if(self.manager.difficulty != "Hard"):
                timingIconTest = Rectangle(pos=(self.barOneStartX, self.barOneStartY + 50), size=(2, 20))
                self.timing_icon_animate(timingIconTest)
            self.distanceBetweenStaffLines = self.barOneSizeY / 5

            for i in range(1,6):  
                Rectangle(pos=(self.barOneStartX - 50, self.barOneStartY - (i * self.distanceBetweenStaffLines)), size=(self.barOneSizeX + 100, 2))
                Rectangle(pos=(self.barTwoStartX - 50, (self.barTwoStartY - (i * self.distanceBetweenStaffLines) - self.barTwoPosOffset)), size=(self.barTwoSizeX +100, 2))
   
            Rectangle(pos=(self.performanceStartX, self.performanceStartY), size = (self.performanceSizeX, self.performanceSizeY))
            Rectangle(pos=(0, Window.height - 105), size=(Window.width, 1))

            Color(1,1,1,0.5)
            Ellipse(pos=(self.width / 2 - 35, self.height / 2 - 35 - self.distanceBetweenStaffLines), size=(70,70))
            Color(1,1,1,1)

        self.failLabel = Label(text="FAIL", font_size = 50)
        self.failLabel.pos=(self.performanceStartX - 100, self.performanceStartY - 50)
        self.add_widget(self.failLabel)

        self.epicLabel = Label(text="EPIC", font_size = 50)
        self.epicLabel.pos=(self.performanceStartX + self.performanceSizeX + 20, self.performanceStartY - 50)
        self.add_widget(self.epicLabel)
        
        self.assign_labels()    
    
    #Updates the labels with the required values
    def draw_labels(self):
        self.score.text= ("Score: " + str(self.player1.curScore))
        self.multiplier.text= (str(self.player1.currentScoreMultipler) + "x")
        self.conCurNotes.text= ("Streak: " + str(self.player1.concurrentNotes))

    #Assgns the positions and sizing of the gamescreen labels
    def assign_labels(self):
            with self.canvas:
                self.score = Label(text= ("Score: " + str(self.player1.curScore)), font_size=50)
                self.multiplier = Label(text= (str(self.player1.currentScoreMultipler)), font_size=50)
                self.conCurNotes = Label(text= ("Streak: " + str(self.player1.concurrentNotes)), font_size=50)
                self.performanceMeter = Label(text=("|"), font_size=20)
                
                self.score.center_x = 200
                self.score.center_y = Window.height - 55
                
                self.multiplier.center_x = Window.width / 2
                self.multiplier.center_y = Window.height / 2  - self.distanceBetweenStaffLines
                
                self.conCurNotes.center_x = Window.width - 115
                self.conCurNotes.center_y = Window.height - 55
       
                self.performanceMeter.pos = (20,20)  
        

    notesAdded = []

    #Draws the notes to the screen
    def draw_notes(self):
        distBetween = self.barOneSizeY / 5
        tripletDetected = 0
        self.clear_notes()
        #Current Bar
        for i in range(len(self.barGenerator.curBarPositions)):
            offset = (self.barGenerator.curBarPositions[i] / self.barGenerator.time)
            draw = ((self.barOneSizeX) * offset) + self.barOneStartX
            if(len(self.barGenerator.curBarNoteTypes) > 0):
                
                if(self.barGenerator.curBarNoteTypes[i] == NoteType.fullNoteTriplet or self.barGenerator.curBarNoteTypes[i] == NoteType.halfNoteTriplet or self.barGenerator.curBarNoteTypes[i] == NoteType.quarterNoteTriplet or self.barGenerator.curBarNoteTypes[i] == NoteType.eigthNoteTriplet or self.barGenerator.curBarNoteTypes[i] == NoteType.sixteethNoteTriplet):
                    tripletDetected += 1
                    if(tripletDetected == 2):
                        tripletLabel = Label(text="3", font_size = 30)
                        tripletLabel.pos = (draw - 20, self.barOneStartY - 20)
                        self.add_widget(tripletLabel)
                    if(tripletDetected == 3):
                        tripletDetected = 0

                if(self.barGenerator.curBarNoteTypes[i] == NoteType.fullNoteRest):
                    fullRest = Image(source = "Assets/Rest semibreve.png", keep_ratio = False, allow_stretch = True)
                    self.add_widget(fullRest)
                    self.notesAdded.append(fullRest)
                    fullRest.pos = (self.width / 2 , (self.barOneStartY - (distBetween * 2) - (distBetween / 2)))
                    fullRest.size = (50, distBetween / 2)
                elif(self.barGenerator.curBarNoteTypes[i] == NoteType.halfNoteRest):
                    halfRest = Image(source = "Assets/Rest minim.png", keep_ratio = False, allow_stretch = True)
                    self.add_widget(halfRest)
                    self.notesAdded.append(halfRest)
                    halfRest.pos = (draw , (self.barOneStartY - (distBetween * 3)))
                    halfRest.size = (50,  distBetween / 2)
                elif(self.barGenerator.curBarNoteTypes[i] == NoteType.quarterNoteRest):
                    quarterRest = Image(source = "Assets/Rest crotchet.png", keep_ratio = False, allow_stretch = True)
                    self.add_widget(quarterRest)
                    self.notesAdded.append(quarterRest)
                    quarterRest.size = (50, distBetween * 3)
                    quarterRest.pos = (draw , (self.barOneStartY- self.barOneSizeY) + distBetween)
                elif(self.barGenerator.curBarNoteTypes[i] == NoteType.eigthNoteRest):
                    eighthRest = Image(source = "Assets/Rest quaver.png", keep_ratio = False, allow_stretch = True)
                    self.add_widget(eighthRest)
                    self.notesAdded.append(eighthRest)
                    eighthRest.pos = (draw , (self.barOneStartY- self.barOneSizeY) + distBetween)
                    eighthRest.size = (50, distBetween * 2)
                elif(self.barGenerator.curBarNoteTypes[i] == NoteType.sixteethNoteRest):
                    sixteenthRest = Image(source = "Assets/Rest semiquaver.png", keep_ratio = False, allow_stretch = True)
                    self.add_widget(sixteenthRest)
                    self.notesAdded.append(sixteenthRest)
                    sixteenthRest.pos = (draw - sixteenthRest.width / 4, self.barOneStartY- self.barOneSizeY)
                    sixteenthRest.size = (50, self.barOneSizeY - (distBetween * 2))
                elif(self.barGenerator.curBarNoteTypes[i] == NoteType.fullNote or self.barGenerator.curBarNoteTypes[i] == NoteType.fullNoteTriplet):
                    full = Image(source = "Assets/Semibreve.png", keep_ratio = False, allow_stretch = True)
                    self.add_widget(full)
                    self.notesAdded.append(full)
                    full.pos = (draw , self.barOneStartY- self.barOneSizeY)
                    full.size = (50, self.barOneSizeY - distBetween)
                elif(self.barGenerator.curBarNoteTypes[i] == NoteType.halfNote or self.barGenerator.curBarNoteTypes[i] == NoteType.halfNoteTriplet):
                    half = Image(source = "Assets/Minim.png", keep_ratio = False, allow_stretch = True)
                    self.add_widget(half)
                    self.notesAdded.append(half)
                    half.pos = (draw , self.barOneStartY- self.barOneSizeY)
                    half.size = (50, self.barOneSizeY - distBetween)
                elif(self.barGenerator.curBarNoteTypes[i] == NoteType.quarterNote or self.barGenerator.curBarNoteTypes[i] == NoteType.quarterNoteTriplet):
                    quarter = Image(source = "Assets/Crotchet.png", keep_ratio = False, allow_stretch = True)
                    self.add_widget(quarter)
                    self.notesAdded.append(quarter)
                    quarter.pos = (draw , self.barOneStartY- self.barOneSizeY)
                    quarter.size = (50, self.barOneSizeY - distBetween)
                elif(self.barGenerator.curBarNoteTypes[i] == NoteType.eigthNote or self.barGenerator.curBarNoteTypes[i] == NoteType.eigthNoteTriplet):
                    eighth = Image(source = "Assets/Quaver single.png", keep_ratio = False, allow_stretch = True)
                    self.add_widget(eighth)
                    self.notesAdded.append(eighth)
                    eighth.pos = (draw, self.barOneStartY- self.barOneSizeY)
                    eighth.size = (50, self.barOneSizeY - distBetween)
                elif(self.barGenerator.curBarNoteTypes[i] == NoteType.sixteethNote or self.barGenerator.curBarNoteTypes[i] == NoteType.sixteenthNoteTriplet):
                    sixteenth = Image(source = "Assets/Semiquaver.png", keep_ratio = False, allow_stretch = True)
                    self.add_widget(sixteenth)
                    self.notesAdded.append(sixteenth)
                    sixteenth.pos = (draw, self.barOneStartY- self.barOneSizeY)
                    sixteenth.size = (50, self.barOneSizeY - distBetween)
                else:
                    Rectangle(pos=(draw, self.barOneStartY- self.barOneSizeY), size=(2, self.barOneSizeY - distBetween))
                    Ellipse(pos=(draw - distBetween, self.barOneStartY - self.barOneSizeY), size=(distBetween, distBetween))
            else:
                pass

        #Next Bar
        tripletDetected = 0
        for i in range(len(self.barGenerator.nextBarPositions)):
            
            offset = (self.barGenerator.nextBarPositions[i] / self.barGenerator.time)
            draw = ((self.barTwoSizeX) * offset) + self.barTwoStartX
            if(len(self.barGenerator.nextBarNoteTypes) > 0):
                if(self.barGenerator.nextBarNoteTypes[i] == NoteType.fullNoteTriplet or self.barGenerator.nextBarNoteTypes[i] == NoteType.halfNoteTriplet or self.barGenerator.nextBarNoteTypes[i] == NoteType.quarterNoteTriplet or self.barGenerator.nextBarNoteTypes[i] == NoteType.eigthNoteTriplet or self.barGenerator.nextBarNoteTypes[i] == NoteType.sixteethNoteTriplet):
                    tripletDetected += 1
                    if(tripletDetected == 2):
                        tripletLabel = Label(text="3", font_size = 30)
                        tripletLabel.pos = (draw - 20, self.barTwoStartY - self.barTwoPosOffset - 50)
                        self.add_widget(tripletLabel)
                    if(tripletDetected == 3):
                        tripletDetected = 0


                if(self.barGenerator.nextBarNoteTypes[i] == NoteType.fullNoteRest):
                    fullRest = Image(source = "Assets/Rest semibreve.png", keep_ratio = False, allow_stretch = True)
                    self.add_widget(fullRest)
                    fullRest.pos = (self.width / 2 , (self.barTwoStartY - (distBetween * 2) - (distBetween / 2)) - self.barTwoPosOffset)
                    fullRest.size = (50, distBetween / 2)
                elif(self.barGenerator.nextBarNoteTypes[i] == NoteType.halfNoteRest):
                    halfRest = Image(source = "Assets/Rest minim.png", keep_ratio = False, allow_stretch = True)
                    self.add_widget(halfRest)
                    halfRest.pos = (draw , self.barTwoStartY - (distBetween * 3) - self.barTwoPosOffset)
                    halfRest.size = (50,  distBetween / 2)
                elif(self.barGenerator.nextBarNoteTypes[i] == NoteType.quarterNoteRest):
                    quarterRest = Image(source = "Assets/Rest crotchet.png", keep_ratio = False, allow_stretch = True)
                    self.add_widget(quarterRest)
                    quarterRest.size = (50, distBetween * 3)
                    quarterRest.pos = (draw , (self.barTwoStartY- self.barOneSizeY) + distBetween - self.barTwoPosOffset)
                elif(self.barGenerator.nextBarNoteTypes[i] == NoteType.eigthNoteRest):
                    eighthRest = Image(source = "Assets/Rest quaver.png", keep_ratio = False, allow_stretch = True)
                    self.add_widget(eighthRest)
                    eighthRest.pos = (draw , (self.barTwoStartY- self.barOneSizeY) + distBetween - self.barTwoPosOffset)
                    eighthRest.size = (50, distBetween * 2)
                elif(self.barGenerator.nextBarNoteTypes[i] == NoteType.sixteethNoteRest):
                    sixteenthRest = Image(source = "Assets/Rest semiquaver.png", keep_ratio = False, allow_stretch = True)
                    self.add_widget(sixteenthRest)
                    sixteenthRest.pos = (draw , self.barTwoStartY- self.barOneSizeY - self.barTwoPosOffset)
                    sixteenthRest.size = (50, self.barOneSizeY - (distBetween * 2))
                elif(self.barGenerator.nextBarNoteTypes[i] == NoteType.fullNote or self.barGenerator.nextBarNoteTypes[i] == NoteType.fullNoteTriplet):
                    full = Image(source = "Assets/Semibreve.png", keep_ratio = False, allow_stretch = True)
                    self.add_widget(full)
                    full.pos = (draw , self.barTwoStartY- self.barOneSizeY - self.barTwoPosOffset)
                    full.size = (50, self.barOneSizeY - distBetween)
                elif(self.barGenerator.nextBarNoteTypes[i] == NoteType.halfNote or self.barGenerator.nextBarNoteTypes[i] == NoteType.halfNoteTriplet):
                    half = Image(source = "Assets/Minim.png", keep_ratio = False, allow_stretch = True)
                    self.add_widget(half)
                    half.pos = (draw , self.barTwoStartY- self.barOneSizeY - self.barTwoPosOffset)
                    half.size = (50, self.barOneSizeY - distBetween)
                elif(self.barGenerator.nextBarNoteTypes[i] == NoteType.quarterNote or self.barGenerator.nextBarNoteTypes[i] == NoteType.quarterNoteTriplet):
                    quarter = Image(source = "Assets/Crotchet.png", keep_ratio = False, allow_stretch = True)
                    self.add_widget(quarter)
                    quarter.pos = (draw , self.barTwoStartY -  self.barOneSizeY - self.barTwoPosOffset)
                    quarter.size = (50, self.barOneSizeY - distBetween)
                elif(self.barGenerator.nextBarNoteTypes[i] == NoteType.eigthNote or self.barGenerator.nextBarNoteTypes[i] == NoteType.eigthNoteTriplet):
                    eighth = Image(source = "Assets/Quaver single.png", keep_ratio = False, allow_stretch = True)
                    self.add_widget(eighth)
                    eighth.pos = (draw , self.barTwoStartY- self.barOneSizeY- self.barTwoPosOffset)
                    eighth.size = (50, self.barOneSizeY - distBetween)
                elif(self.barGenerator.nextBarNoteTypes[i] == NoteType.sixteethNote or self.barGenerator.nextBarNoteTypes[i] == NoteType.sixteethNoteTriplet):
                    sixteenth = Image(source = "Assets/Semiquaver.png", keep_ratio = False, allow_stretch = True)
                    self.add_widget(sixteenth)
                    sixteenth.pos = (draw , self.barTwoStartY- self.barOneSizeY - self.barTwoPosOffset)
                    sixteenth.size = (50, self.barOneSizeY - distBetween)
                else:
                    Rectangle(pos=(draw, self.barOneStartY- self.barOneSizeY), size=(2, self.barOneSizeY - distBetween))
                    Ellipse(pos=(draw - distBetween, self.barOneStartY - self.barOneSizeY), size=(distBetween, distBetween))
            else:
                pass

    #Clears out the stored note images
    def clear_notes(self):
        for note in self.notesAdded:
            self.remove_widget(note)
        del self.notesAdded[:] 

    
    def draw_final_screen(self):
        self.canvas.clear()
        self.remove_widget(self.failLabel)
        self.remove_widget(self.epicLabel)
        results = False
        previousResults = []

        title = Label(text="Results", font_size = 60)
        notes = Label(text= ("Percentage: " + str((float(self.player1.notesHitTotal) / float(self.gameManager.totalNotes - 1)) * 100) + "%"), font_size=40)
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

        self.add_widget(title)
        self.add_widget(notes)
        self.add_widget(scoreFInal)
        self.add_widget(maxNotes)

        #Read in and display results
        file = open("Results.txt", "r")
        if file.mode == 'r':
            contents = file.read().splitlines()
            for i in contents:
                try:
                    previousResults.append(i)
                except:
                    print("not int")


            file.close()

        for num in previousResults:
            try:
                num = int(num)
            except:
                print("NotIn")
        previousResults.sort()
        previousResults.reverse()

        numOfPreviousResults = len(previousResults)
        
        #Print previous results
        if(numOfPreviousResults >= 3):
            for i in range(0,3):
                preScore = Label(text= ("High Score: " + str(i+1) + " " + str(previousResults[i])), font_size=40)
                preScore.center_x = Window.width / 2
                preScore.center_y = Window.height / 2 - 140 - (i * 40)
                self.add_widget(preScore)
        else:
            for i in range(numOfPreviousResults):
                preScore = Label(text= ("High Score: " + str(i+1) + " " + str(previousResults[i])), font_size=40)
                preScore.center_x = Window.width / 2
                preScore.center_y = Window.height / 2 - 140 - (i * 40)
                self.add_widget(preScore)

                
#Mode for players who want to enter their own beat timings in seconds in the beat files
class SongMode(MusicGame):
    def bar_setup_type(self):
        self.barGenerator.curBarPositions, self.barGenerator.curBarNoteTypes = self.barGenerator.calculate_bars_song(0)
        self.barGenerator.nextBarPositions, self.barGenerator.nextBarNoteTypes = self.barGenerator.calculate_bars_song(self.barGenerator.time)

        self.gameManager.maxBars = self.barGenerator.calculate_song_length(self.songLength)
        self.gameManager.totalNotes += self.barGenerator.return_notes_in_bar()
        self.draw_notes()

    def load_beats(self):
        cleanpath = os.path.abspath(self.manager.musicDIR + "/SidecarFiles/" + self.songName + ".beats")
        file = open(cleanpath, 'r')

        contents = file.read().splitlines()

        for i in range (2, len(contents)):
            try:
                if(i != 0):
                    self.barGenerator.beatPositions.append(float(contents[i]))
            except:
                print("error")

        self.bpm = contents[0]
        self.songLength = float(contents[1])
        self.songStart = float(contents[2])

#Sets up gamemode for random bar play. 
class RandomMode(MusicGame):

    def bar_setup_type(self):
        self.barGenerator.curBarPositions, self.barGenerator.curBarNoteTypes = self.barGenerator.calculate_bars_random(0)
        self.barGenerator.nextBarPositions, self.barGenerator.nextBarNoteTypes = self.barGenerator.calculate_bars_random(self.barGenerator.time)

        self.gameManager.maxBars = self.barGenerator.calculate_song_length(self.songLength)
        self.gameManager.totalNotes += self.barGenerator.return_notes_in_bar()
        self.draw_notes()

    def load_beats(self):
        #Get BPM for chosen song
        cleanpath = os.path.abspath(self.manager.musicDIR + "/SidecarFiles/" + self.songName + ".beats")
        file = open(cleanpath, 'r')
        contents = file.read().splitlines()
        self.bpm = contents[0]  
        self.songLength = float(contents[1])
        self.songStart = float(contents[2])

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
        return menu


if __name__ == '__main__':
    MusicApp().run()
