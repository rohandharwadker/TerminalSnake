import os
import pickle
import random
import sys
import time
import keyboard

# Game Size
GAME_WIDTH = 19
GAME_HEIGHT = 19

# ASCII
COLORS = {
    "def" : "\033[0m",
    "red" : "\033[91m",
    "yel" : "\033[93m",
    "gre" : "\033[92m",
    "bol" : "\033[1m"
}
ASCII_WALL_X = "|"
ASCII_WALL_Y = "---"
ASCII_WALL_CORNER = "+"
ASCII_SNAKE = "%s%s[-]%s"%(COLORS["gre"],COLORS["bol"],COLORS["def"])
ASCII_SNAKE_DEAD = "%s%s[-]%s"%(COLORS["gre"],COLORS["bol"],COLORS["def"])
ASCII_APPLE = "%s%s @ %s"%(COLORS["red"],COLORS["bol"],COLORS["def"])
ASCII_CRASH = "%s[-]%s"%(COLORS["red"],COLORS["def"])

# Global Variables
game_instance_exists = False
game_over = False
snake_moving = False
game_speed = .1 # Time between each step (lower = faster)
score = 0
highscore = 0
seconds_played = 0
minutes_played = 0

# Globall Methods
def save(item,file):
    with open(file,"wb") as f:
        pickle.dump(item,f)
    f.close()

def load(file,empty_return_value=0):
    if (os.path.exists(file)):
        with open(file,"rb") as f:
            return pickle.load(f)
    else:
        return empty_return_value

def get_time_str(min,sec):
    seconds = str(int(seconds_played))
    if (len(seconds) == 1):
        seconds = "0%s"%seconds
    return "%s:%s"%(min,seconds)

def send_gameover_message():
    print("\n\n%s  <[][][][] TERMINAL SNAKE [][][][:>%s==\n\n  %s%sGAME OVER"%(COLORS["gre"],COLORS["red"],COLORS["bol"],COLORS["red"]))
    time.sleep(1)
    print("%s%s  --------------------"%(COLORS["def"],COLORS["bol"]))
    print("  %sSCORE          %s%s%s"%(COLORS["def"],COLORS["bol"],COLORS["yel"],str(score)))
    time.sleep(.1)
    if (score == highscore):
        print("  %sNEW HIGH SCORE!"%COLORS["gre"])
        time.sleep(.1)
    print("  %sHIGH SCORE     %s%s%s"%(COLORS["def"],COLORS["bol"],COLORS["yel"],str(highscore)))
    time.sleep(.1)
    print("  %sAPPLES EATEN   %s%s%s"%(COLORS["def"],COLORS["bol"],COLORS["yel"],str(int(score/100))))
    print("  %sTIME PLAYED    %s%s%s"%(COLORS["def"],COLORS["bol"],COLORS["yel"],get_time_str(minutes_played,seconds_played)))
    time.sleep(.1)
    print()

class GameManager(): # manages setup and game states
    def __init__(self,width,height): # initialize game dimensions
        self.width = width
        self.height = height

    def check_pos_is_valid(self,x,y,width,height): # check if an (x,y) pair is within the game dimensions
        if (x >= width or x < 0):
            raise IndexError("x coordinate must be within the game width (0-%s)"%str(width))
        if (y >= height or y < 0):
            raise IndexError("y coordinate must be within the game height (0-%s)"%str(height))

    
    def set_game(self,snake,apple): # Draw the game, end conditions,
        # Get global variables
        global game_over
        global game_instance_exists
        global score

        # Check if this is the first time this function is being called (if so, don't rewrite on the lines above)
        if (not game_instance_exists):
            game_instance_exists = True
        else:
            for i in range(self.height+4):
                sys.stdout.write("\x1b[1A\x1b[2K")

        # Set and print score
        score = (snake.length-1)*100
        print("\n  %s%sHIGH SCORE %s %s     %s%sSCORE %s %s     %s%sTIME %s %s"%(COLORS["bol"],COLORS["yel"],COLORS["def"],str(highscore),COLORS["bol"],COLORS["yel"],COLORS["def"],str(score),COLORS["bol"],COLORS["yel"],COLORS["def"],get_time_str(minutes_played,seconds_played)))
        self.check_pos_is_valid(apple.x,apple.y,self.width,self.height)

        # Check if snake hit a wall or itself
        try:
            self.check_pos_is_valid(snake.x,snake.y,self.width,self.height)
        except IndexError: # snake is not within game dimensions (hit wall)
            game_over = True
            self.game_over()
        for coordpair in snake.get_coords_xy():
            if (snake.get_coords_xy().count(coordpair) > 1): # snake has 2 or more bits in one place (hit itself)
                game_over = True
                self.game_over()
                break

        # Pad the height and width to account for walls
        padded_height = self.height+2
        padded_width = self.width+2

        # Draw the game
        for y in range(padded_height):
            current_row_contents = [] # List of characters in current row
            for x in range(padded_width):
                current_character = "   "
                # Draw the walls
                if (x == 0):
                    if (y == 0 or y == padded_height-1):
                        current_character = "  %s"%ASCII_WALL_CORNER
                    else:
                        current_character = "  %s"%ASCII_WALL_X
                elif (x == padded_width-1):
                    if (y == 0 or y == padded_height-1):
                        current_character = "%s  "%ASCII_WALL_CORNER
                    else:
                        current_character = "%s  "%ASCII_WALL_X
                elif (y == 0 or y == padded_height-1):
                    current_character = "%s"%ASCII_WALL_Y
                else:
                    if ((snake.x,snake.y) == (apple.x,apple.y)): # Check if the snake is over an apple and lengthen accordingly, then move the apple
                        snake.lengthen()
                        apple.place_random(self.width-1,self.height-1,snake.get_coords_xy())
                    if ((x-1,y-1) in snake.get_coords_xy()): # Draw the snake
                        current_character = snake.draw()
                    elif ((apple.x,apple.y) == (x-1,y-1)): # Draw the apple
                        current_character = apple.draw()
                    else: # Draw an empty space
                        current_character = "   "
                
                if (game_over and ((snake.x,snake.y) == (x-1,y-1))): # if the game is over, draw a # at the head of the snake
                    current_character = ASCII_CRASH
                # append the current character to the list
                current_row_contents.append(current_character)
            # turn the current_row_contents list into a string and print to the terminal
            current_row = "".join(current_row_contents)
            print(current_row)
    
    def game_over(self): # destroy the snake and check for a high score
        global highscore
        snake.destroy()
        if (score > highscore):
            highscore = score
            save(highscore,"highscore.pickle")
        

class Apple(): # The apple (handles x,y and movement of apple)
    x = 0
    y = 0
    _ascii = ASCII_APPLE

    def __init__(self,x=0,y=0): # Place the apple at x,y
        self.x = x
        self.y = y
    
    def get(self): # Return x,y of apple
        return (self.x,self.y)

    def set(self,x,y): # Set the x,y of apple
        self.x,self.y = x,y

    def place_random(self,room_width,room_height,snake_coords_xy): # Place the apple in a random place, excluding the snake
        coord = (random.randrange(0,room_width+1),random.randrange(0,room_height+1))
        while (coord in snake_coords_xy):
            coord = (random.randrange(0,room_width+1),random.randrange(0,room_height+1))
        self.x,self.y = coord
    
    def draw(self): # Return the apple's ASCII character
        return self._ascii

class Snake: # The snake object (handles movement, etc.)
    length = 1  
    x = 0
    y = 0
    _ascii = ASCII_SNAKE
    coords = []
    lengthen_snake = False

    def __init__(self,x,y): # Place the snake at x,y
        self.x = x
        self.y = y
        self.coords.append([x,y,"up"])

    def draw(self): # Return the snake's ASCII character
        return self._ascii

    def lengthen(self): # Set the snake's 'lengthen' variable to 'True' (will be reset in 'move()')
        self.lengthen_snake = True

    def set_direction(self,new_direction): # Set the head of the snake's direction
        global snake_moving
        snake_moving = True
        old_direction = self.coords[0][2]
        ud_pair,ud_pair_invert = ("up","down"),("down","up")
        lr_pair,lr_pair_invert = ("left","right"),("right","left")
        change_dir = True
        if ((old_direction,new_direction) == ud_pair or (old_direction,new_direction) == ud_pair_invert):
            change_dir = False
        if ((old_direction,new_direction) == lr_pair or (old_direction,new_direction) == lr_pair_invert):
            change_dir = False
        if (change_dir or self.length == 1):
            self.coords[0][2] = new_direction

    def get_coords_xy(self): # Return a list of the snakes coordinates excluding the direction of each coordinate: [(x,y),(x,y),(x,y)...]
        coords_xy = []
        for x,y,d in self.coords:
            coords_xy.append((x,y))
        return coords_xy
    
    def move(self): # Move the snake and lengthen if neccessary
        last_coord_raw = [str(self.coords[-1][0]),str(self.coords[-1][1]),self.coords[-1][2]] # get the tail of the snake (for lengthening)
        for i in range(len(self.coords)): # Loop through all the coordinates and move them in their designated direction
            dir = self.coords[i][2]
            if (dir == "up"):
                self.coords[i][1] = self.coords[i][1]-1
            elif (dir == "down"):
                self.coords[i][1] = self.coords[i][1]+1
            elif (dir == "right"):
                self.coords[i][0] = self.coords[i][0]+1
            else:
                self.coords[i][0] = self.coords[i][0]-1
            
        for k in range(len(self.coords)): # Have each coordinate set the direction to that of the coordinate in front of it
            i = len(self.coords)-k-1 # Start at the tail and work forwards (required)
            if (i != 0):
                self.coords[i][2] = self.coords[i-1][2]
        
        if (self.lengthen_snake): # Lengthen the snake by adding another coordinate using last_coord (above)
            last_coord = [int(last_coord_raw[0]),int(last_coord_raw[1]),last_coord_raw[2]]
            self.coords.append(last_coord)
            self.lengthen_snake = False 
            self.length += 1

        self.x,self.y = self.coords[0][0],self.coords[0][1] # Set the x and y variables to the head of the snake
    
    def destroy(self): # Set the snakes ASCII character to ASCII_SNAKE_DEAD
        self._ascii = ASCII_SNAKE_DEAD  

gm = GameManager(GAME_WIDTH,GAME_HEIGHT) # Create the game board
snake = Snake(int((gm.width-1)/2),int((gm.height-1)/2)) # Create the snake
apple = Apple(0,0) # Create the apple
apple.place_random(gm.width-1,gm.height-1,snake.get_coords_xy())
# Assign the up,down,left,right keys to turn the snake
keyboard.add_hotkey("up",lambda: snake.set_direction("up"))
keyboard.add_hotkey("down",lambda: snake.set_direction("down"))
keyboard.add_hotkey("left",lambda: snake.set_direction("left"))
keyboard.add_hotkey("right",lambda: snake.set_direction("right"))
# Load the highscore
highscore = load("highscore.pickle")

while (not game_over): # Run the game
    gm.set_game(snake,apple)
    time.sleep(game_speed)
    if (not game_over and snake_moving):
        snake.move()
    if (seconds_played < 59 and snake_moving):
        seconds_played += game_speed
    elif (snake_moving):
        minutes_played += 1
        seconds_played = 0
gm.set_game(snake,apple)
send_gameover_message()
