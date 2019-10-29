
#include "boxing.h"



#define CONSOLE_SPACER(n) for(int _cs_i=0;_cs_i<n;_cs_i++)printf("\n")




// Player functions

// allocate player
Player* player_alloc() 
{
	return malloc( sizeof( Player ) );
}



// prompt for user name
void player_init( Player *p ) 
{
	assert( p );
	
	p->score = 0;
	p->attack_move = ATTACK_GUARD_NONE;
	p->name[0] = '\0';
	
	while ( p->name[0] == '\0' )
	{
		// prompt
		printf("Your name: ");
		// call scanf()
		PLAYER_NAME_READLINE(p->name);
		// spacer
		CONSOLE_SPACER(1);
		
		// verify input has non-space characters in it
		for (int i = 0; i < PLAYER_NAME_MAX_LEN-1; i++)
		{
			char c = p->name[i];
			if (c)
			{
				if ( isspace(c) )
				{
					continue;
				}
				else
				{
					break;
				}
			}
			else
			{
				p->name[0] = '\0';
				break;
			}
		}// end for
	} //end while
}



// player takes their turn, function keeps prompting until input is good.
void player_turn( Player *p ) 
{
	CONSOLE_SPACER(2);
	
	// reset player's attack and guard
	p->attack_move = ATTACK_GUARD_NONE;
	
	// const bit masks
	const char ATTACK_V = ATTACK_HIGH | ATTACK_LOW;
	const char ATTACK_H = ATTACK_LEFT | ATTACK_RIGHT;
	
	// print player's name
	printf( "%s's turn:\n\n", p->name );
	
	// get attack
	char buffer[32];
	
	while ( ! ( p->attack_move & ATTACK_V &&
					p->attack_move & ATTACK_H ) )
	{
	
		if ( ! (p->attack_move & ATTACK_V) )
		{
			printf("High or Low?\n");
		}
		if ( ! (p->attack_move & ATTACK_H) )
		{
			printf("Left or Right?\n");
		}
		printf("\nAttack: ");
		scanf("%31s", buffer);
		CONSOLE_SPACER(4);
		
		// convert to lowercase
		char *ptr = buffer;
		while ( *ptr ) {
			*ptr = tolower(*ptr);
			ptr++;
		}
		
		// use strstr to determine
		if ( ! (p->attack_move & ATTACK_V) )
		{
			if ( strstr( buffer, "hi" ) )
			{
				p->attack_move |= ATTACK_HIGH;
			}
			else if ( strstr( buffer, "lo" ) )
			{
				p->attack_move |= ATTACK_LOW;
			}
		}
		
		if ( ! (p->attack_move & ATTACK_H) )
		{
			if ( strstr( buffer, "le" ) )
			{
				p->attack_move |= ATTACK_LEFT;
			}
			else if ( strstr( buffer, "ri" ) )
			{
				p->attack_move |= ATTACK_RIGHT;
			}
		}
	}
	
	// get guard
	while ( ! (p->attack_move & GUARD_BITS) )
	{
		printf("High, Low, Left, or Right?\n");
		printf("\nGuard: ");
		scanf("%31s", buffer);
		CONSOLE_SPACER(4);
		
		// convert to lowercase
		// use strstr to determine
		char *ptr = buffer;
		while ( *ptr ) {
			*ptr = tolower(*ptr);
			ptr++;
		}
		
		if ( ! (p->attack_move & GUARD_BITS) )
		{
			if ( strstr( buffer, "hi" ) )
			{
				p->attack_move |= GUARD_HIGH;
			}
			else if ( strstr( buffer, "lo" ) )
			{
				p->attack_move |= GUARD_LOW;
			}
			if ( strstr( buffer, "le" ) )
			{
				p->attack_move |= GUARD_LEFT;
			}
			else if ( strstr( buffer, "ri" ) )
			{
				p->attack_move |= GUARD_RIGHT;
			}
		}
	}
	
	clear_screen();
}



void player_attack( Player *attack_player, Player *guard_player ) 
{
	assert( attack_player );
	assert( guard_player );
	assert( attack_player->attack_move );
	assert( guard_player->attack_move );
	assert( attack_player->attack_move & ATTACK_BITS );
	assert( guard_player->attack_move & GUARD_BITS );
	
	
	char attack_str[16], guard_str[16];
	char hit_blocked = 0;
	
	// get strings (attack)
	switch ( attack_player->attack_move & ATTACK_BITS )
	{
		case ATTACK_HL:
		
			strcpy( attack_str, "high left" );
			
		break;
		case ATTACK_HR:
		
			strcpy( attack_str, "high right" );
			
		break;
		case ATTACK_LL:
		
			strcpy( attack_str, "low left" );
			
		break;
		case ATTACK_LR:
		
			strcpy( attack_str, "low right" );
			
		break;
	}
	// get strings (guard)
	switch ( guard_player->attack_move & GUARD_BITS )
	{
		case GUARD_HIGH:
			strcpy( guard_str, "high" );
			if ( attack_player->attack_move & ATTACK_HIGH )
				hit_blocked = 1;
		break;
		case GUARD_LOW:
			strcpy( guard_str, "low" );
			if ( attack_player->attack_move & ATTACK_HIGH )
				hit_blocked = 1;
		break;
		case GUARD_LEFT:
			strcpy( guard_str, "left" );
			if ( attack_player->attack_move & ATTACK_LEFT )
				hit_blocked = 1;
		break;
		case GUARD_RIGHT:
			strcpy( guard_str, "right" );
			if ( attack_player->attack_move & ATTACK_RIGHT )
				hit_blocked = 1;
		break;
	}
	
	printf("%s attacks %s with a %s %s: ", attack_player->name, guard_player->name, attack_str, rand()%8 >= 4 ? "punch":"kick" );
	
	if ( hit_blocked )
	{
		printf("(BLOCKED)\n");
	}
	else
	{
		printf("[HIT]\n");
		// increment score for successful attack
		attack_player->score++;
	}
}



void player_free( Player *p ) 
{
	free( p );
}







// PlayerNode functions

PlayerNode* pn_create( Player *p ) 
{
	if ( p )
	{
		PlayerNode *ret = malloc( sizeof(*ret) );
		ret->player = p;
		ret->next = 0;
		return ret;
	}
	return 0;
}

void pn_append( PlayerNode **list, Player *p ) 
{
	assert( p );
	
	PlayerNode *curr = *list;
	
	if ( curr )
	{
		while ( curr->next )
		{
			curr = curr->next;
		}
		
		curr->next = pn_create( p );
	}
	else
	{
		*list = pn_create( p );
	}
}

void pn_destroy( PlayerNode **list ) 
{
	assert( list );
	
	PlayerNode *prev, *curr = *list;
	
	while ( curr )
	{
		prev = curr;
		curr = curr->next;
		free( prev->player );
		free( prev );
	}
	*list = 0;
}

// invoke a function for every Player in the list
// can be player_init, player_turn, or player_free (after player_alloc)
void pn_for_all( PlayerNode *list, void (*p_fn) (Player*) ) 
{
	assert( list );
	assert( p_fn );
	
	PlayerNode *curr = list;
	
	while ( curr )
	{
		p_fn( curr->player );
		curr = curr->next;
	}
}

void pn_print_scores( PlayerNode *list )
{
	PlayerNode *curr = list;
	
	printf("Scores:\n\n");
	
	while ( curr )
	{
		printf("- %s: %d pts\n", curr->player->name, curr->player->score );
		curr = curr->next;
	}
}







// Engine functions

// initialize engine, prompting for player count and names.
void engine_init( Engine *engine ) 
{
	assert( engine );
	
	srand( time(0) );
	
	// reset "round" counter (as in rounds, matches, games, etc.)
	engine->current_round = 0;
	engine->player_list = 0;
	
	char buffer[16];
	
	// Get number of rounds to play
	while ( 1 )
	{
		printf("How many rounds?: ");
		scanf( "%15s", buffer );
		
		if ( buffer[0] )
		{
			int count = atoi(buffer);
			if ( count >= 1 )
			{
				if ( count > 99 )
				{
					count = 99;
				}
				// store count as number of rounds to play
				engine->rounds = count;
				// break while loop
				break;
			}
		}
	}
	
	// Get number of players, and allocate/initialize them.
	while ( 1 )
	{
		printf("How many players?: ");
		scanf( "%15s", buffer );
		
		if ( buffer[0] )
		{
			int count = atoi(buffer);
			if ( count >= 2 && count <= 16 )
			{
				CONSOLE_SPACER(1);
				Player *p;
				// loop for number of players to setup
				// starting at 1 for output. (alternative: i=0; i < count; i++)
				for ( int i = 1; i <= count; i++ )
				{
					// print which player we're naming
					printf("(Player %d)\n", i );
					p = player_alloc();
					player_init( p );
					
					pn_append( &(engine->player_list), p );
				} //end for
				
				// break while loop
				break;
			}
		}
	} //end while
}



// call player_turn for all and then player_attack
// engine has player_list to iterate
void engine_step( Engine *engine ) 
{
	clear_screen();
	
	// increment round counter
	engine->current_round++;
	printf("~ BEGIN ROUND %d ~\n\n", engine->current_round );
	
	// each player takes a turn.
	pn_for_all( engine->player_list, player_turn );
	
	// battle phase
	PlayerNode *curr = engine->player_list;
	PlayerNode *other;
	
	while ( curr )
	{
		other = engine->player_list;
		
		while ( other )
		{
			if ( curr != other )
			{
				// attack
				player_attack( curr->player, other->player );
			}
			
			// next pointer
			other = other->next;
			
		} //end while
		
		// next pointer
		curr = curr->next;
		
	} //end while
	
	// end phase
	CONSOLE_SPACER(1);
	pn_print_scores( engine->player_list );
	
	printf("\nPress [Enter] to continue... ");
	getchar(); getchar();
}



void engine_destroy( Engine *engine ) 
{
	pn_destroy( &(engine->player_list) );
	engine->rounds = 0;
	engine->current_round = 0;
}



void engine_mainloop( Engine *engine ) 
{
	while ( engine->current_round < engine->rounds )
	{
		engine_step( engine );
	}
	CONSOLE_SPACER(8);
	puts("Match finished!\n");
	
	pn_print_scores( engine->player_list );
	
	printf("\nPress [Enter] to EXIT... ");
	getchar(); getchar();
}
















