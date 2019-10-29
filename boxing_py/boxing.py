#!/usr/bin/env python3
def clear_screen(lines=128):
    if not isinstance(lines, int) or lines < 64:
        lines = 64
    print( '\n' * lines, end='' )
class Player:
    def __init__(self, n):
        self.score = 0
        self.name = n
        self.attack1 = ''
        self.attack2 = ''
        self.guard = ''
    def step(self):
        clear_screen()
        print(self.name + '\'s turn:')
        self.attack1 = ''
        self.attack2 = ''
        while len(self.attack1) <= 0 or len(self.attack2) <= 0:
            print()
            a = ''
            if len(self.attack1) <= 0:
                print('High or Low?')
            if len(self.attack2) <= 0:
                print('Left or Right?')
            while len(a) <= 0:
                a = input('Attack: ').lower()
            # test input
            if 'hi' in a:
                self.attack1 = 'high'
            elif 'lo' in a:
                self.attack1 = 'low'
            if 'le' in a:
                self.attack2 = 'left'
            elif 'ri' in a:
                self.attack2 = 'right'
        self.guard = ''
        while len(self.guard) <= 0:
            print()
            a = ''
            print('High, Low, Left, or Right?')
            while len(a) <= 0:
                a = input('Guard: ').lower()
            # test input
            if 'hi' in a:
                self.guard = 'high'
            elif 'lo' in a:
                self.guard = 'low'
            elif 'le' in a:
                self.guard = 'left'
            elif 'ri' in a:
                self.guard = 'right'
        clear_screen()
    def attack(self, p):
        print(self.name + ' attacks ' + p.name + ' with a ' + self.attack1 + ' ' + self.attack2 + '.')
        print(p.name + ' guards ' + p.guard + '.')
        if (self.attack1 != p.guard) and (self.attack2 != p.guard):
            print('HIT!')
            self.score += 1
        else:
            print('BLOCK!')
        print()
class Engine:
    def __init__(self):
        self.players = list()
        x = input("How many players?: ")
        print()
        try:
            numOfPlayers = int(x)
        except ValueError:
            numOfPlayers = 2
        if numOfPlayers > 8:
            numOfPlayers = 8
        elif numOfPlayers < 2:
            numOfPlayers = 2
        print('Setting to '+ str(numOfPlayers) +' players.\n')
        x = 1
        print('(Player Names)')
        while len(self.players) < numOfPlayers:
            a = input('Player '+str(x)+': ')
            if len(a) > 0:
                self.players.append(Player(a))
                x += 1
        print()
        self.rounds = None
        while not isinstance(self.rounds, int) or self.rounds < 1:
            self.rounds = input('# of Rounds: ')
            try:
                self.rounds = int(self.rounds)
            except ValueError:
                self.rounds = None
        self.roundsC = self.rounds
        input("\nNOTE: You only need the first two letters. (HI LO LE RI) ")
    def mainloop(self):
        if len(self.players) > 1:
            self.running = True
            self.roundsC = self.rounds
            for p in self.players:
                p.score = 0
            while self.running and self.roundsC > 0:
                clear_screen()
                print('Round ' + str((self.rounds - self.roundsC) + 1) + ':')
                input('\n( Begin ) ...')
                for p in self.players:
                    p.step()
                # process player attacks
                for p in self.players:
                    for q in self.players:
                        if p != q:
                            p.attack(q)
                # display scores
                for p in self.players:
                    print(p.name + ': ' + str(p.score))
                a = ''
                while 'ok' not in a:
                    a = input('\n( Type "ok" ) ').lower()
                self.roundsC -= 1
            print('\nFinal scores:\n')
            for p in self.players:
                print(p.name + ': ' + str(p.score) + '\n')
def main():
    e = Engine()
    e.mainloop()
if __name__=="__main__":
    main()
