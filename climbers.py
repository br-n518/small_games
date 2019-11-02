#!/usr/bin/python

from random import random



class Player:
    def __init__(self, name):
        self.name = name
        self.height = 0


def Engine:
    def __init__(self):
        self.players = list()
        self.height = 10
        self.running = False
    
    def addPlayer(self, n):
        self.players.append(Player(n))
    
    def mainloop(self, maxHeight=10)
        self.running = True
        if maxHeight >= 10:
            self.height = maxHeight
        else:
            self.height = 10
        for p in self.players:
            p.height = 0
        winner = ''
        while running:
            for p in self.players:
                # print interactive menu
                # Climb
                # Throw Rock (30% chance)
                # Push (50% chance) [if available]
                pass
                if p.height >= self.height:
                    running = False
                    winner = p.name
                    break
        print('The winner is ' + winner)


def main():
    eng = Engine()
    # prompt player names and add as desired
    
    eng.mainloop()
    pass



if __name__ == "__main__":
    main()

