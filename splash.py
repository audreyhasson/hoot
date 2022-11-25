try: from cmu_cs3_graphics import *
except: from cmu_graphics import *

from runAppWithScreens import *



######## SPLASH SCREEN ##########
def splash_onScreenStart(app):
    pass

def splash_redrawAll(app):
    drawRect(0,0, app.width, app.height, fill=app.colors['stucco'])
    drawLabel('HOOTERS', app.width/2, app.height/2-app.height/5, size=100)
    drawLabel('press space to play!', app.width/2, app.height/2+app.height/5, size=35)

def splash_onKeyPress(app, key):
    if key=='space':
        setActiveScreen('floor')