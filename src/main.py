import logging
import threading

from game_manipulator import GameManipulator
from learner import Learner
from ui import UI

logger = logging.getLogger('main')
def main():
    #Initialize Game manipulator
    gm = GameManipulator()
    gm.findGamePosition()

    # Check for found game
    if (not gm.offset):
        print 'FAILED TO FIND GAME!'
        return
    gm.focusGame()
    # Initialize UI

    global_stop_event = threading.Event()

    # Init Learner
    learner = Learner(gm,12, 4, 0.2)
    try:
        # Initialize UI and start the game
        UI(gm, learner, global_stop_event).run()
    except KeyboardInterrupt:
        global_stop_event.set()
        learner.interuptted = True
        # clear log file
        with open('/tmp/ui.log','w'):
            pass
        raise SystemExit
    

if __name__ == "__main__":
    main()
