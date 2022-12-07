try: from cmu_cs3_graphics import *
except: from cmu_graphics import *

from runAppWithScreens import *
from dependencies import *


######## SPLASH SCREEN ##########
def splash_onScreenStart(app):
    app.instructions = '''
    Move with arrow keys
    Press i to view tray contents
    Press space to complete task when near table
    Get drinks and bills from drink area
    Get food orders from kitchen
    Press number to view that table's order
    '''
    app.splashScreenImg = CMUImage(Image.open('images/splashPic.png'))

def splash_redrawAll(app):
    drawImage(app.splashScreenImg, 0,0)

def drawInstructions(app):
    i = 0
    for line in app.instructions.splitlines():
        drawLabel(line, app.width/2, 250 + i*25, size=24, align='center')
        i+=1

def splash_onKeyPress(app, key):
    if key=='space':
        setActiveScreen('tutorial')

def splash_onMousePress(app, mouseX, mouseY):
    # Check if clicked play button
    buttonLeft1 = 71
    buttonTop = 68
    buttonLeft2 = 616
    buttonWidth = 218
    buttonHeight = 115
    if ((buttonLeft1 <= mouseX <= buttonLeft1+buttonWidth or
        buttonLeft2 <= mouseX <= buttonLeft2+buttonWidth) and
        buttonTop <= mouseY <= buttonTop+buttonHeight):
        setActiveScreen('tutorial')
