from datetime import datetime
import json
import logging
import numpy as np
import pyautogui
import redis
import scanner
import time
import threading
from threading import Thread
from utils import ThreadJob


# Cache screen size
screenSize = scanner.Size(pyautogui.size())
logger=logging.getLogger('gm')





# COLOR DEFINITIONS
# This is the Dino's colour, also used by Obstacles.
COLOR_DINOSAUR = (83, 83, 83)
Scanner = scanner.Scanner()

class Sensor(object):
    def __init__(self):
        
        #distance
        self.value = 0
        # Speed
        self.speed = 0
        #cactus size
        self.size = 0

class GameManipulator(object):
  # Stores the game position (Globally)

    def __init__(self):
        self.offset = None
        self.width = None

        # Stores self.points (distance ran)
        self.points = 0


        # Game State
        self.gamestate = 'OVER'
        self.genome = None
        self.gameOutput = 0.5
        self.gameOutputString = 'Norm'
        self.starting = False
        # GameOver Position
        self.event = threading.Event()
        #Initialize redis connections
        self.redis = redis.StrictRedis(host='127.0.0.1', port=6379, db=3)

        self.sensors = [Sensor()]
        self.next_call = None


# Find out dinosaur (fast)
    def findGamePosition(self):
        pos, dinoPos, skipXFast = [30]*3
        mul = 20
        screenshot = pyautogui.screenshot().convert('RGB')
        notfound = True
        #while(notfound):
        for x in map(lambda x: mul*x,range(1, screenSize.width/mul)):
            dinoPos = Scanner.scanUntil(
                # Start position
                [x, 380],
                # Skip pixels
                [0, skipXFast],
                # Searching Color
                COLOR_DINOSAUR,
                # Normal mode (not inverse)
                False,
                # Iteration limit
                600 / skipXFast, screenshot)

            if dinoPos:
                break
        #print dinoPos
        if not dinoPos:
            return None

        for x in range(dinoPos[0] - 50, dinoPos[0]+1):
            pos = Scanner.scanUntil(
                # Start position
                [x, dinoPos[1] - 5],
                # Skip pixels
                [0, 1],
                # Searching Color
                COLOR_DINOSAUR,
                # Normal mode (not inverse)
                False,
                # Iteration limit
                100, screenshot)

            if pos:
                break

        # Did actually found? If not, error!
        if not pos:
            return None

        # Find the end of the game
        endPos = pos
        while(screenshot.getpixel((endPos[0] + 3, endPos[1])) == COLOR_DINOSAUR):
            endPos = Scanner.scanUntil(
              # Start position
              [endPos[0] + 2, endPos[1]],
              # Skip pixels
              [2, 0],
              # Searching Color
              COLOR_DINOSAUR,
              # Invert mode
              True,
              # Iteration limit
              600, screenshot)

        # Did actually found? If not, error!
        if not endPos:
            return None

        # Save to allow global access
        self.offset = pos
        self.width = 1200
        #print pos

        return pos


        # if gameover is not found and gamestate is over # Reset the sensors for starting afresh
    def resetSensors(self):
             # Clear points
            #self.points = 0
            self.sensors[0].value = 13.0
            self.sensors[0].speed = 0.48
            self.sensors[0].size = 0

            # Clear keys
            self.gameOutput = 0.5
            
            self.lastOutputSet = 'NONE'

            

    # console.log('GAME RUNNING '+self.points)


# Call this to start a fresh new game
# Will wait untill game has ended,
# and call the `next` callback
    def startNewGame(self,genome):

          # Refresh state
        #logger.info('in start game 200')
        logger.info(genome)
        
        #self.readGameState()
        self.resetSensors()
        self.starting = True
        # Press space to begin game
        pyautogui.press(' ')
        self.gamestate = 'PLAYING'
        self.genome = genome
        
        # Read sensors until game is over
        while(not self.gamestate == 'OVER'):
            self.readSensors()
            
            
          

    





# Read sensors
#
# Sensors are like ray-traces=
#   They have a starting point,
#   and a limit to search for.
#
# Each sensor can gatter data about
# the DISTANCE of the object, it's
# SIZE and it's speed
#
# Note= We currently only have a sensor.
    
    def readSensors(self):
        d = json.loads(self.redis.get('p'))
        while(self.starting and d.get('o',True)):
            d = json.loads(self.redis.get('p'))
            logger.info("sdata in redis;%s"%(d,))
            pyautogui.press(' ')
            time.sleep(0.2)
        
        if not self.starting:
            s_data = d
        
            self.points = int(s_data.get('sc'))
            fd = s_data.get('fd',0)
            if s_data.get('n') and not s_data.get('o'):
                self.sensors[0].value = fd
                self.sensors[0].size = s_data.get('fs')
            self.sensors[0].speed = s_data.get('s') 
        

            if s_data.get('o') and not self.starting:
                self.genome.set_fitness(self.points)
                self.gamestate = 'OVER'
                self.resetSensors()
        if self.gamestate == 'PLAYING':
            self.gameOutput = self.genome.activate([[self.sensors[0].value,self.sensors[0].size,self.sensors[0].speed]])[0][0]
            self.setGameOutput()
            self.starting = False


                


# Set action to game
# Values=
#  0.00 to  0.45= DOWN
#  0.45 to  0.55= NOTHING
#  0.55 to  1.00= UP (JUMP)
    def setGameOutput(self):

        self.gameOutputString = self.getDiscreteState(self.gameOutput)

        if (self.gameOutputString == 'DOWN'):
          # Skew
          #pyautogui.keyUp('up')
          pyautogui.keyDown('down')
        elif (self.gameOutputString == 'NORM'):
          # DO Nothing
          pyautogui.keyUp('down')
        else:

            # Filter JUMP
            if (self.lastOutputSet != 'JUMP'):
                self.lastOutputSetTime = time.time()

            # JUMP
            # Check if hasn't jump for more than 0.5 continuous secconds
            if (time.time() - self.lastOutputSetTime < 3):
                pyautogui.keyUp('down')
                pyautogui.press('up')
                
            else:
                pyautogui.keyUp('down')

         
        self.lastOutputSet = self.gameOutputString


#
# Simply maps an real number to string actions
#
    def getDiscreteState(self, value):
        if value < 0.45:
            return 'DOWN'
        elif value > 0.65:
            return 'JUMP'

 
        return 'NORM'


    # Click on the Starting point
    # to make sure game is focused
    def focusGame(self):
        pyautogui.moveTo(self.offset[0], self.offset[1])
        pyautogui.click()

if __name__ == '__main__':
    gm = GameManipulator()
    #gm.findGamePosition()
    gm.offset = [610, 522]
    gm.width = 1200
    gm.readSensors()
    print gm.width
