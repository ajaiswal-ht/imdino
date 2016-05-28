from game_manipulator import GameManipulator
from learner import Learner
import pyautogui
from ui import UI
from utils import ThreadJob
import threading
import logging
logger = logging.getLogger('main')


# Initialize Game
def main():
    GameManipulator.findGamePosition();


    # Check for found game
    if (GameManipulator.offset):
      # Uncomment this line to debug the
      # starting point of sensor (Check if it's detecting it correcly)

        pyautogui.moveTo((GameManipulator.offset[0]+GameManipulator.sensors[0].offset[0],
          GameManipulator.offset[1] + GameManipulator.sensors[0].offset[1]))
        #pyautogui.moveTo((GameManipulator.offset[0], GameManipulator.offset[1]))
    else:
        print 'FAILED TO FIND GAME!'
        return
    # Initialize UI

    global_stop_event = threading.Event()
    learner = Learner(GameManipulator,12, 4, 0.2)
    
   
    


    # Init Learner
    
    t= threading.Thread(target = UI(GameManipulator, learner, global_stop_event).run)
    t.start()
    logger.info('not coming here')

    # Start reading game state and sensors
    t1 = threading.Thread(target =ThreadJob(GameManipulator.readSensors, global_stop_event, 0.04).run)
    t1.start()
    logger.info('not coming here 2')
    ThreadJob(GameManipulator.readGameState, global_stop_event, 0.200).run()
    

if __name__ == "__main__":
    main()
