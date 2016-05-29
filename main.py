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
    gm = GameManipulator()
    gm.findGamePosition();


    # Check for found game
    if (gm.offset):
      # Uncomment this line to debug the
      # starting point of sensor (Check if it's detecting it correcly)

       # pyautogui.moveTo((gm.offset[0]+GameManipulator.sensors[0].offset[0],
        #  GameManipulator.offset[1] + GameManipulator.sensors[0].offset[1]))
        pyautogui.moveTo((gm.offset[0], gm.offset[1]))
    else:
        print 'FAILED TO FIND GAME!'
        return
    # Initialize UI

    global_stop_event = threading.Event()
    learner = Learner(gm,12, 4, 0.2)
    
   
    


    # Init Learner
    try:
        #t= threading.Thread(target = UI(GameManipulator, learner, global_stop_event).run)
        #t.start()
        #logger.info('not coming here')

        # Start reading game state and sensors
        #t1 = threading.Thread(target =ThreadJob(GameManipulator.readSensors, global_stop_event, 0.04).run)
        #t1.start()
        #ThreadJob(gm.readSensors, global_stop_event, 0.04).start()
        #logger.info('not coming here 2')
        #ThreadJob(gm.readGameState, global_stop_event, 0.200).start()
        UI(gm, learner, global_stop_event).run()
    except KeyboardInterrupt:
        global_stop_event.set()
        # clear log file
        with open('/tmp/ui.log','w'):
            pass
        raise SystemExit
    

if __name__ == "__main__":
    main()
