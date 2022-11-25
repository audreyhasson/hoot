try: from cmu_cs3_graphics import *
except: from cmu_graphics import *

from runAppWithScreens import *

####### KITCHEN SCREEN ##################
def kitchen_onScreenStart(app):
    app.tixBarTop = 40
    pass

def kitchen_redrawAll(app):
    drawRect(0,0, app.width, app.height, fill=app.colors['lightBrown'])
    drawBackground(app)
    drawTickets(app)
    drawWaitress(app)
    # drawLabel('ur in da kitch', app.width/2, app.height/2-app.height/5, size=100)
    # drawLabel('press right to get to floor', app.width/2, app.height/2+app.height/5, size=35)

def drawWaitress(app):
    img = app.waitress.imageList[1].picture
    drawImage(img, app.width-50, app.height-200, align='center', height=400, width=400, rotateAngle=-30) 

def drawBackground(app):
    #countertop
    drawRect(0, app.height/2, app.width*(2/3), app.height/2, fill=app.colors['stucco'])
    drawRect(0, app.height/2, app.width*(2/3)+40, 30, fill=app.colors['cream'])
    # top bar
    drawRect(0, app.tixBarTop, app.width, 10, fill=app.colors['blackish'])

def drawTickets(app):
    tickets = getTickets(app)
    print(tickets)
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

def getTickets(app):
    ticketList = []
    for table in app.tableData:
        if not table.ticket.empty:
            print('nonempy', table.ticket)
            ticketList.append(table.ticket)
    return sorted(ticketList)

def kitchen_onKeyPress(app, key):
    if key == 'right':
        setActiveScreen('floor')

def kitchen_onStep(app):
    if not app.paused:
        app.steps +=1