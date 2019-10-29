#!/usr/bin/env python
"""
Copyright (C) 2019 br-n518

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

verbose = False
player = None
last_created_item = None
title_text = None

working_directory = ''

people = list()
places = list()
procedures = dict()

trigger_delim = ','
file_command_delim = ','

# print to stdout if verbose flag enabled
def log(s=""):
    global verbose
    if verbose and len(s) > 0:
        print s

def is_true(s):
    s = s.lower().strip()
    if s == 'true' or s == 'yes' or s == 'y' or s == 'ye':
        return True
    return False

def is_false(s):
    s = s.lower().strip()
    if s == 'false' or s == 'no' or s == 'n':
        return True
    return False

class Proc:
    def __init__(self, n):
        self.name = n
        self.trigger = None


class Place:
    def __init__(self,n="Nowhere"):
        global places
        self.name = n
        self.leadsTo = list()
        places.append(self)
        
        self.items = list()
        self.trigger = None
        
    def addDoorTo(self, p):
        if isinstance(p, Place) and p != self:
            # check if already in list
            for x in self.leadsTo:
                if x.name == p.name:
                    return
            self.leadsTo.append(p)
            p.addDoorTo(self)



def placeByName( n ):
    n = n.lower()
    for x in places:
        if x.name.lower() == n:
            return x
    return None



class Person:
    def __init__(self, add=True):
        global people
        self.dialogues=list()
        self.name="Anonymous"
        self.place = None
        self.items = list()
        self.ask = dict()
        
        self.trigger = None
        
        if add == True:
            people.append(self)
    
    def talk(self):
        for x in self.dialogues:
            print x,
            raw_input()
        
    def addDialogue(self, d=None):
        if d != None:
            self.dialogues.append(d)
    
    def clearDialogue(self):
        del self.dialogues[:]
        
    # key must be a single word, can't have spaces
    def addQuestion(self, key, value):
        if isinstance(key, str) and isinstance(value, str):
            key = key.strip().split(' ')[0]
            if len(key) > 0:
                self.ask[key] = value



def personByName( pn ):
    pn = pn.lower()
    for x in people:
        if x.name.lower() == pn:
            return x
    return None



class Item:
    def __init__(self, n="Nondescript object", takeAble=True):
        self.name = n
        self.trigger = None
        self.canTake = takeAble
        self.edible = False

# get an item by its name "n", searching in Place "src"
# this has to be here because of reference to 'player'
def itemByName(n, src=None):
    global player
    n = n.lower()
    if isinstance(src, Place):
        perList = src.items
    elif isinstance(src, Person) and isinstance(src.place, Place):
        perList = src.place.items
    else:
        perList = player.place.items
    for i in perList:
        if i.name.lower() == n:
            return i
    return None



def findByName(n):
    n = n.lower()
    o = personByName(n)
    if o == None:
        o = placeByName(n)
        if o == None:
            o = itemByName(n)
    return o





# read and return data for file of name 'n'
def loadFileData(n=""):
    global working_directory
    log("Loading file: " + working_directory + n)
    c = ""
    try:
        f = open(working_directory + n, 'r')
        c = f.read()
        f.close()
    except IOError:
        print "(!!!) Failed to load file:",n
        return None
    return c



# Load a game script file
def loadGameFile(fn=""):
    global player
    global places
    global working_directory
    
    if len(fn) > 0:
        
        i = fn.rfind('/')
        if i >= 0:
            working_directory = fn[:i+1]
            fn = fn[i+1:]
        else:
            working_directory = ''
        processGameFileData(loadFileData(fn))
        
        if len(places) > 0:
            player.place = places[0]
        else:
            player.place = None
        updatePersonPlacePairs()


includeFileDepth = 1
def processGameFileData(data):
    global last_created_item
    global procedures
    global includeFileDepth
    global title_text
    global file_command_delim
    if data != None:
        currentPerson = None
        currentObj = None
        lines = data.split('\n')
        for l in lines:
            # EOL comments
            l = l.strip()
            if len(l) > 0:
                if l[0] == '\"':
                    h = l.rfind('\"')
                    if h <= 0:
                        h = len(l)
                    l = l[1:h].strip()
                    if isinstance(currentPerson, Person) and len(l) > 0:
                        currentPerson.addDialogue(l)
                else:
                    h = l.find('#')
                    if h >= 0:
                        l = l[:h]
                    pair = l.split('=')
                    if len(pair) == 2:
                        currentPerson = None
                        pair[0] = pair[0].strip().lower()
                        
                        if pair[0] == "door":
                            r = pair[1].split(file_command_delim)
                            r[0] = r[0].strip()
                            r[1] = r[1].strip()
                            if len(r) >= 2:
                                p1 = placeByName( r[0] )
                                if p1 == None:
                                    index = len(places)
                                    Place(r[0])
                                    p1 = places[index]
                                p2 = placeByName( r[1] )
                                if p2 == None:
                                    index = len(places)
                                    Place(r[1])
                                    p2 = places[index]
                                p1.addDoorTo(p2)
                            currentObj = None
                        
                        elif pair[0] == "item":
                            # item=[!|&]Desk,Classroom E
                            i = pair[1].rfind(file_command_delim)
                            r = [ pair[1][:i], pair[1][i+1:] ]
                            n = r[0].strip()
                            
                            ct = True
                            ed = False
                            while len(n) > 0 and ( n[0] == '!' or n[0] == '&' ):
                                # check if object is non-pickup
                                if n[0] == '!':
                                    ct = False
                                # check if object is edible
                                elif n[0] == '&':
                                    ed = True
                                n = n[1:]
                            if len(n) > 0:
                                i = Item(n, ct)
                                i.edible = ed
                                p = placeByName(r[1].strip())
                                if p != None:
                                    p.items.append(i)
                                currentObj = i
                                last_created_item = i
                            
                            
                        elif pair[0] == "person":
                            # person=Fred,Classroom E
                            i = pair[1].rfind(file_command_delim)
                            r = [ pair[1][:i], pair[1][i+1:] ]
                            n = pair[1][:i]
                            val = pair[1][i+1:]
                            
                            p = Person()
                            p.name = n.strip()
                            p.place = placeByName(val.strip())
                            currentPerson = p
                            currentObj = p
                            pass
                        
                        elif pair[0] == "include":
                            currentObj = None
                            # prevent loops
                            if includeFileDepth < 100:
                                includeFileDepth += 1
                                m = loadFileData(pair[1].strip())
                                processGameFileData(m)
                                includeFileDepth -= 1
                            else:
                                return
                        
                        elif pair[0] == "trigger":
                            # get by name
                            p = findByName(pair[1])
                            if p != None:
                                # set object to receive trigger lines
                                p.trigger = ''
                                currentObj = p
                        
                        elif pair[0] == "proc":
                            n = pair[1].strip()
                            if len(n) > 0:
                                currentObj = Proc(n)
                                procedures[n] = currentObj
                        
                        elif pair[0] == "title":
                            t = ('='.join(pair[1:])).strip()
                            if len(t) > 0:
                                if isinstance(title_text, str):
                                    title_text += '\\n' + t
                                else:
                                    title_text = t
                            
                    elif len(l) > 0:
                        # NO EQUALS SIGN IN LINE:
                        if l[0] == '!':
                            # RESET DIALOGUE+TRIGGER for PERSON
                            # !NAME[:TRIGGER]
                            # DIALOGUE
                            # DIALOGUE
                            t = None
                            col = l.find(':')
                            if col >= 2:
                                p = personByName(l[1:col].strip())
                                t = l[col+1:].strip()
                            else:
                                p = personByName(l[1:].strip())
                                t = None
                            if p != None:
                                currentPerson = p
                                currentPerson.clearDialogue()
                                currentPerson.trigger = t
                                #currentPerson.ask = dict()
                                currentObj = p
                            else:
                                if col >= 2:
                                    log("(!!!) Couldn't find person for dialogue: " + l[1:col])
                                else:
                                    log("(!!!) Couldn't find person for dialogue: " + l[1:])
                        elif l[0] == '$':
                            # TRIGGER LINE
                            # append to current trigger
                            x = l[1:]
                            if currentObj != None:
                                if currentObj.trigger == None:
                                    currentObj.trigger = x.strip()
                                elif isinstance(currentObj.trigger, str):
                                    currentObj.trigger += ';' + x.strip()
                        elif l[0] == '?':
                            # ASK LINE
                            l = l[1:].strip()
                            c = l.find(trigger_delim)
                            if c > 0:
                                q = l[:c].lower().strip().split(' ')
                                t = l[c+1:].strip()
                                if currentPerson != None:
                                    for r in q:
                                        if len(r) > 0:
                                            log("(!!!) Adding ? for \"" + r + "\" on " + currentPerson.name)
                                            currentPerson.ask[r] = t
                        
                        elif currentPerson != None:
                            # add dialog to current person
                            currentPerson.addDialogue(l)
            pass #for


# update all Person objects to have a valid Place where they reside (except player)
def updatePersonPlacePairs():
    global places
    global people
    log("Validating Person locations.")
    # put all people in first room
    for p in people:
        if p.place == None:
            log("Setting place of " + p.name + " to default " + places[0].name)
            p.place = places[0]
        elif isinstance(p.place, str):
            pl = placeByName(p.place)
            if pl != None:
                p.place = pl
                log("Converted place-string for " + p.name)
            else:
                log("Setting place of " + p.name + " to default " + places[0].name)
                p.place = places[0]
        else:
            # check if valid
            valid=False
            for x in places:
                if p.place == x:
                    valid=True
                elif p.place.name == x.name:
                    p.place = x
                    valid=True
            if not valid:
                log("Redefining place of " + p.name + " to " + places[0].name)
                p.place = places[0]


def processEvent( event_holder = None ):
    if event_holder != None:
        if isinstance(event_holder, Person):
            eh = event_holder
        else:
            eh = None
        t = event_holder.trigger
        event_holder.trigger = None
        if t != None:
            leftover = list()
            # leftover_append
            left_app = False
            trigs = t.split(';')
            for k in trigs:
                left_app = True
                l = k.strip()
                if len(l) > 0:
                    if l[0] == "!":
                        left_app = False
                        l = l[1:].strip()
                    if len(l) >= 2 and l[0:2] == "?(":
                        # prompt user
                        qEnd = l.find( ')' )
                        query = l[2:qEnd].strip()
                        ans = ""
                        while len(ans) <= 0:
                            ans = raw_input(query + " (yes/no): ").strip().lower()
                            if is_true(ans):
                                es = l[qEnd+1:].strip()
                                processEventString( es, eh )
                            elif is_false(ans):
                                # if they say no, don't remove action
                                left_app = True
                            else:
                                ans = ""
                        
                    else:
                        processEventString(l, eh)
                if left_app:
                    leftover.append(k)
            # put trigger back together
            if len(leftover) > 0:
                for x in leftover:
                    if event_holder.trigger == None:
                        event_holder.trigger = x
                    else:
                        event_holder.trigger += ";" + x
        else:
            log("(!!!) Empty trigger.")

# this only processes one line, for multiple lines (';' delim) use processEvent
def processEventString(es="", src = None):
    global player
    global last_created_item
    global procedures
    global people
    global places
    global trigger_delim
    if es != None and len(es) > 0:
        es = es.strip()
        if len(es) >= 2:
            log("Processing event: " + es)
            # split by asterisk at string level (chain)
            lines = es.split('*')
            for l in lines:
                l = l.strip()
                # PROCS
                if l[0] == '@':
                    n = l[1:].strip().lower()
                    if n in procedures:
                        processEvent(procedures[n])
                        continue
                space1 = l.find(' ')
                if space1 > 0:
                    context = l[0:space1].lower()
                    space2 = l.find(' ', space1 + 1)
                    if space2 > 0:
                        command = l[space1 + 1:space2].lower()
                        rest = l[space2 + 1:].strip()
                        
                        
                        
                        # PERSON
                        if context == "person":
                            if command == "add":
                                r = rest.split(trigger_delim)
                                p = Person()
                                p.name = r[0]
                                if len(r) > 1:
                                    if r[1].strip().lower() == "here":
                                        if src == None:
                                            p2 = player.place
                                        else:
                                            p2 = src.place
                                    elif r[1].strip().lower() == "player":
                                        p2 = player.place
                                    else:
                                        p2 = placeByName(r[1])
                                    
                                    if p2 != None:
                                        p.place = p2
                                else:
                                    if src == None:
                                        p.place = player.place
                                    else:
                                        p.place = src.place
                        
                        
                            elif command == "move":
                                r = rest.split(trigger_delim)
                                if len(r) >= 2:
                                    r[0] = r[0].strip()
                                    r[1] = r[1].strip()
                                    if r[0].lower() == "player":
                                        p = player
                                    else:
                                        p = personByName(r[0])
                                    if r[1].lower() == "here":
                                        if src == None:
                                            p2 = player.place
                                        else:
                                            p2 = src.place
                                    elif r[1].lower() == "player":
                                        p2 = player.place
                                    else:
                                        p2 = placeByName(r[1])
                                    if p != None and p2 != None:
                                        p.place = p2
                        
                        
                            elif command == "trigger":
                                parts = rest.split(',')
                                per = personByName(parts[0].strip())
                                if per != None:
                                    if len(parts) >= 2:
                                        per.trigger = ';'.join(parts[1:])
                                    else:
                                        per.trigger = None
                        
                            elif command == "say":
                                for l in rest.split('\\n'):
                                    print ""
                                    print l,
                                    raw_input()
                            
                            elif command == "dialogue":
                                col = rest.find(trigger_delim)
                                if col < 0:
                                    col = len(rest)
                                per = personByName(rest[:col])
                                if per != None:
                                    del per.dialogues[:]
                                    if col + 1 < len(rest):
                                        for l in rest[col+1:].split('\\n'):
                                            per.dialogues.append(l)
                                            
                            elif command == "ask":
                                p = rest.split(trigger_delim)
                                if len(p) >= 2:
                                    n = p[0].strip()
                                    q = p[1].lower().strip().split(' ')
                                    t = ''
                                    if len(p) >= 3:
                                        t = (trigger_delim.join(p[2:])).strip()
                                    per = personByName(n)
                                    if per != None:
                                        for r in q:
                                            if len(r) > 0:
                                                per.ask[r] = t
                            
                            
                        
                        # PLACE
                        elif context == "place":
                            if command == "add":
                                r = rest.split(trigger_delim)
                                p = Place(r[0])
                                if len(r) > 1:
                                    if r[1].strip().lower() == "here":
                                        if src == None:
                                            p2 = player.place
                                        else:
                                            p2 = src.place
                                    else:
                                        p2 = placeByName(r[1])
                                
                                    if p2 != None:
                                        p.addDoorTo(p2)
                        
                        
                            elif command == "door":
                                r = rest.split(trigger_delim)
                                if len(r) >= 2:
                                    if r[0].strip().lower() == "here":
                                        if src == None:
                                            p1 = player.place
                                        else:
                                            p1 = src.place
                                    elif r[0].strip().lower() == "player":
                                        p1 = player.place
                                    else:
                                        p1 = placeByName(r[0])
                                
                                    if r[1].strip().lower() == "here":
                                        if src == None:
                                            p2 = player.place
                                        else:
                                            p2 = src.place
                                    elif r[1].strip().lower() == "player":
                                        p2 = player.place
                                    else:
                                        p2 = placeByName(r[1])
                                    
                                    if p1 != None and p2 != None:
                                        p1.addDoorTo(p2)
                        
                            elif command == "trigger":
                                col = rest.find(trigger_delim)
                                if col < 0:
                                    col = len(rest)
                                p = placeByName(rest[:col])
                                if p != None:
                                    if col + 1 < len(rest):
                                        p.trigger = rest[col+1:]
                                    else:
                                        # remove trigger
                                        p.trigger = None
                            
                        
                        
                        # ITEM
                        elif context == "item":
                            if command == "add":
                                # second arg can be place/player/here
                                r = rest.split(trigger_delim)
                                # check item flags
                                n = r[0].strip()
                                i = Item(n)
                                while len(n) > 0 and ( n[0] == '!' or n[0] == '&' ):
                                    if n[0] == '!':
                                        i.canTake = False
                                    elif n[0] == '&':
                                        i.edible = True
                                    n = n[1:].strip()
                                if len(n) > 0:
                                    i.name = n
                                    last_created_item = i
                                    if len(r) > 1:
                                        # arg 2
                                        if r[1].strip().lower() == "here":
                                            if src == None:
                                                # place "here" where player is if no caller
                                                p = player.place
                                            else:
                                                p = src.place
                                            p.items.append(i)
                                        elif r[1].strip().lower() == "player":
                                            # Give to player
                                            player.items.append(i)
                                        else:
                                            p = placeByName(r[1])
                                            p.items.append(i)
                                        
                                    else:
                                        if src == None:
                                            player.place.items.append(i)
                                        else:
                                            src.place.items.append(i)
                                
                            elif command == "trigger":
                                col = rest.find(trigger_delim)
                                if col < 0:
                                    col = len(rest)
                                n = rest[:col]
                                rest = rest[col+1:].strip()
                                if isinstance(last_created_item, Item) and n.lower() == last_created_item.name.lower():
                                    i = last_created_item
                                else:
                                    i = itemByName(n, src)
                                if i != None:
                                    if len(rest) > 0:
                                        i.trigger = rest
                                    else:
                                        # remove trigger
                                        i.trigger = None
                                pass
                                
                        elif context == "load":
                            if command == "file":
                                processGameFileData(loadFileData(rest.strip()))
                        
                        elif context == "delete":
                            if command == "person":
                                # delete person (name)
                                p = personByName(rest)
                                if isinstance(p, Person):
                                    people.remove(p)
                                pass
                                
                            elif command == "place":
                                # delete place (name)
                                p = placeByName(rest)
                                if isinstance(p, Place):
                                    for l in p.leadsTo:
                                        if isinstance(l, Place):
                                            l.leadsTo.remove(p)
                                    places.remove(p)
                                pass
                                
                            elif command == "item":
                                # delete item (name):(place)
                                parts = rest.split(trigger_delim)
                                if len(parts) >= 2:
                                    p = placeByName(parts[1])
                                    if isinstance(p, Place):
                                        i = itemByName(parts[0], p)
                                        if isinstance(i, Item):
                                            p.items.remove(i)
                                pass
                            
                            elif command == "door":
                                # delete door (place):(place) [:(place)]
                                parts = rest.split(trigger_delim)
                                if len(parts) >= 2:
                                    for x in parts:
                                        p1 = placeByName(x)
                                        if isinstance(p1, Place):
                                            for y in parts:
                                                p2 = placeByName(y)
                                                if isinstance(p2, Place):
                                                    if p1 in p2.leadsTo:
                                                        p2.leadsTo.remove(p1)
                                                    if p2 in p1.leadsTo:
                                                        p1.leadsTo.remove(p2)
                                else:
                                    p = placeByName(rest)
                                    if isinstance(p, Place):
                                        for x in p.leadsTo:
                                            x.leadsTo.remove(p)
                                        p.leadsTo = list()
                                pass
                            
                                



def look():
    global player
    global people
    if isinstance(player.place, Place):
        print "( Looking around )"
        print "(Location:)",player.place.name
        #print "( Doors  :)",
        print "(Leads to:)",
        for p in player.place.leadsTo:
            print p.name,".",
        print ""
        peopleHere = list()
        for p in people:
            if p.place.name == player.place.name:
                peopleHere.append(p)
        if len(peopleHere) > 0:
            print "( People :)",
            for p in peopleHere:
                print p.name,".",
            print ""
        #items
        if len(player.place.items) > 0:
            print "( Items  :)",
            for i in player.place.items:
                print i.name,".",
            print ""
    else:
        # player place not set
        print "( You see nothing )"
    return



def userCommand():
    global player
    global verbose
    
    c = raw_input(":Action: ")
    print ""
    c = c.strip()
    a = c.split(' ')
    a[0] = a[0].lower()


    if a[0] == "talk" or a[0] == 't':
        if len(c) > 4:
            p = personByName(' '.join(a[1:]))
            if isinstance(p, Person) and p.place.name == player.place.name:
                p.talk()
                processEvent(p)
            else:
                print "( Nobody here named",' '.join(a[1:]),")"
    
    elif a[0] == "ask":
        if len(a) >= 2:
            who = personByName(' '.join(a[1:]))
            if isinstance(who, Person):
                log("(!!!) Selecting " + who.name)
                what = ' '
                while len(what) > 0:
                    what = raw_input("[?] ")
                    if len(what) > 0:
                        if what[0] == '?':
                            print "Enter a word. If the person knows about it, they'll talk."
                        else:
                            parts = what.lower().split(' ')
                            print ""
                            for w in parts:
                                # Remove punctuation from word
                                for p in ',.?!"\'*#@=+();:':
                                    while p in w:
                                        x = w.find(p)
                                        if x >= 0:
                                            w = w[:x] + w[x+1:]
                                # Print response
                                w = w.strip() # incase of tab
                                log("(!!!) Searching for term: " + w)
                                if w in who.ask and isinstance(who.ask[w], str):
                                    print who.ask[w]
                                    print ""
            else:
                print "( Nobody here named",' '.join(a[1:]),")"
            
    elif a[0] == "eat":
        if len(a) >= 2:
            na = c[4:].lower()
            for i in player.items:
                if i.name.lower() == na:
                    if i.edible:
                        player.items.remove(i)
                        print "( You eat the",i.name,")"
                    else:
                        print "( The",i.name,"is inedible )"
                    return
            for i in player.place.items:
                if i.name.lower() == na:
                    if i.edible:
                        player.place.items.remove(i)
                        print "( You eat the",i.name,")"
                    else:
                        print "( The",i.name,"is inedible )"
                    return
            print "( Can't find item:",na,")"
    
    elif a[0] == "take":
        if len(a) >= 2:
            na = c[5:].lower()
            for i in player.place.items:
                if i.name.lower() == na:
                    if i.canTake:
                        player.items.append(i)
                        player.place.items.remove(i)
                        print "( You take the",i.name,")"
                    else:
                        print "( Can't take the",i.name,")"
                    break


    elif a[0] == "use":
        if len(a) >= 2:
            na = c[4:].lower()
            item = None
            for i in player.place.items:
                if i.name.lower() == na:
                    item = i
                    break
            if item == None:
                for i in player.items:
                    if i.name.lower() == na:
                        item = i
                        break
            if item == None:
                print "( Can't find item:",na,")"
            else:
                if item.trigger != None:
                    print "( You use the",item.name,")"
                    processEvent(item)
                else:
                    print "( Nothing happens )"


    elif a[0] == "drop":
        if len(a) >= 2:
            na = c[5:].lower()
            for i in player.items:
                if i.name.lower() == na:
                    player.place.items.append(i)
                    player.items.remove(i)
                    print "( You drop the",i.name,")"
                    break


    elif a[0] == "look" or a[0] == "l":
        look()
        
    elif a[0] == "go" or a[0] == "g":
        if isinstance(player.place, Place) and len(player.place.leadsTo) > 0:
            print "( Go where? From:",player.place.name,")"
            i = 1
            for x in player.place.leadsTo:
                print i,'=',x.name
                i += 1
            try:
                r = int(raw_input(":Number: "))
            except ValueError:
                r = 0
            
            if r >=1 and r <= len(player.place.leadsTo):
                r = player.place.leadsTo[int(r)-1]
                if isinstance( r, Place ):
                    player.place = r
                    processEvent( player.place )
                    print ""
                    look()
        else:
            print "( There is nowhere to go )"


    elif a[0] == "me":
        print "( Your name is",player.name,")"
        if len(player.items) > 0:
            print "( You are carrying: )"
            x = 0
            for i in player.items:
                print i.name,
                if i.edible:
                    print "( Edible )",
                x += 1
                if x >= 20:
                    x = 0
                    raw_input("(Pause)")
                else:
                    print ""
        else:
            print "( Your hands are free )"



    # op commands
    elif a[0] == "verbose":
        if len(a) >= 2:
            if is_true(a[1]):
                verbose = True
            elif is_false(a[1]):
                verbose = False
        print "( Verbose output is",
        if verbose:
            print "ON )"
        else:
            print "OFF )"

    # help text
    elif a[0] == "help":
        printCommands()
    
    else:
        if len(c) == 0:
            printCommands()
        else:
            if a[0] != 'quit' and a[0] != 'exit':
                print "Unrecognized input."
    
    return a[0]




    
# functions relative to current game
def printCommands():
    print "( Basic Commands: )"
    print "Look"
    print "Go"
    print "me"
    print "( People: )"
    print "Talk (name)"
    print "ask (name)"
    print "( Items: )"
    print "take (name)"
    print "drop (name)"
    print "use (name)"
    print "eat (name)"



# begin game
def main():
    global player
    global verbose
    global title_text
    
    import sys
    
    player = Person(False)
    player.name = "Player"
    
    if len(sys.argv) > 1:
        for arg in sys.argv[1:len(sys.argv)]:
            if arg == "-q" or arg == "--quiet":
                verbose = False
            elif arg == "-v" or arg == "--verbose":
                verbose = True
            elif arg == "-h" or arg == "--help":
            	print 'textgame.py [-q | -v] [-h] [config-file [config-file [...]]]'
            else:
                loadGameFile(arg)
    
    updatePersonPlacePairs()
    
    # print title text
    if isinstance(title_text, str):
        lines = title_text.split('\\n')
        print ""
        for l in lines:
            l = l.strip()
            if len(l) > 0:
                print l,
                raw_input()
                print ""
    else:
        print "\nWelcome.\n"

    # Get a name from the user.
    print "What is your name?"
    l = 0
    while l <= 0:
        try:
            n = raw_input(":Name: ")
            l = len(n)
            if l > 0:
                if n == 'quit' or n == 'exit':
                    return
                player.name = n
        except KeyboardInterrupt:
            print ""
            l = 0
    print ""
    
    # Initial room event process
    if isinstance(player.place, Place):
        try:
            processEvent(player.place)
        except KeyboardInterrupt:
            pass
        print ""
    
    # Main loop
    running=True
    com=0
    while running:
        try:
            com = userCommand()
        except KeyboardInterrupt:
            pass
        print ""
        if com == "quit" or com == "exit":
            print "Goodbye."
            running = False



if __name__=="__main__":
    main()

