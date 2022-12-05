try: from cmu_cs3_graphics import *
except: from cmu_graphics import *

from runAppWithScreens import *
import math
from dependencies import *

####### SERVER STATION SCREEN ##################
def station_onScreenStart(app):
    app.fountainWidth = app.width/3
    app.testTheta = 0
    app.cupList = [] #Contains cups that are not in cup stack
    app.cupHeld = None # index
    app.drinkHeld = None # index
    app.trayHeight = 30
    app.trayWidth = app.width/3 - 60
    app.printerDims = (app.width/36, (app.height/2)-50, ((app.width/6)*(2/3)), 50)
    app.trayX, app.trayY = app.width/3, app.height/2
    

def station_redrawAll(app):
    drawRect(0,0, app.width, app.height, fill='gray')
    drawLabel('ur in da server station', app.width/2, app.height/2-app.height/5, size=80)
    drawLabel('press left to get to floor', app.width/2, app.height/2+app.height/5, size=35)
    # Countertop
    drawRect(0, app.height/2, app.width, app.height/2, fill=app.colors['stucco'])
    drawRect(0, app.height/2, app.width, 30, fill=app.colors['cream'])
    # Receipt printer
    printerLeft, printerTop, printerWidth, printerHeight = app.printerDims
    drawRect(printerLeft, printerTop, printerWidth, 
                printerHeight, fill=app.colors['blackish'])
    drawRect(app.width/12, app.height/2-printerHeight-15, printerWidth*(2/3), 30, fill='white', align='center')
    drawLabel('click for receipts', app.width/36, app.height/2-printerHeight+20, fill='white', align='left')
    # Tray
    app.tray.cx, app.tray.cy = app.trayX, app.trayY
    app.tray.draw(app.trayWidth, app.trayHeight)
    for item in app.tray.inventory:
        if type(item)!=Cup:
            item.draw()
    drawFountain(app)
    # Draw Cup stack
    for i in range(5):
        cup = Cup(app.width*(11/12), app.height/2-35-i*24)
        cup.draw()
    # Draw all cups
    for i in range(len(app.cupList)):
        cup = app.cupList[i]
        cup.draw(180)
    # Instructions
    drawLabel('Press left to leave. Drag cups from cupstack. Fill cups by pressing drink button.', 
                app.width/2, app.height*(3/4), size=24)
    drawLabel('Drag them to your tray to add them to your tray.',
                app.width/2, app.height*(3/4)+30, size=24)
    drawAlert(app)
    drawHelpOverlays(app)

def drawAlert(app):
    if app.alert!=None:
        msg = app.alert[0]
        width = len(msg)*10 + 20
        cx, cy = app.width/2, app.height-80 
        drawRect(cx, cy, width, 40, align='center', fill='white', border='black')
        drawLabel(msg, cx, cy, size = 20)
    
def drawFountain(app):
    leftX = app.width/2
    width = app.width/3
    height = app.height/4
    drawRect(leftX, 0, width, height, fill=app.colors['blackish'])
    margin = 15
    innerWidth = width - margin*2
    drinkWidth = 60
    drinkDist = innerWidth / len(app.drinkLabels)
    for i in range(len(app.drinkLabels)):
        drink = app.drinkLabels[i]
        midX = margin + drinkDist*i + drinkWidth/2 + app.width/2
        if app.drinkHeld!=None and i == app.drinkHeld:
            gushWidth = 10
            drawRect(midX-gushWidth/2, app.height/4, gushWidth, 
                    app.height/4-Cup.cupHeight, fill=getDrinkColor(drink))
        drawRect(midX, app.height/4, drinkWidth, 30, align='center', fill=app.colors['stucco'])
        drawLabel(f'{drink}', midX, app.height/4)
        
def station_onKeyPress(app, key):
    if key == 'left':
        cleanStation(app)
        setActiveScreen('floor')
    elif key == 'up':
        app.testTheta += 10
    elif key == 'down':
        app.testTheta -= 10
    elif key == 'c':
        cleanStation(app)
    manageHelpOverlays(app, key)

def manageHelpOverlays(app, key):
    if key.isnumeric():
        app.orderToShow = int(key)
    elif key == 'i':
        app.showInventory = True
    elif key=='tab':
        app.showHelp = True

def cleanStation(app):
    app.cupList = []

def station_onStep(app):
    if not app.paused:
        app.steps +=1
    for cup in app.cupList:
        if cup.zone!=None:
            if cup.drink==None or cup.drink==app.drinkLabels[cup.zone]:
                cup.fillCup(app.drinkLabels[cup.zone])
    # Take away alert if past time
    if app.alert!=None:
        alertStart = app.alert[1]
        if alertStart + app.alertLength < app.steps:
            app.alert = None

def station_onMousePress(app, mouseX, mouseY):
    # Check if mouse on cupstack
    # Cupstack dims: 
    cupstackLeft = app.width*(11/12) - Cup.brimWidth/2
    cupstackRight = app.width*(11/12) + Cup.brimWidth/2
    cupstackBottom = app.height/2
    cupstackTop = app.height/2 - (2.4 * Cup.cupHeight)
    if (cupstackLeft<=mouseX<=cupstackRight and
        cupstackTop<=mouseY<=cupstackBottom):
        # Add a new cup to cuplist and set that cup to cupHeld
        newCup = Cup(mouseX, mouseY)
        app.cupList.append(newCup)
        app.cupHeld = len(app.cupList) - 1
    # Check if mouse is on cup in cuplist, set it to cupHeld
    else:
        for i in range(len(app.cupList)):
            cup = app.cupList[i]
            if cup.pointInCup(mouseX, mouseY):
                app.cupHeld = i
    # Check if mouse is on Drink
    width = app.width/3
    margin = 15
    innerWidth = width - margin*2
    drinkWidth = 60
    drinkDist = innerWidth / len(app.drinkLabels)
    for i in range(len(app.drinkLabels)):
        # width is drinkWidth, height is 30
        left = margin+drinkDist*i + app.width/2
        right = left+drinkWidth
        top = app.height/4 - 15
        bottom = app.height/4 + 15
        if (left<=mouseX<=right and top<=mouseY<=bottom):
            app.drinkHeld = i
            # If a drink is being filled, fill it
            for cup in app.cupList:
                zone = getDrinkZone(app, cup)
                if zone !=None and zone==i:
                    cup.zone = zone
    # Check if mouse on receipt printer
    xStart, yStart, width, height = app.printerDims
    if (xStart<=mouseX<=xStart+width and
        yStart<=mouseY<=yStart+height):
        setActiveScreen('printer')

def getDrinkZone(app, cup):
    cx, cy = cup.cx, cup.cy
    # If not in server station at all return none
    if cx<app.width/2 or cx>app.width*(5/6): return None
    # If outside of height strip return None
    if cy>app.height/2 or cy<app.height/3: return None
    # Otherwise look for zones
    margin = 15
    innerWidth = app.width/3 - margin*2
    zoneWidth = innerWidth / len(app.drinkLabels)
    for i in range(len(app.drinkLabels)):
        zoneStart = app.width/2 + margin + zoneWidth*i
        zoneEnd = app.width/2 + margin + zoneWidth*(i+1)
        if zoneStart<=cx<=zoneEnd:
            return i    

def station_onMouseDrag(app, mouseX, mouseY):
    if app.cupHeld!=None:
        cup = app.cupList[app.cupHeld]
        cup.cx, cup.cy = mouseX, mouseY

def station_onMouseRelease(app, mouseX, mouseY):
    if app.cupHeld!=None:
        # If it's in the tray, put in the tray inventory
        cup = app.cupList[app.cupHeld]
        x = cup.cx
        y = cup.cy + (Cup.cupHeight*.5)
        if app.tray.pointInTray(x, y, app.trayWidth, app.trayHeight) and not (cup in app.tray.inventory):
            drink = cup.drink if cup.drink!=None else 'nothingness'
            alert(app, f'Added cup of {drink} to tray')
            print('the cup is in the tray')
            app.tray.inventory.append(cup)
        # If it's not in the tray but it's in the inventory, remove it
        elif not app.tray.pointInTray(x, y, app.trayWidth, app.trayHeight):
            if cup in app.tray.inventory:
                app.tray.inventory.remove(cup)
    app.cupHeld = None
    app.drinkHeld = None
    for cup in app.cupList:
        cup.zone = None

def station_onKeyRelease(app, key):
    app.orderToShow = None
    app.showInventory = False
    app.showHelp = False

def getEndpoint(theta, radius, cx, cy):
    dx = radius * math.cos(math.radians(theta))
    dy = radius * math.sin(math.radians(theta))
    return cx+dx, cy+dy

def getThetaFromEndpoint(cx, cy, x, y):
    dy = y - cy
    dx = x - cx
    theta = math.atan(dy/dx)
    return theta

def inTopHalf(cx, cy, x, y):
    return y > cy

def distance(x, y, x1, y1):
    return ((x1-x)**2 +(y1-y)**2)**.5
