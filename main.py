from game_manipulator import GameManipulator
from learner import Learner
import pyautogui
from ui import UI
from utils import ThreadJob
import threading



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

    global_stop_event = threading.Event()
    try:
        UI(GameManipulator, Learner, global_stop_event).run()
    except KeyboardInterrupt:
        global_stop_event.set()
        # clear log file
        with open('/tmp/ui.log','w'):
            pass
        raise SystemExit


    # Init Learner
    Learner(GameManipulator, UI, 12, 4, 0.2)


    # Start reading game state and sensors
    ThreadJob(GameManipulator.readSensors, global_stop_event, 0.04).run()
    ThreadJob(GameManipulator.readGameState,global_stop_event, 0.200).run()

if __name__ == "__main__":
    main()
