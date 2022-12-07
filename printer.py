try: from cmu_cs3_graphics import *
except: from cmu_graphics import *

from runAppWithScreens import *
from dependencies import *


def printer_onScreenStart(app):
    app.tableToShow = 1
    app.topMarg = 100

def printer_redrawAll(app):
    # Split in half
    drawRect(0,0, app.width/2, app.height, fill='lightGray')
    drawLabel('Press digit to see bill for that table', app.width/4, 50)
    start = app.topMarg
    dist = (app.height-app.topMarg*2)/len(app.tableData)
    for i in range(len(app.tableData)):
        thisStart = start + dist*i
        table = app.tableData[i]
        drawLabel(f'Table {table.num}', app.width/4, thisStart)
    if app.tableToShow!=None:
        drawBill(app)
    drawImage(app.leftKey, 40, app.height-100, width=70, height=70)
    drawAlert(app)
    drawLabel('Press left to go back', app.width/4, app.height-50, size=20)
    drawHelpOverlays(app)

def drawAlert(app):
    if app.alert!=None:
        msg = app.alert[0]
        width = len(msg)*10 + 20
        cx, cy = app.width/2, app.height-80 
        drawRect(cx, cy, width, 40, align='center', fill='white', border='black')
        drawLabel(msg, cx, cy, size = 20)

def alert(app, message):
    app.alert = (message, app.steps)

def drawBill(app):
    drawLabel(f'Bill for table {app.tableToShow}', app.width*(3/4), 50)
    table = app.tableData[app.tableToShow]
    items = table.bill.items
    if items == []: 
        drawLabel('No bill available for this table', app.width*(3/4), app.height/2)
        return
    start = app.topMarg
    dist = (app.height-app.topMarg*2-100)/len(items)
    for i in range(len(items)):
        thisStart = start + dist*i
        item = items[i]
        drawLabel(f'{item}', app.width*(3/4), thisStart)
    total = table.bill.getCost(app.menu)
    drawLabel(f'Total is {total}', app.width*(3/4), app.height-100)
    drawLabel('Press enter to add this receipt to your tray', app.width*(3/4), app.height-50)


def printer_onKeyPress(app, key):
    if key == 'left':
        setActiveScreen('station')
    elif key.isnumeric():
        if int(key)<len(app.tableData):
            app.tableToShow = int(key)
    elif key=='enter':
        if app.tableToShow!=None and app.tableData[app.tableToShow].bill.items!=[]:
            bill = app.tableData[app.tableToShow].bill
            alert(app, f'Added bill for table {app.tableToShow} to tray')
            app.tray.inventory.append(bill)
    elif key == 'i':
        app.showInventory = True

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

def printer_onStep(app):
    if not app.paused:
        app.steps +=1
    # Take away alert if past time
    if app.alert!=None:
        alertStart = app.alert[1]
        if alertStart + app.alertLength < app.steps:
            app.alert = None

def printer_onKeyRelease(app, key):
    app.showInventory = False
    app.showHelp = False
