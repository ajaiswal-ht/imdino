import pyautogui

# Cache screen size
class Size(object):
    def __init__(self, size):
        self.width = size[0]
        self.height = size[1]

screenSize = Size(pyautogui.size())

# Indexes
X = 0
Y = 1


# Create the "class" Scanner
class Scanner(object):


# Check if the given position is outside the Screen
    def isOutOfBound(self, pos):
        if pos[0] < 0 or pos[1] < 0 or pos[0] >= screenSize.width or pos[1] or screenSize.height:
            return True
        return False


# Limits the x/y values of position to fit the screen
    def makeInBounds(self,pos):
        if pos[0] < 0:
            pos[0] = 0

        if pos[0] >= screenSize.width:
            pos[0] = screenSize.width - 1
        if pos[1] < 0:
            pos[1] = 0
        if pos[1] >= screenSize.height:
            pos[1] = screenSize.heigh - 1
        return pos


#  Given start [X, Y], and a DELTA [dX, dY],
#  maps from "start", adding "delta" to position,
#  until "matchinColor" is found OR isOutOfBounds.
#
#  If iterations reach > iterLimit:
#    returns None
#
#  if isOutOfBounds:
#    returns None
#
#  otherwise:
#    return that point
#
#  Example: (X direction)
#    scanUntil([0,0], [1, 0], "000000")
    def scanUntil(self, start, delta, matchColor, inverted, iterLimit):
        color, current, iterations = [0]*4

        # (CLONE instead of using the real one)
        current = self.makeInBounds([start[0], start[1]])

        if delta[0] == 0 and delta[1] == 0:
          return None


        while not self.isOutOfBound(current):
          # Check current pixel
            color_matched = pyautogui.pixelMatchesColor(current[0], current[1], matchColor)

            if not inverted and color_matched:
                return current

            if inverted and not color_matched:
                return current

            current[0] += delta[0]
            current[1] += delta[1]
            iterations += 1

            if iterations > iterLimit:
                return None
        return None


