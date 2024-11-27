#Main driver file which will handle user inputs and displaying current gameState object
#Piece and board assets taken from https://github.com/lichess-org/lila/tree/master/public/piece/cburnett (love u lichess)
import pygame as p
import engine
import numpy as np

p.init()
width=height=640 #dimensions of the chessboard
dim=8 #8x8 tiles on a chessboard ofc
sq_size=height//dim
max_fps=16 #for animations
images={}
info=p.display.Info()
screen_width,screen_height=info.current_w, info.current_h #getting the dimensions of user's screen
board_x,board_y=0.12*screen_width,0.08*screen_height #coordinates for the upper left corner of the chessboard on the screen

#Initialising a global dict of images and it'll be called exactly once since it is an expensive operation to load images in pygame

def loadImages():
    pieces=np.array(['wP','wR','wB','wK','wQ','wN','bP','bR','bB','bQ','bK','bN'])
    for piece in pieces:
        images[piece]=p.transform.scale(p.image.load("images/"+piece+".png"),(sq_size-10,sq_size-10))

#Main driver initalising and updating graphics:
def main():
    screen=p.display.set_mode((screen_width,screen_height*(0.93)),p.RESIZABLE)
    chessBoard=p.Surface((width,height))
    clock=p.time.Clock()
    screen.fill(p.Color(105,105,105))
    gs=engine.gameState()
    validMoves=gs.getValidMoves()
    moveMade=False #flag for when a move is made
    loadImages() #runs only once and loads the assets of the pieces and stuff
    running=True
    sqSelected=() #storing last click of the user
    playerClicks=[] #keep track of all player clicks
    while running:
        for e in p.event.get():
            if e.type==p.QUIT:
                running=False
            #mouse handlers:
            elif e.type==p.MOUSEBUTTONDOWN:
                l1=p.mouse.get_pos() #l1->location of the mouse with respect to the screen
                if (l1[0]>board_x and l1[0]<board_x+width and l1[1]>board_y and l1[1]<board_y+height): #checking of the mouse click was within the chessboard 
                    location=(l1[0]-board_x,l1[1]-board_y) #getting the coords of click relative to the chessBoard
                    col=int(location[0]//sq_size)
                    row=int(location[1]//sq_size)
                    if sqSelected==(row,col): #clicking the same square twice
                        sqSelected=() #deselect that piece
                        playerClicks=[]
                    else:
                        sqSelected=(row,col)
                        playerClicks.append(sqSelected) #storing the 1st and 2nd click
                    if len(playerClicks)==2:
                        move=engine.Move(playerClicks[0],playerClicks[1],gs.board) 
                        if move in validMoves:
                            gs.makeMove(move)
                            moveMade=True
                            sqSelected=() 
                            playerClicks=[] 
                        else:
                            playerClicks=[sqSelected] 
            #key handlers:                 
            elif e.type==p.KEYDOWN:
                if e.key==p.K_u: #undo when 'u' is pressed
                    gs.undoMove()
                    moveMade=True
            if moveMade:
                validMoves=gs.getValidMoves()
                moveMade=False
            drawGS(screen,gs,chessBoard)
            clock.tick(max_fps)
            p.display.flip()

#Draws all the graphics for the current gamestate->           
def drawGS(screen,gs,chessBoard):
    drawBoard(chessBoard)   
    drawPieces(chessBoard,gs.board)
    screen.blit(chessBoard,(board_x,board_y)) #add in piece highlinting or move suggestions later idk

def drawBoard(chessBoard):
    colors=[p.Color("white"),p.Color("pink")]
    for r in range(dim):
        for c in range(dim):
            color=colors[(r+c)%2]
            p.draw.rect(chessBoard,(color),(c*sq_size,r*sq_size,sq_size,sq_size))

def drawPieces(chessBoard,board):
    for r in range(dim):
        for c in range(dim):
            piece=board[r][c]
            if piece != "..":
                chessBoard.blit(images[piece],p.Rect(c*sq_size,r*sq_size,sq_size,sq_size))

if __name__=="__main__":
    main()
main()