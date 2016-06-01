# imdino
# Chrome dinasaur automated player


This project is implemented in python and tensorflow

It uses neural networks to train a system to play dinosaur game on chrome when internet is off.

## Requirements:
- redis
- flask
- tensorflow, numpy
- pyautogui for key presses
- npyscreen for displaying stats
- virtual environment


clone the code. and cd to project src folder of git project and
on MAC do following:

```
brew install redis
```

Create and activate virtual environment and run following
```
pip install -r requirements.txt
```

##For capturing data :

Run
```

python fl.py

```
and
copy javascript code from dino.js file.

Now open chrome browser, go offline, and open any website. No internet connection with dino game will appear on chrome.
Right click on the page and select inspect element option. click on console and paste the copied javasript.
now drag the top of console till lowest point possible.


## Running game
shorten the chrome window width by 2/3rd of screen size. open terminal and adjust its screen size to 1/3 rd space left.
Activate virtual environment, cd to project folder
and run
```
python main.py

```

If you get 'FAILED TO FIND GAME!' error, then check if dinosaur game is visible. 
If it is not working even after game is visible, try after removing multiplication by two at line number 6 and 7 in scanner.py.

#### bugs
- Interupttion is not working correctly and may cause system to hang.
- bug in Chrome, dino moves from its postion after many games, workaround - refreshing the dinosaur game page and copy the javascript code and paste in console as described above

#### Improvements Required:
- [ ] Interupttion is not working correctly and may cause system to hang.
- [ ] Docuement the code to explain more precisely.





Credits:

Project: https://github.com/aymericdamien/TensorFlow-Examples/

https://github.com/ivanseidel/IAMDinosaur