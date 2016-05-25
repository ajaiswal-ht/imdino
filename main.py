from game_manipulator import GameManipulator
from learner import Learner
import pyautogui
from ui import UI
from threading import Timer



# Initialize Game
def main():
    GameManipulator.findGamePosition();


    # Check for found game
    if (GameManipulator.offset):
      # Uncomment this line to debug the
      # starting point of sensor (Check if it's detecting it correcly)

      # robot.moveMouse(GameManipulator.offset[0]+GameManipulator.sensors[0].offset[0],
      #    GameManipulator.offset[1] + GameManipulator.sensors[0].offset[1]);

        pyautogui.moveTo((GameManipulator.offset[0], GameManipulator.offset[1]))
    else:
        print 'FAILED TO FIND GAME!'
        return
    # Initialize UI
    UI(GameManipulator, Learner)


    # Init Learner
    Learner(GameManipulator, UI, 12, 4, 0.2)


    # Start reading game state and sensors
    Timer(40,GameManipulator.readSensors)
    Timer(GameManipulator.readGameState, 200)

if __name__ == "__main__":
    main()
