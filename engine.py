#This class is used for storing all info about gameState. Also will determine valid moves and keep a movement log (somehow)
import numpy as np
class gameState():
    def __init__(self):
        #8x8 2d numpy array storing the board. Each element-> tile on chess board
        self.board=np.array([["bR","bN","bB","bQ","bK","bB","bN","bR"],
                             ["bP","bP","bP","bP","bP","bP","bP","bP"],
                             ["..","..","..","..","..","..","..",".."],
                             ["..","..","..","..","..","..","..",".."],
                             ["..","..","..","..","..","..","..",".."],
                             ["..","..","..","..","..","..","..",".."],
                             ["wP","wP","wP","wP","wP","wP","wP","wP"],
                             ["wR","wN","wB","wQ","wK","wB","wN","wR"]])
        self.whiteToMove=True
        self.moveLog=[]
        self.moveFunctions={'P':self.getPawnMoves,'R':self.getRookMoves,'N':self.getKnightMoves,'B':self.getBishopMoves,'K':self.getKingMoves,'Q':self.getQueenMoves}
        self.blackKingLocation=(0,4)
        self.whiteKingLocation=(7,4)
        self.inCheck=False
        self.pins=[]
        self.checks=[]
        self.checkmate=False
        self.stalemate=False
   
    def makeMove(self,move):  #takes moves and just executes it (wont work for casling and en peassant)
        self.board[move.startRow][move.startCol]=".."
        self.board[move.endRow][move.endCol]=move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove=not self.whiteToMove
        #updating the kings location:
        self.whiteKingLocation= (move.endRow,move.endCol) if move.pieceMoved=='wK' else self.whiteKingLocation
        self.blackKingLocation= (move.endRow,move.endCol) if move.pieceMoved=='bK' else self.blackKingLocation
        
    def undoMove(self): #for undoing a move
        if len(self.moveLog)!=0:
            move=self.moveLog.pop()
            self.board[move.startRow][move.startCol]=move.pieceMoved
            self.board[move.endRow][move.endCol]=move.pieceCaptured
            self.whiteToMove=not self.whiteToMove
        #update king's location if needed:
        self.whiteKingLocation= (move.startRow,move.startCol) if move.pieceMoved=='wK' else self.whiteKingLocation
        self.blackKingLocation= (move.startRow,move.startCol) if move.pieceMoved=='bK' else self.blackKingLocation
    
    def getPossibleMoves(self): #Gets all the possible moves in a position which the pieces can move without considering checks 
    #TLDR: generates all moves including king sacrifice
        moves=[]
        for r in range(len(self.board)): #number of rows
            for c in range(len(self.board[r])): #number of columns
                turn=self.board[r][c][0]
                if(turn=='w' and self.whiteToMove) or (turn =='b' and not self.whiteToMove):
                    piece=self.board[r][c][1]
                    self.moveFunctions[piece](r,c,moves) #calls the appropriate moves for each type of piece  
        return moves 
                 
    """
    There are 2 ways to get the valid moves: 
    
    1) Naive algorithm: This one is quite a bit slower than the advanced algorithm but easier to understand and implement:
        i) Generate all possible moves
        ii) For each move, make the actual move
        iii) Generate all the possible moves for the opponent now
        iv) For each of the opponent's moves, check if they attack your king
        v) If they do, that move for you is illegal and should be removed from the valid moves
        
    2) Advanced Algorithm:
        We check from the king's location, three things:
        i) If the king is in check
        ii) If a piece near the king is pinned
        iii) If the king is in a double check
        
    """
    
    #--------------- NAIVE METHOD- ALL DEPRECATED:--------------------
    def getValidMoves_NAIVE(self): # Gets all the playable valid moves in a position (no king sacrifice)
        moves=self.getPossibleMoves()
        for i in range(len(moves)-1,-1,-1):
            self.makeMove(moves[i])
            self.whiteToMove=not self.whiteToMove
            if self.playerinCheck():
                moves.remove(moves[i])
            self.whiteToMove=not self.whiteToMove
            self.undoMove()
        if len(moves)==0: #either checkmate or stalemate now
            if self.inCheck():
                self.checkmate=True
            else:   
                self.stalemate=False
        else:
            self.stalemate=False
            self.checkmate=False
        return moves
    #-------------------- NAIVE METHOD ENDS --------------------------
    
    #Advanced Algorithm:
    def getValidMoves(self): # Gets all the playable valid moves in a position (no king sacrifice)
         getValidMoves_NAIVE(self)
        # moves=[]
        # self.inCheck, self.pins, self.checks=self.checkForPinsAndChecks()
        # kingRow=self.whiteKingLocation[0] if self.whiteToMove else self.blackKingLocation[0]
        # kingCol=self.blackKingLocation[1] if self.whiteToMove else self.blackKingLocation[1]
        # if self.playerinCheck:
        #     if len(self.checks)==1: #One check->Block king or move it
        #         moves=self.getPossibleMoves()
        #         check=self.checks[0]
        #         checkRow=check[0]
        #         checkCol=check[1]
        #         pieceChecking=self.board[checkRow][checkCol]
        #         validTiles=[] #Represents the squares that the pieces can move to
        #         if pieceChecking[1]=='N':
        #             validTiles=[(checkRow,checkCol)]
        #         else:
        #             for i in range(1,8):
        #                 validTile=(kingRow+check[2]*i,kingCol+check[3]*i)
        #                 validTiles.append(validTile)
        #                 if validTile[0]==checkRow and validTile[1]==checkCol:
        #                     break
        #         #Get rid of any moves that dont block check or move king:
        #         for i in range(len(moves)-1,-1,-1):
        #             if moves[i].pieceMoved[1]!='K':
        #                 if not (moves[i].endRow, moves[i].endCol) in validTiles:
        #                     moves.remove(moves[i])
        #     else: #double check->king has to move:
        #         self.getKingMoves(kingRow,kingCol,moves)
        # else: #not in check 
        #     moves=self.getPossibleMoves()
        # return moves
            
    #determining if the player is in check:
    def playerinCheck(self):
        if self.whiteToMove:
            return self.tileAttacked(self.whiteKingLocation[0],self.whiteKingLocation[1])
        else:
            return self.tileAttacked(self.blackKingLocation[0],self.blackKingLocation[1])
    
    #determining if a specific tile is under attack:
    def tileAttacked(self,r,c):
        self.whiteToMove=not self.whiteToMove  #switching to opponents moves
        oppMoves=self.getPossibleMoves()
        self.whiteToMove=not self.whiteToMove #swtich it back after getting their moves
        for move in oppMoves:
            if move.endRow==r and move.endCol==c:
                return True
    
    def checkforPinsAndChecks(self):
        pins=[] #contains the tile in which the allied piece which is pinned and 
        checks=[] #tiles from which enemy is checking our king
        inCheck=False
        enemyColor="b" if self.whiteToMove else "w"
        allyColor="w" if self.whiteToMove else "b"
        startRow=self.whiteKingLocation[0] if self.whiteToMove else self.blackKingLocation[0]
        startCol=self.whiteKingLocation[1] if self.whiteToMove else self.blackKingLocation[1]
        
        #checking outward from kings for pins and checks, keeping track of pins:
        directions=((-1,0),(0,-1),(1,0),(0,1),(-1,-1),(-1,1),(1,-1),(1,1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin=() #reset possible pins
            for i in range(1,8):
                endRow=startRow+d[0]*i
                endCol=startCol+d[1]*i
                if 0<=endRow<8 and 0<=endCol<8:
                    endPiece=self.board[endRow][endCol]
                    if endPiece[0]==allyColor:
                        if possiblePin==(): #this piece could be pinned
                            possiblePin=(endRow,endCol,d[0],d[1])
                        else: #this will happen if there is ANOTHER allied piece in the same direction, hence removing the possibilty of a pin
                            break
                    elif endPiece[0]==enemyColor:
                        type=endPiece[1]
                        #There are 5 possibilities:
                        #1) 1 square diagonally from pawn
                        #2) straight from rook
                        #3) diagonally from bishop
                        #4) 1 tile from king in any direction
                        #5) straight or diagonal from Queen
                        if  (0<=j<4 and type=='R') or \
                            (4<=j<8 and type=='B') or \
                            (i==1 and type=='P' and ((enemyColor=='w' and 6<=j<=7) or (enemyColor=='b' and 4<=j<=5))) or \
                            (type=='Q') or (i==1 and type=='K'):
                                if possiblePin==():
                                    inCheck=True
                                    checks.append((endRow,endCol,d[0],d[1]))
                                    break
                                else:
                                    pins.append(possiblePin)
                                    break
                else:
                    break
        #checking for knight checks: 
        knightMoves=((-2,-1),(-2,1),(2,-1),(2,1),(-1,-2),(-1,2),(1,-2),(1,2))
        for m in knightMoves:
            endRow, endCol= startRow+m[0], startCol+m[1]
            if 0<=endRow<8 and 0<=endCol<8:
                endPiece=self.board[endRow][endCol]
                if endPiece[0]==enemyColor and endPiece=='N':
                    inCheck=True
                    checks.append((endRow,endCol,m[0],m[1]))
        return inCheck, pins, checks
                                    
    """
    IMPORTANT: All the move generating functions for different pieces have been made with a 8x8 chessboard in mind. If chessboard
    is changed, all the functions will have to be changed accordingly.
    All the moves for the pieces will be checked for, if they are pinned that move will not be included in the possible moves. So we deal with pinned pieces in the moves generation itself.
    """
    def getPawnMoves(self,r,c,moves):
        piecePinned=False
        pinDirection=()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0]==r and self.pins[i][1]==c:
                piecePinned=True
                pinDirection=(self.pins[i][2],self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
            
        if self.whiteToMove: #WHITE PAWN MOVES
            if self.board[r-1][c]=="..": #checking if tile in front is empty
                moves.append(Move((r,c),(r-1,c),self.board))
                if r==6 and self.board[r-2][c]=="..": #first pawn move can be two squares as well
                    moves.append(Move((r,c),(r-2,c),self.board))
            if c>0 and self.board[r-1][c-1][0]=='b': #checking the left capture of all white pawns except leftmost pawn ofc
                moves.append(Move((r,c),(r-1,c-1),self.board))
            if c<7 and self.board[r-1][c+1][0]=='b': #checking the right capture of all white pawns except rightmost pawn ofc
                moves.append(Move((r,c),(r-1,c+1),self.board))
                
        else: #FOR BLACK PAWNS
            if self.board[r+1][c]=="..": #checking if tile in front is empty
                moves.append(Move((r,c),(r+1,c),self.board))
                if r==1 and self.board[r+2][c]=="..": #first pawn move can be two squares as well
                    moves.append(Move((r,c),(r+2,c),self.board))
            if c>0 and self.board[r+1][c-1][0]=='w': #checking the left capture of all black pawns except leftmost pawn ofc
                moves.append(Move((r,c),(r+1,c-1),self.board))
            if c<7 and self.board[r+1][c+1][0]=='w': #checking the right capture of all black pawns except rightmost pawn ofc
                moves.append(Move((r,c),(r+1,c+1),self.board))
    
    def getRookMoves(self,r,c,moves):
        piecePinned=False
        pinDirection=()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0]==r and self.pins[i][1]==c:
                piecePinned=True
                pinDirection=(self.pins[i][2],self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
            
        directions=[(0,-1),(0,1),(-1,0),(1,0)] #iterating through the 4 directions the rook can move in (LEFT, RIGHT, UP, DOWN)
        for d in directions:
            for i in range(1,8):
                endRow, endCol=r+d[0]*i, c+d[1]*i
                if 0<=endRow<8 and 0<=endCol<8:
                    if(self.board[endRow][endCol]==".."): # if that space is empty
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                    elif(self.board[endRow][endCol][0]!=self.board[r][c][0]):
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                        break
                    else:
                        break
                else:
                    break
                
    def getBishopMoves(self,r,c,moves):
        piecePinned=False
        pinDirection=()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0]==r and self.pins[i][1]==c:
                piecePinned=True
                pinDirection=(self.pins[i][2],self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
            
        directions=[(-1,-1),(1,1),(-1,1),(1,-1)] #iterating through the 4 directions the rook can move in (LEFT, RIGHT, UP, DOWN)
        for d in directions:
            for i in range(1,8):
                endRow, endCol=r+d[0]*i, c+d[1]*i
                if 0<=endRow<8 and 0<=endCol<8:
                    if(self.board[endRow][endCol]==".."): # if that space is empty
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                    elif(self.board[endRow][endCol][0]!=self.board[r][c][0]):
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                        break
                    else:
                        break
                else:
                    break
    
    def getKnightMoves(self,r,c,moves):
        piecePinned=False
        pinDirection=()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0]==r and self.pins[i][1]==c:
                piecePinned=True
                pinDirection=(self.pins[i][2],self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
            
        tiles=[(-2,-1),(-2,1),(-1,2),(-1,-2),(1,-2,),(1,2),(2,-1),(2,1)]
        for t in tiles:
            endRow, endCol= r+t[0], c+ t[1]
            if 0<=endRow<8 and 0<=endCol<8:
                if self.board[endRow][endCol][0]!=self.board[r][c][0]:
                    moves.append(Move((r,c),(endRow,endCol),self.board))
    
    def getKingMoves(self,r,c,moves):
        tiles=[(0,-1),(0,1),(1,0),(-1,0),(1,1),(1,-1),(-1,-1),(-1,1)]
        for t in tiles:
            endRow, endCol= r+t[0], c+ t[1]
            if 0<=endRow<8 and 0<=endCol<8:
                if self.board[endRow][endCol][0]!=self.board[r][c][0]:
                    moves.append(Move((r,c),(endRow,endCol),self.board))
    
    def getQueenMoves(self,r,c,moves):
        piecePinned=False
        pinDirection=()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0]==r and self.pins[i][1]==c:
                piecePinned=True
                pinDirection=(self.pins[i][2],self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
             
        self.getBishopMoves(r,c,moves)
        self.getRookMoves(r,c,moves)          

class Move():
    def __init__(self,startTile,endTile,board):
        self.startRow=startTile[0]
        self.startCol=startTile[1]
        self.endRow=endTile[0]
        self.endCol=endTile[1]
        self.pieceMoved=board[self.startRow][self.startCol]
        self.pieceCaptured=board[self.endRow][self.endCol] 
        self.moveID=self.startRow*1000+self.startCol*100+self.endRow*10+self.endCol
    
    def __eq__(self, other):
        if(isinstance(other,Move)):
            return self.moveID==other.moveID
        
    def getChessNotation(self):
        rows="87654321"
        cols="abcdefgh"
        piece_symbol="" if self.pieceMoved in ["wP","bP"] else self.pieceMoved[1]
        capture = 'x' if self.pieceCaptured!=".." else ""
        s_notation=cols[self.startCol]+rows[self.startRow]
        e_notation=cols[self.endCol]+rows[self.endRow]
        if piece_symbol=="":
            s_notation=cols[self.startCol] if capture else ""
        return f"{piece_symbol}{s_notation}{capture}{e_notation}"