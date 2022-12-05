from cmu_cs3_graphics import *
from runAppWithScreens import *
import math
import random
import copy
from PIL import Image

###############
### CLASSES ###
###############

class DynamicImage:
    def __init__(self, pictures, keypoints):
        self.stillPicture = pictures[0]
        self.picture = self.stillPicture
        self.keypoints = keypoints
        self.walkingPictures = pictures[1:]
        self.walkIndex = 0

    def walk(self):
        if self.walkingPictures!=[]:
            self.picture = self.walkingPictures[self.walkIndex]
            self.walkIndex = (self.walkIndex+1)%2
    
    def stop(self):
        self.picture = self.stillPicture

class Sprite:
    def __init__(self, imageList, cx, cy, dIndex, lastDIndex):
        self.imageList = [DynamicImage(images, keypoints) for (images, keypoints) in imageList]
        self.cx = cx
        self.cy = cy
        self.dIndex = dIndex
        self.lastDIndex = lastDIndex
        self.radius = 30 # HARDCODED RADIUS RADIUS SPRITE

    def draw(self):
        img = self.imageList[self.dIndex].picture
        drawImage(img, self.cx, self.cy, align='center')

class Customer(Sprite):
    def __init__(self, imageList, cx, cy, dIndex, lastDIndex, path, table):
        super().__init__(imageList, cx, cy, dIndex, lastDIndex)
        self.path = path
        self.seated = False
        self.table = table
        self.followers = []

    def addFollowers(self, app, numOfFollowers):
        for i in range(numOfFollowers):
            #newImageList = randCustomerFromBase(app.waitressImages)
            newImageList = random.choice([app.owl0, app.owl1, app.owl2, app.owl3])
            cx = cy = -2
            path = [(-2, -2) for _ in range((i+1)*5)] + copy.deepcopy(self.path)
            follower = Customer(newImageList, cx, cy, 2, 2, path, self.table)
            self.followers.append(follower)
    
    def move(self, app):
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
        # After moving, make waitress react
        waitress = app.waitress
        # right , down, left, up
        moves = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        if waitressCrashed(app, waitress.cx, waitress.cy, waitress.dIndex):
            # if is legal move, push the waitress
            dx, dy = moves[self.dIndex]
            newx = waitress.cx + dx*app.jumpDist
            newy = waitress.cy + dy*app.jumpDist
            if isLegalMove(app, newx, newy, waitress.imageList, waitress.dIndex, 'wait'):
                waitress.cx = newx
                waitress.cy = newy

    def draw(self):
        # Note the given images are twice the size that i want them to display
        img = self.imageList[self.dIndex].picture
        drawImage(img, self.cx, self.cy, align='center',
                 width=img.image.width/2, height=img.image.width/2)

class Waitress(Sprite):
    def __init__(self, imageList, cx, cy, dIndex, lastDIndex):
        super().__init__(imageList, cx, cy, dIndex, lastDIndex)
        self.message = None
        self.startedSpeaking = None
        self.score = 100
        self.allTableScores = []
    
    def speak(self, message, time):
        self.message = message
        self.startedSpeaking = time

    def draw(self):
        img = self.imageList[self.dIndex].picture
        drawImage(img, self.cx, self.cy, align='center', width=49, height=51)

class Table():
    # [[coords], occupants, maxOccupancy]
    num = 0
    patience = 50
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
        self.waitTimes = []
        self.bill = Bill(self.num) # Will maybe need to create a bill class but maybe also not
        Table.num += 1
        self.tip = None
        self.serverScore = 100
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

    def calculateTip(self, menu, waitress):
        # drink fullness was already accounted for
        averageTimeAttended = int((sum(self.waitTimes)/len(self.waitTimes))/20) # int in seconds
        if averageTimeAttended > 10:
            # Deduct some points for being a slowpoke
            self.serverScore -= (averageTimeAttended - 10)
        if self.serverScore<0: self.serverScore = 1
        # Account for general silliness 
        self.serverScore *= (waitress.score/100)
        return ((self.bill.getCost(menu)*.002*self.serverScore)*100)/100

class Bill:
    id = 20000
    def __init__(self, num):
        self.items = []
        self.table = num
        self.id = Bill.id
        Bill.id +=1
    
    def getCost(self, menu):
        cost = 0
        for item in self.items:
            cost += menu[item]
        return int(cost*100)/100

    def addItems(self, itemList):
        self.items.extend(itemList)

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

    def isFinished(self):
        return len(self.completedItems)==len(self.order)

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

    def __repr__(self):
        return self.label
    
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
        matchingItems = 0
        for item in order:
            if isinstance(item, str):
                print('checking for', item, 'in', self.inventory)
                for inventoryItem in self.inventory:
                    if repr(inventoryItem)==repr(item):
                        matchingItems +=1
                        break
            else:
                for inventoryItem in self.inventory:
                    if item.id == inventoryItem.id:
                        matchingItems += 1
        if matchingItems == len(order):
            return True
        else: return False

    def remove(self, order):
        scoreChange = 0
        print('attempting removal')
        for item in order:
            if isinstance(item, str):
                print('checking for', item, 'in', self.inventory)
                for inventoryItem in self.inventory:
                    if repr(inventoryItem)==repr(item):
                        self.inventory.remove(inventoryItem)
                        if isinstance(inventoryItem, Cup):
                            scoreChange += (1-inventoryItem.fullness)*7
                        break
            else:
                for inventoryItem in self.inventory:
                    if item.id == inventoryItem.id:
                        self.inventory.remove(inventoryItem)
        return scoreChange

class Plate:
    width = 800/3 - 60
    height = 20
    id = 0
    def __init__(self, item):
        self.cx = -100
        self.cy = -100
        self.ready = False
        self.item = item
        self.id = Plate.id
        Plate.id +=1

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

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return repr(self.item)

    def equiv(self, other):
        return isinstance(other, Plate) and self.item == other.item

class Cup():
    brimWidth = 50
    bottomWidth = brimWidth - 15
    cupHeight = 70
    id = 10000
    def __init__(self, cx, cy):
        self.cx = cx
        self.cy = cy
        self.drink = None
        self.fullness = 0
        self.zone = None
        self.id = Cup.id
        Cup.id += 1

    def draw(self, angle=0): # int, int, str, range from 0 to 1, degree (opt)
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
            self.fullness += .05
    
    def pointInCup(self, x, y):
        left, right = self.cx - Cup.brimWidth/2, self.cx + Cup.brimWidth/2
        bottom, top = self.cy + Cup.cupHeight/2, self.cy - Cup.cupHeight/2
        return (left<=x<=right and top<=y<=bottom)
    
    def __repr__(self):
        if self.drink!=None:
            return repr(self.drink)
        else:
            return "Empty cup"

    def equiv(self, other):
        return self.drink == other

##### END CLASSES #####

##### FUNCTIONS ####

# ALL MOVE FUNCTIONS!

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
    objectWidth = 25
    if hitTable(app, (cx, cy), imageList, dIndex, app.tableR)[0]: #app, object, imageList, dIndex
        tableHit = hitTable(app, (cx, cy), imageList, dIndex, app.tableR)[1]
        if spriteType==None:
            return False
        elif spriteType =='ghost':
            app.ghostHit = True, tableHit
            return False
        elif spriteType == 'wait':
            return False
    # chheck if below screen (other boundaries are marked with lines/walls)
    if ((app.height-objectWidth<cy)):
        return False
    # Check if she ran into any customers:
    if waitressCrashed(app, cx, cy, dIndex):
        return handleCrash(app)
    #check if crosses line! crosses not is on!
    # get list of lines in pertinent polygon
    polygonPoints = getCordsFromDeltaPoints(cx, cy, 
        imageList[dIndex].keypoints, True)
    polygonLines = []
    for i in range(len(polygonPoints)-1):
        polygonLines.extend([(*polygonPoints[i], *polygonPoints[i+1])])
    polygonLines.extend([(*polygonPoints[-1], *polygonPoints[0])])
    for line in app.lineList + app.boundaryLines:
        # with list of pertinent lines, check to see if each line intersects
        for line2 in polygonLines:
            if segmentsIntersect(line, line2):
                return False
    return True

def getCordsFromDeltaPoints(cx, cy, deltaList, wrapped):
    res = []
    for i in range(len(deltaList)):
        dx, dy = deltaList[i]
        if wrapped:
            res.extend([(cx+dx, cy-dy)])
        else:
            res.extend([cx+dx, cy-dy])
    return res

# app, cx, cy, imageList, dIndex,
def waitressCrashed(app, cx, cy, dIndex):
    # ADD FOLLOWERS TO THIS
    # get list of lines in waitress polygon
    waitressPolygonPoints = getCordsFromDeltaPoints(cx, cy, 
        app.waitress.imageList[dIndex].keypoints, True)
    waitressPolygonLines = []
    for i in range(len(waitressPolygonPoints)-1):
        waitressPolygonLines.extend([(*waitressPolygonPoints[i], *waitressPolygonPoints[i+1])])
    waitressPolygonLines.extend([(*waitressPolygonPoints[-1], *waitressPolygonPoints[0])])
    #check if waitress is in any of the customer circles
    #radius = app.waitress.imageList[app.waitress.dIndex].picture.image.width
    for i in range(len(app.customerList)):
        customer = app.customerList[i]
        if polygonPolygonIntersection(customer, (cx,cy), waitressPolygonLines):
            return True
        for follower in customer.followers:
            if polygonPolygonIntersection(follower, (cx,cy), waitressPolygonLines):
                return True
    return False

def polygonPolygonIntersection(object, subject, subjectLines):
    if isinstance(subject, tuple):
        cx, cy = subject[0], subject[1]
    else:
        cx, cy = subject.cx, subject.cy
    if distance(object.cx, object.cy, cx, cy)<=((object.radius)*2):
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
    alert(app, 'Yikes, you just ran into someone!')
    app.waitress.score -= 1

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


def linesIntersect(line, line2):
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
    return xInt, yInt

def pointOnSegment(point, line):
    px, py = point
    minx1, miny1 = min(line[0], line[2]), min(line[1], line[3])
    maxx1, maxy1 = max(line[0], line[2]), max(line[1], line[3])
    if ((minx1<=px<=maxx1) and 
        (miny1<=py<=maxy1)):
        return True
    return False

def segmentsIntersect(line, line2):
    intersection = linesIntersect(line, line2)
    if intersection==None:
        return None
    # check if x and y are on both lines
    if pointOnSegment(intersection, line) and pointOnSegment(intersection, line2):
        return intersection
    return None

def drawAlert(app):
    if app.alert!=None:
        msg = app.alert[0]
        width = len(msg)*10 + 20
        cx, cy = app.width/2, app.height-80 
        drawRect(cx, cy, width, 40, align='center', fill='white', border='black')
        drawLabel(msg, cx, cy, size = 20)

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
    else:
        return 'purple'

def alert(app, msg):
    app.alert = (msg, app.steps)

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

def getEndpoint(theta, radius, cx, cy):
    dx = radius * math.cos(math.radians(theta))
    dy = radius * math.sin(math.radians(theta))
    return cx+dx, cy+dy


def randCustomerFromBase(imageList):
    newImageList = []
    # random hair color rgb
    hr, hg, hb = (random.randrange(0,256), random.randrange(0,256), 
                random.randrange(0,256)) 
    # random skin color rgb
    sr, sg, sb = (random.randrange(0,256), random.randrange(0,256), 
                random.randrange(0,256)) 
    for imageSet in imageList:
        sourceImage = imageSet[0][0].image
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
        newImageList.append(([newImage], imageSet[1]))
    return newImageList

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

def manageHelpOverlays(app, key):
    if key.isnumeric():
        app.orderToShow = int(key)
    elif key == 'i':
        app.showInventory = True
    elif key=='tab':
        app.showHelp = True

def distance(x, y, x1, y1):
    return ((x1-x)**2 +(y1-y)**2)**.5