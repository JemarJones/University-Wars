##Author:Jemar Jones
##Title: University Wars
##Descrcription: A civilization inspired conquest game. Themed as a university battle game.

##You'll notice essentially everything is named as if a traditional war game,
##the actual theme of the game came very late in development
from pygame import *
from random import random
import inputbox ##Module for inputing usernames by Timothy Downs (http://www.pygame.org/pcr/inputbox/).  (Though i did edit it slightly)

##Constant Declarations:
screenSize = (500,500)
screenSize = (1140,680)
nX = 30 #Dimension x
nY = 10 #Dimension y
squareSize = (screenSize[0]/nX,screenSize[1]/nY)#The size of one grid square
tiles = [] ##Coloured  backround tiles
mainScreen = display.set_mode(screenSize)
mainScreen = display.set_mode((0,0),FULLSCREEN)

#To be occupied with simpler grid coords
xGrid = []
yGrid = []

holding = []##Used to keep track of which objects are in each square
backColour = (34,139,34)
screenObjects = sprite.LayeredUpdates()##A spritegroup with some control in the order of layers
selectedObject = None
selectedOverlay = None##Stores the overlay related to the currently selected unit
whomsTurn = None##Keeps track of which users turn it is
moveTo = None ##Stores the square a unit may be about to move to /attack
highlightStack = None #Used to determine when to highlight the count badge
class base(sprite.Sprite): ##This will be the basis of all movable chars
    def __init__(self,gridX,gridY,charImage):
        sprite.Sprite.__init__(self)
        self.setNewImage(charImage)
        self.gridX = gridX
        self.gridY = gridY
        holding[gridX][gridY].append(self)##Storing object in respetive location variable for its current loc
        self.rect = Rect(xGrid[gridX], yGrid[gridY], squareSize[0], squareSize[1])
    def setNewImage(self,newImage):
        self.image = image.load(newImage)
        self.image = transform.scale(self.image, squareSize)#Gotta have that image fitting man
        self.image.convert()
class unit(base):
    instances = []
    def __init__(self,gridX,gridY,charImage,unitType,nation,attackStrength,defenseStrength,maxMove):
        base.__init__(self,gridX,gridY,charImage)
        self.instances.append(self)
        self.nation = nation
        self.unitType = unitType
        ##maxMove is the most squares this type can move, movesLeft is the amount it has left to move this turn
        self.maxMoves = maxMove
        self.movesLeft = maxMove
        self.attackStrength = attackStrength
        self.eqAttack = attackStrength##Units equilibrium attack strength
        self.defenseStrength = defenseStrength
        self.eqDefense = defenseStrength ##Units equilibrium defense strength
        self.fortifyBonus = 1
        self.doneMove = False##Used to constrict the number of things a unit does in one turn
    def decisionOverlay(self):##This units personal decision Overlay
        if self.unitType == 2:
            self.menu = buttonOverlay(mainScreen,["Move (" + str(self.movesLeft) + ")","Found","Fortify","End Turn"],overlayColour = self.nation.colour)
        else:
            self.menu = buttonOverlay(mainScreen,["Move (" + str(self.movesLeft) + ")","Fortify","End Turn"],overlayColour = self.nation.colour)
        return self.menu
    def moveUnit(self,gridXNew,gridYNew):
        #Lets take a moment of silence for how crushed my mind got when i was writing this method.
        if not self.doneMove and not ((gridXNew,gridYNew) == (self.gridX,self.gridY)) and (abs(gridYNew-self.gridY) <=self.movesLeft) and (abs(gridXNew-self.gridX) <=self.movesLeft):
            ##Moves self as many times as it takes to get to new pos, following quickest route.
            exclude = []##Will include tiles to exclude from movement do to occupation     
            moveSequence = []##Will store sequence of moves to be made
            moveSequence.append([self.gridX,self.gridY])
            while moveSequence[-1] != [gridXNew,gridYNew]:##Loop through until we get there
                x = 0
                y = 0
                #Simple determination of next iterative x and y
                if (gridXNew-moveSequence[-1][0]) > 0:
                    x = moveSequence[-1][0] + 1
                elif (gridXNew-moveSequence[-1][0]) < 0:
                    x = moveSequence[-1][0] - 1
                else:
                    x = moveSequence[-1][0]
                if (gridYNew-moveSequence[-1][1]) > 0:
                    y = moveSequence[-1][1] + 1
                elif (gridYNew-moveSequence[-1][1]) < 0:
                    y = moveSequence[-1][1] - 1
                else:
                    y = moveSequence[-1][1]
                flag = True
                while flag:
                    flag = False
                    ##Checking if this tile is occupied, flag if so.
                    for i in holding[x][y]:
                        if i.nation != selectedObject.nation:
                            flag = True
                            exclude.append([x,y])##Can't move to this one right now.
                    ##We set both of these equal here, if they diverge before we check then we can continue looping.
                    quickestTile = [x,y]
                    before = quickestTile
                    if flag:
                        quickestDis = len(yGrid) + len(xGrid) ##Basically just want to set this to a large number out of bounds of grid.
                        for i in range(len(yGrid)):
                            for j in range(len(xGrid)):
                                ##This condition essentially considers all alternative options to the tile we'd previosly determined.
                                if (abs(i-y) <=1) and (abs(j-x) <=1) and (abs(i-moveSequence[-1][1]) <=1) and (abs(j-moveSequence[-1][0]) <=1) and moveSequence[-1] != [j,i] and [y,x] != [i,j] and (abs(i-moveSequence[-1][1]) <= self.movesLeft ) and (abs(j-moveSequence[-1][0]) <= self.movesLeft ):
                                    ##We find the best/quickest tile to move out of all available
                                    if abs(gridXNew - j) > abs(gridYNew-i):
                                        distance = abs(gridXNew-j)
                                    elif abs(gridXNew - j) < abs(gridYNew-i):
                                        distance = abs(gridYNew-i)
                                    else:
                                        distance = abs(gridXNew-j)
                                    if distance < quickestDis and distance != 0 and not [j,i] in exclude:
                                        quickestDis = distance
                                        quickestTile = [j,i]
                    ##Checking for competion or failure, either way we must exit.
                    if quickestTile == before:
                        if quickestTile in exclude:
                            moveSequence = []
                            return None
                        else:##At this point the onle else is that we've found the best tile to move to.
                            moveSequence.append(quickestTile)
                            flag = False
            ##Removing the number of moves the user is about to make
            self.movesLeft += -(len(moveSequence) - 1)
            ##Goes through determined movement sequence and performs moves
            for move in range(len(moveSequence) - 1):
                ##Searching for the correct sprite to move
                for i in range(len(holding[moveSequence[move][0]][moveSequence[move][1]])):
                    if holding[moveSequence[move][0]][moveSequence[move][1]][i] == self:
                        ##Removes sprite from list of sprites located at old loc
                        holding[moveSequence[move][0]][moveSequence[move][1]][i]  = None
                        ##Updates references to sprite location
                        holding[moveSequence[move+1][0]][moveSequence[move+1][1]].append(self)
                        self.gridX = moveSequence[move+1][0]
                        self.gridY = moveSequence[move+1][1]
                        ##Moves the sprite the new loc
                        self.rect.left = xGrid[moveSequence[move+1][0]]
                        self.rect.top = yGrid[moveSequence[move+1][1]]
                        if self.movesLeft == 0:
                            self.doneMove = True
                        break
                ##Removes the None entries from all squares
                for i in range(len(holding)):
                    for j in range(len(holding[i])):
                        holding[i][j] = filter(None,holding[i][j])
                draw()
                time.wait(200)##Slight delay, entirely for show.
    def attack(self,toAttack):##Attacks givin unit
        if not self.doneMove:
            tryAttack = True##Flagvar.. Only false once appropriete random value is found and attack completed.
            while tryAttack:
                if random() < self.attackStrength and not(random() <(toAttack.defenseStrength * toAttack.fortifyBonus)):##Seems like a fair way to pick a winner, no?
                    x = toAttack.gridX
                    y = toAttack.gridY
                    if isinstance(toAttack, unit):##Have to call the appropriate method for the type of object being attacked
                        toAttack.die()
                        if len(holding[x][y]) == 0:##Only move if all units/settlements in the square have been defeated
                            self.moveUnit(x,y)##Move the attacking unit to the loc of the attacked
                    elif isinstance(toAttack,settlement):
                        toAttack.annex(self.nation)
                        self.moveUnit(x,y)##Move the attacking unit to the loc of the attacked
                    ##Weakens the unit after battle, but the equilibrium strength of the unit is increased
                    self.attackStrength += - 0.1
                    if self.eqAttack + 0.05 < 0.95:
                        self.eqAttack +=0.05
                    tryAttack = False
                elif not(random() < self.attackStrength) and random() <(toAttack.defenseStrength* toAttack.fortifyBonus):
                    x = self.gridX
                    y = self.gridY
                    self.die()
                    ##Weakens the unit after battle, but the equilibrium strength of the unit is increased
                    toAttack.defenseStrength += -0.1
                    if toAttack.eqDefense + 0.05 < 0.95:
                        toAttack.eqDefense +=0.05
                    tryAttack = False
        self.doneMove = True
    def die(self):##'kills' the unit, removes all references to it.
        for i in range(20):
            ##Could consider series of images here
            self.image = transform.scale(self.image, (int(self.image.get_size()[0]*0.9),int(self.image.get_size()[1]*0.9)))
            draw()
            time.wait(7)
        screenObjects.remove(self)
        self.instances.remove(self)
        self.nation.units.remove(self)
        holding[self.gridX][self.gridY].remove(self)
        draw()
class settlement(base):
    instances = []
    def __init__(self,gridX,gridY,charImage,colour,nation,defenseStrength):
        base.__init__(self,gridX,gridY,charImage)
        self.instances.append(self)
        self.nation = nation
        self.colour = colour##Colour of borders
        self.defenseStrength = defenseStrength
        self.eqDefense = defenseStrength ##Units equilibrium defense strength
        self.fortifyBonus = 1
        self.reach = None
        self.inReach = []##Thisll store all the locations within the reach
        self.doneMove = False
        self.buildCount = None
        self.spiritBuildUp = 0
    def decisionOverlay(self):##This units personal decision Overlay
        self.menu = buttonOverlay(mainScreen,["New Unit","Build Spirit","Fortify","End Turn"],overlayColour = self.nation.colour)
        return self.menu
    def setBorder(self,reach):##Draws out borders within given reach/radius
        previosAdded = len(self.inReach)*100
        self.reach = reach
        self.inReach = []#Resetting  the inReach list as we are about to repopulate
        ##Change all blocks within reach to this instances colour
        for i in range(len(yGrid)):
            for j in range(len(xGrid)):
                if (abs(i-self.gridY) <=reach) and (abs(j-self.gridX) <=reach):
                    colourBlock = True
                    for inst in settlement.instances:
                        if inst!= self and  inst.withinReach(j,i):##If theres already a settlement with that block coloured, dont colour the block
                            colourBlock = False
                    if colourBlock: #Otherwise go ahead and colour the block
                        tiles[j][i].fill(self.colour)
                        self.inReach.append((xGrid[j],yGrid[i]))
        self.nation.score += -previosAdded + (len(self.inReach)*100)
    def withinReach(self,x,y):##Checks if a certain location is in inReach for this object
        loc = (xGrid[x],yGrid[y])
        for i in self.inReach:
            if i == loc:
                return True
        return False
    def annex(self,newNation):##Transfers ownership of the settlement to new nation
        self.colour = backColour
        self.setBorder(self.reach)#Basically just trying to "clean up after itself"
        self.nation.settlements.remove(self)
        self.nation = newNation
        self.nation.settlements.append(self)
        self.colour = newNation.colour
        self.setNewImage(nation.unitImages[self.nation.nationNum][3])
        self.setBorder(0)##After just being annexed, cultural borders are low.
    def build(self,unitType):##Innitiaties the buiilding of the specified thing
        self.buildCount = 0
        self.typeMaking = unitType
        self.fortifyBonus = 1
    def checkBuild(self):##Checks whether the current thing being built is done being built yet, then does so.
        if (self.typeMaking == 0 and self.buildCount == 3) or (self.typeMaking == 1 and self.buildCount == 5) or (self.typeMaking == 2 and self.buildCount == 7):
            self.nation.createUnit(self.gridX,self.gridY,self.typeMaking)
            self.buildCount = None
            self.typeMaking = None
        elif self.typeMaking == 3 and self.buildCount == 6:##This is the special case of building spirit
            self.setBorder(self.reach + 1)
            self.buildCount = 0
    def buildSpirit(self):
        self.spiritBuildUp += 1
        if self.spiritBuildUp == 6:
            self.spiritBuildUp = 0
            self.setBorder(self.reach + 1)
class nation:
    unitImages = [["skater1.png","jock1.png","nerd1.png","uni1.png"],["skater2.png","jock2.png","nerd2.png","uni2.png"],["skater3.png","jock3.png","nerd3.png","uni3.png"],["skater4.png","jock4.png","nerd4.png","uni4.png"]]
    unitStrength = [(0.1,0.1),(0.4,0.4),(0.7,0.7)]##Default strengths for each unit type
    unitMaxMoves = [4,3,2]##Default maximum moves for each unit type
    defaultCityDefense = 0.15
    instances = []
    def __init__(self,colour,startX,startY,name):
        self.instances.append(self)
        self.nationNum = len(self.instances) - 1
        self.nationName = name
        self.colour = colour
        self.units = []#Keeping track of all the units that belong to this nation
        self.settlements = []#Keeping track of all the settlements that belong to this nation
        self.createUnit(startX,startY,2)
        self.score = 0
    def createUnit(self,x,y,unitType):##Creates a unit of a given type
        self.units.append(unit(x,y,self.unitImages[self.nationNum][unitType],unitType,self,self.unitStrength[unitType][0],self.unitStrength[unitType][1],self.unitMaxMoves[unitType]))
        layerToPlace = 0
        if len(screenObjects.layers()) > 0:
            layerToPlace = screenObjects.get_top_layer()
        screenObjects.add(self.units[len(self.units) - 1],layer = layerToPlace)
    def foundSettlement(self,x,y):##Create settlement at the given loc
        self.settlements.append(settlement(x,y,self.unitImages[self.nationNum][3],self.colour,self,self.defaultCityDefense))
        self.settlements[len(self.settlements) - 1].setBorder(1)##Creates a border around the tile
        screenObjects.add(self.settlements[len(self.settlements) - 1],layer = screenObjects.get_top_layer())
        draw()
class button:
    def __init__(self,screen,width,height,text,colour):##Simple button creator
        self.ownerScreen = screen
        self.width,self.height = width,height
        ##Create labels for the text passed in
        self.font = font.SysFont("monospace", 18 )
        self.labels = text.split(" ")
        ##Stretching the width of the box for the text
        for i in self.labels:
            if self.width/9 + self.font.size(i)[0] > self.width:
                self.width = self.width/9 + self.font.size(i)[0]+4
        self.box = Surface((self.width,self.height))
        self.box.fill(colour)
        for i in range(len(self.labels)):
            self.labels[i] = self.font.render(self.labels[i], 1, (255,255,255))
    def display(self,posX,posY):#Blit the button to the screen
        self.posX = posX
        self.posY = posY
        self.center = (posX + (self.width/2), posY + (self.height/2))
        self.ownerScreen.blit(self.box,(posX,posY))
        for i in range(len(self.labels)):
            self.ownerScreen.blit(self.labels[i],(posX + self.width/9,i*12 + posY + self.height/2.5))##Experimentally obtained pos diff vs the button itself
    def changeColour(self,colour):
        self.box.fill(colour)
class buttonOverlay:
    def __init__(self,screen,buttonLabelList,overlayColour = (205,201,201),buttonColour = (0,0,0)):##Feed in a list of buttons and on overlay of buttons will be created
        self.ownerScreen = screen
        self.height = screen.get_size()[1]/5 ##We'll cover this much of the screen
        self.width = screen.get_size()[0]##Using the full screen width
        self.top = False ##If True, overlay will be blitted at the top of the screen, otherwise the bottom
        self.buttonLabelList = buttonLabelList
        self.overlayColour = overlayColour
        self.buttonColour = buttonColour
        ##Creating the overlay surface itself
        self.overlay = Surface((self.width,self.height))
        self.overlay.fill(overlayColour)
        ##Creating a button for each label in the button list
        self.buttons = []
        for i in buttonLabelList:
            self.buttons.append(button(screen,self.height*0.8,self.height*0.8,i,buttonColour))
    def display(self,top = False):##Displays the overlay
        self.top = top
        yPos = (self.ownerScreen.get_size()[1] - self.height)*(not top) ##Might as well take advantage of pythons weird bools..
        self.ownerScreen.blit(self.overlay,(0,yPos))
        disBetween = ((nX - len(self.buttons))*squareSize[0])/len(self.buttons)#Distance between each button
        shift = disBetween/2#Shift factor for all buttons
        for i in range(len(self.buttons)):
            self.buttons[i].display(shift + (i)*(disBetween + squareSize[0]),yPos + self.height/4 - 0.1*self.height)##Ypos is essentially a constant obtained by playing around
    def newButtons(self,buttonLabelList):##Creating a new set of buttons according to a new list.
         self.buttonLabelList = buttonLabelList
         ##Creating a button for each label in the button list
         self.buttons = []
         for i in buttonLabelList:
             self.buttons.append(button(self.ownerScreen,self.height*0.8,self.height*0.8,i,self.buttonColour))
    def buttonClicked(self,clickedPos):##Returns any of the overlays buttons that were clicked, or False.
        for i in range(len(self.buttons)):
            if self.buttons[i].box.get_rect(center = self.buttons[i].center).collidepoint(clickedPos):
                return self.buttonLabelList[i]
        return False
class scoreBoard:
    #This objeect displays user scores aswell as inicating whos turn it is.
    def __init__(self):
        ##These dimesions seemed right.
        self.width = int(squareSize[0]*1.5) + 2
        self.height = squareSize[1]*3
        self.font = font.SysFont("monospace", 18,True)
        self.playerLabels = []##A label for each player.
        self.Pos = (screenSize[0] - self.width,0 )
        self.update(whomsTurn)
        self.board = image.load('semitrans.png')##Pretty background
        self.board = transform.scale(self.board, (self.width,self.height))
        self.board.convert()
        ##Automatically placing on the right side of the screen
        self.changeSide(True)
    def changeSide(self,side = False):#Switches the side of the screen the board is displayed on. False for left, True for right
        self.currSide = side
        if selectedOverlay!= None:
            y = selectedOverlay.top*(screenSize[1] - self.height)
        else:
            y = self.Pos[1]
        if side:
            self.Pos = (screenSize[0] - self.width,y)
        else:
            self.Pos = (0,y)
    def show(self):##Displays the board 
        mainScreen.blit(self.board,self.Pos)
        self.labelPos = []
        for i in range(len(self.playerLabels)):
            ##shift is used to shift this label below the previos
            shift = self.Pos[1] + 20* self.height/150.0
            if i != 0:
                shift =  30* self.height/150.0 + self.labelPos[i-1][1]
            ##Blitting label to scoreboard
            self.labelPos.append(((20* self.width/200) + self.Pos[0],shift))
            mainScreen.blit(self.playerLabels[i],self.labelPos[i])
    def update(self,currPlayer):##Updates all the player labels to indicate current states
        self.playerLabels = []
        longestLabel = 0
        for i in nation.instances:
            if i != currPlayer:
                self.playerLabels.append(self.font.render(i.nationName + ": " + str(i.score), 1, i.colour))
            else:
                self.playerLabels.append(self.font.render(i.nationName + ": " + str(i.score), 1, (255,255,255)))
            ##Finding the longest label
            if longestLabel < len(i.nationName + ": " + str(i.score)):
                longestLabel = len(i.nationName + ": " + str(i.score))
        #Setting width to accomadate longest label
        self.width = (longestLabel + 20)*5
                                                     
def drawBadges(selectingStack = None):#Draws badges on stacked tiles indicating how many many units are stacked 
    for i in holding:
        for j in i:
            if len(j) > 1:
                ##Drawing badge
                ##Checking if this is the stack to be highlighted (if there is one)
                correctStack = False
                for k in j:
                    if k == selectingStack:
                        correctStack = True
                if not correctStack:
                    circle = image.load('countCircle.png')
                else:     
                    circle = image.load('countCircle2.png')##This yellow cirle is drawn to indicate the user is cycling throught the stack
                circle = transform.scale(circle, (15,15))
                circle.convert()
                mainScreen.blit(circle,(xGrid[j[0].gridX] + 32,yGrid[j[0].gridY] - 4))
                Font = font.SysFont("monospace", 14 )
                num = Font.render(str(len(j)), 1, (0,0,0))
                mainScreen.blit(num,(xGrid[j[0].gridX] + 37,yGrid[j[0].gridY] - 4))
def highlight(color):##Returns the corresponding highlighted colour
    ##This just stores pairs of colours with their highlighted counterparts
    colorIndex = [[(34,139,34),(34,200,34)],[(63,72,204),(63,72,255)],[(163,73,164),(220,73,164)],[(255,127,39),(255,167,39)],[(255,174,201),(255,215,201)]]
    ##Returns highlighted entry corresponding to passed in colour
    for i in colorIndex:
        if i[0] ==  color:
            return i[1]
def draw():##Does all the drawing
    global highlightStack
    #while keepDrawing:
    for i in range(len(tiles)):##Draws all of the background tiles with set colours
        for j in range(len(tiles[i])):
            ##Changing to the appropriate highligthed colour if it is selected
            if moveTo == [i,j]:
                tiles[i][j].fill(highlight(backColour))
                for k in nation.instances:
                    for l in k.settlements:
                        if l.withinReach(i,j):
                            tiles[i][j].fill(highlight(k.colour))
            else:##If its not selected, we recolour to default incase its not already reset
                tiles[i][j].fill(backColour)
                for k in nation.instances:
                    for l in k.settlements:
                        if l.withinReach(i,j):
                            tiles[i][j].fill(k.colour)
            mainScreen.blit(tiles[i][j],(xGrid[i],yGrid[j]))
    for i in nation.instances:#Setting borders just incase there isnt some unused tiles (ie city was just annexed)
        for j in i.settlements:
            j.setBorder(j.reach)
    screenObjects.draw(mainScreen)
    drawBadges(highlightStack)##Passes in any stacks to be highlighted
    if selectedOverlay != None:##If there is an overlay selected, we draw it.
        ##If the selected object is done its move, grey out options
        ##Also, taking advantage of pythons weird definitions of booleans
        if  isinstance(selectedObject,unit):
            ##Sets the attack/move button colour corresponding to current selections
            for i in range(len(selectedOverlay.buttons) - 1):
                selectedOverlay.buttons[i].changeColour((139*(selectedObject.doneMove),137*(selectedObject.doneMove),137*(selectedObject.doneMove)))
            for i in selectedObject.nation.settlements:##Decolouring the found option when on another city already
                if (i.gridX,i.gridY) == (selectedObject.gridX,selectedObject.gridY):
                    selectedOverlay.buttons[1].changeColour((139,137,137))
            if moveTo == None:
                selectedOverlay.buttons[0].changeColour((139,137,137))
            else:
                selectedOverlay.buttons[0].changeColour((0,0,0))
            ##If selectedObject has moved a bit, it can't do any other normal actions. So change those button colours correspondly
            if (selectedObject.movesLeft != selectedObject.maxMoves):
                for k in range(1,len(selectedOverlay.buttons)-1):
                    selectedOverlay.buttons[k].changeColour((139,137,137))
        selectedOverlay.display(selectedOverlay.top)
        scores.changeSide(scores.currSide)##Calling this to make sure the scoreboard and the overlay dont overlap
    ##Updating scoreboard
    scores.update(whomsTurn)
    scores.show()
    display.flip()
def setUp():##Setting up all the stuffs
    global mainScreen##Everythings easier if this can be seen elsewhere
    global whomsTurn
    for i in range(nX): ##Setting up a simpler grid system
        xGrid.append((screenSize[0]/nX)*(i))
    for i in range(nY):
        yGrid.append((screenSize[1]/nY)*(i))
    for i in range(nX):##Setting up holding to show all squares empty and creating  actual tiles
        holding.append([])
        tiles.append([])
        for j in range(nY):
            holding[i].append([])
            tiles[i].append(Surface((squareSize[0], squareSize[1])))
            tiles[i][j].fill(backColour)
    nationColourList = [(63,72,204),(163,73,164),(255,127,39),(255,174,201)]
    nationPosList = [[0,0],[len(xGrid) - 1,len(yGrid) - 1],[0,len(yGrid) - 1],[len(xGrid) - 1,0]]
    ##Creates number of nations determined by user input earlier
    for i in range(numberOfPlayers):
        nation(nationColourList[i],nationPosList[i][0],nationPosList[i][1],nationNames[i])
    ##By default it will be the first players turn.
    whomsTurn = nation.instances[0]
    ##Giving the first player the ability to make moves and such.
    for i in whomsTurn.units:
        i.doneMove = False
    ##Creating the games scoreboard
    global scores
    scores = scoreBoard()
    draw()
def endTurn():##Ends the current players turn
    global selectedObject##Because python gets its jimmies rustled over scope and local variables.. Don't remove this.
    global selectedOverlay
    global whomsTurn
    global moveTo
    moveTo = None##In case the user didnt deselect
    ##Setting all of the old player units and settlements to having finished their moves
    for i in whomsTurn.settlements:
        i.doneMove = True
    for i in whomsTurn.units:
        i.doneMove = True
    turnChanged = False
    while not turnChanged:
        nationsLeft = 0
        stop = False
        ##Determining the number of nations still in the game
        liveNations = []
        for i in range(len(nation.instances)):
            if len(nation.instances[i].units + nation.instances[i].settlements):
                liveNations.append(nation.instances[i])
        ##Checking for the end of the game (and ending it if so.)
        if len(liveNations) == 1:
            coverUp = Surface(screenSize)
            coverUp.fill(backColour)
            mainScreen.blit(coverUp,(0,0))
            inputbox.display_box(mainScreen,"Dean " + liveNations[0].nationName + " has the top uni "+"with a " +str(liveNations[0].score)+" GPA!",backColour,40,6)
            display.flip()
            return False
        ##Change to next nations turn
        for i in range(len(nation.instances)):
            if whomsTurn == nation.instances[i] and not stop:
                whomsTurn = nation.instances[(i+1)%numberOfPlayers]
                stop = True
            if (len(nation.instances[i].settlements) + len(nation.instances[i].units)) != 0:
                nationsLeft += 1
        ##If this player has no units or settlements, theyre done.
        if (len(whomsTurn.settlements) + len(whomsTurn.units)) == 0:
            turnChanged = False
        else:
            turnChanged = True
    ##Setting the new users stuff up
    for i in whomsTurn.settlements:
        i.doneMove = False
        i.buildSpirit()
        if i.buildCount != None:##Updating the build counter for whatever is being built in this settlement
            i.buildCount+=1
            i.checkBuild()
        if i.defenseStrength < i.eqDefense:
            i.defenseStrength += 0.05
            if i.defenseStrength > i.eqDefense: i.defenseStrength = i.eqDefense
    for i in whomsTurn.units:
        i.doneMove = False
        i.movesLeft = i.maxMoves
        ##Naturally recovers the unit after battle
        if i.attackStrength < i.eqAttack:
            i.attackStrength += 0.05
            if i.attackStrength > i.eqAttack: i.attackStrength = i.eqAttack
        if i.defenseStrength < i.eqDefense:
            i.defenseStrength += 0.05
            if i.defenseStrength > i.eqDefense: i.defenseStrength = i.eqDefense
        i.fortifyBonus = 1
    selectedObject = None
    selectedOverlay = None
    return True
def gameLoop(): ##This is where the game will generally happen
    gameOn = True
    global selectedObject##Because python gets its jimmies rustled over scope and local variables.. Don't remove this.
    global selectedOverlay
    global whomsTurn
    global moveTo
    letAnythingHappen = True
    while gameOn :
        for even in event.get():##Stupid python gets really confuse if the loop variable is called event
            if even.type == QUIT\
                or (even.type == KEYDOWN\
                    and even.key == K_ESCAPE):
                gameOn = False
                display.quit()
            if letAnythingHappen:
                if mouse.get_pos()[0] > screenSize[0] - scores.width:
                    scores.changeSide(False)
                    draw()
                elif  mouse.get_pos()[0] <  scores.width:
                    scores.changeSide(True)
                    draw()
                if even.type == MOUSEBUTTONUP:                
                    clickedPos = mouse.get_pos()
                    if (selectedOverlay != None and selectedOverlay.buttonClicked(clickedPos) == False) or selectedOverlay == None :##If a overlay button wasnt clicked, process as a normal click
                        handleClick(clickedPos)
                    elif isinstance(selectedObject, unit)  and selectedOverlay != None and selectedOverlay.buttonClicked(clickedPos) == ("Move (" + str(selectedObject.movesLeft) + ")") and moveTo != None and selectedObject.doneMove == False:
                        ##User had a tile chosen, they click "Move" to confirm. Now we move.
                        selectedObject.moveUnit(moveTo[0],moveTo[1])
                        selectedObject = None
                        selectedOverlay = None
                        moveTo = None
                    elif selectedOverlay != None and selectedOverlay.buttonClicked(clickedPos) == "Attack" and moveTo != None and selectedObject.doneMove == False:
                        X =moveTo[0]
                        Y = moveTo[1]
                        ##Sets pos to one tile short of tile to attack
                        if (X-selectedObject.gridX) > 0:
                            x = X - 1
                        elif (X-selectedObject.gridX) < 0:
                            x = X + 1
                        else:
                            x = X
                        if (Y-selectedObject.gridY) > 0:
                            y = Y - 1
                        elif (Y-selectedObject.gridY) < 0: 
                            y = Y + 1
                        else:
                            y = Y
                        ##Please go look at 'moveUnit(..)' for details on what is being done here.
                        flag = True
                        exclude = []
                        while flag:
                            flag = False
                            for i in holding[x][y]:
                                if i.nation != selectedObject.nation:
                                    flag = True
                                    exclude.append([x,y])
                            quickestTile = [x,y]
                            before = quickestTile
                            if flag:
                                quickestDis = len(yGrid) + len(xGrid) ##Basically just want to set this to a large number..
                                leastMoves = len(yGrid) + len(xGrid)
                                for i in range(len(yGrid)):
                                    for j in range(len(xGrid)):
                                        if ((abs(i-chosen.gridY) ==1) and (abs(j-chosen.gridX) <=1) or (abs(i-chosen.gridY) <=1) and (abs(j-chosen.gridX) ==1))and [selectedObject.gridY,selectedObject.gridX] != [i,j] and[y,x] != [i,j]  and (abs(i-selectedObject.gridY) <= selectedObject.movesLeft -1) and (abs(j-selectedObject.gridX) <= selectedObject.movesLeft -1):
                                            if abs(X - j) > abs(Y-i):
                                                distance = abs(X-j)
                                            elif abs(X - j) < abs(Y-i):
                                                distance = abs(Y-i)
                                            else:
                                                distance = abs(X-j)
                                            if distance < quickestDis and distance != 0 and not [j,i] in exclude and max((abs(i-selectedObject.gridY)), (abs(j-selectedObject.gridX))) < leastMoves:
                                                quickestDis = distance
                                                leasstMoves = max((abs(i-selectedObject.gridY)), (abs(j-selectedObject.gridX)))
                                                quickestTile = [j,i]
                                x,y = quickestTile[0],quickestTile[1]
                            if quickestTile == before:
                                if quickestTile in exclude:
                                    return None
                                else:
                                    flag = False
                        selectedObject.moveUnit(x,y)##Moves to pos determined (one short of attack)
                        ##Now within striking distance, we attack.
                        if ((abs(selectedObject.gridY-chosen.gridY) ==1) and (abs(selectedObject.gridX-chosen.gridX) <=1) or (abs(selectedObject.gridY-chosen.gridY) <=1) and (abs(selectedObject.gridX-chosen.gridX) ==1)):
                            handleInteraction(selectedObject, chosen)
                    elif selectedOverlay != None and selectedOverlay.buttonClicked(clickedPos) == "Found" and selectedObject.doneMove == False and (selectedObject.movesLeft == selectedObject.maxMoves):##When a unit is selected and the user presses 's', the unit is sacrificed to create a settlement
                        for i in selectedObject.nation.settlements:
                            if (i.gridX,i.gridY) != (selectedObject.gridX,selectedObject.gridY):##Making sure we arent founding on another city
                                selectedObject.die()
                                selectedObject.nation.foundSettlement(selectedObject.gridX,selectedObject.gridY)##Found settlement at unit loc
                                selectedObject = None##Object is not to be selected after settling
                                selectedOverlay = None
                                break
                        if len(selectedObject.nation.settlements) == 0:
                            selectedObject.die()
                            selectedObject.nation.foundSettlement(selectedObject.gridX,selectedObject.gridY)##Found settlement at unit loc
                            selectedObject = None##Object is not to be selected after settling
                            selectedOverlay = None
                    elif even.type == KEYUP and even.key == K_e or (selectedOverlay != None and selectedOverlay.buttonClicked(clickedPos) == "End Turn"):
                        letAnythingHappen = endTurn()
                    elif selectedOverlay != None and selectedOverlay.buttonClicked(clickedPos) == "New Unit":
                        selectedOverlay.newButtons(["Skater (3)","Jock (5)","Nerd (7)"])
                        selectedObject.fortifyBonus = 1
                    elif selectedOverlay != None and selectedOverlay.buttonClicked(clickedPos) == "Build Spirit":
                        selectedObject.build(3)
                        selectedObject.fortifyBonus = 1
                        selectedObject = None
                        selectedOverlay = None
                    elif selectedOverlay != None and selectedOverlay.buttonClicked(clickedPos) == "Fortify":
                        if isinstance(selectedObject,unit) and (selectedObject.movesLeft != selectedObject.maxMoves):
                            return None
                        if not selectedObject.doneMove:
                            selectedObject.fortifyBonus = 1.3
                            selectedObject.doneMove = True
                            selectedObject = None
                            selectedOverlay = None       
                    elif selectedOverlay != None and selectedOverlay.buttonClicked(clickedPos) == "Skater (3)":
                        selectedObject.build(0)
                        selectedObject = None
                        selectedOverlay = None
                    elif selectedOverlay != None and selectedOverlay.buttonClicked(clickedPos) == "Jock (5)":
                        selectedObject.build(1)
                        selectedObject = None
                        selectedOverlay = None
                    elif selectedOverlay != None and selectedOverlay.buttonClicked(clickedPos) == "Nerd (7)":
                        selectedObject.build(2)
                        selectedObject = None
                        selectedOverlay = None
                    if letAnythingHappen:
                        draw()
                if even.type == KEYUP:
                    if even.key == K_e:#I know... but is it really worth it to make this a function?
                        letAnythingHappen = endTurn()
                    elif selectedOverlay != None:
                        ##Allowing the user to relocate the overlay to the top or bottom of the screen
                        if even.key == K_UP:
                            selectedOverlay.top = True
                        elif even.key == K_DOWN:
                            selectedOverlay.top = False
                    if letAnythingHappen:
                        draw()
def handleInteraction(actingObject, actedUponObject):##Handles the interaction between any two objects
    global selectedObject##Because python gets its jimmies rustled over scope and local variables.. Don't remove this.
    global selectedOverlay
    if not actingObject == actedUponObject and isinstance(actingObject,unit) and (isinstance(actedUponObject,unit) or isinstance(actedUponObject,settlement)):##Two units interacting
        if actingObject.nation == actedUponObject.nation:##Units of the same nation will be stacked.
            actingObject.moveUnit(actedUponObject.gridX,actedUponObject.gridY)
        else:##Otherwise we presume the user wants to attack
            actingObject.attack(actedUponObject)
    selectedObject = None
    selectedOverlay = None
def select(selectables):##Helps user select one of stacked chars
    global highlightStack
    charChosen = False
    if len(selectables) >1:##If theres something to choose between, we'll try to help the user choose
        highlightStack = selectables[0]##When selecting, we set the counting badge to a highlighted colour
        draw()
        chosenOne = len(selectables) - 1 
        while not charChosen:   
            for even in event.get():
                if even.type == KEYDOWN and even.key == K_LEFT and chosenOne > 0:
                    chosenOne += -1
                if even.type == KEYDOWN and even.key == K_RIGHT and chosenOne < -1+len(selectables):
                    chosenOne += 1
                if even.type == KEYDOWN and even.key == K_DOWN:##If confirmed then lets get out of this loop
                    charChosen = True
                if even.type == KEYDOWN and (even.key == K_LEFT or even.key == K_RIGHT):##Update the top displayed char so the user knows what theyre selecting
                    screenObjects.move_to_front(selectables[chosenOne])
                    draw()
                if even.type ==MOUSEBUTTONUP or (even.type == KEYDOWN and even.key == K_UP):##If they click or tap up, we let them out of selection
                    highlightStack = None
                    return None
    else:##Otherwise just pick the one available char
        charChosen = True
        chosenOne = 0
    highlightStack = None
    return selectables[chosenOne]
def handleClick(clickedPos):##This will generally handle all the mouse clicks within the games play
    global selectedObject##Because python gets its jimmies rustled over scope and local variables.. Don't remove this.
    global selectedOverlay
    global moveTo
    X = 0
    Y = 0
    for i in range(len(xGrid)):##Obtaining the square you cliked within
        if clickedPos[0] >= xGrid[i] and (xGrid[i] == xGrid[-1] or clickedPos[0] < xGrid[i+1]):
            X = i
    for i in range(len(yGrid)):
        if clickedPos[1] >= yGrid[i] and (yGrid[i] == yGrid[-1] or clickedPos[1] < yGrid[i+1]):
            Y = i
    handled = False##A flag to keep track of whether the click has been handled
    selectables = []
    for i in holding[X][Y]:
        for j in screenObjects:
            if selectedObject != None and j.nation == selectedObject.nation and i.nation == whomsTurn and not isinstance(selectedObject,settlement):
                ##Making it so that we just move to the square if another of this nations units/settlements are occupying
                selectedObject.moveUnit(X,Y)
                moveTo = None
                selectedObject = None
                selectedOverlay = None
                handled = True
            elif i == j and (i.nation == whomsTurn or selectedObject != None):
                selectables.append(i)
    if len(selectables) > 0 and handled == False:##Did we choose a square with chars?
        if selectedObject == None:##No object previosly selected.. select one from this tile.
            selectedObject = select(selectables)
            if selectedObject == None:
                return None
            selectedOverlay = selectedObject.decisionOverlay()##Also selecting the associated overlay. See draw() for how this is finished up.
            handled = True
        elif isinstance(selectedObject,unit) and (abs(X-selectedObject.gridX)  <=selectedObject.movesLeft) and (abs(Y-selectedObject.gridY) <=selectedObject.movesLeft):
            ##Select object for attacking, if within reach of selectedObject
            global chosen
            ##Autochoosing the strongest unit(not settlement) in the stack
            chosen = selectables[0]
            for i in selectables:
                if i.defenseStrength > chosen.defenseStrength or isinstance(chosen,settlement):
                    chosen = i
            screenObjects.move_to_front(chosen)
            draw()
            ##Setting everything up for the user to be able to decide to attack (with the overlay)
            moveTo = [X,Y]
            buttonReplacer = selectedOverlay.buttonLabelList
            buttonReplacer[0] = "Attack"
            selectedOverlay.newButtons(buttonReplacer)
            handled = True
        else:
            #They probably just want to deselect
            handleInteraction(selectedObject,selectedObject)
            handled = True
    if not isinstance(selectedObject,settlement) and selectedObject != None and handled == False :##If something is selected, we are about to move it.
        if (abs(Y-selectedObject.gridY) <=selectedObject.movesLeft) and (abs(X-selectedObject.gridX) <=selectedObject.movesLeft):## Checking that its within the moves for this turn
            moveTo = [X,Y]
            buttonReplacer = selectedOverlay.buttonLabelList
            buttonReplacer[0] = "Move (" + str(selectedObject.movesLeft) + ")"
            selectedOverlay.newButtons(buttonReplacer)
        else:##Otherwise we just disable and ignore the click
            moveTo = None
        handled = True
    if selectedObject != None and selectedObject.gridY > len(yGrid) - 3:
        selectedOverlay.top = True
def controlsScreen():##Some really basic screen selection stuff
    expoScreens = ["unitExplanation.png","unitExplanation2.png","uniExplanation.png","stackExplanation.png","finalExplanation.png"]
    expoImage = image.load(expoScreens[0])
    expoImage = transform.scale(expoImage,(1140,680))
    expoImage.convert()
    mainScreen.blit(expoImage,(0,0))
    arrowImage = image.load('arrows.png')
    arrowImage = transform.scale(arrowImage,(60,40))
    arrowImage.convert()
    mainScreen.blit(arrowImage,(1030,10))
    Font = font.SysFont("monospace", 14 ,True)
    enterLabel = Font.render('Enter To Return', 1, (255,255,255))
    mainScreen.blit(enterLabel,(1000,60))
    display.flip()
    selected = 0
    optionChosen = False
    while not optionChosen :
        for even in event.get():
            if even.type == KEYUP:
                if even.key == K_RIGHT:
                    selected += 1
                    selected = selected %5
                elif even.key == K_LEFT:
                    selected -= 1
                    selected = selected %5
                elif even.key == K_RETURN:
                    startScreen()
                    return None
            expoImage = image.load(expoScreens[selected])
            expoImage = transform.scale(expoImage,(1140,680))
            expoImage.convert()
            mainScreen.blit(expoImage,(0,0))
            mainScreen.blit(arrowImage,(1030,10))
            mainScreen.blit(enterLabel,(1000,60))
            display.flip()
def creditsScreen():##Some really basic screen selection stuff
    expoImage = image.load('credits.png')
    expoImage = transform.scale(expoImage,(1140,680))
    expoImage.convert()
    mainScreen.blit(expoImage,(0,0))
    Font = font.SysFont("monospace", 14 ,True)
    enterLabel = Font.render('Enter To Return', 1, (255,255,255))
    mainScreen.blit(enterLabel,(1000,10))
    display.flip()
    optionChosen = False
    while not optionChosen :
        for even in event.get():
            if even.type == KEYUP:
                if even.key == K_RETURN:
                    startScreen()
                    return None
def startScreen():##Some really basic screen selection stuff
    backImage = image.load('startScreen2.png')
    backImage = transform.scale(backImage,screenSize)
    backImage.convert()
    mainScreen.blit(backImage,(0,0))
    Font = font.SysFont("monospace", 70 ,True)
    selections = ["Start","Controls","Credits"]
    selectionsLabels = []
    for i in range(len(selections)):
        selectionsLabels.append(Font.render(selections[i], 1, (222,226,28)))
        mainScreen.blit(selectionsLabels[i],(150 ,250 + i*100))
    display.flip()
    selected = 0
    optionChosen = False
    while not optionChosen :
        for even in event.get():
            if even.type == KEYUP:
                if even.key == K_DOWN:
                    selectionsLabels[selected] = Font.render(selections[selected], 1, (222,226,28))
                    mainScreen.blit(selectionsLabels[selected],(150 ,250 + selected*100))
                    selected += 1
                    selected = selected %3
                elif even.key == K_UP:
                    selectionsLabels[selected] = Font.render(selections[selected], 1, (222,226,28))
                    mainScreen.blit(selectionsLabels[selected],(150 ,250 + selected*100))
                    selected -= 1
                    selected = selected %3
                elif even.key == K_RETURN:
                    if selected == 0:
                        playerPicker()
                        return None
                    elif selected == 1:
                        controlsScreen()
                        return None
                    elif selected == 2:
                        creditsScreen()
                        return None
            if not optionChosen:
                selectionsLabels[selected] = Font.render(selections[selected], 1, (255,255,255))
                mainScreen.blit(selectionsLabels[selected],(150 ,250 + selected*100))
                display.flip()
def playerPicker():##Gets the user(s) to pick a number of players, and input names.
    global numberOfPlayers
    backImage = Surface(screenSize)
    backImage.fill(backColour)
    mainScreen.blit(backImage,(0,0))
    ##Creating an overlay for selecting numbers of players.
    playerSelect = buttonOverlay(mainScreen, ["2","3","4"],(255,0,0))
    playerSelect.display()
    ##We'll store all teh players names here
    global nationNames
    nationNames = []
    ##Prompting
    inputbox.display_box(mainScreen,"Please select a number of deans.",backColour)
    ##Getting all the input needed.
    picked = False
    while not picked:
        for even in event.get():
            if even.type == MOUSEBUTTONUP:                
                numberOfPlayers = int(playerSelect.buttonClicked(mouse.get_pos()))
                if numberOfPlayers != 0:
                    for i in range(numberOfPlayers):
                        mainScreen.blit(backImage,(0,0))
                        playerSelect.display()
                        nationNames.append(inputbox.ask(mainScreen,"Dean "+ str(i+1)+" Name",backColour))
                    return None           
def main():
    init()##Initializing pygame
    startScreen()
    #controlsScreen()
    setUp()##Setting up game
    gameLoop()##Starting game
    
main()
