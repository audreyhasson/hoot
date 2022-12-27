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
        self.ticks = 0

    def walk(self):
        self.ticks += 1
        if self.walkingPictures!=[] and self.ticks%5==0:
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
        self.angle = 0

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
            self.angle = 0
            self.lastDIndex = self.dIndex
            # get next direction from path
            cx, cy = self.path.pop(0)
            newDirection = getNewDirection(self.cx, self.cy, cx, cy)
            if newDirection!= None:
                self.dIndex = newDirection
            self.cx = cx
            self.cy = cy  
            self.imageList[self.dIndex].walk()    
        if self.path == [] and not self.seated and self.table!=None:
            print('trying to sit')
            self.table.tip = None
            # Jump to an open seat
            seatedPos = None
            self.dIndex = 1
            self.imageList[self.dIndex].stop()
            for seat in self.table.seats:
                if not seat[1]: # if no one is sitting there
                    seatedPos = seat[0]
                    self.cx, self.cy = seatedPos[0], seatedPos[1]
                    seat[1] = True
                    self.seated = True
                    print('satted')
                    self.angle = getAngle(*seatedPos, self.table.cx, self.table.cy)
                    if self.table.status==0: 
                        self.table.tasks = []
                        self.table.addTask('say hi')
                        self.table.status = 1
                    return
                else:
                    print(
                        'couldnt sit rip'
                    )
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
        img = self.imageList[self.dIndex].picture
        drawImage(img, self.cx, self.cy, align='center', rotateAngle=self.angle,)

    def __lt__(self, other):
        return self.cy < other.cy

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
        drawImage(img, self.cx, self.cy, align='center')
    
    def deduct(self, num):
        if self.score>20:
            self.score -= num
        else:
            self.score = 20

class Table():
    # [[coords], occupants, maxOccupancy]
    num = 0
    patience = 50
    demandItem = 0
    speechBubbles = [CMUImage(Image.open('images/speechBubbleBlue.png')), 
                CMUImage(Image.open('images/speechBubbleGreen.png'))]
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
        self.seats = [[getEndpoint((180/self.maxOccupancy)*p-150, self.radius+10, self.cx, self.cy), False] for p in range(4)]

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
        #drawRect(cx, cy, 100, 40, align='center', fill=color, border='black')
        drawImage(Table.speechBubbles[(Table.demandItem%2)], cx, cy, align='center')
        drawLabel(f'{item}', cx, cy)

    def addTask(self, task):
        self.tasks.append(Task(task, self.num))

    def calculateTip(self, menu, waitress):
        # drink fullness was already accounted for
        averageTimeAttended = int((sum(self.waitTimes)/len(self.waitTimes))/20) # int in seconds
        if averageTimeAttended > 20:
            # Deduct some points for being a slowpoke
            self.serverScore -= .5*(averageTimeAttended - 10)
        if self.serverScore<0: self.serverScore = 1
        # Account for general silliness 
        self.serverScore *= abs((waitress.score/100))
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
    img = CMUImage(Image.open('images/tray.png'))
    def __init__(self, cx, cy):
        self.cx = cx
        self.cy = cy
        self.inventory = []
        self.capacity = 5

    def draw(self, width, height):
        #drawOval(self.cx, self.cy, width, height, fill='steelBlue', border='black')
        drawImage(Tray.img, self.cx, self.cy, align='center', width=width, height=height)
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
        inventoryCopy = copy.deepcopy(self.inventory)
        for item in order:
            if isinstance(item, str):
                for inventoryItem in inventoryCopy:
                    if repr(inventoryItem)==repr(item):
                        matchingItems +=1
                        inventoryCopy.remove(inventoryItem)
                        break
            else:
                for inventoryItem in inventoryCopy:
                    if item.id == inventoryItem.id:
                        matchingItems += 1
        if matchingItems == len(order):
            return True
        else: return False

    def remove(self, order):
        scoreChange = 0
        for item in order:
            if isinstance(item, str):
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
    plateImages = {
        'rat': CMUImage(Image.open('images/rat.png')),
        'frog': CMUImage(Image.open('images/frog.png')),
        'worm': CMUImage(Image.open('images/worm.png')),
        'fish': CMUImage(Image.open('images/fish.png')),
    }
    sampleImg = plateImages['fish']
    width = sampleImg.image.width * 3
    height = sampleImg.image.height
    id = 0
    def __init__(self, item):
        self.cx = -100
        self.cy = -100
        self.ready = False
        self.item = item
        self.id = Plate.id
        Plate.id +=1

    def draw(self):
        img = Plate.plateImages[self.item]
        width = img.image.width * 3
        height = img.image.height* 3
        #drawOval(self.cx, self.cy, Plate.width, Plate.height, fill='white', border='black')
        drawImage(img, self.cx, self.cy, align='center', width=width, height=height)
        # if self.item != None:
        #     color =  'red'
        #     drawCircle(self.cx, self.cy-10, 20, fill=color)

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

def getAngle(posx, posy, x, y):
    angleFromOrigin = getThetaFromEndpoint(posx, posy, x, y)
    if angleFromOrigin>0:
        theta = math.pi - angleFromOrigin + .5*math.pi
        return .2*math.degrees(math.pi - theta)
    else:
        theta = abs(angleFromOrigin)
        return .2*math.degrees(.5*math.pi - theta)


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
    # cx, cy = tryOrientation(app, cx, cy, imageList, dIndex, lastDIndex)
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
    app.waitress.deduct(.05)

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
    if drink=='Sprite':
        return 'white'
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


def layNodes(app):
    print('laying again!')
    # If there are no tables, don't proceed
    if app.tableData == []: 
        return
    validNodes = []
    # Lay nodes around each table at 4 points
    for i in range(len(app.tableData)):
        table = app.tableData[i]
        #cx, cy = table[0][0], table[0][1]
        id1, id2, id3, id4 = [(0,i*4+q) for q in range(4)]
        pos1, pos2, pos3, pos4 = [getEndpoint((180/table.maxOccupancy)*p-150, table.radius+10, table.cx, table.cy) for p in range(4)]
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
    testImageList = app.waitress.imageList
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