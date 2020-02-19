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


from kivy.app import App
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.label import Label
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
import math

class MainMenu(Screen):
    pass

class SongSelect(Screen):
    pass

class GameScreen(Screen):
    #Loads the widget for the game itself
    def on_enter(self):
        self.game = MusicGame()
        self.game.start_game()
        self.add_widget(self.game)
        Clock.schedule_interval(self.game.update, 1.0 / 60.0)
        #self.game.start_song()
#    def call_hit(self, hasHit):
#        self.game.hit_note(hasHit)

class ScreenManager(ScreenManager):
    pass

#calculate these values based on the time sig later
#trouble with python decimal addition is causing problems with smaller beats
class NoteType(Enum):
    fullNote = 1
    halfNote = 0.5
    quarterNote = 0.25
    sixteethNote = 0.125
    #thirtyNote = 0.075
    
class MissType(Enum):
    missDecrease = 10
    missClick = 6
    sucessfulHit = -8

class Bars:  
        
    beatPositions = []  #Holds beat times for entire song
    barPositions = []   #Holds beat times for a bar of a song
    
    bpm = 60
    meter = 4
            
    bps = float(60/float(bpm))
    time = bps * meter  #How long in seconds is a bar based on BPM and time sig

    clock = 0
    lastBarTime = 0     #What time in seconds did the last bar run until
    barNumber = 1
    
    beatsPassed = 0
    
    missMargin = 0.1
    
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
        if(self.clock >= self.lastBarTime + self.time):
            self.lastBarTime += self.time
            self.calculate_bars()
            #self.construct_bar()
            return True
        return False
          
    #Calculates the bar for read in beat files and assigns it
    def calculate_bars(self):
        self.beatsPassed = 0
        del self.barPositions[:]
        for i in range(len(self.beatPositions)):
            if self.beatPositions[i] <= (self.lastBarTime + self.time) and self.beatPositions[i] >= self.lastBarTime:
                self.barPositions.append((self.beatPositions[i] - self.lastBarTime))
    
    def calculate_song_length(self):
        return math.ceil(self.beatPositions[-1] / self.time)

    #Constructs a bar randomly and assigns it         
    def construct_bar(self):
        self.beatsPassed = 0
        del self.barPositions[:]
        bar = self.create_random()
        for x in range(len(bar)):
            if (x == 0):
                self.barPositions.append(bar[x].value)
            else:
                self.barPositions.append(bar[x].value + bar[x - 1].value)
    
    def miss_beat(self, notesHit):
        for i in range(self.beatsPassed, len(self.barPositions)):
            #Used for generated random bars
            accNum = self.lastBarTime + (self.time * self.barPositions[i])
            
            if (self.clock > (self.barPositions[i] + self.lastBarTime) + 0.1):
                self.beatsPassed += 1
                if(i not in notesHit):
                    return True
        return False
        
        
    #Clears out attributes ready to start again
    def end_game(self):
        del self.barPositions[:]
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
    def check_touch(self, barPositions, lastBarTime, time, clock):
        recordTimes = open("RecordTimes.txt", "a")
        recordTimes.write(str(clock) + "\n")
        hasHit = False
        noteHit = -1
        for i in range(len(barPositions)):
            #Just used for random generated bars 
            accNum = lastBarTime + (time * barPositions[i])
            #Replace barPos with acc num for random bars
            if (clock < (barPositions[i] + lastBarTime) + 0.1) and (clock > (barPositions[i] + lastBarTime) - 0.1):
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

    performanceMeter = None
    
    notesHitInBar = []

    #Performance meter boundarys 
    performanceStartX = 0
    performanceSizeX = 0
    performanceStartY = 0
    performanceSizeY = 0
    performanceMaxMoveX = 0
    peformanceCurPos = 0

    passedSong = False

    def start_game(self):
        self.gameEnded = False
        self.calculate_boundaries()
        self.draw_background()
        self.load_beats()
        self.load_song()
        self.barGenerator.calculate_bars()
        #Return how many bars the song contains
        self.gameManager.maxBars = self.barGenerator.calculate_song_length()
        self.gameManager.totalNotes = len(self.barGenerator.beatPositions)
        self.draw_notes()

    def calculate_boundaries(self):
        self.performanceStartX = 20
        self.performanceSizeX = (Window.width / 8)
        self.performanceStartY = 50
        self.performanceSizeY = 2
        self.performanceMaxMoveX = self.performanceStartX + self.performanceSizeX
        

    def end_game(self):
        self.draw_final_screen()
    
    def restart_game(self):
        self.curBar = 0
        self.player1.restart_game()
        self.barGenerator.end_game()
        self.gameManager.restart_game()
        self.start_game()
    
    #Kivy touch event, try and cut down on parameters sent        
    def on_touch_down(self, touch):
        succesfulHit, noteID = self.player1.check_touch(self.barGenerator.barPositions, self.barGenerator.lastBarTime, self.barGenerator.time, self.barGenerator.clock) 
        self.touch_feedback(succesfulHit)
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
                visualHit = Rectangle(pos=(self.timingHelp.center_x, (Window.height / 2)), size=(2, 0))
        self.animate_touch_feedback(visualHit, self.timingHelp.center_x)    
    
    #Maybe change animation to fade? Still need to make notes pulse    
    def animate_touch_feedback(self, visual, posX):
        anim = Animation(pos = (posX, (Window.height / 2) - 40), size = (2,80), duration = 0.1)
        anim.start(visual)
         
    #Kivy function called by clock      
    def update(self, dt):
        if(self.gameEnded == False):
            if(self.barGenerator.bar_setup(dt)):
                self.bar_updated()
            
            if(self.barGenerator.miss_beat(self.notesHitInBar)):
                self.player1.hit_note(False)
                self.player1.success_meter(MissType.missDecrease)

            if(self.player1.curSuccess <= 0):
                self.gameEnded = True
                self.passedSong = False
                self.end_game()   

            self.timingHelp.center_x = float(self.timingHelp.center_x) + (float(self.width) / float(self.barGenerator.time) / 60)
            self.performanceMeter.center_x = self.performanceStartX + ((float(self.player1.curSuccess) / 100) * self.performanceSizeX)
            self.draw_labels()
            self.animate_timing_icon(dt)

    def bar_updated(self):
        self.draw_background()
        del self.notesHitInBar[:]
        self.curBar += 1 
        self.gameEnded = self.gameManager.check_for_end(self.curBar)
        if(self.gameEnded == True):
            self.passedSong = True
            self.end_game()
    
    def load_song(self):
        print("loading song")
        self.sound = SoundLoader.load('song.mp3')
        self.sound.play()

    def load_beats(self):
        file = open("Timings.txt", "r")
        if file.mode == 'r':
            contents = file.read().splitlines()
            file.close()
            for i in contents:
                self.barGenerator.beatPositions.append(float(i))
        
     #FIND A WAY TO COMPRESS THIS INTO ONE LINE THAT SUPPORTS MULTIPLE TIME SIGS
    #PURELY FOR TESTING  
    #Maybe use kivy animation?    
    #Use modulus function in loop with iterations defined by time sig?
    def animate_timing_icon(self, dt):
        if (self.barGenerator.clock < (self.barGenerator.lastBarTime + self.barGenerator.time / 4) + 0.1) and (self.barGenerator.clock > (self.barGenerator.lastBarTime + self.barGenerator.time / 4) - 0.1):
            if(self.timingHelp.font_size <= 25):
                self.timingHelp.font_size += 5
        elif (self.barGenerator.clock < (self.barGenerator.lastBarTime + self.barGenerator.time / 2) + 0.1) and (self.barGenerator.clock > (self.barGenerator.lastBarTime + self.barGenerator.time / 2) - 0.1):
            if(self.timingHelp.font_size <= 25):
                self.timingHelp.font_size += 5
        elif (self.barGenerator.clock < (self.barGenerator.lastBarTime + self.barGenerator.time * 0.75) + 0.1) and (self.barGenerator.clock > (self.barGenerator.lastBarTime + self.barGenerator.time * 0.75) - 0.1):
            if(self.timingHelp.font_size <= 25):
                self.timingHelp.font_size += 5
        else:
            if(self.timingHelp.font_size > 20):
                self.timingHelp.font_size -= 2
                
    #Split into draw class
    def draw_background(self):
        self.canvas.clear()
        Window.clearcolor = (0, 0.5, 0.5, 1)
        self.draw_notes()
        self.assign_labels()
        with self.canvas:
            Rectangle(pos=(0, (Window.height / 2) - 41), size=(Window.width, 2))
            Rectangle(pos=(0, (Window.height / 2) - 21), size=(Window.width, 2))
            Rectangle(pos=(0, (Window.height / 2) - 1), size=(Window.width, 2))
            Rectangle(pos=(0, (Window.height / 2) + 19), size=(Window.width, 2))
            Rectangle(pos=(0, (Window.height / 2) + 39), size=(Window.width, 2))
            
            Rectangle(pos=(self.performanceStartX, self.performanceStartY), size = (self.performanceSizeX, self.performanceSizeY))
            
            title = Label(text='Sight Reading Prototype', font_size=50)
            title.center_x = Window.width / 2
            title.center_y = Window.height - 50
            
    
    def draw_labels(self):
        self.notesHit.text = ("Notes Hit: " + str(self.player1.notesHitTotal))
        self.score.text= ("Score: " + str(self.player1.curScore))
        self.multiplier.text= ("Multiplier: " + str(self.player1.currentScoreMultipler) + "x")
        self.conCurNotes.text= ("Steak: " + str(self.player1.concurrentNotes))
        
    #Split into draw class            

    def draw_notes(self):
        for i in range(len(self.barGenerator.barPositions)):
            #This offset for loaded in bars
            offset = (self.barGenerator.barPositions[i] / self.barGenerator.time) * 100
            #offset = (self.barGenerator.barPositions[i] * 100)
            draw = (Window.width / 100) * offset
            with self.canvas:
                Rectangle(pos=(draw, (Window.height / 2) - 40), size=(2, 80))
                Ellipse(pos=(draw - 16, (Window.height / 2) - 40), size=(16, 16))
                
    def assign_labels(self):
            with self.canvas:
                self.notesHit = Label(text= ("Notes Hit: " + str(self.player1.notesHitTotal)), font_size=30)
                self.score = Label(text= ("Score: " + str(self.player1.curScore)), font_size=30)
                self.multiplier = Label(text= ("Multiplier: " + str(self.player1.currentScoreMultipler)), font_size=30)
                self.conCurNotes = Label(text= ("Steak: " + str(self.player1.concurrentNotes)), font_size=30)
                self.timingHelp = Label(text= ("|"), font_size=20)
                self.performanceMeter = Label(text=("|"), font_size=20)
            
                self.notesHit.center_x = Window.width / 2
                self.notesHit.center_y = Window.height / 4 - 30
                
                self.score.center_x = Window.width / 2
                self.score.center_y = Window.height / 4
                
                self.multiplier.center_x = Window.width / 2
                self.multiplier.center_y = Window.height / 4 + 30
                
                self.conCurNotes.center_x = Window.width / 2
                self.conCurNotes.center_y = Window.height / 4 + 60
                
                self.timingHelp.center_x = 0
                self.timingHelp.center_y = Window.height / 2 + 90 
       
                self.performanceMeter.pos = (20,20)   

    
    def draw_final_screen(self):
        self.canvas.clear()
        Window.clearcolor = (0, 0.5, 0.5, 1)
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
                
#        restartButton = kb.Button(text="Restart")
#        restartButton.bind(on_press=self.start_game)
#        self.add_widget(restartButton)
                
        
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
