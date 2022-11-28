from cmu_cs3_graphics import *
from runAppWithScreens import *

from kitchen import *
from splash import *
from station import *
from printer import *

import random
import math
import copy
from PIL import Image

### CITATIONS
# https://realpython.com/python-sleep/
# https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm
# https://www.freecodecamp.org/news/dijkstras-shortest-path-algorithm-visual-introduction/

def floor_onScreenStart(app):
    #editor tools
    app.editorMode = False
    app.drawLine = False
    app.showNodes = False

    # dimensions
    app.sidebarWidth = 300
    margin = 15
    app.taskButtonWidth = app.sidebarWidth - margin
    app.width = 600 + app.sidebarWidth
    app.height = 600
    app.steps = 0
    app.paused = False
    app.stepsPerSecond = 20
    app.tableR = 30 # THIS DEFAULT VALUE IS ALSO NOW DEFINED IN TABLE CLASS
    app.doorWidth = app.doorMargin = 10
    app.colors = {'stucco': rgb(193, 79, 30), 
                    'cream': rgb(242, 225, 159),
                    'lightBrown': rgb(217, 178, 111),
                    'darkBrown': rgb(84, 57, 21),
                    'blackish': rgb(35, 28, 7)}
    app.tableColor = 'saddleBrown'
    app.easyLayout = [(98, 168), (222, 312), (366, 484), (432, 194)]
    app.midLayout = [(95, 150), (95, 315), (290, 150), (480, 150), (290, 315), 
                    (480, 315), (95, 490), (290, 490), (480, 490)]
    app.hardLayout = [(490, 183), (381, 169), (80, 143), (81, 216), 
                        (503, 341), (323, 382), (368, 544), 
                        (139, 374), (138, 460), (223, 175)]
    app.tempTableList = [(85, 82), (318, 134), (62, 217), 
                        (299, 283), (137, 325)]
    app.difficulty = 1 # int from 1 to 10
    app.lastEntrance = None
    app.tableData = [Table(cx+app.sidebarWidth, cy, 0, 5) for (cx, cy) in app.easyLayout]
    
    app.selectedTable = None
    app.stati = (['empty','say hi', 'give drinks', 'take order', 'give order', 'get dessert order',
                'give dessert', 'give bill', 'say bye (opt)'])
    app.drinks = ['Water', 'Coke', 'Lemonade']
    app.foods = (['sandwich', 'onion soup', 'jam', 'ham', 'toast', 'pumpkin pie',
                'seeds', 'jelly', 'funions'])
    app.desserts = (['chocolate cake', 'cheesecake', 'flan', 'tres leches', 'banana pie', 'muffin'])
    app.orderTime = 2*20
    app.pendingOrder = None
    app.currentOrder = None
    app.tempLineList = [(312, 111, 322, 248), (322, 248, 405, 250), 
                        (405, 250, 406, 409), (407, 409, 406, 407), 
                        (592, 418, 406, 408), (282, 481, 282, 599)]
    app.lineList = []
    app.newLine = ()

    # Alert help
    app.alert = None
    app.alertLength = app.stepsPerSecond * 3

    app.jumpDist = 10
    app.barHeight = 40 
    # Waitress Images
    app.downWaitress = Image.open('images/downWaitress.png')
    app.downWaitressImg = CMUImage(app.downWaitress)
    app.upWaitress = Image.open('images/upWaitress.png')
    app.upWaitressImg = CMUImage(app.upWaitress)
    app.rightWaitress = Image.open('images/rightWaitress.png')
    app.rightWaitressImg = CMUImage(app.rightWaitress)
    app.leftWaitress = Image.open('images/leftWaitress.png')
    app.leftWaitressImg = CMUImage(app.leftWaitress)
    # Refactoring Idea: store images with their key points (image, [key points])
    app.downWaitress = (app.downWaitressImg, [(-20, -2), (-12, 16), (0, 20), 
            (13, 14), (20, -2), (14, -8), (9, -19), (-10, -18), (-14, -10)])
    app.upWaitress = (app.upWaitressImg, [(-20, -2), (-12, 16), (0, 20), 
            (13, 14), (20, -2), (14, -8), (9, -19), (-10, -18), (-14, -10)])
    app.rightWaitress = (app.rightWaitressImg, [(9, 2), (9, 5), (2, 18), 
            (-6, 18), (-15, -4), (-5, -18), (2, -18), (5, -15)])
    app.leftWaitress = (app.leftWaitressImg, [(-9, 2), (-9, 5), (-2, 18), 
            (6, 18), (15, -4), (5, -18), (-2, -18), (-5, -15)])
    app.waitressImages = ([app.rightWaitress, app.downWaitress, 
                    app.leftWaitress, app.upWaitress])

    app.waitress = Waitress(app.waitressImages, 50+app.sidebarWidth, 100, 0, 0)
    app.tray = Tray(50+app.sidebarWidth, 100)
    # Currently max sprite width is just the largest distance any 
    # key point is from the center of the waitress
    app.maxSpriteHeight = app.maxSpriteWidth = 20
    # Customer Info
    newCustomerImageList = randCustomerFromBase(app.waitressImages)
    app.customerOrigin = app.width-100, 100
    app.customerOriginNode0 = (app.width+50, 80, (-1,-1))
    app.customerOriginNode1 = (app.width-50, 80, (-2,-2))
    app.destination = app.customerOrigin
    app.ghostHit = False, None
    startingPath = ['left', 'left', 'left', 'left','left','left',]
    #app.customerList = [[newCustomerImageList, *app.customerOrigin, 2, 2, startingPath, False]]
    app.customerList=[]
    app.customerJumpDist = 5

    app.orderToShow = None
    app.showInventory = False
    app.showHelp = False
    # For pathfinding
    app.nodeList = []
    app.edgeSet = set()
    app.nodeDist = 30
    app.tolerance = app.nodeDist * 2
    # Path finding testing tools
    app.findPath = False
    app.selectedStartNode = None
    app.selectedEndNode = None
    app.nodesOfPath = None
    layNodes(app)
    
    # Tasks <3
    #app.taskList = [Task('get drinks to', 3), Task('get napkin for', 1)]

###############
### CLASSES ###
###############

class DynamicImage:
    def __init__(self, picture, keypoints):
        self.picture = picture
        self.keypoints = keypoints

class Sprite:
    def __init__(self, imageList, cx, cy, dIndex, lastDIndex):
        self.imageList = [DynamicImage(image, keypoints) for (image, keypoints) in imageList]
        self.cx = cx
        self.cy = cy
        self.dIndex = dIndex
        self.lastDIndex = lastDIndex
        self.radius = 30 # HARDCODED RADIUS RADIUS SPRITE

class Customer(Sprite):
    def __init__(self, imageList, cx, cy, dIndex, lastDIndex, path, table):
        super().__init__(imageList, cx, cy, dIndex, lastDIndex)
        self.path = path
        self.seated = False
        self.table = table
        self.followers = []

    def addFollowers(self, app, numOfFollowers):
        for i in range(numOfFollowers):
            newImageList = randCustomerFromBase(app.waitressImages)
            cx = cy = -2
            path = [(-2, -2) for _ in range((i+1)*5)] + copy.deepcopy(self.path)
            follower = Customer(newImageList, cx, cy, 2, 2, path, self.table)
            self.followers.append(follower)
    
    def move(self):
        # Only move if not seated
        if not self.seated and self.path!=[]:
            self.lastDIndex = self.dIndex
            # get next direction from path
            cx, cy = self.path.pop(0)
            newDirection = getNewDirection(self.cx, self.cy, cx, cy)
            if newDirection!= None:
                self.dIndex = newDirection
            self.cx = cx
            self.cy = cy       
        if self.path == [] and not self.seated and self.table!=None:
            # Jump to an open seat
            seatedPos = None
            self.dIndex = 1
            for seat in self.table.seats:
                if not seat[1]: # if no one is sitting there
                    seatedPos = seat[0]
                    self.cx, self.cy = seatedPos[0], seatedPos[1]
                    seat[1] = True
                    self.seated = True
                    if self.table.status==0: 
                        self.table.addTask('say hi')
                        self.table.status = 1
                    return

class Waitress(Sprite):
    def __init__(self, imageList, cx, cy, dIndex, lastDIndex):
        super().__init__(imageList, cx, cy, dIndex, lastDIndex)
        self.message = None
        self.startedSpeaking = None
    
    def speak(self, message, time):
        self.message = message
        self.startedSpeaking = time

class Table():
    # [[coords], occupants, maxOccupancy]
    num = 0
    patience = 100
    demandItem = 0
    def __init__(self, cx, cy, occupants, maxOccupancy, radius=30):
        self.cx = cx
        self.cy = cy
        self.occupants = occupants
        self.maxOccupancy = maxOccupancy
        self.status = 0
        self.ticket = Ticket()
        self.order = []
        self.contents = []
        self.radius = radius
        self.num = Table.num
        self.tasks = []
        self.lastAttended = None
        self.bill = Bill(self.num) # Will maybe need to create a bill class but maybe also not
        Table.num += 1
        self.seats = [[getEndpoint((180/self.maxOccupancy)*p-150, self.radius, self.cx, self.cy), False] for p in range(4)]

    def __eq__(self, other):
        return (isinstance(other, Table) and self.cx==other.cx and 
                self.cy==other.cy and 
                self.occupants == other.occupants and
                self.maxOccupancy==other.maxOccupancy and
                self.status == other.status and 
                self.ticket == other.ticket and
                self.radius == other.radius)
    
    def demand(self, item):
        # Display that in speech bubble
        cx = self.cx + 2*self.radius
        cy = self.cy - 2*self.radius
        color = 'lightGreen' if Table.demandItem%2 == 0 else 'steelBlue'
        drawRect(cx, cy, 100, 40, align='center', fill=color, border='black')
        drawLabel(f'{item}', cx, cy)

    def addTask(self, task):
        self.tasks.append(Task(task, self.num))

class Bill:
    def __init__(self, num):
        self.items = []
        self.cost = 0
        self.table = num
    
    def getCost(self):
        cost = 0
        for item in self.items:
            cost += random.choice([19.95, 12.04, 2.01, 15.50])
        return int(cost*100)/100

    def addItems(self, itemList):
        self.items.extend(itemList)
        if self.items !=[]:
            self.cost = self.getCost()

    def __repr__(self):
        return f'Bill for Table {self.table}'

    def draw(self):
        pass

class Ticket:
    ticketNum = 0
    def __init__(self):
        self.empty = True
        self.order = []
        self.plates = []
        self.completedItems = []
        self.lastProgressMade = None
        self.ran = False

    def reset(self):
        self.empty = True
        self.order = []
        self.plates = []
        self.completedItems = []
        self.lastProgressMade = None
        self.ran = False

    def __repr__(self):
        return repr(self.order)
        
    def addItem(self, item):
        if self.empty:
            self.empty = False
            self.num = Ticket.ticketNum
            Ticket.ticketNum += 1
        self.order.append(item)

    def getLabels(self, ticketHeight):
        distance = ticketHeight*(9/10)/5 # HARDCODED 5 MAX AT TABLE
        fontSize = ticketHeight*(1/7)
        itemsWithDHeight = []
        startHeight = ticketHeight*(1/10)+fontSize
        for i in range(len(self.order)):
            dY = startHeight + distance*i
            itemsWithDHeight.append((self.order[i], dY))
        return itemsWithDHeight

    def __lt__(self, other):
        return self.num < other.num 

class Task:
    taskNum = 0
    def __init__(self, label, tableNum):
        self.label = label
        self.tableNum = tableNum
        self.priority = Task.taskNum
        Task.taskNum += 1
    
    def __lt__(self, other):
        return self.priority < other.priority

class Tray:
    def __init__(self, cx, cy):
        self.cx = cx
        self.cy = cy
        self.inventory = []
        self.capacity = 5

    def draw(self, width, height):
        drawOval(self.cx, self.cy, width, height, fill='steelBlue', border='black')
        for i in range(len(self.inventory)):
            item = self.inventory[i]
            p = 0
            if isinstance(item, Plate):
                cy = self.cy - Plate.height*p
                item.cx = self.cx
                item.cy = cy
                p+=1

    def pointInTray(self, x, y, width, height):
        yRad = height/2
        xRad = width/2
        region = ((x-self.cx)**2)/(xRad**2) + ((y-self.cy)**2)/(yRad**2)
        return region<=1

    def move(self, cx, cy):
        self.cx = cx
        self.cy = cy

    def contains(self, order):
        stringInventory = [repr(item) for item in self.inventory]
        if isinstance(order, Ticket):
            for plate in order.plates:
                if repr(plate) not in stringInventory:
                    return False
            return True
        elif len(order)==1 and isinstance(order[0], str) and order[0].count('Bill')>0: # If we are looking for a bill
            for item in stringInventory:
                if item == order[0]: 
                    print('its in there yuip')
                    return True
            return False
        else:
            for item in order:
                if repr(item) not in stringInventory:
                    return False
            return True

    def remove(self, order):
        print('attempting removal')
        stringInventory = [repr(item) for item in self.inventory]
        if isinstance(order, Ticket):
            for plate in order.plates:
                # if the plate is equiv to something in the inv, take it out then break
                for item in self.inventory:
                    if item.equiv(plate):
                        self.inventory.remove(item)
                        print('removed', item)
                        break
        elif len(order)==1 and isinstance(order[0], str) and order[0].count('Bill')>0: # If we are looking for a bill
            for item in self.inventory:
                if repr(item) == order[0]: 
                    self.inventory.remove(item)
        else:
            for item in order:
                for item2 in self.inventory:
                    if item2.equiv(item):
                        self.inventory.remove(item2)
                        print('removed', item2)
                        break

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
            color =  'red'
            drawCircle(self.cx, self.cy-10, 20, fill=color)

    def pointInPlate(self, x, y):
        yRad = Plate.height/2
        xRad = Plate.width/2
        region = ((x-self.cx)**2)/(xRad**2) + ((y-self.cy)**2)/(yRad**2)
        return region<=1

    def __repr__(self):
        return repr(self.item)

    def equiv(self, other):
        return isinstance(other, Plate) and self.item == other.item
##### END CLASSES #####

def randCustomerFromBase(imageList):
    newImageList = []
    # random hair color rgb
    hr, hg, hb = (random.randrange(0,256), random.randrange(0,256), 
                random.randrange(0,256)) 
    # random skin color rgb
    sr, sg, sb = (random.randrange(0,256), random.randrange(0,256), 
                random.randrange(0,256)) 
    for imageSet in imageList:
        sourceImage = imageSet[0].image
        rgbaImage = sourceImage.convert('RGBA')
        newImage = Image.new(mode='RGBA', size=rgbaImage.size)
        for x in range(newImage.width):
            for y in range(newImage.height):
                r, g, b, a = rgbaImage.getpixel((x,y))
                if (r, g, b) == (104, 58, 11): # this is the shade of her hair
                    newImage.putpixel((x,y),(hr,hg,hb, 255))
                elif (r, g, b) == (240, 207, 122): # this is shade of her skin
                    newImage.putpixel((x,y),(sr,sg,sb, 255))
                # elif (r, g, b) == (0, 0, 0): #if black, its background, make translucent
                #     newImage.putpixel((x,y),(sr,sg,sb, 0))
                else:
                    newImage.putpixel((x,y), (r,g,b,a))
        newImage = CMUImage(newImage)
        newImageList.append((newImage, imageSet[1]))
    return newImageList

def layNodes(app):
    # If there are no tables, don't proceed
    if app.tableData == []: 
        return
    validNodes = []
    # Lay nodes around each table at 4 points
    for i in range(len(app.tableData)):
        table = app.tableData[i]
        #cx, cy = table[0][0], table[0][1]
        id1, id2, id3, id4 = [(0,i*4+q) for q in range(4)]
        pos1, pos2, pos3, pos4 = [getEndpoint((180/table.maxOccupancy)*p-150, table.radius, table.cx, table.cy) for p in range(4)]
        validNodes.extend([(*pos1, id1), 
                            (*pos2, id2),
                            (*pos3, id3), 
                            (*pos4, id4)])
    # Get list of cx,cy of every node based on dimensions of board and dist btwn nodes
    margin = 40
    boardTopLeft = margin+app.sidebarWidth, app.barHeight+margin
    boardWidth = app.width - 2*margin - app.sidebarWidth
    boardHeight = app.height - app.barHeight - 2*margin
    nodeDist = app.nodeDist
    possibleNodes = getPossibleNodes(boardTopLeft, boardWidth, boardHeight, nodeDist)
    # Loop through list of cx,cy and add them to the node list if they are legal positions
    i = 0
    testImageList = [DynamicImage(image, keypoints) for (image, keypoints) in randCustomerFromBase(app.waitressImages)]
    while i<len(possibleNodes):
        cx, cy, id = possibleNodes[i]
        if not isLegalMove(app, cx, cy, testImageList, 1, None):
            possibleNodes.pop(i)
        else: i+=1
    # Note customer origin node must always be a valid node! That will be in table lay rules.
    app.nodeList = [app.customerOriginNode0] + [app.customerOriginNode1]+ validNodes + possibleNodes
    layEdges(app)

def getPossibleNodes(boardTopLeft, boardWidth, boardHeight, nodeDist):
    res = []
    startx, starty = boardTopLeft
    cols = math.ceil(boardWidth /nodeDist) +1
    rows = math.ceil(boardHeight /nodeDist) +1
    for row in range(rows):
        for col in range(cols):
            cx = startx + col*nodeDist
            cy = starty + row*nodeDist
            id = (row+1, col+1) # skips 0 case because 0 is for special nodes
            res += [(cx, cy, id)]
    return res

def layEdges(app):
    # Tolerance = how far away the nodes will be and still connect
    tolerance = app.tolerance
    edgeSet = set()
    possibleEdges = getPossibleEdges(app, tolerance)
    for edge in possibleEdges:
        startNode = edge[0], edge[1]
        endNode = edge[2], edge[3]
        if (isSafePath(app, startNode, endNode)  
            and isSafePath(app, endNode, startNode)):
            length = distance(*startNode, *endNode)
            weight = (10*length // tolerance)
            edgeSet.add((edge, weight))
    # add critical "unsafe" line from exit to entrance
    x1, y1 = app.customerOriginNode0[0], app.customerOriginNode0[1]
    x2, y2 = app.customerOriginNode1[0], app.customerOriginNode1[1]
    weight = weight = (10*distance(x1, y1, x2, y2) // tolerance)
    edgeSet.add(((x1, y1, x2, y2), weight))
    app.edgeSet = edgeSet

def isSafePath(app, startPoint, endPoint):
    # Cannot cross any lines
    # Tbc: Customer cannot cross lines when on this line, therefore we will
    #  project lines on either side of this line, one radius away, and check
    # if they intersect
    x, y, x2, y2 = startPoint[0], startPoint[1], endPoint[0], endPoint[1]
    dx, dy = abs(x2-x), abs(y2-y)
    if dx>dy:
        topLine = x, y+app.maxSpriteWidth, x2, y2+app.maxSpriteWidth
        bottomLine = x, y-app.maxSpriteWidth, x2, y2-app.maxSpriteWidth
    else:
        topLine = x+app.maxSpriteWidth, y, x2+app.maxSpriteWidth, y2
        bottomLine = x-app.maxSpriteWidth, y, x2-app.maxSpriteWidth, y2
    for line1 in app.lineList:
        #line2 = (startPoint[0], startPoint[1], endPoint[0], endPoint[1])
        if segmentsIntersect(line1, topLine)!=None:
            return False
        if segmentsIntersect(line1, bottomLine)!=None:
            return False
    # Cannot intersect any tables
    for table in app.tableData:
        if tableNearLine(app, (table.cx, table.cy), startPoint, endPoint):
            return False
    return True
    
def tableNearLine(app, tableCords, startPoint, endPoint):
    # Increasing tolerance increases how close a line can be to a table
    tolerance = 10
    cx, cy = tableCords[0], tableCords[1]
    startx, starty = startPoint
    endx, endy = endPoint
    midx = (startx+endx)/2
    midy = (starty+endy)/2
    radius = .5*distance(*startPoint, *endPoint)
    # Check if circle surrounding two lines includes the table
    return  (radius+app.tableR-tolerance>distance(cx, cy, midx, midy))

def getPossibleEdges(app, tolerance):
    edgeSet = set()
    for node in app.nodeList:
        cx, cy, id = node
        for node in app.nodeList:
            cx2, cy2, id2 = node
            if id!=id2 and not (id[0]==0 and id2[0]==0):      #skips double point and tablenode-to-tablenode
                if distance(cx, cy, cx2, cy2)<=tolerance:
                    edgeSet.add((cx, cy, cx2, cy2))
    return edgeSet


def drawOccupants(app, tableIndex):
    # get the max occupancy of the table
    table = app.tableData[tableIndex]
    maxOccupancy = table.maxOccupancy
    angle = 360/maxOccupancy
    for customer in range(table.occupants):
        thisAngle = customer*angle +20 
        x, y = getEndpoint(thisAngle, table.radius, table.cx, table.cy)
        drawCircle(x, y, 3, fill='red')

def getEndpoint(theta, radius, cx, cy):
    dx = radius * math.cos(math.radians(theta))
    dy = radius * math.sin(math.radians(theta))
    return cx+dx, cy+dy

def floor_redrawAll(app):
    drawCustomers(app)
    # if there are tables, draw em
    drawTables(app)
    # draw top bar, kitchen, drink station on top of table stuff
    for x, y, x1, y1 in app.lineList:
        drawLine(x, y, x1, y1, fill=app.colors['blackish'])
    drawOverlay(app)
    drawSidebar(app)
    
    drawWaitress(app)
    # draw keypoints
    colors = ['red', 'orange', 'yellow', 'green', 
    'blue', 'purple', 'black', 'gray', 'brown']
    cx, cy = app.waitress.cx, app.waitress.cy
    polygonCords = getCordsFromDeltaPoints(cx, cy, 
                    app.waitress.imageList[app.waitress.dIndex].keypoints, 
                    False)
    wrappedPolygonCords = getCordsFromDeltaPoints(cx, cy, 
                    app.waitress.imageList[app.waitress.dIndex].keypoints, 
                    True)
    # drawPolygon(*polygonCords, fill='turquoise')
    # for i in range(len(app.waitress.imageList[app.waitress.dIndex].keypoints)):
    #     x, y = wrappedPolygonCords[i]
    #     drawCircle(x, y, 2, fill=colors[i])
    if app.showNodes:
        drawNodesAndEdges(app)
    if (app.currentOrder !=None and app.selectedTable!=None 
        and app.currentOrder in app.tableData[app.selectedTable].order):
        app.tableData[app.selectedTable].demand(app.currentOrder)
    drawAlert(app)
    drawHelpOverlays(app)

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
    if app.showHelp:
        drawRect(0, 0, app.width, app.height, fill='white', opacity=80)
        drawInstructions(app)

def drawInstructions(app):
    i = 0
    for line in app.instructions.splitlines():
        drawLabel(line, app.width/2, 300 + i*25, size=24, align='center')
        i+=1
    
def drawTables(app):
    for i in range(len(app.tableData)):
        table = app.tableData[i]
        if app.selectedTable!=None:
            if i == app.selectedTable:
                drawCircle(table.cx, table.cy, table.radius, fill=app.tableColor, opacity=100)
                drawCircle(table.cx, table.cy, table.radius+3, fill=None, border=app.colors['darkBrown'])
                # Old drawing task in "thought bubbles" image.pngfunctionality... May revive later
                # if table.lastAttended!=None and app.steps - table.lastAttended>Table.patience:
                #     drawTask(app, table)
                drawContents(app, table)
            else:
                drawCircle(table.cx, table.cy, table.radius, fill=app.tableColor, opacity=80)
                drawContents(app, table)
        else:
            drawCircle(table.cx, table.cy, table.radius, fill=app.tableColor)
            drawContents(app, table)
        drawLabel(f'{table.num}', table.cx, table.cy-(table.radius/(5/4)), bold=True)
        
def drawContents(app, table):
    if len(table.contents)>=table.occupants:
        for i in range(table.occupants):
            point = getEndpoint((180/table.maxOccupancy)*i-150, table.radius*0.3, table.cx, table.cy)
            drawCircle(*point, 2, fill='green', border='black')
    if len(table.contents)>=2*table.occupants:
        for i in range(table.occupants):
            point = getEndpoint((180/table.maxOccupancy)*i-150, table.radius*0.4, table.cx, table.cy)
            drawCircle(*point, 10, fill='white', border='black')

def drawTask(app, table):
    cx, cy = table.cx + table.radius + 20, table.cy - table.radius - 20
    drawRect(cx, cy, 100, 20, align='center', fill='white', border='black')
    drawLabel(f'{app.stati[table.status]}', cx, cy)

def drawNodesAndEdges(app):
    for edge in app.edgeSet:
        edge, weight = edge
        drawLine(*edge)
        midpoint = (edge[0]+edge[2])/2, (edge[1]+edge[3])/2
        drawLabel(f'{weight}', *midpoint, bold=True)
    for node in app.nodeList:
        cx, cy, id  = node
        color = 'purple'
        if not (app.nodesOfPath== None) and(cx, cy) in app.nodesOfPath:
            color = 'red'
        drawCircle(cx, cy, 3, fill=color)

def drawCustomers(app):
    for customer in app.customerList:
        #if not customer.seated:
        drawImage(customer.imageList[customer.dIndex].picture, customer.cx, customer.cy, align='center')
        for follower in customer.followers:
            drawImage(follower.imageList[follower.dIndex].picture, follower.cx, follower.cy, align='center')

def getCordsFromDeltaPoints(cx, cy, deltaList, wrapped):
    res = []
    for i in range(len(deltaList)):
        dx, dy = deltaList[i]
        if wrapped:
            res.extend([(cx+dx, cy-dy)])
        else:
            res.extend([cx+dx, cy-dy])
    return res

def drawOverlay(app):
    #top bar
    drawRect(0, 0, app.width, app.barHeight, fill = app.colors['stucco'])
    drawLabel('Press tab for instructions.', 
                app.sidebarWidth+30, app.barHeight/2, size=18, fill='white', align='left')
    zeroDig = '0' if (app.steps//20)%60<10 else ''
    drawLabel(f'{(app.steps//20)//60}:{zeroDig}{(app.steps//20)%60}', 
                    app.width-70, app.barHeight/2, size = 24, align='left', fill='white')
    #kitchen
    height = 60
    width = 100
    drawRect(app.sidebarWidth, app.height-height, width, height, fill=app.colors['lightBrown'])
    drawLabel('Kitchen', width/2+app.sidebarWidth, app.height-(height/2), size=18)
    #door
    drawRect(app.width-app.doorWidth, app.barHeight + app.doorMargin, 
        app.doorWidth, 4*app.doorWidth, fill=app.colors['blackish'])
    
    # server station
    drawRect(app.width-width, app.height-height, width, height, fill='gray')
    drawLabel('Drinks', width/2+app.width-width, app.height-(height/2), size=18)

def drawSidebar(app):
    drawRect(0,0, app.sidebarWidth, app.height, fill=app.colors['cream'])
    margin = (app.sidebarWidth - app.taskButtonWidth)/2
    buttonSource = Image.open('images/buttonShape2.png')
    button = CMUImage(buttonSource)
    middle = app.sidebarWidth/2
    height = 50
    
    taskNum = 0
    taskList = getSortedTaskList(app)
    if taskList ==[]:
        msg = 'Check on your tables!'
    else:
        msg = 'To do:'
    drawLabel(msg, middle, margin+10, size = 24)
    for i in range(len(taskList)):
        task = taskList[i]
        drawImage(button, margin, (height+margin)*i+margin+24, width=app.taskButtonWidth, height=height)
        drawLabel(f'{task.label}, table {task.tableNum}', middle, (height+margin)*i+(height/2)+5+24, size = 24)
        taskNum +=1

def getSortedTaskList(app):
    unsortedList = []
    for i in range(len(app.tableData)):
        tasks = app.tableData[i].tasks
        for t in range(len(tasks)):
            unsortedList.append(tasks[t])
    return sorted(unsortedList)
    
def drawWaitress(app):
    img = app.waitress.imageList[app.waitress.dIndex].picture
    if app.waitress.dIndex==3:
        app.tray.draw(15, 4)
    drawImage(img, app.waitress.cx, app.waitress.cy, align='center')   
    if app.waitress.message!=None:
        cx, cy = app.waitress.cx+40, app.waitress.cy-40
        drawRect(cx, cy, 140, 25, fill='white', border='black', align='center')
        drawLabel(f'{app.waitress.message}', cx, cy)
    if app.waitress.dIndex!=3: 
        app.tray.draw(15, 4)

def makeNewCustomer(app):
    if not isOpenTable(app): 
        return
    newImageList = randCustomerFromBase(app.waitressImages)
    cx, cy = -100, -100

    # Choose table and get a path to that table
    tableChoice = getDestinationIndex(app)
    table = app.tableData[tableChoice]
    destinationSet = getDestNodesFromIndex(app, tableChoice)
    path = getCustomerPathFromNodePath(app, getPathFromNodes(app, app.customerOriginNode0, destinationSet))

    followerNum = random.randint(0, table.maxOccupancy-2)
    print(table.maxOccupancy)
    table.occupants += 1+followerNum
    newCustomer = Customer(newImageList, cx, cy, 2, 2, path, table)
    newCustomer.addFollowers(app, followerNum)
    app.customerList.append(newCustomer)

def isOpenTable(app):
    for table in app.tableData:
        if table.occupants == 0:
            return True
    return False

def getDestinationIndex(app):
    tableChoice = None
    while tableChoice==None:
        randomSelection = random.randint(0, len(app.tableData)-1)
        if app.tableData[randomSelection].occupants==0:
            tableChoice = randomSelection
    # Mark destination for debugging
    table = app.tableData[tableChoice]
    destx, desty = table.cx, table.cy+table.radius+5
    app.destination = destx, desty
    return tableChoice

def getDestNodesFromIndex(app, tableChoice):
    destIds = [(0,tableChoice*4+q) for q in range(4)]
    destIds = set(destIds)
    destNodes = set()
    for node in app.nodeList:
        cx, cy, id = node
        if id in destIds:
            destNodes.add((cx, cy))
    return destNodes

def getPathFromCords(app, coordinateList):
    if len(coordinateList[0])<2:
        return []
    directions = [(1, 0), (0,1), (-1, 0), (0, -1)]  # right, down, left, up
    directionNames = ['right', 'down', 'left', 'up']
    path = []
    for i in range(len(coordinateList)-1): #go through all but the last one
        startX, startY = coordinateList[i][0], coordinateList[i][1]
        endX, endY = coordinateList[i+1][0], coordinateList[i+1][1]
        dx = (endX - startX)//app.jumpDist
        dy = (endY - startY)//app.jumpDist
        if (dx,dy) in directions:
            step = directionNames[directions.index((dx, dy))]
            path += [step]
    return path

#Takes in startNode and set of endnodes
def getPathFromNodes(app, startNode, destinationNodes):
    
    # Each path = [weight, node1, node2, etc, destNode]
    startx, starty, id = startNode
    pathList = [[0, (startx, starty)]]
    visitedNodes = set()
    shortestPath = None
    leastPathWeight = None

    #Look for a path unless you've visited every node without finding one
    #while len(visitedNodes)<len(app.nodeList):

    while len(pathList)>0:
        currentPath = pathList.pop(0)
        currentNode = currentPath[-1]

        # Get all the edges that connect to that node
        connectingEdges = getConnectingEdges(app, currentNode)
        for edge in connectingEdges:
            line, weight = edge
            # For each edge, get the second point (nodey node)
            nextNode = line[2], line[3] 
            nextNodeId = getId(app, nextNode)
            # If the point is in the set of destinations, yay! 
            if nextNode in destinationNodes:
                # If there is no shortest path, it is shortest path and its weight leastWeight
                # If it is lighter than shortest path, it is new shortest path and its weight least weight
                candidateWeight = currentPath[0]+weight
                if shortestPath==None or candidateWeight<leastPathWeight:
                    shortestPath = [candidateWeight] + currentPath[1:] + [nextNode]
                    leastPathWeight = candidateWeight
            # If that point was visited already, lame
            if nextNode in visitedNodes:
                continue
            # If that point is another table not destination table, lame
            if nextNodeId[0] == 0:
                continue
            # New weight = path weight + edge weight
            visitedNodes.add(nextNode)
            newWeight = currentPath[0]+weight
            newPath = [newWeight] + currentPath[1:] + [nextNode]
            # Add to pathlist: currentPath but with adjusted weight + newNode
            pathList += [newPath]
        # If the least weight is less than every other pathweight, return shortest path
        if shortestPath!=None:
            numOfPaths = len(pathList)
            heavierPaths = 0
            for path in pathList:
                weight = path[0]
                if weight>=leastPathWeight:
                    heavierPaths += 1
            if numOfPaths==heavierPaths:
                return shortestPath
    print('Theres no possible path')
    return None

def getConnectingEdges(app, currentNode):
    cx, cy = currentNode[0], currentNode[1]
    res = []
    for edge in app.edgeSet:
        line, _ = edge
        x1, y1, x2, y2 = line
        if (cx==x1 and cy==y1):
            res += [edge]
    return res

def getId(app, nextNode):
    x,y = nextNode
    for node in app.nodeList:
        cx, cy, id = node
        if x==cx and y==cy:
            return id
    return None

def getCustomerPathFromNodePath(app, nodePath):
    if nodePath==None: return None
    # Node path will be [weight, (cx, cy), (cx, cy)] etc
    coords = nodePath[1:]
    fullPathOfCoordinates = []
    while len(coords)>1:
        startPoint = coords.pop(0)
        endPoint = coords[0]
        length = distance(*startPoint, *endPoint)
        steps = int(length // app.customerJumpDist)
        dx, dy = getXYFromLine(app, startPoint, endPoint)
        for i in range(steps):
            newX = startPoint[0] + dx*i
            newY = startPoint[1] + dy*i
            fullPathOfCoordinates += [(newX, newY)]
        fullPathOfCoordinates += [(endPoint)]
    return fullPathOfCoordinates

def getXYFromLine(app, startPoint, endPoint):
    x1, y1 = startPoint
    x2, y2 = endPoint
    if x1==x2:
        dx = 0
        dy = app.customerJumpDist
        if y2<y1: dy = -dy
    else:
        theta = math.atan((y2-y1)/(x2-x1))
        dx = app.customerJumpDist*math.cos(theta)
        dy = abs(app.customerJumpDist*math.sin(theta))
        if y2<y1: dy = -dy
        if x2<x1: dx = -dx
    return dx, dy

def tupleMatchesFirstTwoVals(theTuple, listOfTruples):
    for truple in listOfTruples:
        newple = (truple[0], truple[1])
        if newple==theTuple:
            return True
    return False

def floor_onKeyPress(app, key):
    original = app.tableData
    if (key=='right') or (key=='down') or (key=='left') or (key=='up'):
        handleWaitressMovement(app, key)
    elif key=='z' and app.editorMode:
        app.tableData.pop()
    elif key=='h':
        Table.num = 0
        app.lineList = [(x1+app.sidebarWidth, y1, x2+ app.sidebarWidth, y2) for (x1, y1,x2,y2) in app.tempLineList]
        app.tableData = [Table(cx+app.sidebarWidth, cy, 0, 5) for (cx, cy) in app.hardLayout]
        app.difficulty = 3
    elif key=='m':
        app.difficulty = 2
        Table.num = 0
        app.lineList = []
        app.tableData = [Table(cx+app.sidebarWidth, cy, 0, 5) for (cx, cy) in app.midLayout]
    elif key=='e':
        Table.num = 0
        app.difficulty = 1
        app.tableData = [Table(cx+app.sidebarWidth, cy, 0, 5) for (cx, cy) in app.easyLayout]
        app.lineList = []
    elif key=='c':
        makeNewCustomer(app)
    elif key=='C':
        app.customerList = []
    elif key=='N':
        app.showNodes = not app.showNodes
    elif key=='q':
        app.selectedStartNode = None
        app.selectedEndNode = None
        app.nodesOfPath = None
    elif key=='s':
        # Set debugging mode
        table = app.tableData[0]
        table.occupants = 4
        # Add items to order and add items to ticket
        order = ['jelly', 'jam', 'seeds', 'funions']
        table.order = order
        for item in order:
            table.ticket.addItem(item)
            table.ticket.lastProgressMade = app.steps
        # Add give order task to table.task
        table.tasks.append(Task('give order', table.num))
        table.status = 4
    elif key=='space':
        attemptTaskCompletion(app)
    elif key=='l':
        if app.customerList!=[]:
            customerLeave(app, app.customerList[0])
    elif key=='tab':
        app.showHelp = True
    # In case we have changed app.tableData:
    if original != app.tableData:
        layNodes(app)
    manageHelpOverlays(app, key)

def manageHelpOverlays(app, key):
    if key.isnumeric():
        app.orderToShow = int(key)
    elif key == 'i':
        app.showInventory = True

def handleWaitressMovement(app, key):
    #handle waitress movement and direction facing w arrow keys
    if app.currentOrder!=None:
        app.currentOrder = None
        app.pendingOrder = None
        alert(app, "Don't walk away when a guest is talking! Now you'll never know their order.")
    #app.selectedTable = None
    app.waitress.lastDIndex = app.waitress.dIndex
    cx, cy = app.waitress.cx, app.waitress.cy
    imageList = app.waitress.imageList
    if key=='right':
        app.waitress.dIndex = 0
        dx, dy = 1, 0
    elif key=='down':
        app.waitress.dIndex = 1
        dx, dy = 0, 1
    elif key=='left':
        app.waitress.dIndex = 2
        dx, dy = -1, 0
    elif key=='up':
        app.waitress.dIndex = 3
        dx, dy = 0, -1
    app.waitress.cx, app.waitress.cy = tryMove(app, cx, cy, dx, dy,
                imageList, app.waitress.dIndex, app.waitress.lastDIndex, 'wait')
    if waitressCrashed(app):
        handleCrash(app)
    app.tray.cx, app.tray.cy = app.waitress.cx+10, app.waitress.cy+10
    setSelectedTable(app)
    checkScreenSwitch(app)

def checkScreenSwitch(app):
    x, y = app.waitress.cx, app.waitress.cy
    # height width of kitch is 50 100
    # kitchen dimensions
    klowY = app.height - 60 + 10
    klowX = app.sidebarWidth
    khighY = app.height 
    khighX = app.sidebarWidth+90
    # server station dimensions
    slowY = app.height - 60 + 10
    slowX = app.width - 100
    shighY = app.height 
    shighX = app.width-100+90
    if klowX<=x<=khighX and klowY<=y<=khighY:
        app.waitress.cx = 100 + app.sidebarWidth + 20
        app.waitress.cy = app.height - 30
        app.tray.move(app.width-120, app.height-200)
        print(app.tray, 'is now', app.tray.cx, app.tray.cy)
        setActiveScreen('kitchen')
    elif slowX<=x<=shighX and slowY<=y<=shighY:
        app.waitress.cx = app.width - 100 - 20
        app.waitress.cy = app.height - 30
        app.tray.move(app.width/3, app.height/2)
        setActiveScreen('station')

def waitressCrashed(app):
    # ADD FOLLOWERS TO THIS
    # get list of lines in waitress polygon
    waitressPolygonPoints = getCordsFromDeltaPoints(app.waitress.cx, app.waitress.cy, 
        app.waitress.imageList[app.waitress.dIndex].keypoints, True)
    waitressPolygonLines = []
    for i in range(len(waitressPolygonPoints)-1):
        waitressPolygonLines.extend([(*waitressPolygonPoints[i], *waitressPolygonPoints[i+1])])
    waitressPolygonLines.extend([(*waitressPolygonPoints[-1], *waitressPolygonPoints[0])])
    #check if waitress is in any of the customer circles
    radius = app.waitress.imageList[app.waitress.dIndex].picture.image.width
    for i in range(len(app.customerList)):
        customer = app.customerList[i]
        if polygonPolygonIntersection(customer, app.waitress, waitressPolygonLines):
            return True
        for follower in customer.followers:
            if polygonPolygonIntersection(follower, app.waitress, waitressPolygonLines):
                return True
    return False

def polygonPolygonIntersection(object, subject, subjectLines):
    if distance(object.cx, object.cy, subject.cx, subject.cy)<=((object.radius)*2):
    #if she is check if any of the lines of their polygons intersect
        customerPolygonPoints = (getCordsFromDeltaPoints(object.cx, object.cy, 
        object.imageList[object.dIndex].keypoints, True))
        customerPolygonLines = []
        for i in range(len(customerPolygonPoints)-1):
            customerPolygonLines.extend([(*customerPolygonPoints[i], *customerPolygonPoints[i+1])])
        customerPolygonLines.extend([(*customerPolygonPoints[-1], *customerPolygonPoints[0])])
        for line in customerPolygonLines:
            # with list of pertinent lines, check to see if each line intersects
            for line2 in subjectLines:
                if segmentsIntersect(line, line2):
                    return True
    return False

def handleCrash(app):
    app.waitress.cx, app.waitress.cy = 30+app.sidebarWidth,70

        
def floor_onKeyHold(app, keys):
    for z in keys:
        if (z=='right') or (z=='down') or (z=='left') or (z=='up'):
            handleWaitressMovement(app, z)
    if ('l' in keys) and app.editorMode:
        app.drawLine = True
    if ('p' in keys): 
        app.findPath = True

def floor_onKeyRelease(app, key):
    app.orderToShow = None
    app.showInventory = False
    app.showHelp = False
    if key=='l':
        app.drawLine = False 
    if key=='p':
        app.findPath = False

# Takes in cx, cy, dIndex, last Dindex, returns new cx, cy
def tryOrientation(app, cx, cy, imageList, dIndex, lastDIndex):
    # directions: right, down, left, up
    if not isLegalMove(app, cx, cy, imageList, dIndex, None):
        #if it was going right, move it right, else left
        move = 2
        if dIndex==0 or lastDIndex==2:
            move = 1
        elif dIndex==2 or lastDIndex==0:
            move = -1
        #move = -1 if (dIndex ==2) else 1
        while not isLegalMove(app, cx, cy, imageList, dIndex, None):
            cx+=(1*move)
    return cx, cy

# Takes in cx, cy, dx, dy, image list, dirindex, last dirindex, spriteType
# Returns new cx, cy
def tryMove(app, cx, cy, dx, dy, imageList, dIndex, lastDIndex, spriteType):
    # check to see if switching the picture already made things illegal and adj
    cx, cy = tryOrientation(app, cx, cy, imageList, dIndex, lastDIndex)
    # move
    cx += dx*app.jumpDist
    cy += dy*app.jumpDist
    # check if move valid
    if not isLegalMove(app, cx, cy, imageList, dIndex, spriteType):
        # reset then try again pixel by pixel
        cx0, cy0 = cx, cy
        cx0 -= dx*app.jumpDist
        cy0 -= dy*app.jumpDist
        cx, cy = cx0, cy0
        while not isLegalMove(app, cx, cy, imageList, dIndex, spriteType):
            cx += dx
            cy += dy
            if abs(cx-cx0)>app.jumpDist or abs(cy-cy0)>app.jumpDist:
                cx, cy = cx0, cy0
                break
    return cx, cy

# Takes in cx, cy, imageList, direction index, spriteType returns T/F
def isLegalMove(app, cx, cy, imageList, dIndex, spriteType):
    # check if moving hit table
    objectWidth = (imageList[dIndex].picture.image.width)/(1.5)
    if hitTable(app, (cx, cy), imageList, dIndex, app.tableR)[0]: #app, object, imageList, dIndex
        tableHit = hitTable(app, (cx, cy), imageList, dIndex, app.tableR)[1]
        if spriteType==None:
            return False
        elif spriteType =='ghost':
            app.ghostHit = True, tableHit
            return False
        elif spriteType == 'wait':
            return False
        elif spriteType == 'cust':
            handleCustomerTableHit(app, tableHit, (cx, cy))
            return False
    # chheck if out of screen or in nav bar
    if ((app.sidebarWidth> cx-objectWidth or app.width-objectWidth<cx) or 
        (app.barHeight> cy-objectWidth) or
        (app.height-objectWidth<cy)):
        return False
    #check if crosses line! crosses not is on!
    # get list of lines in pertinent polygon
    polygonPoints = getCordsFromDeltaPoints(cx, cy, 
        imageList[dIndex].keypoints, True)
    polygonLines = []
    for i in range(len(polygonPoints)-1):
        polygonLines.extend([(*polygonPoints[i], *polygonPoints[i+1])])
    polygonLines.extend([(*polygonPoints[-1], *polygonPoints[0])])
    for line in app.lineList:
        # with list of pertinent lines, check to see if each line intersects
        for line2 in polygonLines:
            if segmentsIntersect(line, line2):
                return False
    return True

def setSelectedTable(app):
    waitRadius = 15
    nearness = 20
    for i in range(len(app.tableData)):
        table = app.tableData[i]
        if (distance(table.cx, table.cy, app.waitress.cx, app.waitress.cy)
                <=((waitRadius)+(table.radius+nearness))):
            app.selectedTable = i
            return
    app.selectedTable=None

#Clean up if you have time.
def segmentsIntersect(line, line2):
    slope1 = 'undefined' if line[2] ==line[0] else (line[3]-line[1])/(line[2]-line[0])
    if line[3]==line[1]: 
        slope1 = 0
    slope2 =  ('undefined' if line2[2] ==line2[0] 
                else (line2[3]-line2[1])/(line2[2]-line2[0]))
    if line2[3]==line2[1]: 
        slope2 = 0
    if slope1==slope2: 
        return None
    if slope1=='undefined':
        x, y = line2[:2]
        intercept2 = y - slope2*x
        xInt = line[0]
        yInt = slope2*x+intercept2
    elif slope2=='undefined':
        x, y = line[:2]
        intercept1 = y - slope1*x
        xInt = line2[0]
        yInt = slope1*x+intercept1
    #Now, seeing if they are 0 but Python is mean.
    elif slope1==0:
        x,y = line[:2]
        yInt = y
        x, y = line2[:2]
        xInt = (yInt - y)/slope2 + x
    elif slope2==0:
        x,y = line2[:2]
        yInt = y
        x, y = line[:2]
        xInt = (yInt - y)/slope1 + x
    else:
        x,y = line[:2]
        intercept1 = y - slope1*x
        x, y = line2[:2]
        intercept2 = y - slope2*x
        xInt = (intercept2 - intercept1)/(slope1-slope2)
        yInt = slope1*xInt + intercept1
    # check if x and y are on both lines
    minx1, miny1 = min(line[0], line[2]), min(line[1], line[3])
    maxx1, maxy1 = max(line[0], line[2]), max(line[1], line[3])
    minx2, miny2 = min(line2[0], line2[2]), min(line2[1], line2[3])
    maxx2, maxy2 = max(line2[0], line2[2]), max(line2[1], line2[3])
    if ((minx1<=xInt<=maxx1) and 
        (minx2<=xInt<=maxx2) and
        (miny1<=yInt<=maxy1) and
        (miny2<=yInt<=maxy2)):
        return (xInt, yInt)
    return None

# Takes (cx, cy), radius, imageList, dIndex
def hitTable(app, object, imageList, dIndex, givenRadius):
    # First, check if it is in the circle
    radius = imageList[dIndex].picture.image.width
    for i in range(len(app.tableData)):
        table = app.tableData[i]
        if distance(table.cx, table.cy, *object)<=((radius)+givenRadius):
            # If it is in the circle, check if any of the key points is in the
            #table
            x, y = object
            points = getCordsFromDeltaPoints(x, y, 
                    imageList[dIndex].keypoints, True)
            #points = ([(x+dx, y-dy) 
            #        for dx, dy in app.waitressImages[app.directionIndex][1]])
            if pointInCircle(table.cx, table.cy, givenRadius, points): return True, i  
    return False, 0

# Function below takes in a list of points and a circ; True if any point in c
def pointInCircle(cx, cy, r, pointList):
    for point in pointList:
        x, y = point
        if distance(cx, cy, x, y)<=r:
            return True

def distance(x, y, x1, y1):
    return ((x1-x)**2 +(y1-y)**2)**.5

def floor_onMousePress(app, mouseX, mouseY):
    if app.editorMode: 
        if app.drawLine:
            if len(app.newLine)==2:
                app.lineList.append((app.newLine + (mouseX, mouseY)))
                app.newLine = ()
            else:
                app.newLine = (mouseX, mouseY)
        else:
            #if app.tableData == [[[]]]: app.tableData = []
            app.tableData.append(Table(mouseX, mouseY, 0, 5, 0, []))
    if app.findPath:
        ourNode = None
        for node in app.nodeList:
            if distance(node[0], node[1], mouseX, mouseY)<10:
                ourNode = node
        if app.selectedStartNode == None:
            app.selectedStartNode = ourNode
        elif app.selectedEndNode == None:
            app.selectedEndNode = ourNode
            desties = set()
            desties.add((app.selectedEndNode[0], app.selectedEndNode[1]))
            fullPath = getPathFromNodes(app, app.selectedStartNode, desties)
            app.nodesOfPath = fullPath[1:] if isinstance(fullPath, list) else None

def attemptTaskCompletion(app):
    if app.selectedTable==None: return
    table = app.tableData[app.selectedTable]
    # get table task
    if table.tasks==[]: return
    currentTask = table.tasks[0]
    # check if have things
    if equippedForTask(app, currentTask.label, table):
        # if yes execute task and pop it from list
        completeTask(app, currentTask.label, table) # This function should adjust last attended
        table.tasks.pop(0)
        table.status = (1+table.status)%(len(app.stati))
        # set new table task DONE IN COMPLETION FUNCTION
        # nextTask = app.stati[table.status]
        # table.tasks.append(nextTask)
    else:
        alert(app, "You aren't able to do that right now!")

def equippedForTask(app, task, table):
    # If you don't need anything in your tray, you're equipped
    if (task=='say hi' or task=='take order' or task=='get dessert order'
        or task=='say bye (opt)'):
        return True
    # If you need something, check that you have what you need
    if (task=='give drinks' or task=='give order' 
        or task=='give dessert' or task=='give bill'):
        # Check that you have the order in your tray
        order = table.order
        if app.tray.contains(order):
            return True
    # if task=='give bill':
    #     # Check that you printed the receipt and you have it
    #     if app.tray.contains(table.bill):
    #         return True

def completeTask(app, task, table):
    # ['empty','say hi', 'give drinks', 'take order', 'give order', 'get dessert order',
    # 'give dessert', 'give bill', 'say bye (opt)']
    if task=='say hi':
        greet(app, table)
    elif (task=='give drinks' or task=='give order' 
            or task=='give dessert' or task=='give bill'):
        deliverOrder(app, table)
        # Reset order to empty
    elif task=='take order':
        getOrder(app, table)
    elif task=='get dessert order':
        getDessertOrder(app, table)
    table.lastAttended = app.steps

def greet(app, table):
    # Say hi
    app.waitress.speak('Welcome! Want drinks?', app.steps)
    # Choose x random drinks, x = num at table, have them order it
    wants = []
    pendingOrder = dict()
    startTime = app.steps + 10
    print(table.occupants)
    for i in range(table.occupants):
        drink = random.choice(app.drinks)
        wants.append(drink)
        print(wants)
        pendingOrder[startTime+i*app.orderTime] = drink
    # Add drinks to order
    table.order = wants
    table.bill.addItems(wants)
    print(pendingOrder)
    app.pendingOrder = pendingOrder
    table.tasks.append(Task('give drinks', table.num))

def getOrder(app, table):
    # Choose x random food items, x = num at table, have them order it
    wants = []
    pendingOrder = dict()
    startTime = app.steps + 10
    for i in range(table.occupants):
        food = random.choice(app.foods)
        wants.append(food)
        pendingOrder[startTime+i*app.orderTime] = food
    # Add foods to order
    table.order = wants
    table.bill.addItems(wants)
    app.pendingOrder = pendingOrder
    # Add items to order and add items to ticket
    for item in wants:
        table.ticket.addItem(item)
        table.ticket.lastProgressMade = app.steps
    # Add give order task to table.task
    table.tasks.append(Task('give order', table.num))

def deliverOrder(app, table):
    # Say here you go
    app.waitress.speak('Here ya go!', app.steps)
    # populate table with order contents
    table.contents += table.order
    # Remove items from inventory
    # for item in table.order:
    #     if app.tray.contains(item):
    #         print('delivering', app.tray.inventory, item)
    #         app.tray.remove(item)
    app.tray.remove(table.order)
    table.order = []
    if app.stati[table.status]=='give drinks':
        table.tasks.append(Task('take order', table.num))
    elif app.stati[table.status]=='give order':
        table.tasks.append(Task('get dessert order', table.num))
    else:
        table.order = [f'Bill for Table {table.num}']
        table.tasks.append(Task('give bill', table.num))

def getDessertOrder(app, table):
    # Choose x random food items, x = num at table, have them order it
    wants = []
    pendingOrder = dict()
    startTime = app.steps + 10
    for i in range(table.occupants):
        dessert = random.choice(app.desserts)
        wants.append(dessert)
        pendingOrder[startTime+i*app.orderTime] = dessert
    # Add foods to order
    table.order = wants
    table.bill.addItems(wants)
    app.pendingOrder = pendingOrder
    # Add items to order and add items to ticket
    table.ticket.reset()
    for item in wants:
        table.ticket.addItem(item)
        table.ticket.lastProgressMade = app.steps
    # Add give order task to table.task
    table.tasks.append(Task('give dessert', table.num))


def alert(app, message):
    app.alert = (message, app.steps)

def floor_onStep(app):
    if not app.paused:
        app.steps +=1
    #if app.steps%10==0:
    for i in range(len(app.customerList)):
        customer = app.customerList[i]
        if customer.seated and customer.table.status == len(app.stati)-1:
            # Customer should leave if it's time for them to leave
            if (app.steps - customer.table.lastAttended)>Table.patience:
                table = customer.table
                customerLeave(app, customer)
                resetTable(table)
                return
        customer.move()
        for follower in customer.followers:
            follower.move()   
    # Manage waitress talking
    if app.waitress.message!=None:
        if app.steps - app.waitress.startedSpeaking > 80:
            app.waitress.message = None
            app.waitress.startedSpeaking = None 
    # Manage customer talking
    if app.pendingOrder != None:
        if app.steps in app.pendingOrder.keys():
            Table.demandItem += 1
            app.currentOrder = app.pendingOrder[app.steps]
        # If we're past all of the order times, kill it
        if app.steps> max(app.pendingOrder.keys())+app.orderTime:
            app.pendingOrder = None
            app.currentOrder = None
    # Have customers come regularly
    if app.lastEntrance==None:
        makeNewCustomer(app)
        app.lastEntrance = app.steps
    else:
        # How many customers enter per 20 seconds is based on difficulty
        entranceInterval = 20 * 20 / app.difficulty
        if app.lastEntrance + entranceInterval < app.steps:
            makeNewCustomer(app)
            app.lastEntrance = app.steps
    # Take away alert if past time
    if app.alert!=None:
        alertStart = app.alert[1]
        if alertStart + app.alertLength < app.steps:
            app.alert = None
    
def customerLeave(app, customer):
    # Get path for customer to leave
    startNode = getNodeFromXY(app, int(customer.cx), int(customer.cy))
    if startNode==None: 
        print('Failed node find')
        return 
    path = getCustomerPathFromNodePath(app, 
                    getPathFromNodes(app, startNode, {(app.customerOriginNode0[0],app.customerOriginNode0[1])}))
    if path==None: 
        print('Failed path find')
        return 
    # Give it to them and their followers
    customer.path = path
    customer.seated = False
    customer.table = None
    for i in range(len(customer.followers)):
        follower = customer.followers[i]
        fpath = [(follower.cx, follower.cy) for _ in range((i+1)*5)] + copy.deepcopy(customer.path)
        follower.path = fpath
        follower.seated = False
        follower.table = None

def getNodeFromXY(app, x, y):
    for node in app.nodeList:
        if abs(node[0]-x)<app.customerJumpDist and abs(node[1]-y)<app.customerJumpDist:
            return node
    return None

def resetTable(table):
    table.occupants = 0
    table.status = 0
    table.ticket = []
    table.tasks = []
    table.lastAttended = None

# MOVED INTO CUSTOMER CLASS
def handleCustomerMovement(app, customer):
    # Only move if not seated
    if not customer.seated and customer.path!=[]:
        customer.lastDIndex = customer.dIndex
        # get next direction from path
        cx, cy = customer.path.pop(0)
        newDirection = getNewDirection(customer.cx, customer.cy, cx, cy)
        if newDirection!= None:
            customer.dIndex = newDirection
        customer.cx = cx
        customer.cy = cy
        if hitTable(app, (cx, cy), customer.imageList, customer.dIndex, app.tableR)[0]: #app, object, imageList, dIndex
            tableHit = hitTable(app, (cx, cy), customer.imageList, customer.dIndex, app.tableR)[1]
            handleCustomerTableHit(app, tableHit, (cx, cy))

# Takes in current x, current y, new x, new y, returns direction they should face
def getNewDirection(cx, cy, cx2, cy2):
    dx = cx2-cx
    dy = cy2 - cy
    if abs(dx)>abs(dy):
        if dx>0: return 0 # 0 = right
        else: return 2 # 2 = left
    elif abs(dy)>abs(dx):
        if dy>0: return 1 # 1 = down
        else: return 3 # 3 = up
    elif abs(dy)==abs(dx):
        return None

def main():
    runAppWithScreens(initialScreen='splash', width=900, height=600)

main()