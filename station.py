try: from cmu_cs3_graphics import *
except: from cmu_graphics import *

from runAppWithScreens import *
import math

##### CLASSES ###########
class Cup():
    brimWidth = 50
    bottomWidth = brimWidth - 15
    cupHeight = 70
    def __init__(self, cx, cy):
        self.cx = cx
        self.cy = cy
        self.drink = None
        self.fullness = 0
        self.zone = None

    def drawCup(self, angle=0): # int, int, str, range from 0 to 1, degree (opt)
        cx, cy = self.cx, self.cy
        totalArea = Cup.bottomWidth* Cup.cupHeight + ( Cup.brimWidth- Cup.bottomWidth)* Cup.cupHeight
        topLeft = (cx -  Cup.brimWidth/2, cy -  Cup.cupHeight/2)
        topRight = (cx +  Cup.brimWidth/2, cy -  Cup.cupHeight/2)
        bottomLeft =  (cx -  Cup.bottomWidth/2, cy +  Cup.cupHeight/2)
        bottomRight = (cx +  Cup.bottomWidth/2, cy +  Cup.cupHeight/2)

        # Get new points after rotation applied
        bottomRight, bottomLeft = self.getRotatedPoints(bottomRight, bottomLeft, angle)
        topLeft, topRight = self.getRotatedPoints(topLeft, topRight, angle)

        for i in range(1, 5):
            startpoint = [topLeft, bottomLeft, bottomRight, topRight, topLeft][i]
            endpoint = [topLeft, bottomLeft, bottomRight, topRight, topLeft][i-1]
            drawLine(*startpoint, *endpoint, fill='black')
    
        if self.drink!=None and angle==180:
            color = getDrinkColor(self.drink)
            drinkTopLeft = (bottomLeft[0] - (( Cup.brimWidth- Cup.bottomWidth)/2)*self.fullness,
                            bottomLeft[1] -  Cup.cupHeight*self.fullness)
            drinkTopRight = (bottomRight[0] + ((Cup.brimWidth-Cup.bottomWidth)/2)*self.fullness,
                            bottomRight[1] - Cup.cupHeight*self.fullness)
            drawPolygon(*drinkTopLeft, *drinkTopRight, *bottomRight, *bottomLeft, fill=color)
                            
    def getRotatedPoints(self, leadingPoint, followingPoint, angle):
        cx, cy  = self.cx, self.cy
        # Steps for responsive rotation:
        # First point clockwise is leader, second point is always the same angle away from leader
        inTop = inTopHalf(cx, cy, *leadingPoint)
        addition = 180 if inTop else 0
        startAngle = math.degrees(getThetaFromEndpoint(cx, cy, *leadingPoint))
        angleBetween = 180 + math.degrees(getThetaFromEndpoint(cx, cy, *followingPoint)) - startAngle
        startAngle += addition
        # Get distance from cx to bottom right
        radius = distance(cx, cy, *leadingPoint)
        # Get new leading point using rotateAngle + OG angle
        newLeadingPoint = getEndpoint(startAngle+angle, radius, cx, cy)
        # Get new following point using rotateAngle + OG angle + following angle
        newFollowingPoint = getEndpoint(startAngle+angle+angleBetween, radius, cx, cy)
        return newLeadingPoint, newFollowingPoint
    
    def fillCup(self, drink):
        self.drink = drink
        if self.fullness <1:
            self.fullness += .01
    
    def pointInCup(self, x, y):
        left, right = self.cx - Cup.brimWidth/2, self.cx + Cup.brimWidth/2
        bottom, top = self.cy + Cup.cupHeight/2, self.cy - Cup.cupHeight/2
        return (left<=x<=right and top<=y<=bottom)

###### END OF CLASSES #####

####### SERVER STATION SCREEN ##################
def station_onScreenStart(app):
    app.fountainWidth = app.width/3
    app.testTheta = 0
    app.cupList = [] #Contains cups that are not in cup stack
    app.cupHeld = None # index
    app.drinkHeld = None # index

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
    height = 30
    width = app.width/3 - 60
    app.tray.draw(width, height)
    for plate in app.tray.inventory:
        plate.draw()
    drawFountain(app)
    # Draw Cup stack
    for i in range(5):
        cup = Cup(app.width*(11/12), app.height/2-35-i*24)
        cup.drawCup()
    # Draw all cups
    for i in range(len(app.cupList)):
        cup = app.cupList[i]
        cup.drawCup(180)
    
def drawFountain(app):
    leftX = app.width/2
    width = app.width/3
    height = app.height/4
    drawRect(leftX, 0, width, height, fill=app.colors['blackish'])
    margin = 15
    innerWidth = width - margin*2
    drinkWidth = 60
    drinkDist = innerWidth / len(app.drinks)
    for i in range(len(app.drinks)):
        drink = app.drinks[i]
        midX = margin + drinkDist*i + drinkWidth/2 + app.width/2
        if app.drinkHeld!=None and i == app.drinkHeld:
            gushWidth = 10
            drawRect(midX-gushWidth/2, app.height/4, gushWidth, 
                    app.height/4-Cup.cupHeight, fill=getDrinkColor(drink))
        drawRect(midX, app.height/4, drinkWidth, 30, align='center', fill=app.colors['stucco'])
        drawLabel(f'{drink}', midX, app.height/4)
        
def station_onKeyPress(app, key):
    if key == 'left':
        setActiveScreen('floor')
    elif key == 'up':
        app.testTheta += 10
    elif key == 'down':
        app.testTheta -= 10
    elif key == 'c':
        cleanStation(app)

def cleanStation(app):
    app.cupList = []

def station_onStep(app):
    if not app.paused:
        app.steps +=1
    for cup in app.cupList:
        if cup.zone!=None:
            if cup.drink==None or cup.drink==app.drinks[cup.zone]:
                cup.fillCup(app.drinks[cup.zone])

def station_onMousePress(app, mouseX, mouseY):
    # Check if mouse on cupstack
    # Cupstack dims: 
    cupstackLeft = app.width*(11/12) - Cup.brimWidth/2
    cupstackRight = app.width*(11/12) + Cup.brimWidth/2
    cupstackBottom = app.height/2
    cupstackTop = app.height/2 - (5 * (1/3) * Cup.cupHeight)
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
    drinkDist = innerWidth / len(app.drinks)
    for i in range(len(app.drinks)):
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

def getDrinkZone(app, cup):
    cx, cy = cup.cx, cup.cy
    # If not in server station at all return none
    if cx<app.width/2 or cx>app.width*(5/6): return None
    # If outside of height strip return None
    if cy>app.height/2 or cy<app.height/3: return None
    # Otherwise look for zones
    margin = 15
    innerWidth = app.width/3 - margin*2
    zoneWidth = innerWidth / len(app.drinks)
    for i in range(len(app.drinks)):
        zoneStart = app.width/2 + margin + zoneWidth*i
        zoneEnd = app.width/2 + margin + zoneWidth*(i+1)
        if zoneStart<=cx<=zoneEnd:
            return i    

def station_onMouseDrag(app, mouseX, mouseY):
    if app.cupHeld!=None:
        cup = app.cupList[app.cupHeld]
        cup.cx, cup.cy = mouseX, mouseY

def station_onMouseRelease(app, mouseX, mouseY):
    app.cupHeld = None
    app.drinkHeld = None
    for cup in app.cupList:
        cup.zone = None

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

def getDrinkColor(drink):
    if drink=='Coke':
        return rgb(74, 28, 8)
    if drink=='Water':
        return rgb(65, 144, 181)
    if drink=='Lemonade':
        return rgb(201, 197, 111)

def distance(x, y, x1, y1):
    return ((x1-x)**2 +(y1-y)**2)**.5
