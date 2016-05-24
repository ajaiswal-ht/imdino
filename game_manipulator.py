import pyautogui
import scanner
from datetime import datetime
import numpy as np
# Cache screen size
screenSize = scanner.Size(pyautogui.size())




# COLOR DEFINITIONS
# This is the Dino's colour, also used by Obstacles.
COLOR_DINOSAUR = (83, 83, 83)
Scanner = scanner.Scanner()

class Sensor(object):
    def __init__(self):
        self.lastValue = 1

        self.value = None
        self.offset = [84, -15], # 64,-15
        self.step = [4, 0]
        self.length = 0.3

        # Speed
        self.speed = 0
        self.lastComputeSpeed = 0

        # Computes size of the object
        self.size = 0
        self.computeSize = True

class GameManipulator(object):
  # Stores the game position (Globally)
    offset = None
    width = None

    # Stores points (jumps)
    points = 0

    # Listners
    onGameEnd = None
    onGameStart = None
    onSensorData = None

    # Game State
    gamestate = 'OVER'

    # GameOver Position
    gameOverOffset = [190, -82]

    # Stores an array of "sensors" (Ray tracings)
    # Positions are always relative to global "offset"
    sensors = [Sensor()]


# Find out dinosaur (fast)
    def findGamePosition():
        pos, dinoPos, skipXFast = [15]*3
        mul = 20
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
                500 / skipXFast)

            if dinoPos:
                break

        if not dinoPos:
            return None

        for (var x = dinoPos[0] - 50 x <= dinoPos[0]; x += 1) {
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
                100)

            if pos:
                break

        # Did actually found? If not, error!
        if not pos:
            return None

        # Find the end of the game
        endPos = pos

        while (pyautogui.pixelMatchesColor(endPos[0] + 3, endPos[1], COLOR_DINOSAUR):
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
              600)

        # Did actually found? If not, error!
        if not endPos:
            return None

        # Save to allow global access
        GameManipulator.offset = pos
        GameManipulator.width = 600#endPos[0] - pos[0];

        return pos


# Read Game state
# (If game is ended or is playing)
    def readGameState():
      # Read GameOver
        found = Scanner.scanUntil(
        [
          GameManipulator.offset[0] + GameManipulator.gameOverOffset[0],
          GameManipulator.offset[1] + GameManipulator.gameOverOffset[1]
        ],

        [2, 0], COLOR_DINOSAUR, False, 20)

        if found and not GameManipulator.gamestate == 'OVER':
            GameManipulator.gamestate = 'OVER'

            # Clear keys
            GameManipulator.setGameOutput(0.5)

            # Trigger callback and clear
            GameManipulator.onGameEnd && GameManipulator.onGameEnd(GameManipulator.points)
            GameManipulator.onGameEnd = None

            # console.log('GAME OVER= '+GameManipulator.points)

         elif not found and not GameManipulator.gamestate == 'PLAYING':
             GameManipulator.gamestate = 'PLAYING'

              # Clear points
             GameManipulator.points = 0
             GameManipulator.lastScore = 0

             # Clear keys
             GameManipulator.setGameOutput(0.5)

             # Clear sensors
             GameManipulator.sensors[0].lastComputeSpeed = 0
             GameManipulator.sensors[0].lastSpeeds = []
             GameManipulator.sensors[0].lastValue = 1
             GameManipulator.sensors[0].value = 1
             GameManipulator.sensors[0].speed = 0
             GameManipulator.sensors[0].size = 0

             # Clar Output flags
             GameManipulator.lastOutputSet = 'NONE'

             # Trigger callback and clear
             if GameManipulator.toStartGame:
                 GameManipulator.onGameStart()
                 GameManipulator.toStartGame = None

    # console.log('GAME RUNNING '+self.points)


# Call this to start a fresh new game
# Will wait untill game has ended,
# and call the `next` callback
    def startNewGame(next):

          # Refresh state
        GameManipulator.readGameState()

        # If game is already over, press space
        if GameManipulator.gamestate == 'OVER':
            clearInterval(_startKeyInterval)

          # Set start callback
            GameManipulator.onGameStart = function (argument) {
            clearInterval(_startKeyInterval)
            next && next()
          }

          # Press space to begin game (repetidelly)
          _startKeyInterval = setInterval(function (){
            robot.keyTap(' ')
          }, 300)

          # Refresh state
          GameManipulator.readGameState()

        } else {
          # Wait die, and call recursive action
          GameManipulator.onGameEnd = function () {
            GameManipulator.startNewGame(next)
          }
        }




# Compute points based on sensors
#
# Basicaly, checks if an object has
# passed trough the sensor and the
# value is now higher than before
    def computePoints():
        for sensor in GameManipulator.sensors:
            if sensor.value > 0.5 and sensor.lastValue < 0.3:
                GameManipulator.points++
        print 'POINTS= '+ GameManipulator.points
      # console.log('POINTS= '+GameManipulator.points)


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
    def readSensors():
        offset = GameManipulator.offset

        startTime = datetime.now()

        for sensor in GameManipulator.sensors:
          # Calculate absolute position of ray tracing
            start = [
              offset[0] + sensor.offset[0],
              offset[1] + sensor.offset[1],
            ]

            # Compute cursor forwarding
            forward = sensor.value * GameManipulator.width * 0.8 * GameManipulator.length

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
                (GameManipulator.width * sensor.length) / sensor.step[0])

            # Save lastValue
            sensor.lastValue = sensor.value

            # Calculate the Sensor value
            if end:
                sensor.value = (end[0] - start[0]) / (GameManipulator.width * sensor.length)

                # Calculate size of obstacle
                endPoint = Scanner.scanUntil(
                  [end[0] + 75, end[1]],
                  [-2, 0],
                  COLOR_DINOSAUR,
                  False,
                  75 / 2
                )

                # If no end point, set the start point as end
                if not endPoint:
                    endPoint = end

                sizeTmp = (endPoint[0] - end[0]) / 100.0
                if GameManipulator.points == sensor.lastScore:
                  # It's the same obstacle. Set size to "max" of both
                    sensor.size = max(sensor.size, sizeTmp)
                else:
                    sensor.size = sizeTmp


                # We use the current score to check for object equality
                sensor.lastScore = GameManipulator.points


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

            startTime = datetime.now()

        # Compute points
        GameManipulator.computePoints()

        # Call sensor callback (to act)
        GameManipulator.onSensorData && GameManipulator.onSensorData()


# Set action to game
# Values=
#  0.00 to  0.45= DOWN
#  0.45 to  0.55= NOTHING
#  0.55 to  1.00= UP (JUMP)
gameManipulator = GameManipulator()
gameManipulator.lastOutputSet = 'NONE'
gameManipulator.lastOutputSetTime = 0

    def setGameOutput(output):

        GameManipulator.gameOutput = output
        GameManipulator.gameOutputString = GameManipulator.getDiscreteState(output)

        if (GameManipulator.gameOutputString == 'DOWN'):
          # Skew
          pyautogui.keyUp('up')
          pyautogui.keyDown('down')
        elif (GameManipulator.gameOutputString == 'NORM'):
          # DO Nothing
          pyautogui.keyUp('up')
          pyautogui.keyUp('down')
        else:

            # Filter JUMP
            if (GameManipulator.lastOutputSet != 'JUMP'):
                GameManipulator.lastOutputSetTime = time.time()

            # JUMP
            # Check if hasn't jump for more than 3 continuous secconds
            if (time.time() - GameManipulator.lastOutputSetTime < 3000):
                pyautogui.keyUp('down')
                pyautogui.keyDown('up')
            else:
                pyautogui.keyUp('up')
                pyautogui.keyDown('down')

          gameManipulator.lastOutputSet = GameManipulator.gameOutputString


#
# Simply maps an real number to string actions
#
    def getDiscreteState(value):
        if value < 0.45:
            return 'DOWN'
        elif value > 0.55:
            return 'JUMP'

 
        return 'NORM'


    # Click on the Starting point
    # to make sure game is focused
    def focusGame()
        pyautogui.moveTo(gameManipulator.offset[0], gameManipulator.offset[1])
        pyautogui.click()
