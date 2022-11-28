try: from cmu_cs3_graphics import *
except: from cmu_graphics import *

from runAppWithScreens import *
import random

##### CITATIONS #####
# Checking if point is in the plates: https://math.stackexchange.com/questions/76457/check-if-a-point-is-within-an-ellipse

####### KITCHEN SCREEN ##################
def kitchen_onScreenStart(app):
    app.tixBarTop = 40
    app.itemCookTime = 60
    app.trayX2, app.trayY2 = 780, 400

######## CLASSES

class Plate:
    width = 800/3 - 60
    height = 20
    def __init__(self, item):
        self.cx = -100
        self.cy = -100
        self.ready = False
        self.item = item

    def draw(self):
        drawOval(self.cx, self.cy, Plate.width, Plate.height, fill='white', border='black')
        if self.item != None:
            color = 'red'
            drawCircle(self.cx, self.cy-10, 20, fill=color)

    def pointInPlate(self, x, y):
        yRad = Plate.height/2
        xRad = Plate.width/2
        region = ((x-self.cx)**2)/(xRad**2) + ((y-self.cy)**2)/(yRad**2)
        return region<=1

    def __repr__(self):
        return repr(self.item)

    def equiv(self, other):
        return self.item == other

######## END OF CLASSES

def kitchen_redrawAll(app):
    drawRect(0,0, app.width, app.height, fill=app.colors['lightBrown'])
    drawBackground(app)
    drawTickets(app)
    drawWaitress(app)
    drawAlert(app)
    drawHelpOverlays(app)
    drawLabel('Press right to leave. Click plates to add them to tray.', app.width/2, 15, size=24)

def drawAlert(app):
    if app.alert!=None:
        msg = app.alert[0]
        width = len(msg)*10 + 20
        cx, cy = app.width/2, app.height-80 
        drawRect(cx, cy, width, 40, align='center', fill='white', border='black')
        drawLabel(msg, cx, cy, size = 20)

def drawHelpOverlays(app):
    overlayNum = 0
    height = 200
    width = 200
    if app.orderToShow!=None and app.orderToShow<len(app.tableData):
        order = app.tableData[app.orderToShow].order
        drawRect(app.width/2, app.height/2, width, height, fill="white", 
                border='black', align='center')
        if order!= []:
            dist = (height*(7/8))/len(order)
            start = app.height/2 - height/2 + dist
            for i in range(len(order)):
                item = order[i]
                drawLabel(f'{item}', app.width/2, start+dist*i)
        else:
            drawLabel(f'No order yet for table {app.orderToShow}', app.width/2, app.height/2)
        overlayNum+=1
    if app.showInventory:
        drawRect(app.width/2, app.height/2, width, height, fill="white", 
                border='black', align='center')
        if app.tray.inventory != []:
            dist = (height*(7/8))/len(app.tray.inventory)
            start = app.height/2 - height/2 + dist
            for i in range(len(app.tray.inventory)):
                item = app.tray.inventory[i]
                drawLabel(f'{item}', app.width/2, start+dist*i)
        else:
            drawLabel("There's nothing on your tray", app.width/2, app.height/2)
        overlayNum+=1

def drawWaitress(app):
    img = app.waitress.imageList[1].picture
    drawImage(img, app.width-50, app.height-300, align='center', height=400, width=400, rotateAngle=-30) 
    app.tray.cx, app.tray.cy = app.trayX2, app.trayY2
    app.tray.draw(app.width/3-40, 30)
    for item in app.tray.inventory:
        if isinstance(item, Plate):
            item.draw()

def drawBackground(app):
    #countertop
    drawRect(0, app.height/2, app.width*(2/3), app.height/2, fill=app.colors['stucco'])
    drawRect(0, app.height/2, app.width*(2/3)+40, 30, fill=app.colors['cream'])
    # top bar
    drawRect(0, app.tixBarTop, app.width, 10, fill=app.colors['blackish'])

def drawTickets(app):
    tickets = getTickets(app, False)
    ticketHeight = 100
    ticketWidth = 60
    bTixDist = (app.width*(2/3) - 50)/3
    ticketDist = 0 if len(tickets)<=3 else (app.width - 40)/(len(tickets)-3)
    for i in range(len(tickets)):
        
        ticket = tickets[i]
        labelsAndHeights = ticket.getLabels(ticketHeight)
        # If it is first three, draw them below plates
        if i<3:
            leftX = app.width*(2/3)-70-(i*bTixDist) - ticketWidth
            drawRect(leftX, (app.height/2)+50, ticketWidth, ticketHeight, fill=app.colors['cream'])
            midX = leftX + ticketWidth/2
            for p in range(len(ticket.plates)):
                # draw plates 
                plate = ticket.plates[p]
                cy = app.height/2 - p*(Plate.height+20)
                # if plate not in app.tray.inventory:
                if not app.tray.contains([plate]):
                    plate.cx = midX
                    plate.cy = cy
                    plate.draw()
            for (label, height) in labelsAndHeights:
                realHeight = (app.height/2)+50+height
                drawLabel(label, leftX, realHeight, align='left', size=ticketHeight/7)
        # Otherwise, draw them up on the top bar ltr
        else:
            leftX = 50 + ticketDist*(i-3)
            drawRect(leftX, app.tixBarTop-10, ticketWidth, ticketHeight, fill=app.colors['cream'])
            for (label, height) in labelsAndHeights:
                realHeight = app.tixBarTop-10+height
                drawLabel(label, leftX, realHeight, align='left', size=ticketHeight/7)

def getTickets(app, onlyInProgress):
    ticketList = []
    for table in app.tableData:
        if not table.ticket.empty and not table.ticket.ran:
            if onlyInProgress: 
                if len(table.ticket.completedItems)!=len(table.ticket.order):
                    ticketList.append(table.ticket)
            else:
                ticketList.append(table.ticket)
    return sorted(ticketList)

def kitchen_onKeyPress(app, key):
    if key == 'right':
        setActiveScreen('floor')
    elif key == 'q':
        print(app.tray)
        print(app.tray.cx, app.tray.cy)
    manageHelpOverlays(app, key)

def manageHelpOverlays(app, key):
    if key.isnumeric():
        app.orderToShow = int(key)
    elif key == 'i':
        app.showInventory = True

def kitchen_onKeyRelease(app, key):
    app.orderToShow = None
    app.showInventory = False

def alert(app, message):
    app.alert = (message, app.steps)

def kitchen_onMousePress(app, mouseX, mouseY):
    # Check all displayed plates if they are clicked add to inventory
    tickets = getTickets(app, False)
    for ticket in tickets:
        plates = ticket.plates
        for plate in plates:
            if plate.pointInPlate(mouseX, mouseY):
                alert(app, f'{plate.item} added to tray')
                app.tray.inventory.append(plate)
                plate.cx = app.tray.cx
                plate.cy = app.tray.cy - len(app.tray.inventory)*Plate.height
                print(plate.cx, plate.cy)
        # If all plates are on the tray, the ticket has been ran
        if app.tray.contains(ticket):
            ticket.ran = True

def kitchen_onStep(app):
    if not app.paused:
        app.steps +=1
    # Take away alert if past time
    if app.alert!=None:
        alertStart = app.alert[1]
        if alertStart + app.alertLength < app.steps:
            app.alert = None
    manageTickets(app)

def manageTickets(app):
    # Get tickets
    tickets = getTickets(app, True)
    if tickets == []: return 
    # Add a little bit of work to the current ticket
    currentTicket = tickets[0]
    if app.steps - currentTicket.lastProgressMade >= app.itemCookTime:
        if len(currentTicket.plates)<len(currentTicket.order):
            newPlate = Plate(currentTicket.order[len(currentTicket.completedItems)])
            currentTicket.plates.append(newPlate)
        # Finish another item
        nextItem = currentTicket.order[len(currentTicket.completedItems)]
        currentTicket.completedItems.append(nextItem)
        currentTicket.lastProgressMade = app.steps
