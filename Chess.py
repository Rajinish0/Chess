import pygame,random,math,time,copy,os
from pygame.locals import *
run = True
w,h = 1000,680
clock = pygame.time.Clock()
screen = pygame.display.set_mode((w,h))
blocks = 8
blockW = w//blocks
blockH = h//blocks

def CheckEvent(functionality_disabled=False):
	global run,pieceinHand,piece,curValidMoves,lastLegalPos,curfunc,funcs,KINGSPOS,InCheck,CheckMate
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.QUIT
			run = False


		if not CheckMate:
			if event.type == pygame.MOUSEBUTTONDOWN:
				j,i= GetBlockFromMouse()
				piece = board[i][j]
				lastLegalPos = (i,j)
				if not piece == '' and funcs[curfunc](piece):
					pieceinHand = True
					curValidMoves = MOVEFUNCS[piece.lower()](i,j,funcs[curfunc])
					board[i][j] = ''
					# curValidMoves = FilterMoves(piece,funcs[curfunc],curValidMoves);


			if event.type == pygame.MOUSEBUTTONUP:
				j,i = GetBlockFromMouse()
				back = False
				if pieceinHand:
					if (i,j) in curValidMoves:
						board[i][j] = piece
					else:
						origI,origJ = lastLegalPos
						board[origI][origJ] = piece
						curfunc = not curfunc if not lastLegalPos == (i,j) else curfunc
					pieceinHand=False
					piece = None
					curValidMoves = None
					curfunc = not curfunc if (lastLegalPos != (i,j)) else curfunc
					
					if board[i][j].lower() == 'k':															### UPDAATE KING's Position
						KINGSPOS[funcs[not curfunc]] = (i,j) if not (i,j) == lastLegalPos else KINGSPOS[funcs[not curfunc]]

					lastLegalPos = None					

					CheckForPawnPromotion(i,j,funcs[not curfunc]);

					CheckForCheckMate();



	keys = pygame.key.get_pressed()
	return (keys,run,piece)

def GetBlockFromMouse():
	posx,posy = pygame.mouse.get_pos()
	j,i= posx//blockW,posy//blockH
	return j,i


def CheckForPawnPromotion(i,j,func):
	global imgs,board,CheckMate
	if board[i][j].lower() == 'p' and (i==0 or i == 7):
		board[i][j] = 'p' if func == str.islower else 'P';
		screen.fill((0,0,0))
		drawRects()
		drawPieces(board,imgs)
		DrawCheck((i,j),(255,255,0))					## BAD FUNCTION NAMING; THIS JUST DRAWS A RECT AT A GIVEN POSITION
		pygame.display.update()
		CheckMate= True;						## JUST TO DISABLE ANY MOUSE CLICKS DURING PAWN PROMOTION PHASE.
		PawnPromotion(i,j,func);
		CheckMate= False;

def CheckForCheckMate():
	global curfunc,funcs,CheckMate,InCheck,MOVEFUNCS
	if KingInCheck(*KINGSPOS[funcs[curfunc]],funcs[curfunc]):
		InCheck = KINGSPOS[funcs[curfunc]]
		kingsMoves = MOVEFUNCS['k'](*KINGSPOS[funcs[curfunc]],funcs[curfunc])
		if len(kingsMoves) < 2:
			print('POTENTIAL CHECKMATE')
			CheckMate = LousyCheckMateAlgo(funcs[curfunc]);
			winner = players[funcs[not curfunc]] if CheckMate else None;						
			print(winner);
	else:
		InCheck = None


def PawnPromotion(i,j,func):
	newFunc = str.lower if func == str.islower else str.upper

	while True:
		keys = pygame.key.get_pressed()
		if keys[pygame.K_q]:
			board[i][j] = newFunc('q')
			break
		elif keys[pygame.K_r]:
			board[i][j] = newFunc('r')
			break
		elif keys[pygame.K_n]:
			board[i][j] = newFunc('n')
			break
		elif keys[pygame.K_b]:
			board[i][j] = newFunc('b')
			break
		elif keys[pygame.K_p]:
			board[i][j] = newFunc('p')
			break
		CheckEvent()


def movePiece(d,piece):
	posx,posy = pygame.mouse.get_pos()
	screen.blit(d[piece],(posx-50,posy-50))

def GetBoard():
	board = []
	for i in range(0,w,blockW):
		board.append(['' for j in range(0,h,blockH)])
	return board

def drawRects():
	#colors = {0:(195,155,119),1:(181,101,29)}
	colors = {1:(51,51,51),0:(144,238,144)}
	curColor = 0	
	for i in range(0,w,blockW):
		n = []
		for j in range(0,h,blockH):
			r = Rect(i,j,blockW,blockH)
			pygame.draw.rect(screen,colors[curColor],r)
			curColor = not curColor
			n.append('')
		board.append(n)
		curColor = not curColor	
	return board

def RookeMoves(i,j,func,depth=50,lookingFor = []):
	global board,blocks
	validMoves = [(i,j)]
	U = MOVECHECKER(i,j,func,1,0,orig=1,depth=depth,valMoves=[],lookingFor=lookingFor)
	D = MOVECHECKER(i,j,func,-1,0,orig=1,valMoves=[],depth=depth,lookingFor=lookingFor)
	R = MOVECHECKER(i,j,func,0,1,orig=1,valMoves=[],depth=depth,lookingFor=lookingFor)
	L = MOVECHECKER(i,j,func,0,-1,orig=1,valMoves=[],depth=depth,lookingFor=lookingFor)
	validMoves = validMoves + U+D+R+L if lookingFor == [] else (U[1] or D[1] or R[1] or L[1])
	return validMoves

def BishopMoves(i,j,func,depth=50,lookingFor=[]):
	global board,blocks
	validMoves= [(i,j)]
	U = MOVECHECKER(i,j,func,1,1,orig=1,depth=depth,valMoves=[],lookingFor=lookingFor)
	D = MOVECHECKER(i,j,func,-1,-1,orig=1,valMoves=[],depth=depth,lookingFor=lookingFor)
	UR = MOVECHECKER(i,j,func,1,-1,orig=1,valMoves=[],depth=depth,lookingFor=lookingFor)
	DR = MOVECHECKER(i,j,func,-1,1,orig=1,valMoves=[],depth=depth,lookingFor=lookingFor)
	validMoves = validMoves + U+D+UR+DR if lookingFor ==[] else (U[1] or D[1] or UR[1] or DR[1])
	return validMoves

def PawnMoves(i,j,func,lookingFor=[]):
	validMoves = [(i,j)]
	depth = 3 if (i == 1 or i == 6) else 2
	LOOKINGFOR = ['q','p','r','k','n','b']
	if func == str.islower:
		MOVE = MOVECHECKER(i,j,func,1,0,orig=1,depth = depth,valMoves=[],lookingFor=[])
	else:
		MOVE = MOVECHECKER(i,j,func,-1,0,orig=1,depth = depth,valMoves=[],lookingFor=[])

	for ind, each in enumerate(MOVE):
		(vali,valj) = each
		if board[vali][valj] != '':
			del MOVE[ind];


	LOOKINGFOR = LOOKINGFOR if func == str.isupper else [each.capitalize() for each in LOOKINGFOR];
	LOOKINGFOR = LOOKINGFOR if lookingFor == [] else lookingFor;
	sign = 1 if func == str.islower else -1
	potentialMove1, enemyOnRDiag = MOVECHECKER(i,j,func,sign*1,1,orig=1,depth = 2,valMoves=[],lookingFor=LOOKINGFOR)
	potentialMove2, enemyOnLDiag = MOVECHECKER(i,j,func,sign*1,-1,orig=1,depth = 2,valMoves=[],lookingFor=LOOKINGFOR)
	validMoves = validMoves + potentialMove1 if enemyOnRDiag else validMoves
	validMoves = validMoves + potentialMove2 if enemyOnLDiag else validMoves

	return validMoves+MOVE if lookingFor == [] else (enemyOnRDiag or enemyOnLDiag)



def KingMoves(i,j,func,lookingFor=[]):
	valMoves = RookeMoves(i,j,func,depth=2,lookingFor=lookingFor)
	N = BishopMoves(i,j,func,depth=2,lookingFor=lookingFor)
	return list(set(valMoves+N)) if lookingFor == [] else (valMoves or N)


def QueenMoves(i,j,func,lookingFor=[]):
	l1 = [lookingFor[0],lookingFor[-1]] if lookingFor != [] else []
	l2 = lookingFor[:2] if lookingFor != [] else []


	valMoves = RookeMoves(i,j,func,lookingFor=l1)
	N = BishopMoves(i,j,func,lookingFor = l2)
	return list(set(valMoves+N)) if lookingFor == [] else (valMoves or N)


def KnightMoves(i,j,func,lookingFor=[]):
	validMoves = [(i,j)]
	cur = 0
	steps = [1,-1]
	for ind, each in enumerate(steps):
		M1 = MOVECHECKER(i,j,func,2*each,1,orig=1,depth=2,valMoves= [],lookingFor=lookingFor)
		M2 = MOVECHECKER(i,j,func,2*each,-1,orig=1,depth=2,valMoves=[],lookingFor=lookingFor)
		M3 = MOVECHECKER(i,j,func,1,2*each,orig=1,depth=2,valMoves=[],lookingFor=lookingFor)
		M4 = MOVECHECKER(i,j,func,-1,2*each,orig=1,depth=2,valMoves=[],lookingFor=lookingFor)
		validMoves = [] if (lookingFor != [] and ind <1) else validMoves
		validMoves =(validMoves+M1 + M2 + M3 + M4) if lookingFor == [] else (validMoves or M1[1] or M2[1] or M3[1] or M4[1])
	return validMoves;


def MOVECHECKER(i,j,func,moveI,moveJ,valMoves=[],orig=False,depth=50,lookingFor=[],found=False,piece=None):
	global board
	##FUNC btw can be str.isupper, which would be white, or str.islower for black (just built up from fenstrings.)
	##SO if func(board[i][j]); meaning if the piece which im checking the moves for is white and the board's position which im currently at is white too
	##Then i want this to terminate obv.
	if (i >= blocks or j>=blocks or i < 0 or j< 0 or func(board[i][j]) or depth <= 0 or found) and (not orig):
		return valMoves if lookingFor == [] else (valMoves,found)

	piece = copy.copy(board[i][j]) if (orig and (lookingFor == [] or board[i][j].lower() == 'p')) else piece 	##UH used lookingFor for pawn, had to use another condition.
	board[i][j] = '' if (piece is not None and orig) else board[i][j]							## went crazy with if else commands
													##Here's the gist of the code
	if not orig and piece is not None:								##gets a moveI and moveJ, which come from different pieces
		origPiece = copy.copy(board[i][j])				#Moves recursively in that moveI, moveJ until the conditions above are satisfied		
		board[i][j] = piece						##Also works as a look up function; which I used for KingInCheck, really couldn't go through
		if piece.lower() =='k':						#the trouble of writing another function for that. Takes care of not adding a position if that would
			origKingPos = copy.copy(KINGSPOS[func])		#Make the king in check.
			KINGSPOS[func] = (i,j)	
		if not KingInCheck(*KINGSPOS[func],func):
			valMoves.append((i,j))
		board[i][j] = origPiece;
		KINGSPOS[func] = origKingPos if piece.lower() == 'k' else KINGSPOS[func];

	if board[i][j] != '' and not orig:
		found = True if board[i][j] in lookingFor else found
		return valMoves if lookingFor == [] else (valMoves,found)

	res= MOVECHECKER(i+moveI,j+moveJ,func,moveI,moveJ,valMoves,depth=depth-1,lookingFor=lookingFor,found=found,piece=piece)
	board[i][j] = piece if (piece is not None and orig) else board[i][j]
	return res


def KingInCheck(i,j,func):
	newFunc = str.lower if func == str.isupper else str.upper			#TO SEE IF KING IS IN CHECK, MOVE EVERY piece's moves from KING'S current position
	pieces = ['q','b','r','p','k','n']						#And see if the piece whose move you are moving is on one of those blocks.
	pieces = [newFunc(each) for each in pieces]

	c1 = QueenMoves(i,j,func,lookingFor = pieces[:3])
	c2 = PawnMoves(i,j,func,lookingFor=pieces[3])
	c3 = KingMoves(i,j,func,lookingFor=pieces[4])
	c4 = KnightMoves(i,j,func,lookingFor=pieces[-1])

	return (c1 or c2 or c3 or c4)


def parseFen(board,fen):
	splits = fen.split('/')
	for i, each in enumerate(splits):
		ind = 0
		for charac in each:
			try:
				ind += int(charac)-1
			except:
				board[i][ind] = charac;
			ind += 1


def loadPicsDict():
	d = {} ## FOR PYGAME.SURFACE
	l = ['black','white']
	for i,tranche in enumerate(l):
		for each in os.listdir(tranche):
			piece = each.split('.')[0]
			piece = piece.capitalize() if i > 0 else piece
			image = pygame.image.load(tranche+'\\'+each)
			image = pygame.transform.scale(image,(100,100))
			d[piece] = image
	return d


def drawCurValidMoves(curValidMoves):
	for each in curValidMoves:
		x,y = blockW*each[1],blockH*each[0]
		r = Rect(x,y,blockW,blockH)
		pygame.draw.rect(screen,(0, 0, 51),r,5)


def drawPieces(board,imgs):
	global blockW, blockH,screen
	for i in range(len(board)):
		for j,each in enumerate(board[i]):
			if each == '':
				continue
			img = imgs[each]
			x,y = blockW*j,blockH *i
			screen.blit(img,(x+10,y-10))

def DrawCheck(pos):
	global CheckMate
	i,j = pos
	x,y = blockW*j,blockH *i
	r = Rect(x,y,blockW,blockH)
	c = (155,0,0) if not CheckMate else (155,0,155)
	pygame.draw.rect(screen,c,r,5)


## THE WORST ALGORITHM FOR CHECKING FOR CHECK MATE
def LousyCheckMateAlgo(func):
	piecesToCheck = ['q','r','n','b','p'];
	newFunc = str.upper if func == str.isupper else str.lower				#IF KING Can't move anywhere, then check for all moves
	piecesToCheck = [newFunc(each) for each in piecesToCheck];				#of all pieces of same color, if their possible moves are more then one
	for i in range(len(board)):								#(1 move would be their own position) that means checkmate could be avoided
		for j in range(len(board[0])):							#MOVECHECKER doesn't add the position in valid moves, which would cause the king
			if board[i][j] in piecesToCheck:					#to be in check.
				possibleMoves = MOVEFUNCS[board[i][j].lower()](i,j,func)
				if len(possibleMoves) > 1:
					return False
	return True


pieceinHand = 0
piece = None
curValidMoves = None
CheckMate = False
players = {str.islower:'Black',str.isupper:'White'}
lastLegalPos = None
MOVEFUNCS = {'r':RookeMoves,'b':BishopMoves,'k':KingMoves,'n':KnightMoves,'p':PawnMoves,'q':QueenMoves}
funcs = {0:str.islower,1:str.isupper}
KINGSPOS = {str.islower:(0,4),str.isupper:(7,4)}                  ## CHANGE KINGS' POSITIONS FOR DEFAULT STARTING FEN; or write a function that does that for you.
InCheck = None
curfunc = 1
fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR'
#fen = '4k3/1R6/2QQ5/8/8/8/8/4K3'
imgs= loadPicsDict()
board = GetBoard()
parseFen(board,fen)

while run:
	screen.fill((0,0,0))
	drawRects()
	drawPieces(board,imgs)
	keys,run,piece = CheckEvent()
	if pieceinHand:
		drawCurValidMoves(curValidMoves);
		movePiece(imgs,piece)
	if InCheck is not None:
		DrawCheck(InCheck);
	pygame.display.update()
