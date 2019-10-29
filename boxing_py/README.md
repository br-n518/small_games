
## Boxing

Simple hotseat console game where you take turns typing input (punching your friends)
while the others avoid looking at the screen for secrecy. This game is inspired by "rock, paper, scissors."

### Usage

Use Python 3 to play.

Command:
`python3 boxing.py`

***

### Gameplay

- On each round, each player takes a turn.
- On your turn, you choose one attack direction ( **X** ) and one block direction ( **+** )
- Both attack and block have 4 possible directions.
 - Attacks go in a diagonal direction (high-left, high-right, low-left, low-right)
 - Blocks go in one direction, but will cover both of the matching diagonal points.

- If an attack goes to HIGH-LEFT, then a block to HIGH or a block to LEFT will block the attack.

- Finally, if an attack makes it past a block, the attacker scores one point.

***

### Results

After everyone takes a turn, the end of round results shows who scored.

Whoever scores the most points at the end of all rounds is the winner.

***

