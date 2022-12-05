from cmu_cs3_graphics import *
from runAppWithScreens import *

from kitchen import *
from splash import *
from station import *
from printer import *
from dependencies import *

import random
import math
import copy
from PIL import Image

### CITATIONS
# https://realpython.com/python-sleep/
# https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm
# https://www.freecodecamp.org/news/dijkstras-shortest-path-algorithm-visual-introduction/
# https://math.stackexchange.com/questions/103556/circle-and-line-segment-intersection
# https://python.plainenglish.io/how-to-dynamically-declare-variables-inside-a-loop-in-python-21e6880aaf8a



def floor_onScreenStart(app):
    #editor tools
    app.editorMode = True
    app.drawLine = False
    app.showNodes = False
    app.testCircle = (750, 300, 30)
    app.tableNodes = []

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
                    (480, 315), (290, 490), ]
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
                'give dessert', 'give bill', 'wait for tip', 'pick up tip'])
    app.drinks = {'Water': 0.00, 'Coke': 2.50, 'Lemonade': 2.50, 'Sprite': 2.50}
    app.drinkLabels = list(app.drinks.keys())
    app.foods = ({'sandwich': 7.99, 'onion soup': 12.99, 'jam': 3.09,
                  'ham': 5.00, 'toast': 4.50, 'pumpkin': 12.99,
                  'seeds': 10.99, 'jelly': 3.10, 'funions': 3.44})
    app.desserts = ({'chocolate cake':12.00, 'cheesecake':2.00, 
                    'flan':8.00, 'tres leches':17.59, 'banana pie':1.50, 'muffin':2.50})
    app.menu = app.drinks | app.foods | app.desserts
    app.moneyMade = 0
    # Order time determines how long one order is displayed in speech bubble
    app.orderTime = 1*20
    app.pendingOrder = None
    app.currentOrder = None
    app.tempLineList = [(312, 111, 322, 248), (322, 248, 405, 250), 
                        (405, 250, 406, 409), (407, 409, 406, 407), 
                        (592, 418, 406, 408), (282, 481, 282, 599)]
    app.lineList = []
    # These lines outline the walls
    app.boundaryLines = [(299, 539, 327, 70), (328, 68, 868, 65), (868, 66, 896, 537),
                        (299, 541, 399, 540), (899, 538, 800, 540)]
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
    app.downWaitress = ([app.downWaitressImg], [(-20, -2), (-12, 16), (0, 20), 
            (13, 14), (20, -2), (14, -8), (9, -19), (-10, -18), (-14, -10)])
    app.upWaitress = ([app.upWaitressImg], [(-20, -2), (-12, 16), (0, 20), 
            (13, 14), (20, -2), (14, -8), (9, -19), (-10, -18), (-14, -10)])
    app.rightWaitress = ([app.rightWaitressImg], [(9, 2), (9, 5), (2, 18), 
            (-6, 18), (-15, -4), (-5, -18), (2, -18), (5, -15)])
    app.leftWaitress = ([app.leftWaitressImg], [(-9, 2), (-9, 5), (-2, 18), 
            (6, 18), (15, -4), (5, -18), (-2, -18), (-5, -15)])
    app.waitressImages = ([app.rightWaitress, app.downWaitress, 
                    app.leftWaitress, app.upWaitress])

    app.waitress = Waitress(app.waitressImages, 50+app.sidebarWidth, 100, 0, 0)
    #initOwlImages(app)
    owlBaseImage = Image.open('images/first4owls.png')
    printStatement = "print('i want this to please please work', (14+3))"
    exec(printStatement)
    cleverInitOwlImages(app, owlBaseImage)
    app.tray = Tray(50+app.sidebarWidth, 100)
    # Currently max sprite width is just the largest distance any 
    # key point is from the center of the waitress
    app.maxSpriteHeight = app.maxSpriteWidth = 20

    #  PIC SOURCEs
    app.tablePic = Image.open('images/pureTable.png')
    app.tablePic = CMUImage(app.tablePic)
    app.backgroundIm = Image.open('images/paleBackground.png')
    app.backgroundIm = CMUImage(app.backgroundIm)
    app.wallImage = Image.open('images/walls.png')
    app.wallImage = CMUImage(app.wallImage)
    app.doorCover = Image.open('images/doorCover.png')
    app.doorCover = CMUImage(app.doorCover)
    app.kitchenBackground = Image.open('images/kitchenInnards.png')
    app.kitchenBackground = CMUImage(app.kitchenBackground)
    app.toDoImage = Image.open('images/toDo.png')
    app.toDoImage = CMUImage(app.toDoImage)
    buttonSource = Image.open('images/buttonShape2.png')
    buttonSource = makeNewColorImage(buttonSource, (219,198,186))
    app.buttonImg = CMUImage(buttonSource)
    app.settingsImage = Image.open('images/gearPlaceholder.jpg')
    app.settingsImage = CMUImage(app.settingsImage)
    owls = Image.open('images/first4owls.png')
    app.allOwlsImage1 = CMUImage(owls.crop((35, 13, 135, 113)))

    #For activating settings screen
    app.settingsTopLeft = app.width-70, 2
    app.sWidth=40
    app.sHeight=34

    # Customer Info
    newCustomerImageList = randCustomerFromBase(app.waitressImages)
    app.customerOrigin = app.width-100, 100
    app.customerOriginNode0 = (app.width+50, 125, (-1,-1))
    app.customerOriginNode1 = (app.width-50, 125, (-2,-2))
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
    app.nodeDist = 20
    app.tolerance = app.nodeDist * 3
    # Path finding testing tools
    app.findPath = False
    app.selectedStartNode = None
    app.selectedEndNode = None
    app.nodesOfPath = None
    layNodes(app)

def initOwlImages(app):
    # START WITH Version 0 images
    # ALL IMAGES GET OPENED THEN GO WITH THEIR KEYPOINTS
    downStill = Image.open('images/owlDownStill1.png')
    downStill = CMUImage(downStill)
    down1 = Image.open('images/owlDownWalk01.png')
    down1 = CMUImage(down1)
    right1 = Image.open('images/owlRightWalk01.png')
    right1 = CMUImage(right1)
    rightStill = right1 # no image rn
    up1 = Image.open('images/owlUpStill1.png')
    up1 = CMUImage(up1)
    upStill = up1 # no img rn
    left1 = Image.open('images/owlLeftWalk01.png')
    left1 = CMUImage(left1)
    leftStill = left1 # no img rn
    # Motion images (v2)
    down2 = Image.open('images/owlDownWalk11.png')
    down2 = CMUImage(down2)
    right2 = Image.open('images/owlRightWalk01.png') # Only one right image atm...
    right2 = CMUImage(right2)
    up2 = Image.open('images/owlUpStill1.png') # Only one up image
    up2 = CMUImage(up2)
    left2 = Image.open('images/owlLeftWalk11.jpg')
    left2 = CMUImage(left2)
    # HELLO
    rightOwl = ([rightStill, right1, right2,], [(-20, -2), (-12, 16), (0, 20), 
            (13, 14), (20, -2), (14, -8), (9, -19), (-10, -18), (-14, -10)])
    upOwl = ([upStill, up1, up2], [
        (-15, 24), (-12, 19), (0, 20), 
        (11, 19), (14, 24), (18, 6), (21, -4), 
        (21, -13), (9, -25), (-11, -25), (-23, -13), 
        (-23, -4), (-19, 6)])
    leftOwl = ([leftStill, left1, left2], [(9, 2), (9, 5), (2, 18), 
            (-6, 18), (-15, -4), (-5, -18), (2, -18), (5, -15)])
    downOwl = ([downStill, down1, down2], [
        (-15, 24), (-12, 19), (0, 20), 
        (11, 19), (14, 24), (18, 6), (21, -4), 
        (21, -13), (9, -25), (-11, -25), (-23, -13), 
        (-23, -4), (-19, 6)])
    owlImages = ([rightOwl, downOwl, 
                    leftOwl, upOwl])
    app.owlWaitress = Waitress(owlImages, 50+app.sidebarWidth, 100, 0, 0)
    app.waitress = app.owlWaitress

# Takes in a base image of a bunch of owls and a 2D list of their keypoints
def cleverInitOwlImages(app, baseImage):
    left = 41
    width = 92
    # Next is a 2D list of all keypoints for the owls, which goes right, down, left, up
    keypoints = [[
        (-15, 24), (-12, 19), (0, 20), 
        (11, 19), (14, 24), (18, 6), (21, -4), 
        (21, -13), (9, -25), (-11, -25), (-23, -13), 
        (-23, -4), (-19, 6)], [
        (-15, 24), (-12, 19), (0, 20), 
        (11, 19), (14, 24), (18, 6), (21, -4), 
        (21, -13), (9, -25), (-11, -25), (-23, -13), 
        (-23, -4), (-19, 6)],[
        (-15, 24), (-12, 19), (0, 20), 
        (11, 19), (14, 24), (18, 6), (21, -4), 
        (21, -13), (9, -25), (-11, -25), (-23, -13), 
        (-23, -4), (-19, 6)],[
        (-15, 24), (-12, 19), (0, 20), 
        (11, 19), (14, 24), (18, 6), (21, -4), 
        (21, -13), (9, -25), (-11, -25), (-23, -13), 
        (-23, -4), (-19, 6)]]
    tops = [17, 140, 260, 386, 494, 620, 731, 857]
    bottoms = [115, 239, 358, 485, 592, 719, 829, 956]
    # This image contains 4 owls, two rows per owl, each row has 2 angles, each angle has 3 versions
    for owl in range(4):
        rightImgs = []
        leftImgs = []
        upImgs = []
        downImgs = []
        for row in range(2):
            # Within each row, the owls start and end at the same heights
            top = tops[owl*2+row]
            bottom = bottoms[owl*2+row]
            for i in range(6):
                # However, the left and right endpoints are unique to each owl
                thisLeft = left + width*i
                thisRight = thisLeft + width
                if i==0:
                    print('cords are', (thisLeft, top, thisRight, bottom))
                thisOwl = CMUImage(baseImage.crop((thisLeft, top, thisRight, bottom)))

                # Now I want to add each of these to their respective list
                if i<3:
                    if row==0:
                        rightImgs.append(thisOwl)
                    else:
                        upImgs.append(thisOwl)
                else:
                    if row==0:
                        leftImgs.append(thisOwl)
                    else:
                        downImgs.append(thisOwl)
        # Now want to set an app-wide variable to a list of the images with their keypoints
        varName = f'app.owl{owl}' # Ex: app.owl1, app.owl2, app.owl3, etc
        varValue = '[(rightImgs, keypoints[0]),(downImgs, keypoints[1]),(leftImgs, keypoints[2]),(upImgs, keypoints[3])]'
        prog = f'{varName}={varValue}'
        exec(prog)


### level gen!
def setNewLevel(app, difficulty):
    Table.num = 0
    app.difficulty = difficulty
    app.lineList = [] # For now since we are not setting a line list
    app.tableData = makeNewLevel(app,difficulty)

def makeNewLevel(app, difficulty):
    # Get number of tables
    tableNum = 4 if difficulty==1 else 7 if difficulty==2 else 10
    # Get number of lines
    # lay down where the lines go
    # get valid nodes where tables can be placed
    tableNodes = layNodesForTables(app)

    app.tableNodes = [(cx, cy) for cx,cy,_ in tableNodes]
    # Make sure each level has uniqueish placement
    tableNodes = set(tableNodes)
    
    taken = set()
    # randomly place x tables at those nodes
    # if tableList == None:
    #     print('cant do nothing without tables') 
    #     return []
    tableList =  random.sample(list(tableNodes), tableNum) #getTablePlacements(app, tableNodes, taken, tableNum, [])
    levelData = [Table(cx, cy, 0, 5) for (cx, cy, _) in tableList]
    # Maybe return lines as well
    return levelData

def getTablePlacements(app, tableNodes, taken, tableNum, solSoFar):
    print(solSoFar)
    if len(solSoFar)==tableNum:
        return solSoFar
    else:
        remainingPositions = tableNodes - taken
        random.shuffle(list(remainingPositions))
        print(remainingPositions)
        for position in remainingPositions:
            if isLegalTableSpot(app, position):
                solSoFar.append(position)
                taken.add(position)
                solution = getTablePlacements(app, tableNodes, taken, tableNum, solSoFar)
                if solution!=None:
                    return solution
            taken.add(position)
        print('there was no layout')
        return None


def isLegalTableSpot(app, position):
    # Table cannot be on any border lines or linelist lines
    cx, cy, _ = position
    radius = app.tableR
    for line in app.boundaryLines+app.lineList:
        if circleLineIntersects(line, cx, cy, radius):
            return False
    # Table cannot be in kitchen or station
    return True

def circleLineIntersects(line, cx, cy, radius):
    # NEW PLAN!
    # Get equation of line
    x1, y1, x2, y2 = line
    slope = 'undefined' if x2 ==x1 else (y2-y1)/(x2-x1)
    if slope == 'undefined':
        print('i didnt do this part yet')
        return
    else:
        intercept = y1 - slope*x1 
        perpSlope = 1/slope
        newLine = (cx, cy, cx+5, cy+5*perpSlope)
        intersection = linesIntersect(line, newLine)
        if intersection==None:
            return False
        if distance(cx, cy, *intersection)>radius:
            return False
        else:
            # If the intersection is on the given segment, return True
            if pointOnSegment(intersection, line):
                return True
            # If at least one endpoint is inside of the circle, return true
            if distance(x1, y1, cx, cy)<radius or distance(x2, y2, cx, cy)<radius:
                return True
        return False

# Returns set of possible x,y coordinates a table could be placed at
def layNodesForTables(app):
    margin = 40
    wallHeight = 10 
    boardTopLeft = margin+app.sidebarWidth, app.barHeight+margin+wallHeight+app.tableR
    boardWidth = app.width - 2*margin - app.sidebarWidth - 3*app.tableR
    boardHeight = app.height - app.barHeight - 2*margin - 5*app.tableR
    nodeDist = app.tableR*2 + 50 # 30 is max sprite width
    nodeList = getPossibleNodes(boardTopLeft, boardWidth, boardHeight, nodeDist)
    i = 0
    while i<len(nodeList):
        node = nodeList[i]
        if not isLegalTableSpot(app, node):
            nodeList.pop(i)
        else:
            i+=1
    return nodeList


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
    wallHeight = 10 
    boardTopLeft = margin+app.sidebarWidth, app.barHeight+margin+wallHeight
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
    # Draw cute background
    drawImage(app.backgroundIm, app.sidebarWidth, app.height/2+app.barHeight, align='left')
    drawImage(app.doorCover, app.sidebarWidth, app.height/2+app.barHeight, align='left')
    drawImage(app.wallImage, app.sidebarWidth, app.height/2+app.barHeight, align='left')
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
    drawPolygon(*polygonCords, fill='turquoise')
    for i in range(len(app.waitress.imageList[app.waitress.dIndex].keypoints)):
        x, y = wrappedPolygonCords[i]
        drawCircle(x, y, 2, fill=colors[i%len(colors)])
    if app.showNodes:
        # drawNodesAndEdges(app)
        for node in app.tableNodes:
            drawCircle(*node, 4, fill='blue')
    if (app.currentOrder !=None and app.selectedTable!=None 
        and app.currentOrder in app.tableData[app.selectedTable].order):
        app.tableData[app.selectedTable].demand(app.currentOrder)
    drawAlert(app)
    drawHelpOverlays(app)

def drawTables(app):
    width = app.tableR * 2
    for i in range(len(app.tableData)):
        table = app.tableData[i]
        if app.selectedTable!=None:
            if i == app.selectedTable:
                drawImage(app.tablePic, table.cx, table.cy, align='center', width=width, height=width)
                # drawCircle(table.cx, table.cy, table.radius, fill=app.tableColor, opacity=100)
                drawCircle(table.cx, table.cy, table.radius+3, fill=None, border=app.colors['darkBrown'])
                # Old drawing task in "thought bubbles" image.pngfunctionality... May revive later
                # if table.lastAttended!=None and app.steps - table.lastAttended>Table.patience:
                #     drawTask(app, table)
                drawContents(app, table)
            else:
                # drawCircle(table.cx, table.cy, table.radius, fill=app.tableColor, opacity=80)
                drawImage(app.tablePic, table.cx, table.cy, align='center', width=width, height=width)
                drawContents(app, table)
        else:
            # drawCircle(table.cx, table.cy, table.radius, fill=app.tableColor)
            drawImage(app.tablePic, table.cx, table.cy, align='center', width=width, height=width)
            drawContents(app, table)
        if table.tip!=None:
            drawTip(app, table)
        drawLabel(f'{table.num}', table.cx, table.cy-(table.radius/(5/4)), bold=True)


def drawTip(app, table):
    # Draw three rectangles getting tilted
    for i in range(3):
        drawRect(table.cx, table.cy, 15, 7, 
                border='darkGreen', fill='forestGreen', rotateAngle=i*10, align='center')
        
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
    for node in app.nodeList:
        cx, cy, id  = node
        color = 'purple'
        if not (app.nodesOfPath== None) and(cx, cy) in app.nodesOfPath:
            color = 'red'
        drawCircle(cx, cy, 3, fill=color)
    i = 0
    for edge in app.edgeSet:
        edge, weight = edge
        if edge[0] > 599 and edge[1]<200:
            drawLine(*edge)
            midpoint = (edge[0]+edge[2])/2, (edge[1]+edge[3])/2
            drawLabel(f'{weight}', *midpoint, bold=True)
            i +=1

def drawCustomers(app):
    for customer in app.customerList:
        customer.draw()
        for follower in customer.followers:
            follower.draw()


def drawOverlay(app):
    #top bar
    drawRect(0, 0, app.width, app.barHeight, fill = app.colors['stucco'])
    drawLabel('Press tab for instructions.', 
                app.sidebarWidth+30, app.barHeight/2, size=18, fill='white', align='left')
    drawLabel(f'Tips: ${(app.moneyMade*100)//100}', app.sidebarWidth+300, app.barHeight/2,
                 size=18, fill='white', align='left')
    zeroDig = '0' if (app.steps//20)%60<10 else ''
    drawImage(app.settingsImage, *app.settingsTopLeft, width=app.sWidth, height=app.sHeight)
    # Optional Code Below draws the timer
    # drawLabel(f'{(app.steps//20)//60}:{zeroDig}{(app.steps//20)%60}', 
    #                 app.width-70, app.barHeight/2, size = 24, align='left', fill='white')
    #kitchen
    height = 60
    width = 100
    drawRect(app.sidebarWidth, app.height-height, width, height, fill=app.colors['lightBrown'])
    drawLabel('Kitchen', width/2+app.sidebarWidth, app.height-(height/2), size=18)    
    # server station
    drawRect(app.width-width, app.height-height, width, height, fill='gray')
    drawLabel('Drinks', width/2+app.width-width, app.height-(height/2), size=18)

# THIS IS SOURCED FROM THE CMU PIL DEMO2 PROVIDED EDITING PIXELS FILE (and slightly adjusted)
def makeNewColorImage(sourceImage, newColor):
    # First, get the RGB version of the image so getpixel returns r,g,b values:
    rgbaImage = sourceImage.convert('RGBA')

    # Now, a new image in the 'RGB' mode with same dimensions as app.image
    newImage = Image.new(mode='RGB', size=rgbaImage.size)
    for x in range(newImage.width):
        for y in range(newImage.height):
            r,g,b,a = rgbaImage.getpixel((x,y))
            if (r,g,b)==(172,83,83):
                newImage.putpixel((x,y),newColor) 
    return newImage

def drawSidebar(app):
    # drawRect(0,0, app.sidebarWidth, app.height, fill=app.colors['cream'])
    # Draw background image
    drawImage(app.toDoImage, 0, 0)
    margin = (app.sidebarWidth - app.taskButtonWidth)/2
    middle = app.sidebarWidth/2
    height = 50
    
    taskNum = 0
    taskList = getSortedTaskList(app)
    if taskList ==[]:
        msg = 'Check on your tables!'
    else:
        msg = 'To do:'
    #drawLabel(msg, middle, margin+10, size = 24)
    for i in range(len(taskList)):
        task = taskList[i]
        drawImage(app.buttonImg, margin, (height+margin)*i+margin+60, width=app.taskButtonWidth, height=height)
        drawLabel(f'{task.label}, table {task.tableNum}', middle, (height+margin)*i+(height/2)+5+60, size = 24)
        taskNum +=1

def getSortedTaskList(app):
    unsortedList = []
    for i in range(len(app.tableData)):
        tasks = app.tableData[i].tasks
        for t in range(len(tasks)):
            unsortedList.append(tasks[t])
    return sorted(unsortedList)
    
def drawWaitress(app):
    if app.waitress.dIndex==3:
        app.tray.draw(15, 4)
    app.waitress.draw()
    if app.waitress.message!=None:
        cx, cy = app.waitress.cx+40, app.waitress.cy-40
        drawRect(cx, cy, 140, 25, fill='white', border='black', align='center')
        drawLabel(f'{app.waitress.message}', cx, cy)
    if app.waitress.dIndex!=3: 
        app.tray.draw(15, 4)

def makeNewCustomer(app):
    if not isOpenTable(app): 
        return
    #newImageList = randCustomerFromBase(app.waitressImages)
    newImageList = random.choice([app.owl0, app.owl1, app.owl2, app.owl3])
    cx, cy = -100, -100

    # Choose table and get a path to that table
    tableChoice = getDestinationIndex(app)
    table = app.tableData[tableChoice]
    print('finding path to...', table.num)
    destinationSet = getDestNodesFromIndex(app, tableChoice)
    path = getCustomerPathFromNodePath(app, getPathFromNodes(app, app.customerOriginNode0, destinationSet))
    # Reset the table's tip and tasklist
    table.tip = None
    table.status = 0
    table.tasks = []

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
        app.difficulty = 3
        app.tableData = [Table(cx+app.sidebarWidth, cy, 0, 5) for (cx, cy) in app.easyLayout]
        app.lineList = []
    elif key=='n':
        setNewLevel(app, app.difficulty)
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
        print(app.lineList)
    elif key=='s':
        # Set debugging mode
        table = app.tableData[0]
        table.occupants = 4
        # Add items to order and add items to ticket
        order = ['jelly', 'jam', 'jam', 'funions']
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
            customer = app.customerList.pop(0)
            resetTable(customer.table)
            customerLeave(app, customer)
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
    if app.currentOrder!=None and app.selectedTable==None:
        app.currentOrder = None
        app.pendingOrder = None

        alert(app, "Don't walk away when a guest is talking! Now you'll never know their order.")
        app.waitress.score -= 1
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
        setActiveScreen('kitchen')
    elif slowX<=x<=shighX and slowY<=y<=shighY:
        app.waitress.cx = app.width - 100 - 20
        app.waitress.cy = app.height - 30
        app.tray.move(app.width/3, app.height/2)
        setActiveScreen('station')
    pass

        
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

def floor_onMousePress(app, mouseX, mouseY):
    # if settings gear clicked, move to settings screen
    if app.editorMode: 
        if app.drawLine:
            if len(app.newLine)==2:
                thisLine = (app.newLine + (mouseX, mouseY))
                app.lineList.append(thisLine)
                app.newLine = ()
            else:
                app.newLine = (mouseX, mouseY)
        else:
            #if app.tableData == [[[]]]: app.tableData = []
            app.tableData.append(Table(mouseX, mouseY, 0, 5)) 
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
        if currentTask.label!='wait for tip':
            if table.tasks!=[]: table.tasks.pop(0)
            table.status = (1+table.status)%(len(app.stati))
        # set new table task DONE IN COMPLETION FUNCTION
        # nextTask = app.stati[table.status]
        # table.tasks.append(nextTask)
    else:
        alert(app, f"You aren't able to {currentTask.label} right now! Bad look...")
        # Minus points for going to a table without what they wanted!
        table.serverScore -= 1 

def equippedForTask(app, task, table):
    # If you don't need anything in your tray, you're equipped
    if (task=='say hi' or task=='take order' or task=='get dessert order'
        or task=='pick up tip'):
        return True
    # If you need something, check that you have what you need
    if (task=='give drinks' or task=='give order' 
        or task=='give dessert' or task=='give bill'):
        # Check that you have the order in your tray
        order = table.order
        if app.tray.contains(order):
            return True
    if task=='pick up tip':
        # Check that there's a tip there
        if table.tip == None:
            return alert(app, 'No tip for you here!')
        else:
            return True

def completeTask(app, task, table):
    # ['empty','say hi', 'give drinks', 'take order', 'give order', 'get dessert order',
    # 'give dessert', 'give bill', 'pick up tip']
    if task=='say hi':
        greet(app, table)
        table.lastAttended = app.steps
    elif (task=='give drinks' or task=='give order' 
            or task=='give dessert' or task=='give bill'):
        deliverOrder(app, table)
        table.waitTimes.append(app.steps-table.lastAttended)
        table.lastAttended = app.steps
    elif task=='take order':
        getOrder(app, table)
        table.waitTimes.append(app.steps-table.lastAttended)
        table.lastAttended = app.steps
    elif task=='get dessert order':
        getDessertOrder(app, table)
        table.waitTimes.append(app.steps-table.lastAttended)
        table.lastAttended = app.steps
    elif task=='pick up tip':
        app.moneyMade = ((app.moneyMade + table.tip)*100)/100
        table.tip = None
        table.tasks = []
    print(table.waitTimes)

def greet(app, table):
    # Say hi
    app.waitress.speak('Welcome! Want drinks?', app.steps)
    # Choose x random drinks, x = num at table, have them order it
    wants = []
    pendingOrder = dict()
    startTime = app.steps + 10
    print(table.occupants)
    for i in range(table.occupants):
        drink = random.choice(list(app.drinks.keys()))
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
        food = random.choice(list(app.foods.keys()))
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
    if table.order!= []:
        scoreChange = app.tray.remove(table.order)
        table.serverScore -= scoreChange
    table.order = []
    if app.stati[table.status]=='give drinks':
        table.tasks.append(Task('take order', table.num))
    elif app.stati[table.status]=='give order':
        table.tasks.append(Task('get dessert order', table.num))
    elif app.stati[table.status]=='give dessert':
        table.order = [table.bill]
        table.tasks.append(Task('give bill', table.num))
    elif app.stati[table.status]=='give bill':
        table.contents = []
        table.tasks.append(Task('wait for tip', table.num))
    elif app.stati[table.status]=='wait for tip':
        if app.steps - table.lastAttended> Table.patience:
            print(table.tasks)
            table.status += 1
            table.tip = table.calculateTip(app.menu, app.waitress)
            app.waitress.allTableScores.append(table.tip)
            table.tasks = [Task('pick up tip', table.num)]
            #table.tasks.append()
            print('Switching and now tasks are', table.tasks, 'status is', app.stati[table.status])

def getDessertOrder(app, table):
    # Choose x random food items, x = num at table, have them order it
    wants = []
    pendingOrder = dict()
    startTime = app.steps + 10
    for i in range(table.occupants):
        dessert = random.choice(list(app.desserts.keys()))
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
    for i in range(len(app.customerList)):
        customer = app.customerList[i]
        if customer.seated and customer.table.status == len(app.stati)-1:
            # Customer should leave if it's time for them to leave
            if (app.steps - customer.table.lastAttended)>Table.patience:
                table = customer.table
                customerLeave(app, customer)
                resetTable(table)
                return
        customer.move(app)
        for follower in customer.followers:
            follower.move(app)   
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
    # # See if customers should tip and leave
    for table in app.tableData:
        if app.stati[table.status]=='wait for tip':
            deliverOrder(app, table)
    
def customerLeave(app, customer):
    # Get path for customer to leave
    startNode = getNodeFromXY(app, int(customer.cx), int(customer.cy))
    if startNode==None: 
        print('Failed node find')
        return 
    nodesToDoor = getPathFromNodes(app, startNode, {(app.customerOriginNode1[0],app.customerOriginNode1[1])})
    nodesToDoor.append((app.customerOriginNode0[0],app.customerOriginNode0[1]))
    path = getCustomerPathFromNodePath(app, nodesToDoor)
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
    #table.tasks = []
    table.lastAttended = None

    table.ticket = Ticket()
    table.order = []
    table.contents = []
    table.bill = Bill(table.num) # Will maybe need to create a bill class but maybe also not
    table.seats = [[getEndpoint((180/table.maxOccupancy)*p-150, table.radius, table.cx, table.cy), False] for p in range(4)]


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