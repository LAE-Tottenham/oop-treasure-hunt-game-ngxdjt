from random import shuffle, choice, randint
from entities import *
from getch import getch
from time import sleep
from termcolor import colored
import os
from ability import Ability
import pyfiglet as pfg

def dprint(string:str):
    for char in string:
        print(char, end='', flush=True)
        sleep(0.05)
    print()

class MazeDimensionError(Exception):
    pass

class Location:
    def __init__(self, size:int):
        self.size = size
        self.room = []

    def show_room(self):
        for row in self.room:
            print(' '.join(row))

class Maze(Location):
    def __init__(self, size:int):
        super().__init__(size)

    def generate_maze(self):
        if self.size % 2 == 0:
            raise MazeDimensionError("Dimensions must be odd")

        self.room = [["x" for i in range(self.size)] for i in range(self.size)]

        x, y = (-1, 1)
        stack = [(y, x)]
        directions = [(0,2), (0,-2), (2,0), (-2,0)]
        
        while len(stack) > 0:
            y, x = stack[-1]

            shuffle(directions)

            for dy, dx in directions:
                ny, nx = y + dy, x + dx
                if nx > 0 and ny > 0 and nx < self.size-1 and ny < self.size-1 and self.room[ny][nx] == "x":
                    self.room[ny][nx] = " "
                    self.room[ny-dy//2][nx-dx//2] = " "
                    stack.append((ny, nx))
                    break
            else:
                stack.pop()

        self.room[-2][-1] = " "
    
    def load_enemies(self):
        for i in range(self.size*7):
            y = randint(1, self.size-1)
            x = randint(1, self.size-1)
            if randint(1, 10) == 1 and self.room[y][x] == " ":
                self.room[y][x] = colored("E", 'light_magenta')
                
    def load_items(self):
        for i in range(self.size*7):
            y = randint(1, self.size-1)
            x = randint(1, self.size-1)
            if randint(1, 10) == 1 and self.room[y][x] == " ":
                self.room[y][x] = colored("I", 'light_blue')

    def load_npcs(self):
        for i in range(self.size*7):
            y = randint(1, self.size-1)
            x = randint(1, self.size-1)
            if randint(1, 10) == 1 and self.room[y][x] == " ":
                self.room[y][x] = colored("N", 'light_green')

class Minigame(Location):
    def __init__(self, reward:tuple):
        self.room = [["x", "x", "x", "x", "x"], 
                     [colored("@", 'red'), " ", colored("P", 'light_yellow'), " ", "x"], 
                     ["x", " ", " ", " ", "x"], 
                     ["x", " ", " ", " ", " "], 
                     ["x", "x", "x", "x", "x"]
                    ]
        self.reward = reward

    def win(self, player):
        player.atk += self.reward[1]
        player.health[0] += self.reward[0]
        player.health[1] += self.reward[0]

        return player

    def lose(self, player):
        player.atk -= self.reward[1]
        player.health[0] -= self.reward[0]
        player.health[1] -= self.reward[0]

        return player

class ColourSwitch(Minigame):
    def __init__(self):
        super().__init__((100, 5))

    def play(self, player):
        os.system("clear")
        print(pfg.figlet_format("Colour Switch",font="larry3d"))
        sleep(2)
        os.system("clear")

        print("Press any button when this message changes colour")
        sleep(randint(1,5))
        start = time()
        print(colored("\033[FPress any button when this message changes colour", 'red'))
        input = getch()
        end = time()

        if end-start < 1:
            os.system("clear")
            print("You succeeded!")
            print(f"You gained {self.reward[0]} health and {self.reward[1]} attack")
            player = self.win(player)
            sleep(2)
        else:
            os.system("clear")
            print(f"You reacted too slowly and lost {self.reward[0]} health and {self.reward[1]} attack")
            player = self.lose(player)
            sleep(2)

        return player

class BoxPush(Minigame):
    def __init__(self):
        super().__init__((40, 40))
        
    def play(self, player):
        self.room = [["x","x", "x", "x", "x", "x", "x"],
                     ["x",colored("@", 'red'), " ", " ", " ", "'", "x"],
                     ["x"," ", "#", " ", "'", "'", "x"],
                     ["x"," ", " ", " ", " ", " ", "x"],
                     ["x"," ", " ", "#", "#", " ", "x"],
                     ["x"," ", " ", " ", " ", " ", "x"],
                     ["x","x", "x", "x", "x", "x", "x"]
                    ]
        
        player.currentPos = [1,1]
        
        os.system("clear")
        print(pfg.figlet_format("Box Push",font="larry3d"))
        sleep(2)
        os.system("clear")

        dprint("Push the boxes over the flames to put them out")
        dprint("Be careful as stepping on the flames will kill you")
        sleep(2)
        os.system("clear")

        while any("'" in row for row in self.room):
            if self.room[1][5] != "#":
                self.room[1][5] = "'"
            if self.room[2][5] != "#":
                self.room[2][5] = "'"
            if self.room[2][4] != "#":
                self.room[2][4] = "'"
            
            os.system("clear")
            self.show_room()
            direction = getch()
            player.move(direction, self)
            os.system("clear")
            self.show_room()

            if player.currentPos == [5, 6]:
                break
            if player.currentPos == [1, 5] or player.currentPos == [2, 5] or player.currentPos == [2, 4]:
                player.health[1] = 0
                sleep(0.5)
                os.system("clear")
                print("You died by stepping in the fire")
                sleep(2)
                break
        
        if not any("'" in row for row in self.room):
            sleep(0.5)
            os.system("clear")
            print("You succeeded!")
            print(f"You gained {self.reward[0]} health and {self.reward[1]} attack")
            player = self.win(player)
            player.currentPos = [1,2]
            sleep(2)

        self.room = [["x", "x", "x", "x", "x"], 
                     [" ", " ", colored("@", 'red'), " ", "x"], 
                     ["x", " ", " ", " ", "x"], 
                     ["x", " ", " ", " ", " "], 
                     ["x", "x", "x", "x", "x"]
                    ]
        
        return player
    
class Buckshot(Minigame):
    def __init__(self):
        super().__init__((200, 30))

    def play(self, player):
        os.system("clear")
        print(pfg.figlet_format("Buckshot Roulette",font="larry3d"))
        sleep(2)
        os.system("clear")

        dprint("You will be presented with a shotgun with your goal to kill the dealer")
        dprint("A random amount of shells will be added with some live and some blank")
        dprint("There will always be at least 1 live round and 1 blank round")
        dprint("If you shoot yourself and it is a blank round, you gain an extra turn")
        dprint("Use items to gain an advantage over the dealer")
        sleep(2)
        os.system("clear")

        shells = randint(2,8)
        shellList = []
        for shell in range(shells):
            if shell == 0:
                shellList.append("live")
            elif shell == 1:
                shellList.append("blank")
            else:
                shellList.append(choice(["live","blank"]))
        shuffle(shellList)

        itemList = ['magnifying glass', 'beer', 'handcuffs']
        playerItems = [choice(itemList),choice(itemList)]
        dealerItems = [choice(itemList),choice(itemList)]
        
        def show_details():
            print(f"There are {len(shellList)} shells")
            print(f"{shellList.count("live")} live shells, {shellList.count("blank")} blank shells")
            print(f"\nDealer's items: {', '.join(dealerItems)}")
            print(f"Your items: {', '.join(playerItems)}")
            print()

        handcuffed = False
        playerItemUsed = ""
        dealerShoot = ""

        while shells > 0 and player.health[1] > 0 and dealerShoot != "s":
            os.system("clear")
            show_details()

            dealerHandcuffed = False
            dealerKnows = ""
            dealerShoot = ""
            
            if not handcuffed and dealerShoot != "s":
                if len(playerItems) == 2:
                    print(f"Do you want to use the {playerItems[0]} (1) or {playerItems[1]} (2) or not use an item (3)?")
                    itemUse = getch()
                    while itemUse != "1" and itemUse != "2" and itemUse != "3":
                        print("\033[FInvalid input")
                        sleep(1)
                        os.system("clear")
                        show_details()
                        print(f"Do you want to use the {playerItems[0]} (1) or {playerItems[1]} (2) or not use an item (3)?")
                        itemUse = getch()
                    
                    if itemUse == "1":
                        playerItemUsed = playerItems.pop(0)
                    elif itemUse == "2":
                        playerItemUsed = playerItems.pop(1)
                    elif itemUse == "3":
                        print("You did not use an item")

                elif len(playerItems) == 1:
                    print(f"Do you want to use the {playerItems[0]} (1) or not use it (2)?")
                    itemUse = getch()
                    while itemUse != "1" and itemUse != "2":
                        print("\033[FInvalid input")
                        sleep(1)
                        os.system("clear")
                        show_details()
                        print(f"Do you want to use the {playerItems[0]} (1) or not use it (2)?")
                        itemUse = getch()

                    if itemUse == "1":
                        playerItemUsed = playerItems.pop(0)
                    elif itemUse == "2":
                        print("You didnt use the item")
                        sleep(2)

                os.system("clear")
                show_details()

                if playerItemUsed == "magnifying glass":
                    print(f"The current shell is {shellList[0]}")
                    sleep(2)
                elif playerItemUsed == "beer":
                    print("You drank the beer and rack the gun")
                    print(f"A {shellList.pop(0)} shell is thrown out")
                    sleep(2)
                elif playerItemUsed == "handcuffs":
                    print("You put the dealer in handcuffs")
                    dealerHandcuffed = True
                    sleep(2)

                playerItemUsed = None
                os.system("clear")
                show_details()

                print("Do you want to shoot yourself (1) or the dealer (2)?")
                shoot = getch()
                while shoot != "1" and shoot != "2":
                    print("\033[FInvalid input")
                    sleep(1)
                    os.system("clear")
                    show_details()
                    print("Do you want to shoot yourself (1) or the dealer (2)?")
                    shoot = getch()

                os.system("clear")
                show_details()

                if shoot == "1":
                    print("You shoot yourself")
                    sleep(1)
                    shell = shellList.pop(0)
                    if shell == "live":
                        player.health[1] = 0
                        print("\033[F\033[KYou shot a live")
                        break
                    elif shell == "blank":
                        print("\033[F\033[KYou shot a blank")
                        continue
                
                if shoot == "2":
                    print("You shoot the dealer")
                    sleep(1)
                    shell = shellList.pop(0)
                    if shell == "live":
                        print("\033[FYou shot a live and killed the dealer")
                        break
                    elif shell == "blank":
                        print("\033[F\033[KYou shot a blank")
            elif handcuffed:
                print("You are handcuffed and cannot move")

            handcuffed = False
            sleep(2)
            os.system("clear")
            show_details()

            if not dealerHandcuffed:
                if len(dealerItems) > 0:
                    dealerItemUsed = dealerItems.pop(0)
                    if dealerItemUsed == "magnifying glass" and not dealerHandcuffed:
                        print("The dealer used a magnifying glass")
                        dealerKnows = shellList[0]
                    elif dealerItemUsed == "beer" and not dealerHandcuffed:
                        print("The dealer drank the beer and racked the gun")
                        print(f"A {shellList.pop(0)} shell is thrown out")
                    elif dealerItemUsed == "handcuffs" and not dealerHandcuffed:
                        handcuffed = True
                        print("The dealer put you in handcuffs")

                sleep(2)
                os.system("clear")
                show_details()

                shell = shellList.pop(0)
                if dealerKnows == "live":
                    print("The dealer shot you a live and killed you")
                    player.health[1] = 0
                elif dealerKnows == "blank":
                    print("The dealer shot themself")
                    sleep(2)
                    print("\033[FThe dealer shot a blank")
                    dealerShoot = "s"
                elif randint(1,2) == 1:
                    print("The dealer shot you")
                    sleep(2)
                    os.system("clear")
                    show_details()
                    if shell == "live":
                        print("The dealer shot a live and killed you")
                        player.health[1] = 0
                    elif shell == "blank":
                        print("The dealer shot a blank")
                else:
                    print("The dealer shot themself")
                    sleep(2)
                    os.system("clear")
                    show_details()
                    if shell == "live":
                        print("The dealer shot a live and killed themself")
                        break
                    elif shell == "blank":
                        dealerShoot = "s"
                        print("The dealer shot a blank")
            else:
                print("The dealer is handcuffed")

        if player.health[1] > 0:
            print("You win")
            print(f"You receive {self.reward[0]} health and {self.reward[1]} attack")
            player = self.win(player)
            sleep(2)
        else:
            print("You died")
            sleep(2)

        return player

class Slot(Minigame):
    def __init__(self):
        super().__init__((2,2,2,2))
        self.items = ["*","$","&","%","#","@","~"]

    def play(self, player):
        os.system("clear")
        print(pfg.figlet_format("Slot Machine",font="larry3d"))
        sleep(2)
        os.system("clear")

        dprint("Using the slot machine will use 10% of your max health and can kill you")
        dprint("Getting 3 in a row will double all your stats")
        dprint("Getting 4 in a row will triple all your stats")
        dprint("Getting 5 in a row will quadruple all your stats")
        sleep(2)
        os.system("clear")

        print(f"Current Health: {player.health[1]}/{player.health[0]}")
        print("Do you want to play (1) or quit (2)?")
        decision = getch()
        while decision != "1" and decision != "2":
            print("Invalid input")
            sleep(1)
            decision = getch()
        os.system("clear")

        while decision == "1" and player.health[1] > 0:
            os.system("clear")
            player.health[1] = floor(player.health[1] - (0.1*player.health[0]))
            wheel1 = self.items.copy()
            wheel2 = self.items.copy()
            wheel3 = self.items.copy()
            wheel4 = self.items.copy()
            wheel5 = self.items.copy()

            shuffle(wheel1)
            shuffle(wheel2)
            shuffle(wheel3)
            shuffle(wheel4)
            shuffle(wheel5)
    
            for i in range(randint(20,35)):
                print(wheel1[i%4+1])
                print(wheel1[i%4])
                print(wheel1[i%4-1])
                sleep(0.1)
                os.system("clear")
            wheel1 = [wheel1[i%4+1],wheel1[i%4],wheel1[i%4-1]]

            for i in range(randint(20,35)):
                print(wheel1[0], wheel2[i%4+1])
                print(wheel1[1], wheel2[i%4])
                print(wheel1[2], wheel2[i%4-1])
                sleep(0.1)
                os.system("clear")
            wheel2 = [wheel2[i%4+1],wheel2[i%4],wheel2[i%4-1]]

            for i in range(randint(20,35)):
                print(wheel1[0], wheel2[0], wheel3[i%4+1])
                print(wheel1[1], wheel2[1], wheel3[i%4])
                print(wheel1[2], wheel2[2], wheel3[i%4-1])
                sleep(0.1)
                os.system("clear")
            wheel3 = [wheel3[i%4+1],wheel3[i%4],wheel3[i%4-1]]

            for i in range(randint(20,35)):
                print(wheel1[0], wheel2[0], wheel3[0], wheel4[i%4+1])
                print(wheel1[1], wheel2[1], wheel3[1], wheel4[i%4])
                print(wheel1[2], wheel2[2], wheel3[2], wheel4[i%4-1])
                sleep(0.1)
                os.system("clear")
            wheel4 = [wheel4[i%4+1],wheel4[i%4],wheel4[i%4-1]]

            for i in range(randint(30,50)):
                print(wheel1[0], wheel2[0], wheel3[0], wheel4[0], wheel5[i%4+1])
                print(wheel1[1], wheel2[1], wheel3[1], wheel4[1], wheel5[i%4])
                print(wheel1[2], wheel2[2], wheel3[2], wheel4[2], wheel5[i%4-1])
                sleep(0.1)
                os.system("clear")
            wheel5 = [wheel5[i%4+1],wheel5[i%4],wheel5[i%4-1]]

            print(wheel1[0], wheel2[0], wheel3[0], wheel4[0], wheel5[0])
            print(wheel1[1], wheel2[1], wheel3[1], wheel4[1], wheel5[1])
            print(wheel1[2], wheel2[2], wheel3[2], wheel4[2], wheel5[2])
            sleep(1)
            os.system("clear")

            if wheel1[0] == wheel2[0] == wheel3[0] or wheel2[0] == wheel3[0] == wheel4[0] or wheel3[0] == wheel4[0] == wheel5[0] or wheel1[1] == wheel2[1] == wheel3[1] or wheel2[1] == wheel3[1] == wheel4[1] or wheel3[1] == wheel4[1] == wheel5[1] or wheel1[2] == wheel2[2] == wheel3[2] or wheel2[2] == wheel3[2] == wheel4[2] or wheel3[2] == wheel4[2] == wheel5[2]:
                if wheel1[0] == wheel2[0] == wheel3[0]:
                    wheel1[0] = colored(wheel1[0], 'green')
                    wheel2[0] = colored(wheel2[0], 'green')
                    wheel3[0] = colored(wheel3[0], 'green')
                if wheel2[0] == wheel3[0] == wheel4[0]:
                    wheel2[0] = colored(wheel2[0], 'green')
                    wheel3[0] = colored(wheel3[0], 'green')
                    wheel4[0] = colored(wheel4[0], 'green')
                if wheel3[0] == wheel4[0] == wheel5[0]:
                    wheel3[0] = colored(wheel3[0], 'green')
                    wheel4[0] = colored(wheel4[0], 'green')
                    wheel5[0] = colored(wheel5[0], 'green')
                if wheel1[1] == wheel2[1] == wheel3[1]:
                    wheel1[1] = colored(wheel1[1], 'green')
                    wheel2[1] = colored(wheel2[1], 'green')
                    wheel3[1] = colored(wheel3[1], 'green')
                if wheel2[1] == wheel3[1] == wheel4[1]:
                    wheel2[1] = colored(wheel2[1], 'green')
                    wheel3[1] = colored(wheel3[1], 'green')
                    wheel4[1] = colored(wheel4[1], 'green')
                if wheel3[1] == wheel4[1] == wheel5[1]:
                    wheel3[1] = colored(wheel3[1], 'green')
                    wheel4[1] = colored(wheel4[1], 'green')
                    wheel5[1] = colored(wheel5[1], 'green')
                if wheel1[2] == wheel2[2] == wheel3[2]:
                    wheel1[2] = colored(wheel1[2], 'green')
                    wheel2[2] = colored(wheel2[2], 'green')
                    wheel3[2] = colored(wheel3[2], 'green')
                if wheel2[2] == wheel3[2] == wheel4[2]:
                    wheel2[2] = colored(wheel2[2], 'green')
                    wheel3[2] = colored(wheel3[2], 'green')
                    wheel4[2] = colored(wheel4[2], 'green')
                if wheel3[2] == wheel4[2] == wheel5[2]:
                    wheel3[2] = colored(wheel3[2], 'green')
                    wheel4[2] = colored(wheel4[2], 'green')
                    wheel5[2] = colored(wheel5[2], 'green')
                print(wheel1[0], wheel2[0], wheel3[0], wheel4[0], wheel5[0])
                print(wheel1[1], wheel2[1], wheel3[1], wheel4[1], wheel5[1])
                print(wheel1[2], wheel2[2], wheel3[2], wheel4[2], wheel5[2])
                sleep(2)
                os.system("clear")

                print("You won!")
                player.health[1] += player.health[0]
                player.health[0] *= 2
                player.atk *= 2
                player.sp[0] *= 2
                player.sp[1] *= 2
            if wheel1[0] == wheel2[0] == wheel3[0] == wheel4[0] or wheel2[0] == wheel3[0] == wheel4[0] == wheel5[0] or wheel1[1] == wheel2[1] == wheel3[1] == wheel4[1] or wheel2[1] == wheel3[1] == wheel4[1] == wheel5[1] or wheel1[2] == wheel2[2] == wheel3[2] == wheel4[2] or wheel2[2] == wheel3[2] == wheel4[2] == wheel5[2]:
                if wheel1[0] == wheel2[0] == wheel3[0] == wheel4[0]:
                    wheel1[0] = colored(wheel1[0], 'green')
                    wheel2[0] = colored(wheel2[0], 'green')
                    wheel3[0] = colored(wheel3[0], 'green')
                    wheel4[0] = colored(wheel4[0], 'green')
                if wheel2[0] == wheel3[0] == wheel4[0] == wheel5[0]:
                    wheel2[0] = colored(wheel2[0], 'green')
                    wheel3[0] = colored(wheel3[0], 'green')
                    wheel4[0] = colored(wheel4[0], 'green')
                    wheel5[0] = colored(wheel5[0], 'green')
                if wheel1[1] == wheel2[1] == wheel3[1] == wheel4[1]:
                    wheel1[1] = colored(wheel1[1], 'green')
                    wheel2[1] = colored(wheel2[1], 'green')
                    wheel3[1] = colored(wheel3[1], 'green')
                    wheel4[1] = colored(wheel4[1], 'green')
                if wheel2[1] == wheel3[1] == wheel4[1] == wheel5[1]:
                    wheel2[1] = colored(wheel2[1], 'green')
                    wheel3[1] = colored(wheel3[1], 'green')
                    wheel4[1] = colored(wheel4[1], 'green')
                    wheel5[1] = colored(wheel5[1], 'green')
                if wheel1[2] == wheel2[2] == wheel3[2] == wheel4[2]:
                    wheel1[2] = colored(wheel1[2], 'green')
                    wheel2[2] = colored(wheel2[2], 'green')
                    wheel3[2] = colored(wheel3[2], 'green')
                    wheel4[2] = colored(wheel4[2], 'green')
                if wheel2[2] == wheel3[2] == wheel4[2] == wheel5[2]:
                    wheel2[2] = colored(wheel2[2], 'green')
                    wheel3[2] = colored(wheel3[2], 'green')
                    wheel4[2] = colored(wheel4[2], 'green')
                    wheel5[2] = colored(wheel5[2], 'green')
                print(wheel1[0], wheel2[0], wheel3[0], wheel4[0], wheel5[0])
                print(wheel1[1], wheel2[1], wheel3[1], wheel4[1], wheel5[1])
                print(wheel1[2], wheel2[2], wheel3[2], wheel4[2], wheel5[2])
                sleep(2)
                os.system("clear")
                
                print("You won big!")
                player.health[1] += player.health[0]*2
                player.health[0] *= 3
                player.atk *= 3
                player.sp[0] *= 3
                player.sp[1] = player.sp[0]
            if wheel1[0] == wheel2[0] == wheel3[0] == wheel4[0] == wheel5[0] or wheel1[1] == wheel2[1] == wheel3[1] == wheel4[1] == wheel5[1] or wheel1[2] == wheel2[2] == wheel3[2] == wheel4[2] == wheel5[2]:
                if wheel1[0] == wheel2[0] == wheel3[0] == wheel4[0] == wheel5[0]:
                    wheel1[0] = colored(wheel1[0], 'green')
                    wheel2[0] = colored(wheel2[0], 'green')
                    wheel3[0] = colored(wheel3[0], 'green')
                    wheel4[0] = colored(wheel4[0], 'green')
                    wheel5[0] = colored(wheel5[0], 'green')
                if wheel1[1] == wheel2[1] == wheel3[1] == wheel4[1] == wheel5[1]:
                    wheel1[1] = colored(wheel1[1], 'green')
                    wheel2[1] = colored(wheel2[1], 'green')
                    wheel3[1] = colored(wheel3[1], 'green')
                    wheel4[1] = colored(wheel4[1], 'green')
                    wheel5[1] = colored(wheel5[1], 'green')
                if wheel1[2] == wheel2[2] == wheel3[2] == wheel4[2] == wheel5[2]:
                    wheel1[2] = colored(wheel1[2], 'green')
                    wheel2[2] = colored(wheel2[2], 'green')
                    wheel3[2] = colored(wheel3[2], 'green')
                    wheel4[2] = colored(wheel4[2], 'green')
                    wheel5[2] = colored(wheel5[2], 'green')
                print(wheel1[0], wheel2[0], wheel3[0], wheel4[0], wheel5[0])
                print(wheel1[1], wheel2[1], wheel3[1], wheel4[1], wheel5[1])
                print(wheel1[2], wheel2[2], wheel3[2], wheel4[2], wheel5[2])
                sleep(2)
                os.system("clear")

                print("You won the jackpot!")
                player.health[1] += player.health[0]*3
                player.health[0] *= 4
                player.atk *= 4
                player.sp[0] *= 4
                player.sp[1] = player.sp[0]
            
            print(f"Current Health: {player.health[1]}/{player.health[0]}")
            print("Do you want to try again (1) or quit (2)?")
            decision = getch()

        return player

class Maths(Minigame):
    def __init__(self):
        super().__init__((50, 100))

    def play(self, player):
        os.system("clear")
        print(pfg.figlet_format("Maths Challenge",font="larry3d"))
        sleep(2)
        os.system("clear")

        dprint("You will be presented with a multiplication problem with 5 seconds to solve it")
        dprint("You will only be given one attempt")
        sleep(3)
        
        os.system("clear")

        num1 = randint(3,21)
        num2 = randint(3,21)

        start = time()
        print(f"What is {num1} multiplied by {num2}")
        answer = input()

        while True:
            try:
                int(answer)
                break
            except:
                print("\033[FInvalid input")
                sleep(1)
                os.system("clear")
                print(f"What is {num1} multiplied by {num2}")
                answer = input()
        end = time()
        os.system("clear")

        if int(answer) == int(num1*num2) and end-start < 5:
            print("You got it right!")
            print(f"You gained {self.reward[0]} health and {self.reward[1]} attack")
            player = self.win(player)
            sleep(2)
        elif end-start >= 5:
            print("You took too long")
            print(f"The gods are furious and you lose {self.reward[0]} health and {self.reward[1]} attack")
            player = self.lose(player)
            sleep(2)
        else:
            print("You got it wrong")
            print(f"The gods are furious and you lose {self.reward[0]} health and {self.reward[1]} attack")
            player = self.lose(player)
            sleep(2)

        return player

class Combat:
    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy
        self.savedEnemy = enemy
        self.exp = enemy.exp[0]
        self.itemAtk = 0

    def start(self):
        turnOrder = sorted(self.player.summons + [self.player, self.enemy], key=lambda x: x.speed, reverse=True)
        for entity in turnOrder:
            entity.sp[1] = entity.sp[0]

        while self.player.health[1] > 0 and self.enemy.health[1] > 0:
            os.system("clear")
            print(f"Health: {self.player.health[1]}/{self.player.health[0]}")
            print(f"SP {self.player.sp[1]}/{self.player.sp[0]}")
            print(f"Weakness {self.player.weaknessBar[1]}/{self.player.weaknessBar[0]}")
            print()
            print(f"Enemy Health: {self.enemy.health[1]}/{self.enemy.health[0]}")
            print(f"Enemy SP {self.enemy.sp[1]}/{self.enemy.sp[0]}")
            print(f"Enemy Weakness {self.enemy.weaknessBar[1]}/{self.enemy.weaknessBar[0]}")
            print()

            current = turnOrder.pop(0)

            if current.broken:
                current.unBreak()
                continue

            if type(current) is Player:
                print("Do you want to attack (1), wait (2), rest (3) or use an item (4)?")
                action = int(getch())
                while action not in range(1,5):
                    print("Invalid input", end="\r")
                    sleep(1)
                    print("\033[K")
                    action = int(getch())
                print("\033[F\033[K\033[F\033[K")
                if action == 1:
                    for number, ability in enumerate(current.abilities):
                        print(f"{number+1} {ability.name} ({ability.cost})")
                    print("What move do you want to use?")
                    num = int(getch())
                    while num not in range(1,len(self.player.abilities)+1):
                        print("Invalid input", end="\r")
                        sleep(1)
                        print("\033[K\033[F")
                        num = int(getch())
                    print("\033[F\033[K\033[F\033[K\033[F\033[K")
                    self.enemy = current.attack(self.enemy, self.player.abilities[num-1])
                    sleep(1)
                elif action == 2:
                    self.player.wait()
                    sleep(1)
                elif action == 3:
                    self.player.rest()
                    sleep(1)
                elif action == 4:
                    for number, item in enumerate(current.inventory):
                        print(number+1, item.name)
                    print("What item do you want to use?")
                    num = int(getch())
                    while num not in range(1,len(self.player.inventory)+1):
                        print("Invalid input", end="\r")
                        sleep(1)
                        print("\033[K\033[F")
                        num = int(getch())
                    print("\033[F\033[K\033[F\033[K\033[F\033[K")
                    self.itemAtk += self.player.inventory[num-1]
                    current.use_item(self.player.inventory.pop(num-1))
            else:
                shuffle(current.abilities)
                for move in current.abilities:
                    if move.cost <= current.sp[1]:
                        if current.isSummon:
                            self.enemy = current.attack(self.enemy, move)
                            sleep(1)
                            break
                        else:
                            target = choice(turnOrder)
                            target = current.attack(target, move)
                            sleep(1)
                            break
                else:
                    if current.sp[1] < 0.1 * current.sp[0]:
                        current.rest()
                        sleep(1)
                    else:
                        current.wait()
                        sleep(1)

            turnOrder.append(current)

        if self.enemy.health[1] <= 0:
            os.system("clear")
            self.player.weaknessBar[1] = self.player.weaknessBar[0]
            self.player.atk -= self.itemAtk
            for summon in self.player.summons:
                summon.exp[1] += self.exp
                summon.weaknessBar[1] = summon.weaknessBar[0]
                while summon.exp[1] > summon.exp[0]:
                    summon.levelUp()
            print(f"You have defeated the {self.enemy.name}")
            print("Do you want to absorb it (1) or necromance it (2)")
            input = int(getch())
            while input != 1 and input != 2:
                print("Invalid input", end="\r")
                sleep(1)
                print("\033[K")
                input = int(getch())
            if input == 1:
                self.player.absorb(self.savedEnemy)
            elif input == 2:
                self.player.necromance(self.savedEnemy)
        else:
            os.system("clear")
            self.player.alive = False
            print("You died")

        return self.player

Fireball = Ability("Fireball", 1.5, "Fire", 30, 20)
os.system("clear")
enemy = Enemy("Dragon", [50,50], ["Ice"], [100,100], 20, 20, [200,200], [Fireball], {1: Fireball}, [100,0], 11)
player = Player("Bob", [100,100], ["Fire"], [100,100], 50, 10, [50,50], [Fireball])

# maze = Maze(51)
# maze.generate_maze()
# maze.load_enemies()
# maze.load_items()
# maze.load_npcs()
# maze.room[1][0] = colored("@", 'red')

slot = Slot()
colour = ColourSwitch()
box = BoxPush()
maths = Maths()
buckshot = Buckshot()

while player.health[1] > 0:
    os.system("clear")
    # colour.show_room()
    # box.show_room()
    # maths.show_room()
    # slot.show_room()
    buckshot.show_room()
    direction = getch()
    # player.move(direction, colour)
    # player.move(direction, box)
    # player.move(direction, slot)
    # player.move(direction, maths)
    player.move(direction, buckshot)

# combat = Combat(player, enemy)
# player = combat.start()
