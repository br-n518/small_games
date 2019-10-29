#ifndef BOXING_GAME_H
#define BOXING_GAME_H

#include <assert.h>
#include <ctype.h>
#include <time.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>



#define ATTACK_BITS 0x0F
#define GUARD_BITS 0xF0

#define ATTACK_GUARD_NONE 0
#define ATTACK_HIGH 1
#define ATTACK_LOW 2
#define ATTACK_LEFT 4
#define ATTACK_RIGHT 8

#define ATTACK_HL 5
#define ATTACK_HR 9
#define ATTACK_LL 6
#define ATTACK_LR 10
	
#define GUARD_HIGH 16
#define GUARD_LOW 32
#define GUARD_LEFT 64
#define GUARD_RIGHT 128




// these two defs to be in-sync (LEN and LEN-1)
#define PLAYER_NAME_MAX_LEN 32
#define PLAYER_NAME_READLINE(a) scanf("%31s",a)

typedef struct Player
{
	int score;
	char name[PLAYER_NAME_MAX_LEN];
	char attack_move;
} Player;


typedef struct PlayerNode
{
	Player *player;
	struct PlayerNode *next;
} PlayerNode;

typedef struct Engine
{
	PlayerNode *player_list;
	int rounds, current_round;
} Engine;




static inline void clear_screen( void )
{
	int i = 8;
	while ( --i > 0 )
	{
		puts("\n\n\n\n\n\n\n");
	}
}

// Player functions

// allocate player
Player* player_alloc();

// prompt for user name
void player_init( Player *p );

// player takes their turn, func keeps prompting until input is good.
void player_turn( Player *p );

// process attack
void player_attack( Player *attack_player, Player *guard_player );

// no player_destroy
void player_free( Player *p );



// PlayerNode functions

PlayerNode* pn_create( Player *p );
void pn_append( PlayerNode **list, Player *p );
void pn_destroy( PlayerNode **list );
// invoke a function for every Player in the list
void pn_for_all( PlayerNode *list, void (*p_fn) (Player*) );

void pn_print_scores( PlayerNode *list );



// Engine functions

// initialize engine, prompting for player count and names.
void engine_init( Engine *engine );

// call player_turn for each and then player_attack
void engine_step( Engine *engine );

void engine_destroy( Engine *engine );

void engine_mainloop( Engine *engine );



#endif

