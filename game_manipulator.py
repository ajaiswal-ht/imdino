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

        self.value = 1
        self.offset = [500, -20]
        #self.crossed_offset = [-250,-20]
        self.step = [8, 0]
        self.length = 0.6
        self.lastScore = 0
        self.lastSpeeds = []
        self.sesorPrevLast = None

        # Speed
        self.speed = 0
        self.lastComputeSpeed = time.time()

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
        self.gameOutput = 0.5
        self.gameOutputString = 'Norm'
        self.starting = False
        # GameOver Position
        self.gameOverOffset = [400, -70]
        #self.last_found = [400, -70]
        self.lastOutputSet = 'NONE'
        self.lastOutputSetTime = 0
        self.event = threading.Event()

        # Stores self.an array of "sensors" (Ray tracings)
        # Positions self.are always relative to global "offset"
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
        print dinoPos
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
        print pos

        return pos


        # if gameover is not found and gamestate is over # Reset the sensors for starting afresh
    def resetSensors(self):
            #logger.info('163 trying to start')
            #self.gamestate = 'PLAYING'
            #logger.info('164 trying to start')
             # Clear points
            self.points = 0
            self.lastScore = 0

            # Clear keys
            #self.setGameOutput(0.5)

            # Clear sensors
            self.sensors[0].lastComputeSpeed = time.time()
            self.sensors[0].lastSpeeds = []
            self.sensors[0].lastValue = 1
            self.sensors[0].value = 1
            self.sensors[0].speed = 0
            self.sensors[0].size = 0

            # Clar Output flags
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
        #logger.info(self.gamestate)
         
        #logger.info('Trying to start')
          # Press space to begin game
        pyautogui.press(' ')
        self.gamestate = 'PLAYING'
        self.genome = genome
        #i=1
        #self.setSensorData = True
        while(not self.gamestate == 'OVER'):
            t1 = time.time()
            self.readSensors()
            logger.info("####after sensor time diff ### %f"%(time.time()-t1,))
            
          

    



# Compute points based on sensors
#
# Basicaly, checks if an object has
# passed trough the sensor and the
# value is now higher than before
    def computePoints(self):
        for sensor in self.sensors:
            if sensor.prevLastValue:
                if sensor.prevLastValue == sensor.value and sensor.value == 1.0:
                    return
            logger.info('sensor value %f - %f'%(sensor.value, sensor.lastValue,))
            if sensor.value - sensor.lastValue >0.1 and not sensor.value - sensor.lastValue == 1.0 :
                self.points += 1
      #  logger.info('POINTS=%d'%( self.points))
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
        screenshot = pyautogui.screenshot().convert('RGB')
        #print('screenshot time :%f',(time.time()-startTime,))
        # First check if game is over
        found = Scanner.scanUntil(
        [
          self.offset[0] + self.gameOverOffset[0],
          self.offset[1] + self.gameOverOffset[1]
        ],

        [2, 0], COLOR_DINOSAUR, False, 150,screenshot)
        print found
        if found and not self.starting:
            self.last_found = found
            logger.info('Found game over at %s'%(str(found),))
            if self.gamestate == 'PLAYING':
                self.genome.set_fitness(self.points)
            self.gamestate = 'OVER'
            
            # Clear keys
            self.setGameOutput(0.5)
            self.resetSensors()
        else:

            for sensor in self.sensors:
                s1 = time.time()
                #logger.info('time in read sensor starting %f'%(s1,))
                gameover_or_noobst = False
                first_time = False
              # Calculate absolute position of ray tracing
                start = [
                  offset[0] + sensor.offset[0],
                  offset[1] + sensor.offset[1],
                ]

                
                #logging.info('sensor length and size: %s %s'%(sensor.length, sensor.size,))
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
                sensor.prevLastValue = sensor.lastValue
                sensor.lastValue = sensor.value

                #cross_start = [
                #  offset[0] + sensor.crossed_offset[0],
                #  offset[1] + sensor.crossed_offset[1],
                #]
                m1 = s1-time.time()
                logger.info('time in sensor after finding obst ending %f'%(m1,))
               
                #crossed_end = Scanner.scanUntil(
                #   # console.log(
                #     # Start position
                #     cross_start,
                #     # Skip pixels
                #     [2,0],
                #     # Searching Color
                #     COLOR_DINOSAUR,
                #     # Invert mode?
                #     False,
                #     # Iteration limit
                #     70, screenshot)
                
                # if crossed_end:
                #     self.points += 1

                #logger.info('cross ended : %s'%(str(crossed_end),))

                # Calculate the Sensor value
                if end:
                    sensor.value = (end[0] - start[0]) / (self.width * sensor.length)
                    
                    # Calculate size of obstacle
                    endPoint = Scanner.scanUntil(
                      [end[0] + 150, end[1]],
                      [-4, 0],
                      COLOR_DINOSAUR,
                      False,
                      150 / 2, screenshot
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


                
                else:
                    sensor.value = 1
                    sensor.size = 0
                m2 = time.time()-s1-m1
                logger.info('time in sensor after finding size ending %f' %(m2,))

                now = time.time()
                dt = now - sensor.lastComputeSpeed
                more_than_one_time = False
                first_time = False
                gameover_or_noobst = False
                sensor.lastComputeSpeed = now
                if sensor.value == sensor.lastValue: #Either game over or no obstacles during two intervals
                    gameover_or_noobst = True
                
                if sensor.lastValue == 1.0 and sensor.value<1.0:
                    first_time = True 
                
                if sensor.value < 1.0 and sensor.lastValue <1.0:
                    more_than_one_time = True
                if more_than_one_time:
                    if sensor.value < sensor.lastValue:
                        sensor.speed = (sensor.lastValue - sensor.value) / dt
                    else:
                        if sensor.lastValue > 0.2:
                            sensor.speed = sensor.lastValue/dt
                        else:
                            sensor.speed = (1-sensor.value)/dt
                elif first_time:
                    if sensor.value > 0.2 and sensor.value<0.8:
                        sensor.speed = (sensor.lastValue - sensor.value) / dt
                    elif sensor.value < 0.2:
                        sensor.speed = (1-sensor.value)/dt
                    else:
                        sensor.speed = 0

                

                
                # sensor.lastComputeSpeed = time.time()
                # #logger.info('time diff %s %s'%(dt, str(sensor.lastSpeeds),))
                # if sensor.value < sensor.lastValue:
                #   # Compute speed
                #     newSpeed = (sensor.lastValue - sensor.value) / dt

                #     sensor.lastSpeeds = [newSpeed] + sensor.lastSpeeds

                #     sensor.lastSpeeds = sensor.lastSpeeds[:10]

                #     # Take Average
                #     avgSpeed = np.mean(sensor.lastSpeeds)

                #     sensor.speed = max(avgSpeed - 1.5, newSpeed)
                if not gameover_or_noobst:

                    # We use the current score to check for object equality
                    sensor.lastScore = self.points
                    self.computePoints()
                # Save length/size of sensor value
                    sensor.size = min(sensor.size, 1.0)
                #print( sensor.value, sensor.size, end, forward, start)
                #startTime = time.time()
                #print('screenshot  total time :%f',(time.time()-startTime,))

                # Compute points
                #self.computePoints()

                # Call sensor callback (to act)
                #logger.info(self.setSensorData)
                    self.setGameOutput(self.genome.activate([[self.sensors[0].value,
                    self.sensors[0].size,
                    self.sensors[0].speed]])[0][0])
                    self.starting = False

                logger.info('time in read sensor ending %f'%(s1-time.time(),))


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
            if (time.time() - self.lastOutputSetTime < 3):
                pyautogui.keyUp('down')
                pyautogui.keyDown('up')
                
            else:
                pyautogui.keyUp('up')
                pyautogui.keyUp('down')

         
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

if __name__ == '__main__':
    gm = GameManipulator()
    #gm.findGamePosition()
    gm.offset = [610, 522]
    gm.width = 1200
    gm.readSensors()
    print gm.width
