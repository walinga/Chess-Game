import sys

# Global Constants:
Pval = 1
Nval = 3
Bval = 3.2
Rval = 5
Qval = 9
Kval = 100

class Piece:
    piecelist = []
    colour = ""
    name = ""
    picture = ""
    value = 0
    
    # For Kings only
    cancastleshort = True
    cancastlelong = True

    def loop(self):
        self.piecelist = []
        for num in range(64):
            if boardlist[num] == id(self):
                self.piecelist.append(num)


class boardState:
    prevBoard = range(64)
    prevState = False
    enPassant = False

curState = boardState()


# White pieces:
wk = Piece()
wk.name = "king"
wk.picture = "WhiteKing.png"

wq = Piece()
wq.name = "queen"
wq.picture = "WhiteQueen.png"

wb = Piece()
wb.name = "bishop"
wb.picture = "WhiteBishop.png"

wn = Piece()
wn.name = "knight"
wn.picture = "WhiteKnight.png"

wr = Piece()
wr.name = "rook"
wr.picture = "WhiteRook.png"

wp = Piece()
wp.name = "pawn"
wp.picture = "WhitePawn.png"

whitepieces = [wk, wq, wb, wn, wr, wp]
for y in whitepieces:
    y.colour = 'white'

# Black pieces:
bk = Piece()
bk.name = "king"
bk.picture = "BlackKing.png"

bq = Piece()
bq.name = "queen"
bq.picture = "BlackQueen.png"

bb = Piece()
bb.name = "bishop"
bb.picture = "BlackBishop.png"

bn = Piece()
bn.name = "knight"
bn.picture = "BlackKnight.png"

br = Piece()
br.name = "rook"
br.picture = "BlackRook.png"

bp = Piece()
bp.name = "pawn"
bp.picture = "BlackPawn.png"

blackpieces = [bk, bq, bb, bn, br, bp]
for y in blackpieces:
    y.colour = 'black'

# Misc.
allpieces = whitepieces + blackpieces
boardlist = range(64)


# Clears the board of all pieces
def emptyboard():
    for i in range(64):
        boardlist[i] = 0


# Adds the positions of all pieces on the board to their respective objects
def updatepieces():
    for y in allpieces:
            y.loop()


# Reverts the board to the starting position
def resetboard():
    emptyboard()
    boardlist[4] = id(wk) ## Idea is to use this approach for the entire boardlist, even in MovePiece
    boardlist[3] = id(wq) ## Remove piecelist from Piece class eventually ... orrrr not
    boardlist[2], boardlist[5] = id(wb), id(wb)
    boardlist[1], boardlist[6] = id(wn), id(wn)
    boardlist[0], boardlist[7] = id(wr), id(wr)
    for i in range(8, 16):
        boardlist[i] = id(wp)
    boardlist[60] = id(bk)
    boardlist[59] = id(bq)
    boardlist[61], boardlist[58] = id(bb), id(bb)
    boardlist[62], boardlist[57] = id(bn), id(bn)
    boardlist[63], boardlist[56] = id(br), id(br)
    for i in range(48, 56):
        boardlist[i] = id(bp)
    curState.prevBoard = boardlist
    curState.prevState = False
    updatepieces()

resetboard()


# Resets the board and initializes some values
def resetgame():
    resetboard()
    wk.cancastleshort = True
    wk.cancastlelong = True
    bk.cancastleshort = True
    bk.cancastllong = True


# Converts sqr to a number for ease of calculation (sqr is a string coord)
def coordtonum(sqr):
    j = ord(sqr[0]) - 97
    return 8 * (int(sqr[1]) - 1) + j


# Converts num back to a coordinate
def numtocoord(num):
    q = num % 8
    n = (num / 8) + 1
    m = chr(q + 97)
    return m + str(n)


# Returns the piece on square num
def pieceatsqr(num):
    s = boardlist[num]
    if s == 0:
        return False
    for y in allpieces:
        if id(y) == s:
            return y
    return False


# Changes the value of the piece on start to end
def ChangeVar(start, end):
    j = pieceatsqr(start)
    boardlist[start] = 0
    boardlist[end] = id(j)


# Checks if a pawn has made it to the eighth/first rank
def pawnPromoted(end):
    s = numtocoord(end)
    pce = pieceatsqr(end)
    if s[1] == '8' and pce == wp:
        return True
    if s[1] == '1' and pce == bp:
        return True
    return False


# Moves the piece on start to end
def MovePiece(start, end):
    j = pieceatsqr(start)
    m = pieceatsqr(end)

    tempboardlist = range(64)
    for i in range(64):
        tempboardlist[i] = boardlist[i]

    tempState = boardState()
    tempState.prevBoard = curState.prevBoard
    tempState.prevState = curState.prevState
    tempState.enPassant = curState.enPassant

    curState.prevState = tempState
    curState.prevBoard = tempboardlist
    
    if not j or (m and j.colour == m.colour):
        return 'Invalid move'
    else:
        ChangeVar(start, end)

    # Move the rook if the king castled
    if j.name == 'king' and (end - start) == 2:
        ChangeVar(end + 1, start + 1)
    elif j.name == 'king' and (start - end) == 2:
        ChangeVar(end - 2, start - 1)

    # Turn a promoted pawn into a queen
    if pawnPromoted(end):
        if j.colour == 'white':
            boardlist[end] = id(wq)
        if j.colour == 'black':
            boardlist[end] = id(bq)

    curState.enPassant = False
    # Checks if En Passant is valid (work in progress)
    if j.name == 'pawn':
        s, e = start, end
        if abs(s-e) == 16:
            if j.colour == 'black':
                curState.enPassant = e+8
            if j.colour == 'white':
                curState.enPassant = e-8
        if abs(s-e) == 7 or abs(s-e) == 9:
            if not m:
                if j.colour == 'white':
                    boardlist[e-8] = 0
                elif j.colour == 'black':
                    boardlist[e+8] = 0

    updatepieces()


# Checks if each side can still castle
def updateCastlingRights():
    if boardlist[4] != id(wk):
        wk.cancastleshort, wk.cancastlelong = False, False
    if boardlist[60] != id(bk):
        bk.cancastlshort, bk.cancastlelong = False, False
    if boardlist[0] != id(wr):
        wk.cancastlelong = False
    if boardlist[56] != id(br):
        bk.cancastlelong = False
    if boardlist[7] != id(wr):
        wk.cancastleshort = False
    if boardlist[63] != id(br):
        bk.cancastleshort = False


# Undoes the previous move made
def UndoMove():
    if curState.prevState == False:
        return False

    tempboardlist = curState.prevBoard

    tempState = boardState()
    tempState = curState.prevState

    curState.prevBoard = tempState.prevBoard
    curState.prevState = tempState.prevState
    curState.enPassant = tempState.enPassant
    
    for i in range(64):
        boardlist[i] = tempboardlist[i]

    updatepieces()

    
#helper
def rookMovement(i, colour):
    p = []
    x = i - 8
    while x >= 0:
        if boardlist[x] != 0:
            if (pieceatsqr(x)).colour != colour:
                p.append(x)
            break
        p.append(x)
        x -= 8
    x = i + 8
    while x < 64:
        if boardlist[x] != 0:
            if (pieceatsqr(x)).colour != colour:
                   p.append(x)
            break
        p.append(x)
        x += 8
    x = i
    while x % 8 > 0:
        if boardlist[x-1] != 0:
            if (pieceatsqr(x-1)).colour != colour:
                p.append(x -1)
            break
        p.append(x - 1)
        x -= 1
    x = i + 1
    while x % 8 > 0:
        if boardlist[x] != 0:
            if (pieceatsqr(x)).colour != colour:
                p.append(x)
            break
        p.append(x)
        x += 1
    return p

#helper
def bishopMovement(i, colour):
    p =[]
    x = i - 9
    while x % 8 < 7 and x > 0:
        if boardlist[x] != 0:
            if (pieceatsqr(x)).colour != colour:
                p.append(x)
            break
        p.append(x)
        x -= 9
    x = i + 9
    while x % 8 > 0 and x < 64:
        if boardlist[x] != 0:
            if (pieceatsqr(x)).colour != colour:
                p.append(x)
            break
        p.append(x)
        x += 9
    x = i - 7
    while x % 8 > 0 and x > 0:
        if boardlist[x] != 0:
            if (pieceatsqr(x)).colour != colour:
                p.append(x)
            break
        p.append(x)
        x -= 7
    x = i + 7
    while x % 8 < 7 and x < 64:
        if boardlist[x] != 0:
            if (pieceatsqr(x)).colour != colour:
                p.append(x)
            break
        p.append(x)
        x += 7
    return p

#helper
def kingMovement(i):
    sqr = numtocoord(i)
    m = sqr[0]
    n = sqr[1]
    p = []
    if m != 'a':
        p.append(i - 1)
        if n != '1':
            p.append(i - 9)
        if n != '8':
            p.append(i + 7)
    if m != 'h':
        p.append(i + 1)
        if n != '1':
            p.append(i - 7)
        if n != '8':
            p.append(i + 9)
    if n != '1':
        p.append(i - 8)
    if n != '8':
        p.append(i + 8)
    return p

#helper
def knightMovement(i):
    sqr = numtocoord(i)
    m = sqr[0]
    n = sqr[1]
    p = []
    if m != 'a' and m != 'b':
        if n != '1':
            p.append(i - 10)
        if n != '8':
            p.append(i + 6)
    if n != '1' and n != '2':
        if m != 'a':
            p.append(i - 17)
        if m != 'h':
            p.append(i - 15)
    if n != '7' and n != '8':
        if m != 'a':
            p.append(i + 15)
        if m != 'h':
            p.append(i + 17)
    if m != 'g' and m != 'h':
        if n != '1':
            p.append(i - 6)
        if n != '8':
            p.append(i + 10)
    return p

# Returns a list of squares that are valid moves for the piece on num
def PieceMovementHelp(num):
    i = num
    j = pieceatsqr(num)
    sqr = numtocoord(num)
    m = sqr[0]
    n = sqr[1]
    p = []
    q = []

    if not j:
        return 'Invalid start square'

    # King Movement
    elif j.name == 'king':
        p = kingMovement(i)
        # Castling
        if j.cancastleshort and i <= 61:
            a = pieceatsqr(i + 1)
            b = pieceatsqr(i + 2)
            if not a and not b:
                p.append(i + 2)
        if j.cancastlelong and i >= 3:
            a = pieceatsqr(i - 1)
            b = pieceatsqr(i - 2)
            c = pieceatsqr(i - 3)
            if not(a) and not(b) and not(c):
                p.append(i - 2)    

    # Pawn Movement
    elif j.name == 'pawn':
        ep = curState.enPassant
        if j.colour == 'white':
            u = 1
            startrank = '2'
            endrank = '8'
            leftfile = 'a'
            rightfile = 'h'
        elif j.colour == 'black':
            u = -1
            startrank = '7'
            endrank = '1'
            leftfile = 'h'
            rightfile = 'a'
        # u is used to signify direction of pawn movement
        if n != endrank:
            s = pieceatsqr(i + 8*u)
            if not(s):
                q.append(i + 8*u)
            z = pieceatsqr(i + 7*u)
            if m != leftfile:
                if (z and z.colour != j.colour) or ep == i + 7*u:
                    q.append(i + 7*u)
            if i <= 54:
                y = pieceatsqr(i + 9*u)
                if m != rightfile:
                    if (y and y.colour != j.colour) or ep == i + 9*u:
                        q.append(i + 9*u)
        if n == startrank:
            t = pieceatsqr(i + 16*u)
            if not(s) and not(t):
                q.append(i + 16*u)
        
    # Knight Movement
    elif j.name == 'knight':
        p = knightMovement(i)

    # Rook Movement
    elif j.name == 'rook':
        q = rookMovement(i, j.colour)

    # Bishop Movement
    elif j.name == 'bishop':
        q = bishopMovement(i, j.colour)

    # Queen Movement
    elif j.name == 'queen':
        q = rookMovement(i, j.colour) + bishopMovement(i, j.colour)

    # Make sure we don't have friendly fire (from the king or knight)
    for x in p:
        if boardlist[x] != 0 and (pieceatsqr(x)).colour == j.colour:
            continue
        else:
            q.append(x)

    return q


# Danger Functions
def PawnDanger(i, colour):
    if colour == 'white':
        if i <= 47 and i % 8 != 7 and boardlist[i+9] == id(bp):
            return True
        if i <= 47 and i % 8 != 0 and boardlist[i+7] == id(bp):
            return True
    elif colour == 'black':
        if i >= 16 and i % 8 != 0 and boardlist[i-9] == id(wp):
            return True
        if i >= 16 and i % 8 != 7 and boardlist[i-7] == id(wp):
            return True

def KnightDanger(sqr, colour):
    if colour == 'white':
        knight = id(bn)
    else:
        knight = id(wn)
    for y in knightMovement(sqr):
        if boardlist[y] == knight:
            return True

def KingDanger(sqr, colour):
    if colour == 'white':
        king = id(bk)
    else:
        king = id(wk)
    for y in kingMovement(sqr):
        if boardlist[y] == king:
            return True

def BigPieceDanger(sqr, colour):
    if colour == 'white':
        rook, bishop, queen = id(br), id(bb), id(bq)
    else:
        rook, bishop, queen = id(wr), id(wb), id(wq)
    for y in rookMovement(sqr, colour):
        if boardlist[y] == rook or boardlist[y] == queen:
            return True
    for y in bishopMovement(sqr, colour):
        if boardlist[y] == bishop or boardlist[y] == queen:
            return True

# Determines whether a move can get you killed
def isSafe(sqr, colour):
    if PawnDanger(sqr, colour):
        return False
    if KnightDanger(sqr, colour):
        return False
    if KingDanger(sqr, colour):
        return False
    if BigPieceDanger(sqr, colour):
        return False
    return True


# determines whether the 'colour' king is in check
def isInCheck(colour):
    if colour == 'white':
        kingsqr = wk.piecelist[0]
    if colour == 'black':
        kingsqr = bk.piecelist[0]
    return not(isSafe(kingsqr, colour))


# determines whether colour is in checkmate, stalemate or neither
def isMated(colour):
    if colour == 'white':
        pieces = whitepieces
    elif colour == 'black':
        pieces = blackpieces
    for y in pieces:
        for i in y.piecelist:
            if len(PieceMovement(i)) > 0:
                return False
    if isInCheck(colour):
        return 'checkmate'
    return 'stalemate'


# Determines whether the game is a draw by insufficient material
def isDraw():
    if len(wp.piecelist) > 0 or len(bp.piecelist) > 0:
        return False
    elif len(wq.piecelist) > 0 or len(bq.piecelist) > 0:
        return False
    elif len(wr.piecelist) > 0 or len(br.piecelist) > 0:
        return False
    elif len(wb.piecelist) > 1 or len(bb.piecelist) > 1:
        return False
    elif len(wb.piecelist) > 0 and len(wn.piecelist) > 0:
        return False
    elif len(bb.piecelist) > 0 and len(bn.piecelist) > 0:
        return False
    return True


# (see PieceMovementHelper)
def PieceMovement(sqr):
    j = pieceatsqr(sqr)
    q = []
    for move in PieceMovementHelp(sqr):
        # Cannot castle out of check
        if isInCheck(j.colour) and j.name == 'king' and (move == sqr+2 or move  == sqr-2):
            continue
        state = MovePiece(sqr, move)
        if not isInCheck(j.colour):
            q.append(move)
        UndoMove()
    return q


# Slap some values on errthing
for y in allpieces:
    if y.name == 'pawn':
        y.value = Pval
    elif y.name == 'knight':
        y.value = Nval
    elif y.name == 'bishop':
        y.value = Bval
    elif y.name == 'rook':
        y.value = Rval
    elif y.name == 'queen':
        y.value = Qval


# Gives a numerical value for how good colour's position is
def EvaluatePosition(colour):
    evalu = 0

    if colour == 'white':
        opp = 'black'
        p, n, b, r, q, k = wp, wn, wb, wr, wq, wk
        badpawns = bp
        u = 1
        
    elif colour == 'black':
        opp = 'white'
        p, n, b, r, q, k = bp, bn, bb, br, bq, bk
        badpawns = wp
        u = -1

    evalu += Pval * len(p.piecelist)
    evalu += Nval * len(n.piecelist)
    evalu += Bval * len(b.piecelist)
    evalu += Rval * len(r.piecelist)
    evalu += Qval * len(q.piecelist)

    for y in p.piecelist:
        # Add incentives for centred pawns
        if y == 27 or y == 28 or y == 35 or y == 36:
            evalu += 0.4

        # Add incentives for making use of outposts for knights
        if y > 24 and y < 48:
            if boardlist[y+9*u] == id(n) or boardlist[y+7*u] == id(n):
                evalu += 0.35

        # Passed pawns are GREAT
        if colour == 'white' and y > 32 and pieceatsqr(y+8) == 0:
            if y <= 54 and boardlist[y+9] != id(bp) and boardlist[y+7] != id(bp):
                evalu += y/8 - 3
        if colour == 'black' and y < 31 and pieceatsqr(y-8) == 0:
            if y >= 9 and boardlist[y-9] != id(wp) and boardlist[y-7] != id(wp):
                evalu += 4 - y/8

        # Doubled pawns are BAD
        if y < 56 and boardlist[y + 8] == id(p):
            evalu -= 0.5

        # Don't let pawns drop off like flies
        if not(isSafe(y, colour)) and isSafe(y, opp):
            evalu -= 0.4

    for y in n.piecelist:
        # Add incentives for development / attacking w knights
        if y == 18 or y == 21 or y == 42 or y == 45:
            evalu += 0.3
        # Don't hang your knights
        if not(isSafe(y, colour)):
            evalu -= 1.2

    for y in b.piecelist:
        # Fianchetto
        if colour == 'white' and (y == 9 or y == 14):
            evalu += 0.35
        if colour == 'black' and (y == 49 or y == 54):
            evalu += 0.35
        # Don't hang your bishops
        if not(isSafe(y, colour)):
            evalu -= 1.3

    for y in r.piecelist:
        f = y % 8
        # Centralize rooks
        if f == 3 or f == 4:
            evalu += 0.25
        # Rooks behind passed pawns or on open files
        for x in [f+8, f+16, f+24, f+32, f+40, f+48, f+56]:
            if boardlist[x] == id(p):
                evalu -= 0.5
        # Make sure you don't make a ROOKie mistake
        if not(isSafe(y, colour)):
            evalu -= 2.1

    # Add incentives for castling
    hs = k.piecelist[0]
    if hs == 2 or hs == 6 or hs == 57 or hs == 62:
        evalu += 0.7

    # Subtract brownie points for pieces attacked by pawns
    for i in badpawns.piecelist:
        if i <= 54 and i >= 9:
            j = pieceatsqr(i - 9*u)
            if (j and j.colour == colour):
                evalu -= 0.6
        if i <= 55 and i >= 7:
            m = pieceatsqr(i - 7*u)
            if (m and m.colour == colour):
                evalu -= 0.6

    # Make sure bae is safe
    for y in q.piecelist:
        if not(isSafe(y, colour)):
           evalu -= 4.2

    # Try to corner the king
    kingpos = k.piecelist[0]
    kingCanMove = False
    rekt = False
    if not isSafe(kingpos, colour):
        rekt = True
        evalu -= 0.5
    for y in kingMovement(kingpos):
        if isSafe(y, colour):
            kingCanMove = True
    if not(kingCanMove) and rekt:
        if isMated(colour) == 'checkmate':
            evalu -= Kval

    return evalu


class Position:
    evaluation = 0
    movestart = 0
    moveend = 0
    

# Returns the "best" move for colour
def FindBest(colour, first):
    if colour == 'white':
        pieces = whitepieces
        opp = 'black'
    elif colour == 'black':
        pieces = blackpieces
        opp = 'white'

    bestsofar = Position()
    bestsofar.evaluation = -1000

    for p in pieces:
        for start in p.piecelist:
            moveslist = PieceMovement(start)
            for end in moveslist:
                cur = Position()
                cur.movestart = start
                cur.moveend = end
                i = pieceatsqr(end)
                j = pieceatsqr(start)

                state = MovePiece(start, end)
                if not(i) and not(isSafe(end, colour)) and isSafe(end, opp):
                        # Don't hang pieces unless you need to
                        cur.evaluation -= j.value
                cur.evaluation += EvaluatePosition(colour) - EvaluatePosition(opp)
                UndoMove()

                # No kamikaze allowed
                if i and i.value < j.value:
                    if not(isSafe(end, colour)):
                        # Unless absolutely necessary
                        cur.evaluation -= j.value

                if cur.evaluation >= bestsofar.evaluation:
                    nextbest = bestsofar
                    bestsofar = cur   

    if (first):
        print bestsofar.evaluation
        print bestsofar.movestart
        print bestsofar.moveend
        state = MovePiece(bestsofar.movestart, bestsofar.moveend)
        oppeval = FindBest(opp, 0)
        bestsofar.evaluation -= oppeval
        UndoMove()

        if nextbest.movestart != nextbest.moveend:
            print nextbest.movestart
            print nextbest.moveend
            print ":)"
            state = MovePiece(nextbest.movestart, nextbest.moveend)
            oppeval = FindBest(opp, 0)
            nextbest.evaluation -= oppeval
            UndoMove()

        if nextbest.evaluation > bestsofar.evaluation:
            return nextbest.movestart, nextbest.moveend
        return bestsofar.movestart, bestsofar.moveend
    else:
        print bestsofar.movestart
        print bestsofar.moveend
        return bestsofar.evaluation


# returns the file or rank that colour can use to attack the enemy king
def hasOpposition(kingpos, opp_pos):
    a, af, ar = kingpos, kingpos%8, kingpos/8
    b, bf, br = opp_pos, opp_pos%8, opp_pos/8
    if a == b + 2 or b == a + 2:
        f = b % 8
        return [f, f+8, f+16, f+24, f+32, f+40, f+48, f+56]
    elif a == b + 16 or b == a + 16 or (bf == 0 and a == b+17):
        r = (b / 8) * 8
        return [r, r+1, r+2, r+3, r+4, r+5, r+6, r+7]
    return False

# Opposes the enemy king (returns the square to move ur king to)
def getOpposition(kingpos, opp_pos):
    b = opp_pos
    for y in PieceMovement(kingpos):
        if y == b + 16 or b == y + 16 or (y/8 == b/8 and (y == b + 2 or b == y + 2)):
            return y
    for y in PieceMovement(kingpos):
        if y == b + 32 or b == y + 32 or (y/8 == b/8 and (y == b + 4 or b == y + 4)):
            return y
    for y in PieceMovement(kingpos):
        if y == b + 48 or b == y + 48 or (y/8 == b/8 and (y == b + 6 or b == y + 6)):
            return y
    return False


# Returns true if the position seems to be an endgame
def isEndgame():
    if len(wp.piecelist) == 0 or len(bp.piecelist) == 0:
        return True
    elif len(wq.piecelist) == 0 and len(bq.piecelist) == 0:
        return True
    elif len(wb.piecelist) == 0 and len(wn.piecelist) == 0:
        if len(bb.piecelist) == 0 and len(bn.piecelist) == 0:
            return True
    return False


# Returns a move to maybe get closer to destroying the player
def BasicMates(colour):
    if colour == 'white':
        opp = 'black'
        king = wk.piecelist
        rooks = wr.piecelist + wq.piecelist
        queen = wq.piecelist
        xking = bk.piecelist
    elif colour == 'black':
        opp = 'white'
        king = bk.piecelist
        rooks = br.piecelist + bq.piecelist
        queen = bq.piecelist
        xking = wk.piecelist
    kingpos = king[0]
    opp_pos = xking[0]
    
    # 2 Rook Checkmate
    if len(rooks) >= 2:
        kf = opp_pos % 8
        kr = opp_pos / 8
        for y in rooks:
            for x in PieceMovement(y):
                if not(isSafe(y, colour)) and isSafe(x, colour):
                    if y / 8 == kr + 1:
                        if x / 8 == kr+1 and x%8 != kf+2 and x%8 != kf-2:
                            return y, x
                    else:
                        return y, x
        if rooks[0] / 8 == kr + 1 or rooks[1] / 8 == kr + 1:
            for y in rooks:
                for x in PieceMovement(y):
                    if isSafe(x, colour) and x / 8 == kr:
                        if y / 8 != kr + 1 or (rooks[0]/8 == kr+1 and rooks[1]/8 == kr+1):
                            return y, x
        else:
            for y in rooks:
                for x in PieceMovement(y):
                    if isSafe(x, colour) and x / 8 == kr + 1:
                        return y, x

    # King and Queen Checkmate
    elif len(queen) > 0:
        k = hasOpposition(kingpos, opp_pos)
        if k:
            start = queen[0]
            for y in k:
                for end in PieceMovement(start):
                    if end == y and isSafe(y, colour):
                        return start, end
        elif opp_pos + 15 == kingpos or opp_pos + 17 == kingpos:
            for y in PieceMovement(queen[0]):
                if y == opp_pos + 8:
                    return queen[0], y
        elif opp_pos - 15 == kingpos or opp_pos - 17 == kingpos:
            for y in PieceMovement(queen[0]):
                if y == opp_pos - 8:
                    return queen[0], y
        elif opp_pos - 10 == kingpos or opp_pos + 6 == kingpos:
            for y in PieceMovement(queen[0]):
                if y == opp_pos - 1:
                    return queen[0], y
        elif opp_pos - 6 == kingpos or opp_pos + 10 == kingpos:
            for y in PieceMovement(queen[0]):
                if y == opp_pos + 1:
                    return queen[0], y
        else:
            v = getOpposition(kingpos, opp_pos)
            if v:
                return kingpos, v

    # King and Rook Checkmate
    elif len(rooks) == 1:
        k = hasOpposition(kingpos, opp_pos)
        kf = opp_pos % 8
        kr = opp_pos / 8
        if k:
            start = rooks[0]
            for y in k:
                for end in PieceMovement(start):
                    if end == y and isSafe(y, colour):
                        return start, end
        elif rooks[0] / 8 != kr + 1 or not(isSafe(rooks[0], colour)):
            start = rooks[0]
            for y in PieceMovement(start):
                if y/8 == kr+1 and isSafe(y, colour):
                    if start / 8 == kr + 1:
                        if y / 8 == kr+1 and y%8 != kf+2 and y%8 != kf-2:
                            return start, y
                    else:
                        return start, y
        elif kingpos / 8 > kr + 2:
            for y in PieceMovement(kingpos):
                if y == kingpos - 8:
                    return kingpos, kingpos - 8
        for y in PieceMovement(kingpos):
            if y / 8 == kr + 2:
                if opp_pos + 15 == y or opp_pos + 17 == y or opp_pos + 16 == y:
                    return kingpos, y
        for y in PieceMovement(kingpos):
            if y / 8 == kr + 2:
                if opp_pos + 14 == y or opp_pos + 18 == y:
                    return kingpos, y
                    
    return FindBest(colour, 1)
                

# Finds possible opening moves for black
def OpeningMoves(colour, movenum, randnum):
    #randnum = random.random()
    if movenum == 0 and colour == 'white':
        if randnum < 0.3:
            return 11, 27 #d4
        elif randnum < 0.6:
            return 12, 28 #e4
        elif randnum < 0.9:
            return 10, 26 #c4
        else:
            return 14, 22 #g3

    if movenum == 1 and colour == 'black':
        if boardlist[26] == id(wp):
            if randnum < 0.75:
                return 50, 34 #c5
            else:
                return 52, 36 #e5
        elif boardlist[27] == id(wp):
            if randnum < 0.25:
                return 62, 45 #Nf6
            else:
                return 51, 35 #d5
        elif boardlist[28] == id(wp):
            if randnum < 0.5:
                return 50, 34
            else:
                return 52, 36

    elif movenum == 2 and colour == 'black':
        if boardlist[27] == id(wp) and boardlist[26] == id(wp):
            if boardlist[35] == id(bp):
                if randnum < 0.5:
                    return 35, 26 #dxc4
                else:
                    return 52, 44 #e6
            elif boardlist[45] == id(bk):
                return 52, 44
        if boardlist[28] == id(wp) and boardlist[21] == id(wn):
            if boardlist[51] == id(bp) and boardlist[34] == id(bp):
                return 51, 43 #d6
            if boardlist[57] == id(bn) and boardlist[36] == id(bp):
                return 57, 42 #Nc6

    elif movenum >= 3 and colour == 'black':
        if boardlist[27] == id(wn) and boardlist[62] == id(bn):
            if boardlist[34] != id(bp) and boardlist[36] != id(bp):
                return 62, 45
        if boardlist[27] == id(wp) and boardlist[26] == id(wp):
            if boardlist[62] == id(bn):
                return 62, 45
    return FindBest(colour, 1)
    
