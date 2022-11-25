try: from cmu_cs3_graphics import *
except: from cmu_graphics import *

from runAppWithScreens import *

####### SERVER STATION SCREEN ##################
def station_onScreenStart(app):
    app.fountainWidth = app.width/3
    app.drinks = ['Water', 'Coke', 'Lemonade']

def station_redrawAll(app):
    drawRect(0,0, app.width, app.height, fill='gray')
    drawLabel('ur in da server station', app.width/2, app.height/2-app.height/5, size=80)
    drawLabel('press left to get to floor', app.width/2, app.height/2+app.height/5, size=35)
    # Countertop
    drawRect(0, app.height/2, app.width, app.height/2, fill=app.colors['stucco'])
    drawRect(0, app.height/2, app.width, 30, fill=app.colors['cream'])
    # Receipt printer
    printerWidth = (app.width/6)*(2/3)
    printerHeight = 50
    drawRect(app.width/36, app.height/2-printerHeight, 
            printerWidth, printerHeight, fill=app.colors['blackish'])
    drawRect(app.width/12, app.height/2-printerHeight-15, printerWidth*(2/3), 30, fill='white', align='center')
    # Tray
    centerX = app.width/3
    height = 30
    width = app.width/3 - 60
    centerY = app.height/2
    drawOval(centerX, centerY, width, height, fill='steelBlue',)
    drawFountain(app)
    
def drawFountain(app):
    leftX = app.width/2
    width = app.width/3
    height = app.height/4
    drawRect(leftX, 0, width, height, fill=app.colors['blackish'])
    margin = 15
    innerWidth = width - margin*2
    drinkDist = innerWidth / len(app.drinks)
    for i in range(len(app.drinks)):
        drink = app.drinks[i]
        

def station_onKeyPress(app, key):
    if key == 'left':
        setActiveScreen('floor')

def station_onStep(app):
    if not app.paused:
        app.steps +=1