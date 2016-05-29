import pyautogui
from utils import ThreadJob
import scanner
from datetime import datetime
import numpy as np
import time
import threading
import logging
# Cache screen size
screenSize = scanner.Size(pyautogui.size())
logger=logging.getLogger('gm')



# COLOR DEFINITIONS
# This is the Dino's colour, also used by Obstacles.
COLOR_DINOSAUR = (83, 83, 83)
Scanner = scanner.Scanner()

class Sensor(object):
    def __init__(self):
        self.lastValue = 1

        self.value = 0
        self.offset = [84, -15]
        self.step = [4, 0]
        self.length = 0.3
        self.lastScore = 0

        # Speed
        self.speed = 0
        self.lastComputeSpeed = 0

        # Computes size of the object
        self.size = 0
        self.computeSize = True

class GameManipulator(object):
  # Stores the game position (Globally)

    def __init__(self):
        self.offset = None
        self.width = None

        # Stores self.points (jumps)
        self.points = 0

        # Listners
        self.setGameEnd = 0
        self.onGameStart = None
        self.setSensorData = False

        # Game State
        self.gamestate = 'OVER'
        self.genome = None

        # GameOver Position
        self.gameOverOffset = [190, -82]
        self.lastOutputSet = 'NONE'
        self.lastOutputSetTime = 0
        self.event = threading.Event()

        # Stores self.an array of "sensors" (Ray tracings)
        # Positions self.are always relative to global "offset"
        self.sensors = [Sensor()]
        self.next_call = None


# Find out dinosaur (fast)
    def findGamePosition(self):
        pos, dinoPos, skipXFast = [15]*3
        mul = 20
        screenshot = pyautogui.screenshot().resize((screenSize.width, screenSize.height)).convert('RGB')
        for x in map(lambda x: mul*x,range(1, screenSize.width/mul)):
            dinoPos = Scanner.scanUntil(
                # Start position
                [x, 80],
                # Skip pixels
                [0, skipXFast],
                # Searching Color
                COLOR_DINOSAUR,
                # Normal mode (not inverse)
                False,
                # Iteration limit
                500 / skipXFast, screenshot)

            if dinoPos:
                break

        if not dinoPos:
            return None

        for x in range(dinoPos[0] - 50, dinoPos[0]+1):
            pos = Scanner.scanUntil(
                # Start position
                [x, dinoPos[1] - 2],
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
        self.width = 600#endPos[0] - pos[0];

        return pos


# Read Game state
# (If game is ended or is playing)
    def readGameState(self):
      # Read GameOver
        logger.info("In thread %d" %(threading.active_count(),))
        found = Scanner.scanUntil(
        [
          self.offset[0] + self.gameOverOffset[0],
          self.offset[1] + self.gameOverOffset[1]
        ],

        [2, 0], COLOR_DINOSAUR, False, 20, pyautogui.screenshot().resize((screenSize.width, screenSize.height)).convert('RGB'))
        logger.info("%s, %s" %(found,self.gamestate ))
        if found and not self.gamestate == 'OVER':
            self.gamestate = 'OVER'

            # Clear keys
            self.setGameOutput(0.5)

            # Trigger callback and clear
            if self.setGameEnd:
                if self.setGameEnd == 1:
                    self.genome.set_fitness(self.points)
                else:
                    self.startNewGame()
                self.setGameEnd = False

            # console.log('GAME OVER= '+self.points)

        elif not found and not self.gamestate == 'PLAYING':
            logger.info('163 trying to start')
            self.gamestate = 'PLAYING'
            logger.info('164 trying to start')
             # Clear points
            self.points = 0
            self.lastScore = 0

            # Clear keys
            self.setGameOutput(0.5)

            # Clear sensors
            self.sensors[0].lastComputeSpeed = 0
            self.sensors[0].lastSpeeds = []
            self.sensors[0].lastValue = 1
            self.sensors[0].value = 1
            self.sensors[0].speed = 0
            self.sensors[0].size = 0

            # Clar Output flags
            self.lastOutputSet = 'NONE'

            # Trigger callback and clear
            if self.onGameStart:
                logger.info('185 on gamestart %s'%(self.onGameStart))
                self.onGameStart_callback()
                self.onGameStart = False

    # console.log('GAME RUNNING '+self.points)


# Call this to start a fresh new game
# Will wait untill game has ended,
# and call the `next` callback
    def startNewGame(self, genome=None):

          # Refresh state
        logger.info('in start game 200')
        logger.info(genome)
        self.readGameState()
        logger.info(self.gamestate)

        
        if genome:
            self.genome = genome
        # If game is already over, press space
        if self.gamestate == 'OVER' or not self.onGameStart:
            self.event.set()

          # Set start callback
            self.onGameStart = True
            logger.info('Trying to start')
          # Press space to begin game (repetidelly)
            pyautogui.press(' ')
            #ThreadJob(lambda x:pyautogui.press(' '),self.event, 0.3 ).start()

          # Refresh state
            self.readGameState()

        else:
          # Wait die, and call recursive action
            self.setGameEnd = 2
            
    
    def onGameStart_callback(self):
        self.setSensorData = True
        self.setEndGame = 1

    



# Compute points based on sensors
#
# Basicaly, checks if an object has
# passed trough the sensor and the
# value is now higher than before
    def computePoints(self):
        for sensor in self.sensors:
            if sensor.value > 0.5 and sensor.lastValue < 0.3:
                self.points += 1
        logger.info('POINTS=%d'%( self.points))
      # console.log('POINTS= '+self.points)


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
        offset = self.offset

        startTime = time.time()
        screenshot = pyautogui.screenshot().resize((screenSize.width, screenSize.height)).convert('RGB')
        for sensor in self.sensors:
          # Calculate absolute position of ray tracing
            start = [
              offset[0] + sensor.offset[0],
              offset[1] + sensor.offset[1],
            ]

            # Compute cursor forwarding
            forward = sensor.value * self.width * 0.8 * sensor.length

            end = Scanner.scanUntil(
              # console.log(
                # Start position
                [start[0], start[1]],
                # Skip pixels
                sensor.step,
                # Searching Color
                COLOR_DINOSAUR,
                # Invert mode?
                False,
                # Iteration limit
                (self.width * sensor.length) / sensor.step[0], screenshot)

            # Save lastValue
            sensor.lastValue = sensor.value

            # Calculate the Sensor value
            if end:
                sensor.value = (end[0] - start[0]) / (self.width * sensor.length)

                # Calculate size of obstacle
                endPoint = Scanner.scanUntil(
                  [end[0] + 75, end[1]],
                  [-2, 0],
                  COLOR_DINOSAUR,
                  False,
                  75 / 2, screenshot
                )

                # If no end point, set the start point as end
                if not endPoint:
                    endPoint = end

                sizeTmp = (endPoint[0] - end[0]) / 100.0
                if self.points == sensor.lastScore:
                  # It's the same obstacle. Set size to "max" of both
                    sensor.size = max(sensor.size, sizeTmp)
                else:
                    sensor.size = sizeTmp


                # We use the current score to check for object equality
                sensor.lastScore = self.points


            else:
                sensor.value = 1
                sensor.size = 0

            # Compute speed
            dt = time.time() - sensor.lastComputeSpeed
            sensor.lastComputeSpeed = time.time()

            if sensor.value < sensor.lastValue:
              # Compute speed
                newSpeed = (sensor.lastValue - sensor.value) / dt

                sensor.lastSpeeds = [newSpeed] + sensor.lastSpeeds

                while len(sensor.lastSpeeds) > 10:
                    sensor.lastSpeeds.pop()

                # Take Average
                avgSpeed = np.mean(sensor.lastSpeeds)

                sensor.speed = max(avgSpeed - 1.5, sensor.speed)


            # Save length/size of sensor value
            sensor.size = min(sensor.size, 1.0)

            startTime = time.time()

        # Compute points
        self.computePoints()

        # Call sensor callback (to act)
        logger.info(self.setSensorData)
        if self.setSensorData:
            self.setGameOutput(self.genome.activate([[self.sensors[0].value,
            self.sensors[0].size,
            self.sensors[0].speed]])[0][0]) 

        


# Set action to game
# Values=
#  0.00 to  0.45= DOWN
#  0.45 to  0.55= NOTHING
#  0.55 to  1.00= UP (JUMP)
    def setGameOutput(self,output):

        self.gameOutput = output
        self.gameOutputString = self.getDiscreteState(output)

        if (self.gameOutputString == 'DOWN'):
          # Skew
          pyautogui.keyUp('up')
          pyautogui.keyDown('down')
        elif (self.gameOutputString == 'NORM'):
          # DO Nothing
          pyautogui.keyUp('up')
          pyautogui.keyUp('down')
        else:

            # Filter JUMP
            if (self.lastOutputSet != 'JUMP'):
                self.lastOutputSetTime = time.time()

            # JUMP
            # Check if hasn't jump for more than 3 continuous secconds
            if (time.time() - self.lastOutputSetTime < 3000):
                pyautogui.keyUp('down')
                pyautogui.keyDown('up')
            else:
                pyautogui.keyUp('up')
                pyautogui.keyDown('down')

         
        self.lastOutputSet = self.gameOutputString


#
# Simply maps an real number to string actions
#
    def getDiscreteState(self, value):
        if value < 0.45:
            return 'DOWN'
        elif value > 0.55:
            return 'JUMP'

 
        return 'NORM'


    # Click on the Starting point
    # to make sure game is focused
    def focusGame(self):
        pyautogui.moveTo(self.offset[0], self.offset[1])
        pyautogui.click()
