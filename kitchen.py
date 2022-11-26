try: from cmu_cs3_graphics import *
except: from cmu_graphics import *

from runAppWithScreens import *

##### CITATIONS #####
# Checking if point is in the plates: https://math.stackexchange.com/questions/76457/check-if-a-point-is-within-an-ellipse

####### KITCHEN SCREEN ##################
def kitchen_onScreenStart(app):
    app.tixBarTop = 40
    app.itemCookTime = 200
    app.testPlate = Plate(None)

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
            if self.item == 'banana': color = 'yellow'
            else: color = 'brown'
            drawCircle(self.cx, self.cy-10, 20, fill=color)

    def pointInPlate(self, x, y):
        yRad = Plate.height/2
        xRad = Plate.width/2
        region = ((x-self.cx)**2)/(xRad**2) + ((y-self.cy)**2)/(yRad**2)
        return region<=1

    def __repr__(self):
        return f'plate of {self.item}'

######## END OF CLASSES

def kitchen_redrawAll(app):
    drawRect(0,0, app.width, app.height, fill=app.colors['lightBrown'])
    drawBackground(app)
    drawTickets(app)
    drawWaitress(app)
    app.testPlate.draw()

def drawWaitress(app):
    img = app.waitress.imageList[1].picture
    drawImage(img, app.width-50, app.height-300, align='center', height=400, width=400, rotateAngle=-30) 
    app.tray.draw(app.width/3-40, 30)
    for plate in app.tray.inventory:
        plate.draw()

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
                plate.cx = midX
                plate.cy = cy
                if plate not in app.tray.inventory:
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

def kitchen_onMousePress(app, mouseX, mouseY):
    if app.testPlate.pointInPlate(mouseX, mouseY):
        # Add plate to tray inventory
        app.tray.inventory.append(app.testPlate)
    # Check all displayed plates if they are clicked add to inventory
    tickets = getTickets(app, False)
    for ticket in tickets:
        plates = ticket.plates
        for plate in plates:
            if plate.pointInPlate(mouseX, mouseY):
                app.tray.inventory.append(plate)
        # If all plates are on the tray, the ticket has been ran
        if app.tray.contains(ticket):
            ticket.ran = True

def kitchen_onStep(app):
    if not app.paused:
        app.steps +=1
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
