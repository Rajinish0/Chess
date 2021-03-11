  
import pygame,random,math,time,copy,os
from pygame.locals import *
run = True
w,h = 1000,680
clock = pygame.time.Clock()
screen = pygame.display.set_mode((w,h))
blocks = 8
blockW = w//blocks
blockH = h//blocks

def CheckEvent():
	global run,pieceinHand,piece,curValidMoves,lastLegalPos,curfunc,funcs,KINGSPOS,InCheck,CheckMate,EnPassantMoves_
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
					board[i][j] = ''
					curValidMoves = MOVEFUNCS[piece.lower()](i,j,funcs[curfunc],piece=piece)


			if event.type == pygame.MOUSEBUTTONUP:
				j,i = GetBlockFromMouse()
				back = False
				if pieceinHand:
					if (i,j) in curValidMoves:
						piecesAvailable[board[i][j]] -= 1
						board[i][j] = piece
					else:
						origI,origJ = lastLegalPos
						board[origI][origJ] = piece
						curfunc = not curfunc if not lastLegalPos == (i,j) else curfunc
					pieceinHand=False
					piece = None
					curValidMoves = None
					curfunc = not curfunc if (lastLegalPos != (i,j)) else curfunc
					AfterMath(i,j,curfunc);
					



	keys = pygame.key.get_pressed()
	return (keys,run,piece)

def GetBlockFromMouse():
	posx,posy = pygame.mouse.get_pos()
	j,i= posx//blockW,posy//blockH
	return j,i


def AfterMath(i,j,curfunc):
	global run,pieceinHand,piece,curValidMoves,lastLegalPos,funcs,KINGSPOS,InCheck,CheckMate,EnPassantMoves_,piecesAvailable

	if board[i][j].lower() == 'k':															### UPDAATE KING's Position
		KINGSPOS[funcs[not curfunc]] = (i,j) if not (i,j) == lastLegalPos else KINGSPOS[funcs[not curfunc]]

	CheckCastlingRights(i,j,funcs[not curfunc]);
	ResetPawnHistory(((board[i][j].lower() == 'p' and ((i,j) != lastLegalPos))))
	CheckPawnHistory(i,j,curfunc)
	CheckEnPassantKill(i,j,curfunc)

	if board[i][j].lower() != '' and ((i,j) != lastLegalPos):
		EnPassantMoves_ = []
	lastLegalPos = None

	CheckForPawnPromotion(i,j,funcs[not curfunc]);
	CheckForCheckMate(curfunc);	

'''
So if a pawn is at starting position and it moves 2 steps, i record that pawn in a dictionary
then when the other pawn moves and the pawn to its left or right has moved 2 steps it has the right to kill it.
the move is added to EnPassantMoves_. The rule for enpassant being applicable only once for every pawn implementation:
the record in dictionary gets changed to 0 and EnPassantMoves_ gets emptied every time a move is played.
'''

def CheckPawnHistory(i,j,curfunc):
	global lastLegalPos, funcs
	if board[i][j].lower() == 'p' and lastLegalPos != (i,j) and (lastLegalPos[0] == 1 or lastLegalPos[0] == 6):
		UpdatePawnHistory(lastLegalPos,(i,j),funcs[not curfunc]);

def CheckEnPassantKill(i,j,curfunc):
	global EnPassantMoves_,funcs,lastLegalPos
	if board[i][j].lower() == 'p' and lastLegalPos != (i,j) and ((i,j) in EnPassantMoves_):
		print('KILLING',i,j)
		DoTheDeed(i,j,funcs[curfunc]);


def CheckForPawnPromotion(i,j,func):
	global imgs,board,CheckMate
	if board[i][j].lower() == 'p' and (i==0 or i == 7):
		board[i][j] = 'p' if func == str.islower else 'P';
		screen.fill((0,0,0))
		drawRects()
		drawPieces(board,imgs)
		DrawCheck((i,j),(255,255,0))			## BAD FUNCTION NAMING; THIS JUST DRAWS A RECT AT A GIVEN POSITION
		pygame.display.update()
		CheckMate= True;						## JUST TO DISABLE ANY MOUSE CLICKS DURING PAWN PROMOTION PHASE.
		PawnPromotion(i,j,func);
		CheckMate= False;

def CheckCastlingRights(i,j,func):
	global board, castlingRights, lastLegalPos,castlingMoves_
	newFunc = str.lower if func == str.islower else str.upper
	piecesToCheck = ['r','k']
	if board[i][j].lower() in piecesToCheck and (i,j) != lastLegalPos:
		word = 'left' if j < 4 else 'right'
		castlingRights[func][word] = False
		(castlingRights[func]['left'],castlingRights[func]['right']) = (0,0) if board[i][j].lower() == 'k' else (castlingRights[func]['left'],castlingRights[func]['left']);

	if board[i][j].lower() == 'k' and (i,j) in castlingMoves_:
		ind = 7 if func == str.isupper else 0
		if j < 5:
			board[ind][0] = ''
			board[ind][j+1] = newFunc('r')
		else:
			board[ind][7] = ''
			board[ind][j-1] = newFunc('r')
	castlingMoves_ = []

def CheckForCheckMate(curfunc):
	global funcs,CheckMate,InCheck,MOVEFUNCS
	if KingInCheck(*KINGSPOS[funcs[curfunc]],funcs[curfunc]):
		InCheck = KINGSPOS[funcs[curfunc]]
		newFunc = str.lower if funcs[curfunc] == str.islower else str.upper
		kingsMoves = MOVEFUNCS['k'](*KINGSPOS[funcs[curfunc]],funcs[curfunc],piece=newFunc('k'))
		if len(kingsMoves) < 2:
			print('POTENTIAL CHECKMATE')
			print(funcs[curfunc],KINGSPOS[funcs[curfunc]])
			CheckMate = LousyCheckMateAlgo(funcs[curfunc]);
			winner = players[funcs[not curfunc]] if CheckMate else None;						
			print(winner);
			return True
	else:
		InCheck = None
	return False

def UpdateKingsPos(i,j,func):
	global KINGSPOS
	KINGSPOS[func] = (i,j)

def PawnPromotion(i,j,func):
	newFunc = str.lower if func == str.islower else str.upper

	while True:
		keys = pygame.key.get_pressed()
		board[i][j] = newFunc('q')
		return
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

def RookeMoves(i,j,func,depth=50,lookingFor = [],piece=None,isMaximizing=True,d= None,returnBestMove=False,origPos=None,curfunc=None):
	global board,blocks
	validMoves = [(i,j)]
	U = MOVECHECKER(i,j,func,1,0,orig=1,depth=depth,valMoves=[],lookingFor=lookingFor,piece=piece,isMaximizing=isMaximizing,d= d,returnBestMove=returnBestMove,origPos=origPos,curfunc=curfunc)
	D = MOVECHECKER(i,j,func,-1,0,orig=1,valMoves=[],depth=depth,lookingFor=lookingFor,piece=piece,isMaximizing=isMaximizing,d= d,returnBestMove=returnBestMove,origPos=origPos,curfunc=curfunc)
	R = MOVECHECKER(i,j,func,0,1,orig=1,valMoves=[],depth=depth,lookingFor=lookingFor,piece=piece,isMaximizing=isMaximizing,d= d,returnBestMove=returnBestMove,origPos=origPos,curfunc=curfunc)
	L = MOVECHECKER(i,j,func,0,-1,orig=1,valMoves=[],depth=depth,lookingFor=lookingFor,piece=piece,isMaximizing=isMaximizing,d= d,returnBestMove=returnBestMove,origPos=origPos,curfunc=curfunc)
	if returnBestMove:
		return L;
	validMoves = validMoves + U+D+R+L if lookingFor == [] else (U[1] or D[1] or R[1] or L[1])
	return validMoves

def BishopMoves(i,j,func,depth=50,lookingFor=[],piece=None,isMaximizing=True,d= None,returnBestMove=False,origPos=None,curfunc=None):
	global board,blocks
	validMoves= [(i,j)]
	U = MOVECHECKER(i,j,func,1,1,orig=1,depth=depth,valMoves=[],lookingFor=lookingFor,piece=piece,isMaximizing=isMaximizing,d= d,returnBestMove=returnBestMove,origPos=origPos,curfunc=curfunc)
	D = MOVECHECKER(i,j,func,-1,-1,orig=1,valMoves=[],depth=depth,lookingFor=lookingFor,piece=piece,isMaximizing=isMaximizing,d= d,returnBestMove=returnBestMove,origPos=origPos,curfunc=curfunc)
	UR = MOVECHECKER(i,j,func,1,-1,orig=1,valMoves=[],depth=depth,lookingFor=lookingFor,piece=piece,isMaximizing=isMaximizing,d= d,returnBestMove=returnBestMove,origPos=origPos,curfunc=curfunc)
	DR = MOVECHECKER(i,j,func,-1,1,orig=1,valMoves=[],depth=depth,lookingFor=lookingFor,piece=piece,isMaximizing=isMaximizing,d= d,returnBestMove=returnBestMove,origPos=origPos,curfunc=curfunc)
	if returnBestMove:
		return DR
	validMoves = validMoves + U+D+UR+DR if lookingFor ==[] else (U[1] or D[1] or UR[1] or DR[1])
	return validMoves

def PawnMoves(i,j,func,lookingFor=[],piece=None,isMaximizing=True,d= None,returnBestMove=False,origPos=None,curfunc=None):
	validMoves = [(i,j)]
	depth = 3 if (i == 1 or i == 6) else 2
	LOOKINGFOR = ['q','p','r','k','n','b']
	if func == str.islower:
		MOVE = MOVECHECKER(i,j,func,1,0,orig=1,depth = depth,valMoves=[],lookingFor=[],piece=piece,isMaximizing=isMaximizing,d= d,returnBestMove=returnBestMove,origPos=origPos,curfunc=curfunc)
	else:
		MOVE = MOVECHECKER(i,j,func,-1,0,orig=1,depth = depth,valMoves=[],lookingFor=[],piece=piece,isMaximizing=isMaximizing,d= d,returnBestMove=returnBestMove,origPos=origPos,curfunc=curfunc)


	LOOKINGFOR = LOOKINGFOR if func == str.isupper else [each.capitalize() for each in LOOKINGFOR];
	LOOKINGFOR = LOOKINGFOR if lookingFor == [] else lookingFor;
	sign = 1 if func == str.islower else -1
	potentialMove1, enemyOnRDiag = MOVECHECKER(i,j,func,sign*1,1,orig=1,depth = 2,valMoves=[],lookingFor=LOOKINGFOR,piece=piece,isMaximizing=isMaximizing,d= d,returnBestMove=returnBestMove,origPos=origPos)
	potentialMove2, enemyOnLDiag = MOVECHECKER(i,j,func,sign*1,-1,orig=1,depth = 2,valMoves=[],lookingFor=LOOKINGFOR,piece=piece,isMaximizing=isMaximizing,d= d,returnBestMove=returnBestMove,origPos=origPos)
	if returnBestMove:
		return (potentialMove2, enemyOnLDiag)
	validMoves = validMoves + potentialMove1 if enemyOnRDiag else validMoves
	validMoves = validMoves + potentialMove2 if enemyOnLDiag else validMoves

#	if returnBestMove:
#		for each in [potentialMove1,potentialMove2]:
	## MOVE THERE AND CALL GETALLPOSSIBLEMOVES WITH d-1

	validMoves = validMoves + CheckForEnPassant(i,j,func) if lookingFor == [] else validMoves;

	return validMoves+MOVE if lookingFor == [] else (enemyOnRDiag or enemyOnLDiag)


def CheckForEnPassant(i,j,func):
	global PawnHistory, EnPassantMoves_
	LookUpFunc = str.islower if func == str.isupper else str.isupper
	NewFunc = str.lower if func == str.isupper else str.upper
	sign = 1 if func == str.islower else -1
	EnPassantMoves = []

	lookingFor = [NewFunc('p')]
	move, enemyOnLeft = MOVECHECKER(i,j,func,0,-1,orig=1,depth=2,valMoves =[],lookingFor=lookingFor,piece=piece)
	move2, enemyOnRight = MOVECHECKER(i,j,func,0,1,orig=1,depth=2,valMoves=[],lookingFor=lookingFor,piece=piece)

	EnPassantMoves = EnPassantMoves + [(i+1*sign,j-1)] if (enemyOnLeft and PawnHistory[LookUpFunc][j-1] == 2) else EnPassantMoves
	EnPassantMoves = EnPassantMoves + [(i+1*sign,j+1)] if (enemyOnRight and PawnHistory[LookUpFunc][j+1] == 2) else EnPassantMoves
	EnPassantMoves_ += EnPassantMoves

	return EnPassantMoves

def DoTheDeed(i,j,func):				## EN PASSANT BRUTAL KILL.
	global board 
	sign = 1 if func == str.islower else -1
	board[i+sign][j] = ''


def KingMoves(i,j,func,lookingFor=[],piece=None,isMaximizing=True,d= None,returnBestMove=False,origPos=None,curfunc=None):
	valMoves = RookeMoves(i,j,func,depth=2,lookingFor=lookingFor,piece=piece,isMaximizing=isMaximizing,d= d,returnBestMove=returnBestMove,origPos=origPos,curfunc=curfunc)
	N = BishopMoves(i,j,func,depth=2,lookingFor=lookingFor,piece=piece,isMaximizing=isMaximizing,d= d,returnBestMove=returnBestMove,origPos=origPos,curfunc=curfunc)
	if returnBestMove:
		return N;
	valMoves = valMoves + LookForCastling(i,j,func) if lookingFor == [] else valMoves;
	return list(set(valMoves+N)) if lookingFor == [] else (valMoves or N)

def LookForCastling(i,j,func):
	global castlingRights,castlingMoves_,InCheck
	newFunc = str.lower if func == str.islower else str.upper
	castlingMoves = []
	## Can't castle if king is in check
	if InCheck is None:
		_, RookeOnLeft = MOVECHECKER(i,j,func,0,-1,orig=1,valMoves=[],lookingFor=[newFunc('r')],depth=50) if castlingRights[func]['left'] else (None,False)
		_, RookeOnRight = MOVECHECKER(i,j,func,0,1,orig=1,valMoves=[],lookingFor=[newFunc('r')],depth=50) if castlingRights[func]['right'] else (None,False)
		castlingMoves = castlingMoves + [(i,j-2)] if RookeOnLeft else castlingMoves
		castlingMoves = castlingMoves + [(i,j+2)] if RookeOnRight else castlingMoves
		castlingMoves = FilterCastlingMoves(i,j,castlingMoves,newFunc('k'),func)
		castlingMoves_ += castlingMoves;

	return castlingMoves;


def FilterCastlingMoves(i,j,castlingMoves,piece,func):
	new = copy.copy(castlingMoves)
	for each in castlingMoves:		
		x,y = each 
		board[x][y] = piece
		origKingPos = copy.copy(KINGSPOS[func])
		KINGSPOS[func] = (x,y)
		if KingInCheck(*KINGSPOS[func], func):
			new.remove(each)
		board[x][y] = ''
		KINGSPOS[func] = origKingPos;
	return new;

def QueenMoves(i,j,func,lookingFor=[],piece=None,isMaximizing=True,d= None,returnBestMove=False,origPos=None,curfunc=None):
	l1 = [lookingFor[0],lookingFor[-1]] if lookingFor != [] else []
	l2 = lookingFor[:2] if lookingFor != [] else []


	valMoves = RookeMoves(i,j,func,lookingFor=l1,piece=piece,isMaximizing=isMaximizing,d= d,returnBestMove=returnBestMove,origPos=origPos,curfunc=curfunc)
	N = BishopMoves(i,j,func,lookingFor = l2,piece=piece,isMaximizing=isMaximizing,d= d,returnBestMove=returnBestMove,origPos=origPos,curfunc=curfunc)
	if returnBestMove:
		return N
	return list(set(valMoves+N)) if lookingFor == [] else (valMoves or N)


def KnightMoves(i,j,func,lookingFor=[],piece=None,isMaximizing=True,d= None,returnBestMove=False,origPos=None,curfunc=None):
	validMoves = [(i,j)]
	cur = 0
	steps = [1,-1]
	for ind, each in enumerate(steps):
		M1 = MOVECHECKER(i,j,func,2*each,1,orig=1,depth=2,valMoves= [],lookingFor=lookingFor,piece=piece,isMaximizing=isMaximizing,d= d,returnBestMove=returnBestMove,origPos=origPos,curfunc=curfunc)
		M2 = MOVECHECKER(i,j,func,2*each,-1,orig=1,depth=2,valMoves=[],lookingFor=lookingFor,piece=piece,isMaximizing=isMaximizing,d= d,returnBestMove=returnBestMove,origPos=origPos,curfunc=curfunc)
		M3 = MOVECHECKER(i,j,func,1,2*each,orig=1,depth=2,valMoves=[],lookingFor=lookingFor,piece=piece,isMaximizing=isMaximizing,d= d,returnBestMove=returnBestMove,origPos=origPos,curfunc=curfunc)
		M4 = MOVECHECKER(i,j,func,-1,2*each,orig=1,depth=2,valMoves=[],lookingFor=lookingFor,piece=piece,isMaximizing=isMaximizing,d= d,returnBestMove=returnBestMove,origPos=origPos,curfunc=curfunc)
		validMoves = [] if (lookingFor != [] and ind <1) else validMoves
		validMoves =(validMoves+M1 + M2 + M3 + M4) if (lookingFor == [] and not returnBestMove) else (validMoves or M1[1] or M2[1] or M3[1] or M4[1])
	if returnBestMove:
		return M4
	return validMoves;


'''
MOVECHECKER - 
I obv went crazy with if else commands
Here's the gist of the code
gets a moveI and moveJ, which come from different pieces
Moves recursively in that moveI, moveJ until the conditions above are satisfied		
Also works as a look up function; which I used for KingInCheck, really couldn't go through
the trouble of writing another function for that. Takes care of not adding a position if that would
make the king in check.'''


''' 
Alright so tried creating a chess AI, went at it with 2 approaches: 1. getting all the moves and then moving to each of them and then getting opponent's moves and
moving to those, yk the casual recursive minmax algo. 2. That was a slow, so since MOVECHECKER moves the piece to check the vacant spot
I used this as a function for returning best move; so first, say, a white pawn's move is checked (it's called from GetAllPossibleMoves),
movechecker moves it to that position and then calls
GetAllPossibleMoves again, which then call MOVECHECKER again and checks all moves of black, depth is decreased by 1 everytime 
GetAllPossibleMoves is called from MOVECHECKER, for the static evaluation. UH, this is still slow.. and this doesn't take into account the special moves:
En passant, castling, pawn promotion unlike the previous approach; gotta figure that out.
'''
def MOVECHECKER(i,j,func,moveI,moveJ,valMoves=[],orig=False,depth=50,lookingFor=[],found=False,piece=None,isMaximizing=True,d= None,returnBestMove=False,origPos=None,curfunc=None):
	##FUNC btw can be str.isupper, which would be white, or str.islower for black (just built up from fenstrings.)
	##SO if func(board[i][j]); meaning if the piece which im checking the moves for is white and the board's position which im currently at is white too
	##Then i want this to terminate obv.
	global board, lastLegalPos, maximScore, minimScore, bestMove,alpha,beta,MAXDEPTH, piecesAvailable
	if (i >= blocks or j>=blocks or i < 0 or j< 0 or (func(board[i][j]) and not board[i][j] in lookingFor) or depth <= 0 or found) and (not orig):
		if returnBestMove:
			return ([origPos,bestMove],maximScore) if isMaximizing else (None, minimScore)
		return valMoves if lookingFor == [] else (valMoves,found)
	if not orig and piece is not None and not (lookingFor == [] and piece.lower() == 'p' and board[i][j] != ''):
		if lookingFor == [] or (lookingFor != [] and board[i][j] in lookingFor):
			config = SaveOrigConfig()
			origPiece = copy.copy(board[i][j])
			board[i][j] = piece
			if piece.lower() =='k':
				origKingPos = copy.deepcopy(KINGSPOS[func])
				KINGSPOS[func] = (i,j)	

			if not KingInCheck(*KINGSPOS[func],func):
				valMoves.append((i,j))

				if returnBestMove:
					piecesAvailable[origPiece] -= 1
					lastLegalPos = origPos
					AfterMath(i,j,not curfunc)
					maxScore = copy.copy(maximScore)
					minScore = copy.copy(minimScore)
					alpha_,beta_ = copy.copy(alpha),copy.copy(beta)
					_, score = GetAllPossibleMoves(not curfunc,d-1, not isMaximizing);
					maximScore, minimScore = maxScore,minScore
					alpha,beta = alpha_,beta_

					board[i][j] = origPiece;
					piecesAvailable[origPiece] += 1
					KINGSPOS[func] = origKingPos if piece.lower() == 'k' else KINGSPOS[func];
					LoadConfig(config)


					if isMaximizing:
						if score >= maximScore:
							bestMove = [origPos, (i,j)] if d == MAXDEPTH else bestMove
							maximScore = score;
						alpha = max(alpha,score)
						if alpha >= beta:
							return (bestMove, maximScore)
					else:
						minimScore = min(minimScore, score)
						beta = min(alpha,score)
						if alpha >= beta:
							return (bestMove,minimScore)

			board[i][j] = origPiece;
			KINGSPOS[func] = origKingPos if piece.lower() == 'k' else KINGSPOS[func];
			LoadConfig(config)

	if board[i][j] != '' and not orig:
		found = True if board[i][j] in lookingFor else found
		if returnBestMove:
			return ([origPos,bestMove],maximScore) if isMaximizing else (None, minimScore)
		return valMoves if lookingFor == [] else (valMoves,found)

	return MOVECHECKER(i+moveI,j+moveJ,func,moveI,moveJ,valMoves,depth=depth-1,lookingFor=lookingFor,found=found,piece=piece,isMaximizing=isMaximizing,d= d,returnBestMove=returnBestMove,origPos=origPos,curfunc=curfunc)


	
def KingInCheck(i,j,func):
	newFunc = str.lower if func == str.isupper else str.upper
	pieces = ['q','b','r','p','k','n']
	pieces = [newFunc(each) for each in pieces]										#TO SEE IF KING IS IN CHECK, MOVE EVERY piece's moves from KING'S current position
	c1 = QueenMoves(i,j,func,lookingFor = pieces[:3])								#And see if the piece whose move you are moving is on one of those blocks.
	c2 = PawnMoves(i,j,func,lookingFor=pieces[3])
	c3 = KingMoves(i,j,func,lookingFor=pieces[4])
	c4 = KnightMoves(i,j,func,lookingFor=pieces[-1])
	return (c1 or c2 or c3 or c4)


def ResetPawnHistory(condition):
	global PawnHistory
	if condition:
		for each in list(PawnHistory.keys()):
			for j in list(PawnHistory[each].keys()):
				PawnHistory[each][j] = 0

def UpdatePawnHistory(lastLegalPos,newPos,func):
	global PawnHistory
	oldI, oldJ = lastLegalPos;
	i, j = newPos;
	PawnHistory[func][j] = abs(oldI - i)


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
	global EnPassantMoves_,castlingMoves_
	for each in curValidMoves:
		x,y = blockW*each[1],blockH*each[0]
		r = Rect(x,y,blockW,blockH)
		c = (51,51,81) if not each in EnPassantMoves_ else (155,21,21)
		c = c if not each in castlingMoves_ else (81,51,81)
		pygame.draw.rect(screen,c,r)
		pygame.draw.rect(screen,(0,0,51),r,5)


def drawPieces(board,imgs):
	global blockW, blockH,screen
	for i in range(len(board)):
		for j,each in enumerate(board[i]):
			if each == '':
				continue
			img = imgs[each]
			x,y = blockW*j,blockH *i
			screen.blit(img,(x+10,y-10))

def DrawCheck(pos,col=None):
	global CheckMate
	i,j = pos
	x,y = blockW*j,blockH *i
	r = Rect(x,y,blockW,blockH)
	c = (155,0,0) if not CheckMate else (155,0,155)
	c = c if col is None else col
	pygame.draw.rect(screen,c,r,5)


'''
IF KING Can't move anywhere, then check for all moves
of all pieces of same color, if their possible moves are more than one
(1 move would be their own position) that means checkmate could be avoided
MOVECHECKER doesn't add the position in valid moves, which would cause the king
to be in check.
'''

## THE WORST ALGORITHM FOR CHECKING FOR CHECK MATE
def LousyCheckMateAlgo(func):
	piecesToCheck = ['q','r','n','b','p'];
	newFunc = str.upper if func == str.isupper else str.lower
	piecesToCheck = [newFunc(each) for each in piecesToCheck];
	for i in range(len(board)):
		for j in range(len(board[0])):
			if board[i][j] in piecesToCheck:
				possibleMoves = MOVEFUNCS[board[i][j].lower()](i,j,func,piece=board[i][j])
				if len(possibleMoves) > 1:
					return False
	return True


def GetAllPossibleMoves(curfunc,depth=2,isMaximizing=True):
	global funcs, lastLegalPos,KINGSPOS,board,bestMove,maximScore,minimScore,alpha,beta, InCheck, CheckMate
	if not CheckMate:
		if depth <= 0:
			return (None, StaticEvaluation(board,False,curfunc))

		maximScore = float('-inf')
		minimScore = float('inf')
		for i in range(len(board)):
			for j in range(len(board[0])):
				if funcs[curfunc](board[i][j]):
					origPiece = copy.copy(board[i][j])
					board[i][j] = ''
					MOVEFUNCS[origPiece.lower()](i,j,funcs[curfunc],piece=origPiece,isMaximizing=isMaximizing,d= depth,returnBestMove=True,origPos=(i,j),curfunc=curfunc)
					board[i][j] = origPiece
		return (bestMove, maximScore) if isMaximizing else (None,minimScore)
	else:
		CheckMate = False
		InCheck = None
		return (None,StaticEvaluation(board,CheckMate,curfunc))

def HandleAITurn():
	global curfunc,board,lastLegalPos,KINGSPOS,bestMove,maximScore,minimScore,MAXDEPTH
	depth = MAXDEPTH
	if curfunc == 0 and not CheckMate:
		bestMove = None
		alpha, beta = float('-inf'),float('inf')
		bMove, _ = GetAllPossibleMoves(curfunc,depth=depth)
		print(bMove,'BEST MOVE')
		try:
			lastLegalPos = bMove[0]
			MakeMove(*bMove,funcs[curfunc]);
			curfunc = not curfunc;
			AfterMath(*bMove[1],curfunc)
		except:
			print("NO MOVE")



def GetPieceCountScore():
	global pieceScore, piecesAvailable,pieceCount

	score = 0
	for each in list(pieceScore.keys()):
		try:
			score += (pieceCount[each.upper()]-piecesAvailable[each])*pieceScore[each]
		except:
			score += (pieceCount[each.upper()]*pieceScore[each]);
	return score


def StaticEvaluation(board,isInCheckMate,curfunc):
	## CUR FUNC 0 is BLACK
	global CheckMate,InCheck
	CheckMateScores = {0:-100,1:100}
	s = 0
	# if KingInCheck(*KINGSPOS[funcs[curfunc]], funcs[curfunc]):
	# 	s += CheckMateScores[curfunc]//3
	if isInCheckMate:
		CheckMate = False
		InCheck = None
		return CheckMateScores[curfunc]

	return GetPieceCountScore() + s

def MakeMove(pos, move,func):
	global piecesAvailable
	i,j = pos
	piece = copy.copy(board[i][j])
	board[i][j] = ''
	newI, newJ = move
	oldPiece=  copy.copy(board[newI][newJ])
	piecesAvailable[oldPiece] -=1
	board[newI][newJ] = piece;
	if piece.lower() == 'k':
		#print(newI,newJ,func)
		KINGSPOS[func] = (newI,newJ);
	#print(f'MOVED {piece,(i,j)} to {(newI,newJ)}')
	#DrawCheck((i,j),(255,255,255))
	#DrawCheck((i,j),(255,255,0))
	return oldPiece

def SaveOrigConfig():
	global PawnHistory, castlingRights,EnPassantMoves_
	config = {}
	config['pawnHistory'] = copy.deepcopy(PawnHistory)
	config['castlingRights'] = copy.deepcopy(castlingRights)
	config['EnPassantMoves_'] = copy.deepcopy(EnPassantMoves_)
	return config

def LoadConfig(config):
	global PawnHistory, castlingRights,EnPassantMoves_
	PawnHistory = config['pawnHistory']
	castlingRights = config['castlingRights']
	EnPassantMoves_= config['EnPassantMoves_'] 


def GetPieceStuff():
	p = {'P':1,"Q":50,"R":20,"N":10,"K":100,'B':10}
	pieceCount = {'P':8,"Q":1,"R":2,"N":2,"K":1,'B':2,'':20}
	for each in list(p.keys()):
		p[each.lower()] = p[each]*-1
		pieceCount[each.lower()] = pieceCount[each]
	return p, copy.copy(pieceCount),pieceCount

def GetKingsPos():
	global board,KINGSPOS
	for i in range(len(board)):
		for j in range(len(board[0])):
			if board[i][j].lower() == 'k':
				if str.islower(board[i][j]):
					KINGSPOS[str.islower] = (i,j)
				else:
					KINGSPOS[str.isupper] = (i,j)

pieceinHand = 0
piece = None
curValidMoves = None
CheckMate = False
bestMove = None
players = {str.islower:'Black',str.isupper:'White'}
lastLegalPos = None
MOVEFUNCS = {'r':RookeMoves,'b':BishopMoves,'k':KingMoves,'n':KnightMoves,'p':PawnMoves,'q':QueenMoves}
funcs = {0:str.islower,1:str.isupper}
KINGSPOS = {str.islower:(0,4),str.isupper:(7,4)}                  ## CHANGE KINGS' POSITIONS FOR DEFAULT STARTING FEN; or write a function that does that for you.
castlingRights = {each:{'left':True,'right':True} for each in list(players.keys())}
castlingMoves_ = []
alpha = float('-inf')
beta = float('inf')
maximScore = float('-inf')
minimScore = float('inf')
pieceScore,piecesAvailable,pieceCount = GetPieceStuff()
MAXDEPTH = 2
InCheck = None
curfunc = 1
PawnHistory = {str.islower:{i:0 for i in range(8)},
			   str.isupper:{i:0 for i in range(8)}}			##FOR MEASURING CHANGE IN POSITION
fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR'
# fen = 'rnbqkbnr/pp1p2p1/2p2p2/7p/1QPP1P2/5K1N/PP2P1Pp/RNB2B2'
EnPassantMoves_ = []
# fen = '4k3/8/2QQ5/8/8/8/8/4K3'
imgs= loadPicsDict()
board = GetBoard()
parseFen(board,fen)
GetKingsPos()

while run:
	screen.fill((0,0,0))
	drawRects()
	if pieceinHand:
		drawCurValidMoves(curValidMoves);
		drawPieces(board,imgs)
		movePiece(imgs,piece)
	else:
		drawPieces(board,imgs)
	keys,run,piece = CheckEvent()
	if InCheck is not None:
		DrawCheck(InCheck)
	HandleAITurn()
	pieceCount = copy.copy(piecesAvailable)
	pygame.display.update()