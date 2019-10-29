/**
 * Random game
 * This is not tested for cross browser compatibility and makes no attempt to achieve such. Tested on chrome & firefox.
 */


// CONSTANTS
var TWO_PI = Math.PI * 2;
var FOURTH_PI = Math.PI / 4;

// store these values to avoid reprocessing
var COS_FOURTH_PI = Math.cos( FOURTH_PI );
var SIN_FOURTH_PI = Math.sin( FOURTH_PI );

var GAME_DIFFICULTY=1;
var STARTING_ENEMIES = 100;
var ENEMY_RESPAWN_RATIO = 1;
var ENEMY_RESPAWN_RATE = 1000;

function setDifficulty(d) {
	if (d >= 0 && d <= 3) {
		GAME_DIFFICULTY = d;
		STARTING_ENEMIES = (50 + (50 * GAME_DIFFICULTY));
		ENEMY_RESPAWN_RATIO = 0.5 + (0.5 * GAME_DIFFICULTY);
		if (ENEMY_RESPAWN_RATIO > 0) ENEMY_RESPAWN_RATE = Math.floor(1000 / ENEMY_RESPAWN_RATIO);
		else ENEMY_RESPAWN_RATE = 1000;
	} else {
		console.log("Failed to set selected difficulty. Value=" + d);
	}
}



// GLOBALS
var gameCanvas = null; // canvas to draw to
var gameContext = null; // graphics context for canvas drawing
var gameLoopLock = null; // pointer to setInterval timer, also used to determine if game is running
var horiOffset = 2;
var vertOffset = 6;

var gamePaused = false;

var nightEnabled = false;

var player = null; // player object, interacts with user input
var enemies = null; // enemies, currently do nothing special
var enemySpawnLock = null;
var bulletSpeed = 4;
var noSpawnZone = {x:0,y:0,radius:200};

var map;
var currentOrbs = 0;
var tilesize = 40;
var viewport = { x:0, y:0, width:0, height:0 };

var VKEY={BACKSPACE:8,TAB:9,ENTER:13,SHIFT:16,CONTROL:17,CAPSLOCK:20,ESCAPE:27,SPACE:32,PAGEUP:33,PAGEDOWN:34,END:35,HOME:36,DELETE:36,LEFT:37,RIGHT:39,UP:38,DOWN:40,INSERT:45,ZERO:48,ONE:49,TWO:50,THREE:51,FOUR:52,FIVE:53,SIX:54,SEVEN:55,EIGHT:56,NINE:57,A:65,B:66,C:67,D:68,E:69,F:70,G:71,H:72,I:73,J:74,K:75,L:76,M:77,N:78,O:79,P:80,Q:81,R:82,S:83,T:84,U:85,V:86,W:87,X:88,Y:89,Z:90,NUMPAD0:96,NUMPAD1:97,NUMPAD2:98,NUMPAD3:99,NUMPAD4:100,NUMPAD5:101,NUMPAD6:102,NUMPAD7:103,NUMPAD8:104,NUMPAD9:105,NUMPAD_MULT:106,NUMPAD_PLUS:107,NUMPAD_MINUS:109,NUMPAD_DELETE:110,NUMPAD_DIVIDE:111,F1:112,F2:113,F3:114,F4:115,F5:116,F6:117,F7:118,F8:119,F9:120,F10:121,F11:122,F12:123,NUMLOCK:144,SEMICOLON:186,EQUALS:187,COMMA:188,MINUS:189,PERIOD:190,GRAVE:192,APOSTROPHE:222};

//KEYBOARD INPUT (PRESS)
function keyPressed( event ) {
	// ignore F5 and F11, also check that game is running
	if ( event.keyCode != VKEY.F5 && event.keyCode != VKEY.F11 && gameLoopLock ) {
		event.preventDefault(); // prevent default key actions in browser
		
		// pause/unpause
		if ( event.keyCode == VKEY.ESCAPE || event.keyCode == VKEY.BACKSPACE || event.keyCode == VKEY.P ) {
			gamePaused = !gamePaused;
		}
		
		// break life (action)
		if ( event.keyCode == VKEY.F2 ) {
			if (player.lives >= 1) {
				player.lives -= 1;
				player.mana += 25;
				player.hitpoints += 5;
			}
		}
		
		if (! gamePaused) {
			
			// shoot/move
			if ( event.shiftKey ) {
				if ( event.keyCode == VKEY.LEFT || event.keyCode == VKEY.A ) { //left
					player.bullets.push(createBullet(player.x, player.y, -1 * bulletSpeed, 0));
			    }
				else if ( event.keyCode == VKEY.UP || event.keyCode == VKEY.W ) { //up
					player.bullets.push(createBullet(player.x, player.y, 0, -1 * bulletSpeed));
			    }
				else if( event.keyCode == VKEY.RIGHT || event.keyCode == VKEY.D ) { //right
					player.bullets.push(createBullet(player.x, player.y, bulletSpeed, 0));
			    }
				else if ( event.keyCode == VKEY.DOWN || event.keyCode == VKEY.S ) { //down
					player.bullets.push(createBullet(player.x, player.y, 0, bulletSpeed));
			    }
				
			} else {
				if ( event.keyCode == VKEY.LEFT || event.keyCode == VKEY.A ) { //left
			        player.dx = -5;
			    }
				else if ( event.keyCode == VKEY.UP || event.keyCode == VKEY.W ) { //up
			    	player.dy = -5;
			    }
				else if( event.keyCode == VKEY.RIGHT || event.keyCode == VKEY.D ) { //right
			        player.dx = 5;
			    }
				else if ( event.keyCode == VKEY.DOWN || event.keyCode == VKEY.S ) { //down
			    	player.dy = 5;
			    }
			}
			
			// grab/drop dirt; grab mana orb
			if ( event.keyCode == VKEY.SPACE || event.keyCode == VKEY.NUMPAD0) {
				var t = map.getTileOf(player);
				if (player.hasDirt) {
					// drop dirt at tile
					if (t.height < 3) {
						t.height += 1;
						t.setColor();
						player.hasDirt = false;
					}
				} else {
					// grab dirt
					if (t.height > 0) {
						t.height -= 1;
						t.setColor();
						player.hasDirt = true;
					}
				}
			}
			
			// consume dirt
			else if (event.keyCode == VKEY.C || event.keyCode == VKEY.NUMPAD_PLUS) {
				var t = map.getTileOf(player);
				if (t.height > 0) {
					t.height -= 1;
					t.setColor();
					player.mana++;
				}
			}
			// create dirt block
			else if (event.keyCode == VKEY.E) {
				var t = map.getTileOf(player);
				if (t.height < 3 && player.mana >= 1) {
					t.height += 1;
					player.mana -= 1;
					t.setColor();
				}
			}
			// heal
			else if (event.keyCode == VKEY.Q) {
				if (player.mana >= 3) {
					player.mana -= 3;
					player.hitpoints += 2;
				}
			}
			// create extra life
			else if (event.keyCode == VKEY.G) {
				if (player.mana >= 50) {
					player.mana -= 50;
					player.lives += 1;
				}
			}
			
			// shoot sides
			else if (event.keyCode == VKEY.NUMPAD4) {
				player.bullets.push(createBullet(player.x, player.y, -1 * bulletSpeed, 0));
			}
			else if (event.keyCode == VKEY.NUMPAD5 || event.keyCode == VKEY.NUMPAD2) {
				player.bullets.push(createBullet(player.x, player.y, 0, bulletSpeed));
			}
			else if (event.keyCode == VKEY.NUMPAD8) {
				player.bullets.push(createBullet(player.x, player.y, 0, -1 * bulletSpeed));
			}
			else if (event.keyCode == VKEY.NUMPAD6) {
				player.bullets.push(createBullet(player.x, player.y, bulletSpeed, 0));
			}
			// shoot diagonals
			else if (event.keyCode == VKEY.NUMPAD7) {
				player.bullets.push(createBullet(player.x, player.y, -1 * bulletSpeed, -1 * bulletSpeed));
			}
			else if (event.keyCode == VKEY.NUMPAD9) {
				player.bullets.push(createBullet(player.x, player.y, bulletSpeed, -1 * bulletSpeed));
			}
			else if (event.keyCode == VKEY.NUMPAD1) {
				player.bullets.push(createBullet(player.x, player.y, -1 * bulletSpeed, bulletSpeed));
			}
			else if (event.keyCode == VKEY.NUMPAD3) {
				player.bullets.push(createBullet(player.x, player.y, bulletSpeed, bulletSpeed));
			}
		}
	}
}



//KEYBOARD INPUT (RELEASE)
function keyReleased( event ) {
	// ignore F5 and F11, also check that game is running
	if ( event.keyCode != VKEY.F5 && event.keyCode != VKEY.F11 && gameLoopLock ) {
		event.preventDefault();
		
		if (! gamePaused) {
			if ( event.keyCode == VKEY.LEFT || event.keyCode == VKEY.A ) { //left
		        if (player.dx < 0) player.dx = 0;
		    }
			else if ( event.keyCode == VKEY.UP || event.keyCode == VKEY.W ) { //up
				if (player.dy < 0) player.dy = 0;
		    }
			else if( event.keyCode == VKEY.RIGHT || event.keyCode == VKEY.D ) { //right
		        if (player.dx > 0) player.dx = 0;
		    }
			else if ( event.keyCode == VKEY.DOWN || event.keyCode == VKEY.S ) { //down
				if (player.dy > 0) player.dy = 0;
		    }
		}
	}
}



function game_init() {

	map = createTiledMap(100,100);
	console.log("Map Created.");
	
	player = createGameObject();
	player.color = '#FFFFFF';
	
	player.x = Math.floor((map.width * tilesize)/2);
	player.y = Math.floor((map.height * tilesize)/2);
	
	player.hasDirt = false;
	
	player.lives = 2;
	player.hitpoints = 5;
	player.mana = 10;
	
	player.bullets = new Array();
	
	player.step = function pstep() {
		var a = null;
		for (var b = 0; b < player.bullets.length; b++) {
			if (player.bullets[b]) {
				player.bullets[b].move(null);
				a = player.bullets[b].step();
				if (a) { //if the bullet hit an enemy, or should otherwise be destroyed...
					player.bullets.splice(b, 1);
				}
			}
		}
		
		for (var i = 0; i < enemies.length; i++) {
			if (circlesCollide(player, enemies[i])) {
				player.hitpoints -= 0.15;
			}
		}
		
		if ( ! player.isAlive()) {
			if (player.lives > 0) {
				player.hitpoints = 5;
				player.mana = 10;
				player.lives -= 1;
				
				// scramble nearby enemies
				scrambleAllEnemies();
			} else {
				alert("Game Over.\nF5 for a new game.");
				game_stop();
			}
		}
		
	}

	// create enemies AFTER player has been created
	enemies = [];
	gamePaused = false; // make sure initial enemies will indeed spawn
	for (var i = 0; i < STARTING_ENEMIES; i++) {
		spawnEnemy();
	}
	
	console.log("Done making characters.");
	
}







//create a generic game character object
function createGameObject() {
	return {
		x:20,
		y:20,
		dx:0,
		dy:0,
		radius:10,
		color:'red',
		
		hitpoints:1,
		mana:0,
		
		isAlive: function isalive() {
			return (this.hitpoints > 0);
		},
		
		
		
		step:null,
		
		move: function mv(m) {
			// move
			
			if (m) {
				var tileX1 = this.getTileX(tilesize);
				var tileY1 = this.getTileY(tilesize);
				var t1 = m.getTileAt(tileX1, tileY1);
				var t2;

				if (this.dx != 0 && this.dy != 0) {
					// limit diagonal speed
					this.x += (this.dx * COS_FOURTH_PI);
					this.y += (this.dy * SIN_FOURTH_PI);
				} else {
					this.x += this.dx;
					this.y += this.dy;
				}
				
				// keep in bounds
				if (this.x < 0) this.x = 0;
				if (this.y < 0) this.y = 0;
				if (this.x >= m.pixelWidth) this.x = m.pixelWidth-1;
				if (this.y >= m.pixelHeight) this.y = m.pixelHeight-1;
				
				// position of destination tile
				var tileX2 = this.getTileX(tilesize);
				var tileY2 = this.getTileY(tilesize);
				
				// test height of horizontal tile
				if (tileX1 != tileX2) {
					t2 = m.getTileAt(tileX2, tileY1);
					if ((t2.height - t1.height) >= 2) {
						this.x -= this.dx;
					}
				}
				
				// test height of vertical tile
				if (tileY1 != tileY2) {
					t2 = m.getTileAt(tileX1, tileY2);
					if ((t2.height - t1.height) >= 2) {
						this.y -= this.dy;
					}
				}
				
			} else {
				if (this.dx != 0 && this.dy != 0) {
					// limit diagonal speed
					this.x += (this.dx * COS_FOURTH_PI);
					this.y += (this.dy * SIN_FOURTH_PI);
				} else {
					this.x += this.dx;
					this.y += this.dy;
				}
			}
		},
		
		getTileX: function gettilex(size) {
			return (this.x - (this.x % size)) / size;
		},
		getTileY: function gettiley(size) {
			return (this.y - (this.y % size)) / size
		}
	};
}

function createBullet( x, y, dx, dy ) {
	if (player.mana >= 1) {
		player.mana -= 1;
		
		var b = createGameObject();
		
		// add values for origin, used for distance traveled test
		b.ox = x;
		b.oy = y;
		
		b.x = x;
		b.y = y;
		b.dx = dx;
		b.dy = dy;
		
		b.color = '#000000';
		
		b.radius = 5;
		
		b.step = function bulletStep() {
			
			// distance limiter
			if ( Math.sqrt( Math.pow( this.ox - this.x, 2 ) + Math.pow( this.oy - this.y, 2 ) ) > tilesize*5 ) {
				return true;
			}
			
			for (var i = 0; i < enemies.length; i++) {
				if ( enemies[i] && circlesCollide(this, enemies[i]) ) {
					enemies[i].hitpoints -= 1;
					if (enemies[i].hitpoints <= 0) killEnemy(i);
					return true;
				}
			}
			return false;
		}
		
		return b;
	}
	return null;
}



// w,h - width and height in tiles
function createTiledMap( w, h ) {
	var m = new Array(w*h);
	var moc = 0;
	for (var i = 0; i < m.length; i++) {
		m[i] = {};
		m[i].height = Math.floor( 3 * Math.random() );
		m[i].setColor = function scolor() {
			if (this.height <= 0) {
				this.color = '#00F088';
			} else if (this.height == 1) {
				this.color = '#A0FF00';
			} else if (this.height == 2) {
				this.color = '#00FF00';
			} else {
				this.color = '#AAFFAA';
			}
		}
		
		m[i].color = '#222222';
		m[i].setColor();
		
		if (Math.random() < 0.02) {
			m[i].hasMana = true;
			moc++;
		} else m[i].hasMana = false;
		
	} // END create tiles
	currentOrbs = moc;
	console.log( moc + " mana orbs created (of " + (w*h) + " tiles).");
	
	m.width = w;
	m.height = h;
	m.pixelWidth = w * tilesize;
	m.pixelHeight = h * tilesize;
	
	m.getTileAt = function gta( c, r ) {
		return this[(r * this.width) + c];
	};
	
	m.getTileOf = function gto( ch ) {
		if (ch) {
			var x = ch.getTileX(tilesize);
			var y = ch.getTileY(tilesize);
			return this[(y * this.width) + x];
		} else {
			return null;
		}
	}
	
	m.getArea = function ga( c, r, w, h ) {
		var result = new Array();
		var k = 0;
		var current;
		
		for (var i = r; i < r + h; i++) {
			for (var j = c; j < c + w; j++) {
				if (i < 0 || i >= this.height) current = null;
				else if (j < 0 || j >= this.width) current = null;
				else current = this[ (i * this.width) + j ];
				
				if (current) result[k] = current;
				else result[k] = null;
				k++;
			}
		}
		
		result.width = w;
		result.height = h;
		return result;
	}
	
	return m;
}







// simple routine that causes an object to follow player
function AI_followPlayer() {
	if (player) {
		if (player.x < this.x - 1) this.dx = -2.5;
		else if (player.x > this.x + 1) this.dx = 2.5;
		else this.dx = 0;
		
		if (player.y < this.y - 1) this.dy = -2.5;
		else if (player.y > this.y + 1) this.dy = 2.5;
		else this.dy = 0;
	}
}



function killEnemy( i ) {
	if (i >= 0) {
		if (enemies[i]) {
			enemies[i] = null;
			enemies.splice(i, 1);
		}
	}
}

function spawnEnemy() {
	if (!gamePaused && enemies.length < 500) {
		var e = createGameObject();
		e.x = Math.floor(map.pixelWidth * Math.random());
		e.y = Math.floor(map.pixelHeight * Math.random());
		e.step = AI_followPlayer;
		e.color = 'rgba(255,0,0,0.3)';
		
		noSpawnZone.x = player.x;
		noSpawnZone.y = player.y;
		
		while (circlesCollide(e, noSpawnZone)) {
			e.x = Math.floor(map.pixelWidth * Math.random());
			e.y = Math.floor(map.pixelHeight * Math.random());
		}
		
		enemies.push(e);
	}
}

function scrambleAllEnemies() {
	var e = null;
	noSpawnZone.x = player.x;
	noSpawnZone.y = player.y;
	
	for (var i = 0; i < enemies.length; i++) {
		e = enemies[i];
		while (circlesCollide(e, noSpawnZone)) {
			e.x = Math.floor(map.pixelWidth * Math.random());
			e.y = Math.floor(map.pixelHeight * Math.random());
		}
	}
}



// return true if they collide, false otherwise
//requires: x, y, radius
function circlesCollide( a, b ) {
	if (a && b) {
		var distance = Math.sqrt(Math.pow(a.x - b.x, 2) + Math.pow(a.y - b.y, 2));
		
		if (distance < a.radius + b.radius) {
			return true;
		}
	}
	return false;
}



function game_drawTiledMap( m, view, offset, ctx ) {
	if ( m && view && offset && ctx ) {
		var currentTile = null;
		
		var area = m.getArea( view.x, view.y, view.width+1, view.height+1 );
		
		var a=0, b=0;
		var x, y;
		
		for (var row = 0; row < area.height; row++) {
			for (var col = 0; col < area.width; col++) {
				
				currentTile = area[(row * area.width) + col];
				
				if (currentTile) {
					
					// x y values
					x = (a - offset.x) - (horiOffset * currentTile.height);
					y = (b - offset.y) - (vertOffset*currentTile.height);
					
					// draw tile
					ctx.fillStyle = currentTile.color;
					ctx.fillRect(x, y, tilesize, tilesize );
					ctx.strokeStyle = '#000033';
					ctx.strokeRect(x, y, tilesize, tilesize );
					
					// draw orb
					if (currentTile.hasMana) {
						ctx.fillStyle = '#2222EE';
						ctx.strokeStyle = '#EEEEFF';
						ctx.beginPath();
						ctx.arc(x + (tilesize/2), y + (tilesize/2), tilesize/4, 0, TWO_PI);
						ctx.closePath();
						ctx.fill();
						ctx.stroke();
					}
				}
				a += tilesize;
			}
			b += tilesize;
			a = 0;
		}
		
	}
}







// draw a game character
function game_drawCharacter(ch, offset, ctx) {
	if (ch) {
		var tileX = ch.getTileX(tilesize);
		var tileY = ch.getTileY(tilesize);
		var t = map.getTileAt(tileX, tileY);
		
		if (tileX >= viewport.x && tileX <= viewport.x + viewport.width) {
			if (tileY >= viewport.y && tileY <= viewport.y + viewport.height) {
				
				ctx.strokeStyle = '#000000';
				ctx.fillStyle = ch.color;
				ctx.beginPath();
				if (offset) {
					ctx.arc((ch.x - (viewport.x*tilesize)-offset.x) - (horiOffset*t.height), (ch.y - (viewport.y*tilesize)-offset.y) - (t.height*vertOffset), ch.radius, 0, TWO_PI);
				} else {
					ctx.arc(ch.x, ch.y, ch.radius, 0, TWO_PI);
				}
				ctx.closePath();
				ctx.fill();
				ctx.stroke();
				
			}
		}
	}
}

// draw a pie graph...
function game_drawPie( cx, cy, radius, percent, ctx ) {
	ctx.beginPath();
	ctx.moveTo( cx, cy );
	ctx.arc(cx, cy, radius, 0, (TWO_PI * percent)); // needs to be rotated
	ctx.lineTo( cx, cy );
	ctx.closePath();
	ctx.fill();
}



// TODO: offset player and enemies based on map position
function game_render() {
	
	if ( gameCanvas && gameContext ) {
		
		var playerOffset = {
			x: (player.x % tilesize),
			y: (player.y % tilesize)
		};
		
		gameContext.globalAlpha = 1;
		gameContext.lineWidth = 1;
		
		// clear screen
		gameContext.fillStyle = '#00AA00';
		gameContext.fillRect(0,0,gameCanvas.width,gameCanvas.height);
		
		if (map) {
			// draw floating map tiles
			game_drawTiledMap(map, viewport, playerOffset, gameContext);
		} else {
			// clear screen
			gameContext.fillStyle="#00BBFF";
			gameContext.fillRect(0,0,gameCanvas.width,gameCanvas.height);
		}
		
		// draw player
		var t = map.getTileOf(player);
		gameContext.fillStyle = player.color;
		gameContext.strokeStyle = '#000000';
		gameContext.beginPath();
		gameContext.arc((gameCanvas.width/2) - (t.height *horiOffset), (gameCanvas.height/2) - (t.height*vertOffset), player.radius, 0, TWO_PI);
		gameContext.closePath();
		gameContext.fill();
		gameContext.stroke();
		
		// draw enemies
		for (var i = 0; i < enemies.length; i++) {
			game_drawCharacter( enemies[i], playerOffset, gameContext );
		}
		
		// draw bullets
		for (var b = 0; b < player.bullets.length; b++) {
			if (player.bullets[b]) {
				gameContext.fillStyle = player.bullets[b].color;
				gameContext.strokeStyle = '#FEEF00';
				gameContext.beginPath();
				gameContext.arc(player.bullets[b].x - (viewport.x*tilesize)-playerOffset.x, player.bullets[b].y - (viewport.y*tilesize)-playerOffset.y, player.bullets[b].radius, 0, TWO_PI);
				gameContext.closePath();
				gameContext.fill();
				gameContext.stroke();
			}
		}
		
		
		// HUD
		// background
		gameContext.fillStyle = 'rgba(0,0,0,0.5)';
		gameContext.fillRect( 0, gameCanvas.height - 65, gameCanvas.width, 65);
		
		// dirt possession
		if (player.hasDirt) {
			gameContext.fillStyle = player.color;
			gameContext.fillRect( 5, gameCanvas.height - 60, 10, 10 );
		}
		
		// player hitpoints
		gameContext.fillStyle = '#FF2020';
		gameContext.fillRect(5, gameCanvas.height - 30, player.hitpoints * 5, 10);
		// player lives
		gameContext.fillStyle = '#DDFF20';
		for (var i = 0; i < player.lives; i++) {
			gameContext.fillRect( 5 + (i * 15), gameCanvas.height - 45, 10, 10)
		}
		if (player.mana >= 50) {
			gameContext.strokeStyle = '#DDFF20';
			gameContext.strokeRect( 5 + ((i) * 15), gameCanvas.height - 45, 10, 10)
		}
		
		// player mana
		gameContext.fillStyle = '#00AAFF';
		gameContext.fillRect(5, gameCanvas.height - 15, player.mana * 5, 10);
		
		//nighttime
		if (nightEnabled) {
			gameContext.fillStyle = 'rgba(0,0,85,0.5)';
			gameContext.fillRect(0, 0, gameCanvas.width, gameCanvas.height);
		}
		
		// enemy display
		gameContext.fillStyle = '#FFFFFF';
		gameContext.font="16px Georgia";
		gameContext.fillText("Enemies: " + enemies.length, 90, gameCanvas.height - 48);
		
		// orb display
		gameContext.font="16px Georgia";
		gameContext.fillText("Orbs: " + currentOrbs, 240, gameCanvas.height - 48);
		
	} else {
		console.log("ERROR: Canvas or Context is not set.");
	}
}



function game_loop() {
	if (!gamePaused) {
		for (var i = 0; i < enemies.length; i++) {
			if (enemies[i]) {
				if (enemies[i].step) enemies[i].step();
				enemies[i].move(map);
			} else {
				// remove array element
				enemies.splice(i, 1);
			}
		}
		
		// player routine
		if (player) {
			if (player.step) player.step();
			player.move(map);
			viewport.x = player.getTileX(tilesize) - (viewport.width/2);
			viewport.y = player.getTileY(tilesize) - (viewport.height/2);
			
			// pickup mana orb
			var t = map.getTileOf(player);
			if (t.hasMana) {
				t.hasMana = false;
				player.mana += 5;
				currentOrbs -= 1;
			}
			
			for (var i = 0; i < player.bullets.length; i++) {
				if (player.bullets[i]) {
					player.bullets[i].step();
				} else {
					player.bullets.splice(i, 1);
				}
			}
		}
		
		if (currentOrbs <= 0) {
			gamePaused = true;
			currentOrbs = 0;
			game_render();
			alert("You won by collecting all mana orbs.\nF5 for a new game.\nOr you may continue exploring.");
			currentOrbs = 9001;
		}
		
		requestAnimationFrame(game_render);
		
	} else {
		gameContext.fillStyle = '#FFFFFF';
		gameContext.font="20px Georgia";
		gameContext.fillText("Paused.",20,gameCanvas.height - 48);
	}
}



function game_start( canvas_obj, difficulty ) {
	if (! gameLoopLock) {
		// set up canvas and drawing context
		gameCanvas = canvas_obj;
		if (gameCanvas) {
			gameContext = gameCanvas.getContext("2d");
		} else {
			console.log("Failed to load canvas.");
			game_stop();
			return false;
		}
		
		// check graphics context
		if (! gameContext) {
			console.log("Failed to start renderer.");
			game_stop();
			return false;
		}
		
		viewport.width = Math.floor(gameCanvas.width / tilesize);
		viewport.height = Math.floor(gameCanvas.height / tilesize);
		
		setDifficulty(difficulty);
		game_init();
		
		// start paused
		viewport.x = player.getTileX(tilesize) - (viewport.width/2);
		viewport.y = player.getTileY(tilesize) - (viewport.height/2);
		gamePaused = false;
		game_render();
		gamePaused = true;
		
		console.log("Game initialized.");
		
		// start main game loop
		gameLoopLock = setInterval( game_loop, 25 ); // FPS controlled here
		enemySpawnLock = setInterval( spawnEnemy, ENEMY_RESPAWN_RATE );
		
		console.log("Game loop started.");
		return true;
	} else {
		console.log("game_start called after already started...");
	}
}

// stop game function. Leave gameCanvas alone for resume ability.
function game_stop() {
	clearInterval(gameLoopLock);
	gameLoopLock = null;
	gameContext = null;
	console.log("Game stopped.");
}
