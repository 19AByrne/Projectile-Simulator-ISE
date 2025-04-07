import pygame
import math

##errors / to-do
'''
hovering over points that touch the floor display a y distance as -0.0 how awesome 🤩🤩
'''

pygame.init()
wh = pygame.display.get_desktop_sizes()[0]
height = wh[1]
width = wh[0]
screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)

clock = pygame.time.Clock()
running = True

scale = 20 #default scale value
g = 9.8 #gravity

initial = (5,5) #default initial value
savedinitial = initial #saving the initial so as it changes due to restitution it reverts back to the user selected input when reset button is clicked

xshift = 0 # offset in the x-axis used with left and arrow keys
yshift = 0 # offset in the y-axis used with up and down arrow keys
#both offsets are applied to all coordinates of points

fontsize = 32
font = pygame.font.Font('freesansbold.ttf', fontsize)
debugfont = pygame.font.Font('freesansbold.ttf', 16)


e = 1/2 #value for restitution, denoted with e in applied maths
displayRestitution = ('1/2') #string of value for e

def time(init): #gets the time of a single motion
    return (init[1]) / (4.9)

def xrange(init): #horizontal distance covered in a motion
    mag = math.sqrt((init[0])**2+(init[1])**2) #magnitude of velocity
    theta = math.atan(init[1]/init[0]) #angle particle is projected at in radians
    return ( (mag**2) * (math.sin(2*theta)) ) / g

def maxheight(init): #maximum height reached in a single motion
    mag = math.sqrt((init[0])**2+(init[1])**2) #magnitude of velocity
    theta = math.atan(init[1]/init[0]) #angle particle is projected at in radians
    return ( (mag**2) * (math.sin(theta))*(math.sin(theta)) ) / (2*g)

###declaring all the images and their required states/rects

#list of different states for ready to fire, in motion, or Cross through it while hovering to say you can't press
FireButtonStates = [pygame.image.load('Images/Fire!.png').convert_alpha(),
                    pygame.image.load('Images/Fire! italic.png').convert_alpha(),
                    pygame.image.load('Images/Fire! strike.png').convert_alpha()]
FireButton = FireButtonStates[0]
FireButton_rect = FireButton.get_rect(center=(width/12,height/4))

ResetButton = pygame.image.load('Images/reset.png').convert_alpha()
ResetButton_rect = ResetButton.get_rect(center=(width/12, height/3))

ShowTrailButton_States = [pygame.image.load('Images/ShowTrail.png').convert_alpha(),
                          pygame.image.load('Images/XShowTrail.png').convert_alpha()]
showtrail = False
ShowTrailButton = ShowTrailButton_States[showtrail] #showtrail is boolean therefore, the bool val can be used to index its states
ShowTrailButton_rect = ShowTrailButton.get_rect(center=(width/12,height*7.69/19))

#list of different states for velocity input, box 1 selected, box 2 selected, or none
InputterStates = [pygame.image.load('Images/Inputter.png').convert_alpha(),
                    pygame.image.load('Images/InputterBox1selected.png').convert_alpha(),
                    pygame.image.load('Images/InputterBox2selected.png').convert_alpha()]
Inputter = InputterStates[0]
Inputter_rect = Inputter.get_rect(center=(width/12,height/7))
Box1_rect = pygame.Rect(Inputter_rect.left+12,Inputter_rect.top+25, 50, 50)
Box2_rect = pygame.Rect(Inputter_rect.left+120,Inputter_rect.top+25, 50, 50)
IJmode = True #input mode is defualt set to i and j vectors
inputting = False

#overlays showing the unit depending on which mode you are in for velocity input. magnitude & angle or I & J.
OverlayStates = [pygame.image.load('Images/MDoverlay.png').convert_alpha(), 
                 pygame.image.load('Images/IJoverlay.png').convert_alpha()]
Overlay = OverlayStates[IJmode] #bool value to index 

SwitchButton = pygame.image.load('Images/Switch.png').convert_alpha() #switch button for switching IJmode
SwitchButton_rect = SwitchButton.get_rect()
SwitchButton_rect.center = (Inputter_rect.center[0]+110,Inputter_rect.center[1])

#display box 1 and box 2 are for the velocity input
displayValueBox1 = ''
displayBox1Text = font.render(displayValueBox1, True, (255,255,255))
displayBox1Text_rect = displayBox1Text.get_rect()
displayBox1Text_rect.center = Box1_rect.center

displayValueBox2 = ''
displayBox2Text = font.render(displayValueBox2, True, (255,255,255))
displayBox2Text_rect = displayBox2Text.get_rect()
displayBox2Text_rect.center = Box2_rect.center

# testTextValue = 0
# testText = font.render(str(testTextValue), True, (255,255,255))

RestitutionButtonStates = [pygame.image.load('Images/restitution.png').convert_alpha(),
                           pygame.image.load('Images/restitutionSelected.png').convert_alpha()]
inputtingE = False
RestitutionButton = RestitutionButtonStates[inputtingE]#bool value to index
RestitutionButton_rect = RestitutionButton.get_rect(center = (width/12,height*8.09/17))

Bounce = False
BounceButtonStates = [pygame.image.load('Images/Bounce.png').convert_alpha(),
                      pygame.image.load('Images/XBounce.png').convert_alpha()]
BounceButton = BounceButtonStates[Bounce] #bool value to index
BounceButton_rect = BounceButton.get_rect(center=(width/12, height*8.09/17 + 77))

BlankBox = pygame.image.load('Images/BlankBox.png').convert_alpha() #blank boxes for top right as its only text to be rendered over it
baseBlankBox_rect = BlankBox.get_rect(center=(width-105,45))

NeedHelp = False 
HelpButton = pygame.image.load('Images/Help.png').convert_alpha()
HelpButton_rect = HelpButton.get_rect(center=(width-60,height-60))
HelpMenu = pygame.image.load('Images/HelpMenu.png').convert_alpha()

HideButton = pygame.image.load('Images/HideUI.png').convert_alpha()
HideButton_rect = HideButton.get_rect(topleft=(0,0))
HideUI = False


#custom event for when the projectile lands. (called when the time of the current motion elapses)
landing = pygame.event.custom_type()

#custom event for when zoomed in or out, to multiply coordinates by the scale variable
scaleshift = pygame.event.custom_type()
scaleshiftevent = pygame.event.Event(scaleshift)

#custom event for if drawmode is enabled and three point parabola needs to run.
GetParabola = pygame.event.custom_type()
GetParabolaEvent = pygame.event.Event(GetParabola)


showMousePos = False
simulating = False #projectile not in motion
landed = False #projectile not landed
originstate = False #origin state is a ready to fire state
boolListValues = [0,0] #list for the inputs to be ready. if no inputs have been entered [0,0], if box 1 has been enter [1,0], box 1 and box 2 [1,1] so on.
path = [] #list for points of the motion with scale applied
rawpath = [] #raw list of the points without scale applied so the points can be recalculated in the scaleshiftevent
initials = [initial] #list of initials
ranges = [] #list of each range of seperate motion
rawranges = [] #list of each range of seperate motion in cartesian form (scaled)
linesList = [] #list of each line
maxpoints = [] #list of each max point

#if custom lines exist it can change the projectiles range as it may end its motion before or after it passes through the same y value it began at. this dictionary stores the real range of a motion if it is not ordinary and its motion number is the key
RawRangeOutliers = {} 
#if custom lines exist the origins will also have outliers, this stores origins that were collisions with lines
CollisionOriginPoints = {}

totalT = 0 #total time of the current motion
displayTimeValue = 0 #true total time value of entire motion to be displayed to user in the top right
bounceCount = 0
maxCount = 0 #counter for maximum points of motions

fakeinitial = initial #called fakeinitial as it is using the format of the initial (tuple). and it being the values for box 1 and box 2. but it cannot be the initial as when both values are confirmed for fake initial, as they are mag and angle. they need to be converted into I and J coordinates.

def currentpoint(initial, deltaTime, gravity): #function to give any coordinate of a motion at any time.
    t = deltaTime/1000    
    x = (initial[0]*t)
    y = ( (initial[1]*t) - (gravity/2)*(t**2) )
    return (x,y)

class Motion:
    def __init__(self, initial, origin, range, maxh, totaltime, gravity, motionNo):
        self.initial = initial
        self.initialx = self.initial[0]
        self.initialy = self.initial[1]
        self.range = range
        self.origin = origin
        self.originx = self.origin[0]
        self.totalT = totaltime
        self.gravity = gravity
        self.motionNo = motionNo
        self.maxheight = maxh
        
    def getpoint(self, deltaTime):
        deltaTime = deltaTime/1000
        x = (self.initialx*deltaTime) #Sx = Ux*t
        y = (self.initialy*deltaTime) - (self.gravity/2)*(deltaTime**2) #Sy = Uy-(g/2)t^2
        return [(x,y), self.motionNo]
            
points_rects = [] #list of rects of maximum points
originpoints_rects = [] #list of rects of originpoints
Neworigins = [] #list of origin points
motions = [] #list of classes of motions
origin = (width/8, height*7/8) #True Origin point 

#initialising values for top right
displayTime = font.render(f'{round(displayTimeValue/1000,1)}s', True, (255,255,255)) 
displayTime_rect = displayTime.get_rect()
displayTime_rect.center = baseBlankBox_rect.center

displayBounceCount = font.render(f'Bounces: {bounceCount}' , True, (255,255,255))
displayBounceCount_rect = displayBounceCount.get_rect()
displayBounceCount_rect.center = (baseBlankBox_rect.center[0],baseBlankBox_rect.center[1]+77)


displayfinal = False #bool value to show the final point
hoveringMax = False #if hovering over a maximum point
hoveringOrigin = False #if hovering over an origin point

DrawMode = False #custom lines are enabled
drawing = False #actively ready to draw a line
incomingCollision = False
pointa = (0,0)
pointb = (0,0)
CollidingPoints = [] #list of collision points

#checks the difference between 2 values and if they are considered the same point
def ToleranceCheck(x,y):
    Tolerance = 0.005
    difference = abs(x-y)
    if difference > Tolerance:
        return True
    else:
        return False


def QuadraticSolver(a,b,c):
    discriminant = (b**2) - (4*a*c)
    if discriminant < 0:
        return 'Not Real'
    elif discriminant == 0:
        return ( -(b) + math.sqrt((b**2) - (4*a*c) ) ) / (2 * a)
    elif discriminant > 0:
        value1 = ( -(b) + math.sqrt((b**2) - (4*a*c) ) ) / (2 * a)
        value2 = ( -(b) - math.sqrt((b**2) - (4*a*c) ) ) / (2 * a)
        return [value1,value2]

class Line:
    def __init__(self, pointA, pointB):
        #pointA and B are in cartesian form,
        self.pointA = pointA
        self.pointB = pointB
        linesList.append(self)

        try:
            self.slope = (self.pointB[1]-self.pointA[1]) / (self.pointB[0]-self.pointA[0])
        except ZeroDivisionError:
            self.slope = float('inf')
        self.yIntercept = self.pointA[1] - (self.slope * self.pointA[0])
        
        self.angle = (math.atan(self.slope))

    def collisionCheck(self, Coefficients, origin): #coefficients of current motion.
        if self.slope == float('inf'): #vertical line, slope = inf
            xVal = self.pointA[0]
            yVal = Coefficients[0]*(xVal**2) + Coefficients[1]*xVal + Coefficients[2] #getting y value through quadratic function
            Restriction = sorted([self.pointA[1],self.pointB[1]])
            if yVal >= Restriction[0] and yVal <= Restriction[1]: #vertical lines cant have an x range so must use a y range
                if ToleranceCheck(origin[0], xVal):
                    return xVal
                else: return False
        else:
            #letting the line equation equal the quadratic equation and solving for intersection points
            intersectionXValues = QuadraticSolver(Coefficients[0], Coefficients[1] - self.slope, Coefficients[2] - self.yIntercept) 
            Restriction = sorted([self.pointA[0],self.pointB[0]])
            
            if type(intersectionXValues) == list:
                intersectionXValues_valid = []
                #finding the collision point thats inside the range
                for xVal in intersectionXValues:
                    if xVal >= Restriction[0] and xVal <= Restriction[1]: 
                        intersectionXValues_valid.append(xVal)

                #Tolerance check the point
                for xVal in intersectionXValues_valid:
                    if ToleranceCheck(origin[0], xVal):
                        return xVal
                    else: return False

            elif type(intersectionXValues) == float:
                if intersectionXValues >= Restriction[0] and intersectionXValues <= Restriction[1]:
                    return intersectionXValues
            else: return False
    

#Origin should be in cart form, time taken for any motion with given initial to reach X meters in horizontal displacement
def timeToReachX(initial, X, currentOrigin):
    return (X-currentOrigin[0]) / (initial[0])

# Line( (38,1), (44,2.5) )
# Line( (20,2), (30,8))
# Line( (-2,2), (8,4))
# Line( (10,2), (50,16))
Line( (13,3), (13,9))

#function will return coeffs of quadratic equation in the form of ax2+bx+c, they should all be cartesian form
def threepointparabola(x1,y1,x2,y2,x3,y3):
    a = ( ((x3-x2)*(y2-y1)) - ((x2-x1)*(y3-y2)) ) / ( ((x3-x2)*(x2**2-x1**2)) - ((x2-x1)*(x3**2-x2**2)) )
    
    b = ( (y2-y1)-a*(x2**2-x1**2) ) / (x2-x1)
    
    c = y1 - a * x1**2-b*x1
    
    return [a,b,c]

#this functions takes in a point that is already scaled and in the correct form to be displayed on screen, takes in the current variables for scaling and undoes the scale and returns the point in cartesian form
def pixelToCart(p, CurrentXshift, CurrentYshift, CurrentScale):
    p = ( (p[0] - origin[0] + CurrentXshift)/CurrentScale, (origin[1] - p[1] - CurrentYshift)/CurrentScale )
    return p

#finds the xrange of a motion given the origin, if the origin is not on the ground, the projectile will continue to fall beneath the y value of the origin and the x displacement will increase
def xrangeGivenOrigin(init, currentOrigin):
    timeValues = QuadraticSolver( ((-1/2)*g), (init[1]), (currentOrigin[1]))
    if timeValues[0] > 0:
        posTVal = timeValues[0]
    else:
        posTVal = timeValues[1]
    return (init[0]*posTVal)



while running:
    pygame.event.post(scaleshiftevent) #calls the event that shifts all coordinates to the current scale

    '''
    If the values are entered, it displays the saved initial. and it displays it according to which mode you are in
    so if the values are entered in IJMode it can display the savedinitial fine, but if in the other mode, it needs to convert them into magnitude and angle form before displaying.
    I keep the initial variable in the form I & J the entire time to make calculations simple. I only need to adjust if in angle & mag mode and displaying it to user
    '''
    if not inputting:
        if IJmode:
            if boolListValues[0] == 1:
                displayValueBox1 = str(savedinitial[0])
            if boolListValues[1] == 1:
                displayValueBox2 = str(savedinitial[1])
        else:
            if boolListValues[0] == 1:
                ddisplayValueBox1 = str(round(math.sqrt((savedinitial[0]**2)+(savedinitial[1]**2)),2))
            if boolListValues[1] == 1:
                displayValueBox2 = str(round(math.degrees(math.atan(savedinitial[1]/savedinitial[0])),1))

    
    dT = clock.get_time() #deltaTime
            
    #turning the display values of box 1 and box 2 into fonts ready to be blit
    displayBox1Text = font.render(displayValueBox1, True, (255,255,255))
    displayBox1Text_rect = displayBox1Text.get_rect()
    displayBox1Text_rect.center = Box1_rect.center
    displayBox2Text = font.render(displayValueBox2, True, (255,255,255))
    displayBox2Text_rect = displayBox2Text.get_rect()
    displayBox2Text_rect.center = Box2_rect.center
    
    
    #Information boxes of the motion in the top right, inside game loop so text can update
    displayBounceCount = font.render(f'Bounces: {bounceCount}' , True, (255,255,255)) 
    displayTime = font.render(f'{round(displayTimeValue/1000,1)}s', True, (255,255,255))

    Restitution_text = font.render(displayRestitution, True, (255,255,255))
    Restitution_text_rect = Restitution_text.get_rect()
    Restitution_text_rect.center = (RestitutionButton_rect.center[0]+55,RestitutionButton_rect.center[1]+2)
    
    # testText = font.render(str([round(x) for x in rawranges]), True, (255,255,255))
    # testText = debugfont.render((f'{Neworigins}'), True, (255,255,255))


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        #will not attempt to detect input on rects if UI is hidden or if already inputting
        if event.type == pygame.MOUSEBUTTONDOWN and not HideUI and not inputting and not inputtingE: 
            if FireButton_rect.collidepoint(event.pos):
                if not simulating and originstate: #only fires when in a ready to fire state
                    pygame.time.set_timer(landing, round(time(initial)*1000), 1)
                    motions.append(Motion(initial, origin, xrange(initial),maxheight(initial), time(initial), g, 0))
                    simulating = True
                    originstate = False
                    if DrawMode:
                        pygame.event.post(GetParabolaEvent)                
                    
            if ResetButton_rect.collidepoint(event.pos):
                #resets all values to default value
                simulating = False
                landed = False
                if all(boolListValues):
                    originstate = True
                totalT = 0
                displayTimeValue = 0
                path = []
                rawpath = []
                initials = [savedinitial]
                ranges = []
                Neworigins = []
                bounceCount = 0
                initial = savedinitial
                motions = []
                maxpoints = []
                maxCount = 0
                points_rects = []
                originpoints_rects = []
                displayfinal = False
                rawranges = []
                CollisionOriginPoints = {}
                RawRangeOutliers = {}
                incomingCollision = False
                linesList = []
                CollidingPoints = []
                
            if ShowTrailButton_rect.collidepoint(event.pos):
                showtrail = not showtrail #swaps bool value
                ShowTrailButton = ShowTrailButton_States[showtrail] #bool value for index
            
            if Box1_rect.collidepoint(event.pos):
                #if in ready state to be fired or if not all values have been entered, as values can not be entered and will not be in a ready to fire state
                #all(boolListValues) returns True if all values inside the list equal True, therefore it means ready to fire
                if originstate or not all(boolListValues): 
                    Inputter = InputterStates[1]
                    inputting = True
                    selected = 0 #box 1
                    displayWorkingValue = ''#when inputting it displays nothing by default because nothing has been typed
                    
            if Box2_rect.collidepoint(event.pos):
                if originstate or not all(boolListValues): 
                    Inputter = InputterStates[2]
                    inputting = True
                    selected = 1 #box 2
                    displayWorkingValue = '' 
                    
            if SwitchButton_rect.collidepoint(event.pos):
                if originstate or not all(boolListValues):
                    IJmode = not IJmode #reverses bool value
                    Overlay = OverlayStates[IJmode] #bool value for index
                    boolListValues = [0,0] #empties the values when switching mode therefore values are not ready
                    originstate = False #not in a ready to fire state as the values have just been emptied
                    displayValueBox1 = '' #when inputting displays nothing as nothing has been typed
                    displayValueBox2 = ''
                
            if BounceButton_rect.collidepoint(event.pos):
                Bounce = not Bounce #reverses bool value
                
            if RestitutionButton_rect.collidepoint(event.pos):
                if originstate or not all(boolListValues):
                    inputtingE = True
                    workingRestitution = '' #when inputting displays nothing as nothing has been typed
            
            #doesnt allow lines that go below the ground
            if drawing:
                if event.pos[1] > origin[1]:
                    drawing = False
                else:
                    drawingPointA = event.pos
                        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if HideButton_rect.collidepoint(event.pos):
                HideUI = not HideUI #swaps bool

        if event.type == pygame.MOUSEBUTTONUP and not HideUI and not inputting and not inputtingE:
            if drawing:
                if event.pos[1] < (height*7/8):
                    drawingPointB = event.pos
                    
                    #converting from raw pixel coordinate to cartesian form (scaled coordinate system the projectile uses)
                    drawingPointA = ( (drawingPointA[0] - origin[0] + xshift)/scale, (origin[1] - drawingPointA[1] - yshift)/scale )
                    drawingPointB = ( (drawingPointB[0] - origin[0] + xshift)/scale, (origin[1] - drawingPointB[1] - yshift)/scale )
                    
                    Line(drawingPointA, drawingPointB)
                drawing = False

        if event.type == pygame.KEYDOWN:
            if inputting: 
                if event.key >= 48 and event.key <= 57: #48-57 is the relative key for digits 0-9, if inputting it detects if a key from 0-9 has been inputted and it adds it to emptystring, backspace and period is also allowed
                    displayWorkingValue = displayWorkingValue + str(pygame.key.name(event.key))
                if event.key == pygame.K_PERIOD:
                    displayWorkingValue = displayWorkingValue + str(pygame.key.name(event.key))
                if event.key == pygame.K_BACKSPACE:
                    displayWorkingValue = displayWorkingValue[:-1] #deletes last value of str
                if event.key == pygame.K_RETURN and not not displayWorkingValue.strip('0') and displayWorkingValue.count('.') <= 1: #(not str) returns True if the str is empty therefore (not not str) returns False if the str is empty, stripping the 0 so if the inputted value is only 0 and it is stripped the len() will then be 0. making sure only one period is entered
                    if IJmode:
                        if selected == 0: #box 1
                            try:
                                initial = ( int(displayWorkingValue), initial[1] ) 
                            except:
                                initial = ( float(displayWorkingValue), initial[1] )
                        
                        #an integer display of x.0 is unnecasary and can just be displayed as x, if must be a float then it will be displayed x.y        
                        if selected == 1:
                            try:
                                initial = ( initial[0], int(displayWorkingValue) ) 
                            except:
                                initial = ( initial[0], float(displayWorkingValue) )
                    if not IJmode:
                        if selected == 0:
                            try:
                                fakeinitial = ( int(displayWorkingValue), fakeinitial[1] ) 
                            except:
                                fakeinitial = ( float(displayWorkingValue), fakeinitial[1] )
                        if selected == 1:
                            try:
                                fakeinitial = ( fakeinitial[0], int(displayWorkingValue) ) 
                            except:
                                fakeinitial = ( fakeinitial[0], float(displayWorkingValue) )
                        #converting magnitude and angle to i & j
                        initial = ( round(fakeinitial[0]*math.cos(math.radians(fakeinitial[1])),2), round(fakeinitial[0]*math.sin(math.radians(fakeinitial[1])),2))
                    savedinitial = initial #because the value has been confirmed the new constant displayed value needs to be redeclared.
                    initials = [savedinitial]
                    boolListValues[selected] = 1 #selected is a 0 or 1 for corresponding box. therefore can be used to index the boollistvalues and declare that this value is ready
                    inputting = False
                    if all(boolListValues): #if all values are ready it is in a ready to fire state
                        originstate = True
                
            if inputtingE:
                if event.key >= 48 and event.key <= 57: #getting keys from 0-9, slash is also allowed
                    workingRestitution = workingRestitution + str(pygame.key.name(event.key))
                if event.key == pygame.K_SLASH:
                    workingRestitution = workingRestitution + str(pygame.key.name(event.key))
                if event.key == pygame.K_BACKSPACE:
                    workingRestitution = workingRestitution[:-1] #deletes last value of str

                #the length of the string must be 3 and we must strip '/'s before checking the length. I must also check that '/' is in the str after '/' is stripped and that the count of '/' is only 1. I must also check the length of str when '0' is stripped as I cannot have 'x/0' or '0/x'
                if event.key == pygame.K_RETURN and len(workingRestitution.strip('/')) >= 3 and '/' in workingRestitution.strip('/') and workingRestitution.count('/') == 1 and len(workingRestitution.strip('0')) >= 3: 
                    inputtingE = False 
                    a = int(workingRestitution[:workingRestitution.find('/')]) #grabbing the a from this str
                    b = int(workingRestitution[workingRestitution.find('/')+1:]) #grabbing the b from this str
                    e = a/b #declaring restitution value
                    
            if event.key == pygame.K_ESCAPE:
                running = False #ends game loop
                
            if event.key == pygame.K_UP:
                yshift -= 20
                
            if event.key == pygame.K_DOWN:
                if yshift != 0: #limits the yshift so it cannot go more down then needed
                    yshift += 20
                    
            if event.key == pygame.K_RIGHT:
                xshift += 20
                
            if event.key == pygame.K_LEFT:
                if xshift != 0: #limits the xshift so it cannot go more left then needed
                    xshift -= 20
                
            if event.key == pygame.K_i:
                scale += 0.25
                
            if event.key == pygame.K_o:
                if scale != 0.25: #limiting scale as scale equalling 0 causes errors
                    scale -= 0.25
            
            if event.key == pygame.K_m:
                showMousePos = not showMousePos #swap bool
                
            if event.key == pygame.K_r: #resets offset and scale
                xshift, yshift = 0,0
                scale = 20

            #inputs to be turned into buttons
            if event.key == pygame.K_d:
                drawing = True
            if event.key == pygame.K_f:
                DrawMode = not DrawMode

        if event.type == scaleshift: #event called to adjust the coordinate points to the required scale
            rawranges = [xrange(init) for init in initials]
            
            #ranges have been regenerated from the initial velocities but the outliers must be changed
            if RawRangeOutliers:
                for index, RealRange in RawRangeOutliers.items():
                    rawranges[index] = RealRange

            ranges = [scale*r for r in rawranges]

            Neworigins = []
            for i,r in enumerate(ranges):
                if i == 0:
                    Neworigins.append((r,0))
                else:
                    Neworigins.append((Neworigins[i-1][0]+r,0))

            #inserting the true origin at the beginning
            Neworigins.insert(0,(0,0))
            #changing the outlier origin points to the collisionpoints
            if CollisionOriginPoints:
                for i, o in CollisionOriginPoints.items():
                    Neworigins[i] = (scale*o[0],scale*o[1])
            
            Neworigins = [ ( (o[0]+(width/8), (height*7/8)-o[1]) ) for o in Neworigins]

            if incomingCollision:
                currentOriginCartForm = pixelToCart(Neworigins[bounceCount],xshift,yshift,scale)
                RawRangeOutliers[bounceCount] = NextCollisionXPoint - currentOriginCartForm[0]
                CollisionOriginPoints[bounceCount+1] = (NextCollisionXPoint, NextCollisionYPoint)
            
            maxpoints = [(scale*xrange(init)/2 + Neworigins[i][0] - xshift, Neworigins[i][1] - scale*maxheight(init)- yshift) for i,init in enumerate(initials)] #updates list of maxheights for every initial

            #creating rects for important points to be highlighted
            points_rects = []
            for i in range(len(maxpoints)):
                temprect = pygame.Rect(0,0,10,10)
                temprect.center = maxpoints[i]
                points_rects.append(temprect)

            originpoints_rects = []
            for i in range(len(Neworigins)):
                temprect = pygame.Rect(0,0,10,10)
                temprect.center = (Neworigins[i][0]-xshift,Neworigins[i][1]-yshift)
                originpoints_rects.append(temprect)

            temprect = pygame.Rect(0,0,10,10)
            if incomingCollision:
                temprect.center = (origin[0] + scale*NextCollisionXPoint-xshift,origin[1] - scale*NextCollisionYPoint - yshift)
                finalpoint_rect = temprect
                Neworigins.append(finalpoint_rect.center)
            else:
                temprect.center = (origin[0] + sum(ranges) - xshift, origin[1] - yshift)
                finalpoint_rect = temprect
                Neworigins.append(finalpoint_rect.center)
                
            '''this is taken from the getpoint function in the motion class,the points are multiplied by the scale as it can be constantly changed. 
            index 1 is the motion number label. not scale dependant but used so when drawing each circle it knows what origin it is relative to as there is a list of origins'''
            path = [[(scale*p[0][0],scale*p[0][1]), p[1]] for p in rawpath] 

        if event.type == GetParabola and len(rawranges) != 0:
            # print('getting parabola🥺')
            #getting the 3 known points of the parabola and getting the coefficients
            originCartForm = pixelToCart((Neworigins[bounceCount][0],Neworigins[bounceCount][1]), xshift, yshift, scale)
            finalxPointCoeff = (originCartForm[0] + xrange(initial))
            maxpointxCoeff = ( (originCartForm[0] + finalxPointCoeff) / 2)
            Coeffs = threepointparabola(originCartForm[0], originCartForm[1], maxpointxCoeff, originCartForm[1] + maxheight(initial), finalxPointCoeff, originCartForm[1])

            CollidingPoints = []
            #getting all collision points and sorting them to know whats the first collision
            for i,line in enumerate(linesList):
                lineCollisionPoint = line.collisionCheck(Coeffs, originCartForm)
                if lineCollisionPoint:
                    CollidingPoints.append(lineCollisionPoint)
                    NextLineIndex = i
            CollidingPoints = sorted(CollidingPoints)
            if len(CollidingPoints) != 0:
                #conditions are making sure the collision point is in the direction the projectile is moving
                Condition1 = CollidingPoints[0] > originCartForm[0] and initial[0] > 0
                Condition2 = CollidingPoints[0] < originCartForm[0] and initial[0] < 0
                if Condition1 or Condition2:
                    incomingCollision = True
                    NextCollisionXPoint = CollidingPoints[0]
                    #time will be different so calls function to get time when projectile reaches the collision point
                    pygame.time.set_timer(landing, round(timeToReachX(initial,NextCollisionXPoint,originCartForm)*1000), 1)
                    NextCollisionYPoint = Coeffs[0]*(NextCollisionXPoint**2) + Coeffs[1]*NextCollisionXPoint + Coeffs[2]
            else:
                incomingCollision = False

        if event.type == landing and simulating:
            #if the origin is not on the floor and its not going to collide the projectile must fall to the floor, therefore range is an outlier
            if Neworigins[bounceCount][1] != height*7/8 and not incomingCollision:
                currentOriginCartForm = pixelToCart(Neworigins[bounceCount],xshift, yshift, scale)
                RawRangeOutliers[bounceCount] = xrangeGivenOrigin(initial,currentOriginCartForm)
            CollidingPoints = [] #clearing list for new motion to calc new ones
            if not Bounce: #if bounce is disabled and the time has elapsed then simulating must become False.
                simulating = False
                landed = True
            else:
                if incomingCollision:
                    SlopeOfSurface = math.degrees(linesList[NextLineIndex].angle)
                    originCartForm = pixelToCart(Neworigins[bounceCount],xshift,yshift,scale)
                    FinalVelocity = (initial[0], initial[1] - (g * timeToReachX(initial, NextCollisionXPoint, originCartForm)))
                    initial = (e*FinalVelocity[0],e*FinalVelocity[1])
                    magnitude = math.sqrt(initial[0]**2 + initial[1]**2)
                    direction = abs(math.degrees(math.atan2(initial[1],initial[0])))
                    
                    a = Coeffs[0]
                    b = Coeffs[1]
                    TangentSlope = (2*a*NextCollisionXPoint+b)

                    if linesList[NextLineIndex].slope < TangentSlope and initial[0] > 0:
                        newdirection = 2*SlopeOfSurface - direction
                    else:
                        newdirection = direction + 2*SlopeOfSurface
                    initial = (magnitude*math.cos(math.radians(newdirection)),magnitude*math.sin(math.radians(newdirection)))
                else:
                    #if not colliding with a line it will reflect with the final velocity, solves for time when it hits the floor, when its y displacement is equal to negative of origins y value it hits the floor
                    CartFormOrigin = pixelToCart(Neworigins[bounceCount], xshift, yshift, scale)
                    tValues = QuadraticSolver( ((-1/2)*g), (initial[1]), (CartFormOrigin[1]))
                    if tValues[0] > 0:
                        posTVal = tValues[0]
                    else:
                        posTVal = tValues[1]
                    FinalYVel = initial[1] - (g * posTVal)
                    initial = (initial[0], (-e)*FinalYVel)
               
                incomingCollision = False

                if abs(initial[1]) < 0.5:
                    #caps the y-value. When the Y-velocity is uncapped because its being reduced by a fraction therefore it can never reach 0. therefore infinite bounces.
                    #this only happens in this simulation as it cannot truly account for every acting force on a real particle
                    simulating = False
                    landed = True
                else:
                    bounceCount += 1
                    CartFormOrigin = pixelToCart(Neworigins[bounceCount], xshift, yshift, scale)
                    tValues = QuadraticSolver( ((-1/2)*g), (initial[1]), (CartFormOrigin[1]))
                    if tValues[0] > 0:
                        posTVal = tValues[0]
                    else:
                        posTVal = tValues[1]

                    pygame.time.set_timer(landing, round(posTVal*1000),1)
                    initials.append(initial) #appends the new initial velocity to the list
                    rawranges.append(xrange(initial)) #appends the new range
                
                motions.append(Motion(initial, Neworigins[bounceCount], xrange(initial),maxheight(initial), time(initial), g, bounceCount))                 
            
                totalT = 0 #resets the time to be used for new motion
                
                #calls event to get coefficents of the motion
                if DrawMode:
                    pygame.event.post(GetParabolaEvent)

    screen.fill("black") #background
    if DrawMode:
        for line in linesList:
            pygame.draw.aaline(screen, 'white', (width/8 + scale*line.pointA[0] - xshift, height*7/8 - scale*line.pointA[1] - yshift), (width/8 + scale*line.pointB[0] - xshift, height*7/8 - scale*line.pointB[1] - yshift))
    ground = pygame.Rect(0 , (height*7/8) - yshift ,width,height/8)
    pygame.draw.rect(screen, 'dark green', ground) #ground
    
    for x in range(100):
        pygame.draw.circle(screen, 'blue', (width/8 + x*scale -xshift, (height*7/8) - yshift), 3)#Blue points, (placed exactly 1m apart)
            
    if HelpButton_rect.collidepoint(pygame.mouse.get_pos()):
        NeedHelp = True #if needhelp true help menu is shown
    else:
        NeedHelp = False
    
    if simulating:
        totalT += dT #totalT is the total time of the current motion. deltaTime must be added every update in the game loop
        displayTimeValue += dT #dt must be added to the displayTimeValue as displayTimeValue is the entire collected time of all motions
        path.append(motions[bounceCount].getpoint(totalT)) #appending the points to the path
        rawpath.append(motions[bounceCount].getpoint(totalT)) #rawpath exists as it is unscaled and when the scale event is called. it does not repeadetly rescale the path as that would not work. it needs to multiply the scale by the raw value
        if totalT >= (time(initial)*1000/2) and maxCount == bounceCount: #if half of the time of the current motion elapses, the maxcount should go up.
            maxCount += 1
        
    if not originstate: 
        if FireButton_rect.collidepoint(pygame.mouse.get_pos()): #Checking if hovering over the button,
            FireButton = FireButtonStates[2] #changes the state of the button to visually diplay to user it cannot currently be pressed
        else:
            FireButton = FireButtonStates[1]
            
    if inputting:#while inputting the box should display the working value. the value as its being typed
        if selected == 0:
            displayValueBox1 = displayWorkingValue
        else:
            displayValueBox2 = displayWorkingValue
    
    if inputtingE:#same as above
        displayRestitution = workingRestitution

    if landed:
        displayfinal = True
        
        
    if originstate:
        FireButton = FireButtonStates[0]
    elif all(boolListValues):
        if showtrail:
            for p in path[:-1]: #Filtering out latest point in list as it cannot be scaled fast enough
                '''
                p[1] is taken form the motion.getpoint(...) function, it is the motion Number.
                It is used so I can index the origins list and it will correctly use the correct offset when iterating through the path,
                as each point in the path has a origin assigned it it
                '''
                pygame.draw.circle(screen, 'white', (Neworigins[p[1]][0] + p[0][0] - xshift,Neworigins[p[1]][1] - p[0][1] - yshift), 3)
            for i in range(len(ranges)): #iterates through ranges calculated. if the index is below the maxcount display all maxpoints. same for bounceCount and origins
                if i < maxCount:
                    pygame.draw.circle(screen, 'green', maxpoints[i] , 5)

                if i <= bounceCount:
                    pygame.draw.circle(screen, 'blue', (Neworigins[i][0]-xshift,Neworigins[i][1]-yshift), 5)

            if displayfinal:
                pygame.draw.circle(screen, 'brown', Neworigins[-1], 5)

        if not showtrail:
            '''
            if not showing trail, the entire path does not need to be kept track of, so I can just calculate the point at the exact current time,
            indexing origins with the bounceCount as the bounceCount cannot go down as I wouldnt need to render any past motions.
            '''
            if not displayfinal:
                currentpos = currentpoint(initial, totalT, g)
                pygame.draw.circle(screen, 'white', (Neworigins[bounceCount][0] + currentpos[0]*scale - xshift,Neworigins[bounceCount][1] - currentpos[1]*scale - yshift), 3)
            else:
                pygame.draw.circle(screen, 'white', (Neworigins[-1][0], Neworigins[-1][1]), 3)
    pygame.draw.circle(screen, 'red', (origin[0]-xshift,origin[1]-yshift), 5) # True Origin

    if not HideUI:
        #information boxes in top right
        screen.blit(BlankBox,baseBlankBox_rect)
        screen.blit(BlankBox,(baseBlankBox_rect[0],baseBlankBox_rect[1]+77))
        
        #information values in top right
        screen.blit(displayTime,displayTime_rect) 
        screen.blit(displayBounceCount,displayBounceCount_rect)
        
        #buttons for user and their values
        screen.blit(FireButton,FireButton_rect)
        screen.blit(ResetButton, ResetButton_rect)
        screen.blit(ShowTrailButton, ShowTrailButton_rect)
        
        
        if not inputting:
            Inputter = InputterStates[0]
        screen.blit(Inputter,Inputter_rect)
        screen.blit(Overlay,Inputter_rect)
        
        screen.blit(SwitchButton,SwitchButton_rect)
        screen.blit(RestitutionButtonStates[inputtingE], RestitutionButton_rect)
        screen.blit(Restitution_text,Restitution_text_rect)
        
        
        if showMousePos:
            MouseCoords = font.render( (f'({ round( (pygame.mouse.get_pos()[0] - origin[0] + xshift)/scale,2  ) },{ round((origin[1] - pygame.mouse.get_pos()[1]-yshift)/scale,2)})m or {pygame.mouse.get_pos()}'), True, (255,255,255))
            screen.blit(MouseCoords, (pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1]-32))

        screen.blit(displayBox1Text, displayBox1Text_rect)
        screen.blit(displayBox2Text, displayBox2Text_rect)        
        screen.blit(BounceButtonStates[Bounce],BounceButton_rect)
        screen.blit(HelpButton,HelpButton_rect)
        
        if NeedHelp:
            screen.blit(HelpMenu,((width/5),height/12))
            
        if showtrail:
            for i,rect in enumerate(points_rects):
                if i <= maxCount: #so it only displays what the projectile has passed through
                    if rect.collidepoint(pygame.mouse.get_pos()):
                        hoveringMax = True
                        if not hoveringOrigin:
                            maxpoint_Cart = pixelToCart(rect.center,xshift,yshift,scale)
                            maxpointText = font.render(f'({round(maxpoint_Cart[0],1)},{round(maxpoint_Cart[1],1)})m',True, (68,71,187))
                            screen.blit(maxpointText,(rect.center[0], rect.center[1]-45))
                    else:
                        hoveringMax = False

                        
            for i,rect in enumerate(originpoints_rects):
                if i <= bounceCount: #so it only displays what the projectile has passed through
                    if rect.collidepoint(pygame.mouse.get_pos()):
                        hoveringOrigin = True
                        if not hoveringMax:
                            originCartForm = pixelToCart(rect.center,xshift,yshift,scale)
                            originText = font.render(f'({round(originCartForm[0],1)},{round(originCartForm[1],1)})m', True, (68,71,187))
                            screen.blit(originText,(rect.center[0], rect.center[1]-45))
                    else:
                        hoveringOrigin = False        

            if displayfinal:
                if finalpoint_rect.collidepoint(pygame.mouse.get_pos()):
                    finalpoint_Cart = pixelToCart(Neworigins[-1], xshift, yshift, scale)
                    finalpointText = font.render(f'({round(finalpoint_Cart[0],1)},{round(finalpoint_Cart[1],1)})m', True, (68,71,187))

                    finalpoint_rect.center = (finalpoint_rect.center[0], finalpoint_rect.center[1]-45)
                    screen.blit(finalpointText, finalpoint_rect)
                    
    screen.blit(HideButton,HideButton_rect)
    pygame.display.flip()
    clock.tick(144)  # fps limit
pygame.quit()
exit()