
Readme file for:
textgame.py

Python 2 required.

Usage:
python textgame.py [filename]

[filename] = A file to load and run. (Such as mystery/main.txt)


python textgame.py mystery/main.txt



[THE FILE STRUCTURE]

Comments are marked by a hash symbol #.
Comments can start anywhere in the line, except when dialogues are quoted. (More on that later)

# This is an example of a comment.
  # This is another example of a comment. Doesn't matter what's before.

The files you load expect certain things to be written.
You can perform several actions in the file.

Each object starts with a keyword, followed by an equals sign (=).
Object keywords are:
title   Set title text shown at start of game. (Before name)
door    Create a Door between two Places.
person  Create a Person, put them in a certain Place.
item    Create an Item, put it in a certain Place.
proc    Create a procedure. (Makes triggers easier)
include Include a file right now.
trigger Begin modifying trigger code for named object.
!       Reset a Person's trigger and dialogue. (Followed immediately by person's name)



# Examples:

title=Example.

  # Create Room 1 and Room 2, and link them together.
  # Room 1 is the first room ever listed, so player starts there.
door=Room 1,Room 2

  # Create Bob and place him in Room 1.
  # Have him say "Hello World!", "How are you?" when talked to (without quotes)
  # These quotes let you type anything you want. Below is another example.
person=Bob,Room 1
"Hello World!"
"How are you?"

!Bob
Hello World!
How are you?
  # Also valid, but can't use # or = in dialogue without quotes.

  # Create an item called 'Fish' and give it directly to the player.
  # Make the fish 'edible' with an ampersand (&)
item=&Fish,player

  # Create a heavy stove the player can't pick up. (with an exclamation mark (!))
item=!Stove,Room 2

  # Create a normal basic item, but put it in the same room as the player
item=Leaf,here

item=&!Giant Pizza,Room 2

# include everything in "filename" here in this file
include=filename

  # Make a spooky message at beginning when player enters Room 1
trigger=Room 1
$ person say Turn back!

  # Do the same thing in Room 2, using a procedure (proc).
proc=spooky_text
$ person say Turn back!

trigger=Room 2
$ @spooky_text

  # Reset Bob's dialogue and trigger, then set new ones
!Bob
$ item add &Fish,here
"Here, have a fish."

  # What will happen:
  # Room 1 and Room 2 are created, connected, and Room 1 has Bob.
  # Bob will NOT say Hello World because it's overwritten with "Here, have a fish."
  # Both rooms say "Turn back!" when you enter them.
  # Bob "gives you" (drops on the floor) an edible fish each time you talk to him.
  # If there's no file named "filename" then the game says it can't find the file.

  # Bob could've instead done "item add &Fish,player" to put it in the player's inventory.



[DIALOGUES]

Dialogue for a person can be set when the person is created by
writing lines starting with a double quote mark. (")

The ending quote mark is optional, only the starting one is required.
EXCEPT when you need to use quote marks in the dialogue. Then you need the ending quote.

# Example
person=Adam
""The End" of the movie."

Optionally, you can just start typing the text, with some limitations:
You can't use # or =
You can't start with ? or ! or $

But with a quote mark at the start, anything can be written.

# EXAMPLE
door=One,One
person=A,One
"ZERO, ONE, AND TWO QUOTES"
I see # of people = 1
"I see # of people = 1
"I see # of people = 1"
"The End" of the movie.
""The End" of the movie.
""The End" of the movie."
"DONE"

# RESULTS OF TALK:
ZERO, ONE, AND TWO QUOTES
I see 
I see # of people = 1
I see # of people = 1
The End
"The End
"The End" of the movie.
DONE



[TRIGGERS]

After some objects, you can place something called a "trigger".
A trigger is an action that is "triggered" by an event.
A trigger always starts with a dollar sign ($).

There are three kinds of events: Person, Place, and Item.

Person events activate when the player "talks" to the person.
Place events activate when the player "goes" to that place.
Item events activate when the player "uses" that item. (Not eat; eating is pointless)

A trigger is written in the file by starting a line with a dollar sign ($).
This is seen in the examples above, where the trigger "person say " outputs some text.

Triggers are split into four different context groups: person, place, item, and load

The available triggers are as follows:



Note: ONLY a single space can separate CONTEXT COMMAND and STRING
      Multiple spaces or other "whitespace" will cause problems.

CONTEXT COMMAND STRING

As in: PERSON SAY STUFF OF TEXT THAT FOLLOWS
PERSON is the CONTEXT
SAY is the COMMAND
and STUFF OF TEXT THAT FOLLOWS is the STRING

Below I put in parenthesis what is required input,
and in brackes I put what is optional input. For example:

PERSON
add (name),[placeName]

Means the context is PERSON, the command is ADD, and you have to put a name.
The name must be of a person, and if you want you can put their starting place.
Otherwise, the starting place is where they start.



PERSON
add (name),[placeName]
move (name/"player"),(placeName)
say (text)      # This only prints out text. See "dialogue" for making people talk.
trigger (name),[text]  #set trigger to "text"
trigger (name)  #remove trigger
dialogue (name),[text] #put "\n" for multi line (without quotes)
ask (name),(keyword),[text] # no second comma means remove text

PLACE
add (name),[placeName]
door (name),(name)
trigger (name),[text] #only name means remove trigger

ITEM
add (name),(placeName/"player"/"here") #"player" means put in inventory
trigger (name),[text] #only name means remove trigger

LOAD
file (name) #Load a new file on top of the already loaded one. Useful for resetting dialogues.

DELETE
person (name)
place (name)
item (name),(place)
door (place),(place) [, place]
door (place)  #delete all doors




# Examples
proc=setup
$ place add Room 1
$ place add Room 2
$ place door Room 1,Room 2
$ person add Bob,Room 1
$ person dialogue Bob,Hello World!\nHow are you?
  # Set Bob to have the trigger defined by proc=give_food
$ person trigger Bob,@give_food

proc=give_food
  # ( & makes the item edible ) ( ! makes the item too heavy to pick up )
$ item add &Fish,here
$ item trigger Fish,person say Smells... fishy.
$ item add !Rock,player
$ item trigger Rock,person say That's a BIG rock.

  # Make a room with no doors.
door=Field,Field
door=Room 1,Room 1
  # Change trigger for Field
trigger=Field
$ !@setup
  # ! means "only do once; then remove trigger line"

  # Upon entering room, add a door...
proc=setup
$ place door Field,Room 1

  # Ask user a question before doing something
proc=switch
$ place add Room 2,Room 1

item=!Door Switch,Room 1
$ ?( Open the door? ) @switch
  # Do what's after the closing parenthesis, if user says "yes" to question.



[ASKING PEOPLE]

After creating a person, or after resetting them with !, then
you can start a line with a question mark (?) with the following syntax:
? KEY,VALUE

The colon is required, and KEY IS EXACTLY ONE WORD and case-insensitive.
When the user asks about that word, VALUE is printed out (like "person say")

In-game the player uses the "ask" command to ask a person something.
If one of their words match, like food/color/bob below, then the matching text is printed.

# Example:
door=Room 1,Room 1
person=Bob,Room 1
? food,I like steak.
? color,My favorite color is blue.
? bob,Yes! My name is Bob!
" Hello, how are you?
" Have a fish.
$ !item add &Fish,player
$ person dialogue Bob,Hello, how are you?

  # Bob will say "Hello, how are you?" then "Have a fish." and give you a fish.
  # Then Bob stops giving fish and changes his dialogue to just "Hello, how are you?"

# Alternative:
door=Room 1,Room 1
person=Bob,Room 1
? food,I like steak.
? color,My favorite color is blue.
? bob,Yes! My name is Bob!
" Hello, how are you?
$ !person say Have a fish.
$ !item add &Fish,player

    # "Have a fish" only works once, after talking to Bob again, he won't say "Have a fish."
    # The same applies to Bob giving a fish, and any trigger starting with !
    # NOTE: Triggers must start with a $ first, then the !, then the trigger itself.
    # The end result looks different. "person say" puts a blank line before its text.



  # NOTE: You can put multiple keywords for each ask statement. Just separate with spaces.
person=Bob,Room 1
? food steak grub,I love steak!
" Ask me about my favorite food.
  # If player asks about "food", "steak", OR "grub" then output "I love steak!"
  # The same applies to a trigger
$ person ask Bob,color blue orange,My favorite color is blue.
" Or my favorite color.

  # Though out of order, the above lines are the same as writing:
person=Bob,Room 1
" Ask me about my favorite food.
" Or my favorite color.
$ person ask Bob,color blue orange,My favorite color is blue.
? food steak grub,I love steak!
  # The order of different types of lines doesn't matter.
  # It also doesn't matter how many blank lines are between.





