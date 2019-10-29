BINARY=boxing
SRC=src/boxing.c src/main.c
CFLAGS=-std=c99 -Wall -Werror
LDFLAGS=

.PHONY: all clean



all: bin/$(BINARY)


bin/$(BINARY): $(SRC)
	gcc $(CFLAGS) -o bin/$(BINARY) $(SRC) $(LDFLAGS)


clean:
	rm -f bin/$(BINARY)

