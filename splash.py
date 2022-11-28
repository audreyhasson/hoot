try: from cmu_cs3_graphics import *
except: from cmu_graphics import *

from runAppWithScreens import *

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

def splash_redrawAll(app):
    drawRect(0,0, app.width, app.height, fill=app.colors['stucco'])
    drawLabel('HOOTERS', app.width/2, app.height/2-app.height/5, size=100)
    drawLabel('press space to start!', app.width/2, app.height-100, size=24)
    drawInstructions(app)

def drawInstructions(app):
    i = 0
    for line in app.instructions.splitlines():
        drawLabel(line, app.width/2, 250 + i*25, size=24, align='center')
        i+=1

def splash_onKeyPress(app, key):
    if key=='space':
        setActiveScreen('floor')