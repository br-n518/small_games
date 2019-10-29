
#include "boxing.h"



int main( int argc, char *argv[] )
{
	Engine e;
	engine_init( &e );
	engine_mainloop( &e );
	engine_destroy( &e );

	return 0;
}

