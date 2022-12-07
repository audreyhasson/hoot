from dependencies import *

def tutorial_onScreenStart(app):
    imageList = []
    for i in range(1, 16):
        image = CMUImage(Image.open(f'images/tutorialImages/tutorial{i}.png'))
        imageList.append(image)
    app.repeatedImage = imageList[5]
    imageList.insert(9, app.repeatedImage)
    imageList.insert(14, app.repeatedImage)
    
    app.tutorialImages = imageList
    app.currentImg = 0

def tutorial_redrawAll(app):
    # Draw page
    # Click to continue and skip button
    drawImage(app.tutorialImages[app.currentImg], 0, 0)
    drawRect(10, 10, 380, 40, fill=rgb(174, 152, 140))
    drawLabel('click anywhere to continue', 30, 27, align='left', size=30)
    drawRect(app.width-10-170, 10, 170, 40, fill=rgb(175, 175, 175))
    drawLabel('skip tutorial', app.width-10-(170/2), 27, align='center', size=30)

def tutorial_onMousePress(app, mouseX, mouseY):
    # if they pressed skip, skip!
    left = app.width-10-170
    top = 10
    width = 170
    height = 40
    if left<=mouseX<=left+width and top<=mouseY<=top+height:
        setActiveScreen('floor')
    if app.currentImg<len(app.tutorialImages)-1:
        app.currentImg += 1
    else:
        setActiveScreen('floor')
