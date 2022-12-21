from dependencies import *

def settings_onScreenStart(app):
    app.settingsBackground = CMUImage(Image.open('images/settingsScreen.png'))
    app.settingsArrowImg = CMUImage(Image.open('images/settingsArrow.png'))
    app.musicPlaying = True
    # app.soundTrack =  Sound('https://audio.jukehost.co.uk/zJwz1x8NsTp4RV48I87b4KhT1cJAe4xL') 
    # app.soundTrack.play(loop=True)

def getArrowY(app):
    if app.difficulty == 1:
        return 183
    elif app.difficulty == 2:
        return 299
    elif app.difficulty == 3:
        return 413


def settings_redrawAll(app):
    drawImage(app.settingsBackground, 0, 0)
    arrowX = 119
    arrowY = getArrowY(app)
    drawImage(app.settingsArrowImg, arrowX, arrowY)
    boxY = 405
    boxX = 522 if app.musicPlaying else 685
    width = 90
    height = 55
    drawRect(boxX, boxY, width, height, fill=None, border='black')

def settings_onMousePress(app, mouseX, mouseY):
    handleModes(app, mouseX, mouseY)
    handleMusic(app, mouseX, mouseY)
    # If the back button is pressed, go back
    backLeft = 696
    backTop = 505
    width = 141
    height = 52
    if backLeft<=mouseX<=backLeft+width and backTop<=mouseY<=backTop+height:
        setActiveScreen('floor')

def handleMusic(app, mouseX, mouseY):
    targetY = 405
    targetX = 685 if app.musicPlaying else 522
    # Target box is opposite of current one
    width = 90
    height = 55
    if targetY<=mouseY<=targetY + height and targetX<=mouseX<=targetX+width:
        app.musicPlaying = not app.musicPlaying
        if app.musicPlaying:
            app.soundTrack.play(loop=True)
        else:
            app.soundTrack.pause()


def handleModes(app, mouseX, mouseY):
    xStart = 155
    xEnd = 383
    buttonHeight = 72
    easyY = 169
    midY = 286
    hardY = 400     
    currentDifficulty = app.difficulty   
    if xStart<=mouseX<=xEnd:
        if easyY<=mouseY<=easyY+buttonHeight:
            Table.num = 0
            app.tableData = [Table(cx+app.sidebarWidth, cy, 0, 5) for (cx, cy) in app.easyLayout]
            app.lineList = []
            app.difficulty = 1
        elif midY<=mouseY<=midY+buttonHeight:
            app.difficulty = 2
            Table.num = 0
            app.lineList = []
            app.tableData = [Table(cx+app.sidebarWidth, cy, 0, 5) for (cx, cy) in app.midLayout]
        elif hardY<=mouseY<=hardY+buttonHeight:
            Table.num = 0
            app.lineList = [(x1+app.sidebarWidth, y1, x2+ app.sidebarWidth, y2) for (x1, y1,x2,y2) in app.tempLineList]
            app.tableData = [Table(cx+app.sidebarWidth, cy, 0, 5) for (cx, cy) in app.hardLayout]
            app.difficulty = 3
    if app.difficulty!=currentDifficulty:
        app.customerList = []
        app.waitress.cx = 600
        app.waitress.cy = app.height - 40
        layNodes(app)
