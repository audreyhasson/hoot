### HOOTERS ###
This game is a owl themed restaurant simulator, where the player acts as the server.
Good fun for all ages.

### HOW TO RUN ###
Run the game by running the 'floor.py' file.

### DEPENDENCIES ###
You must have cmu cs graphics installed to play this game.
Access that here: https://academy.cs.cmu.edu/desktop

### DEVELOPER COMMANDS ###
Level creation!!
    Press "Shift+E" to toggle editor mode. 
    In editor mode, click anywhere to place a table. 
    Hold down "l" and click two points to draw a line between those points. 
    Danger! Note that you must create "legal" levels. If it is impossible to arrive at a table, the app will be unhappy.
    On exiting editor mode, you will be playing on your own level.
Press "Shift+N" while on the restaurant floor screen to toggle viewing path-finding nodes.
Note this will make the app run slower.
Press "c" to force a customer entrance. (Will not work if no table is available).
Press "l" to force the last customer to disappear/"leave".
Press "Shift+C" to clear all customers.

Files:
splash.py (Short start screen)
tutorial.py (Manages tutorial mode at start of game)
floor.py (Contains bulk of code, intersection management, task management)
dependencies.py (Contains Dijkstra's pathfinding, more intersection management)
kitchen.py (Keeps kitchen cooking food)
station.py (Contains cup filling animations)
printer.py (Allows server to access receipts)

Major functions:
getPathFromNodes (dependencies.py) *Dijkstras*
tryMove (dependencies.py) *Polygon-polygon intersection, polygon-line intersection*
makeNewLevel (floor.py) *Level generation, described as 'renovation' in-game*