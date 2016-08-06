import sys
import PieceMovement as pm
from PieceMovement import PieceMovement, isSafe, isInCheck
from PieceMovement import wk, wq, wb, wn, wr, wp
from PieceMovement import bk, bq, bb, bn, br, bp
from PieceMovement import WHITE, BLACK
from PieceMovement import PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING

# Global Constants:
Pval = 1
Nval = 3
Bval = 3.2
Rval = 5
Qval = 9
Kval = 100

mateThreshold = Kval - 2*Qval - 2*Pval
maxPlies = 4
NOISY_LOGGING = False

# Assign a value to each piece
for y in pm.allpieces:
    if y.name == PAWN:
        y.value = Pval
    elif y.name == KNIGHT:
        y.value = Nval
    elif y.name == BISHOP:
        y.value = Bval
    elif y.name == ROOK:
        y.value = Rval
    elif y.name == QUEEN:
        y.value = Qval


def isSafeWithParams(sqr, colour, *args):
    if 'P' in args and pm.PawnDanger(sqr, colour):
        return False
    if 'N' in args and pm.KnightDanger(sqr, colour):
        return False
    if 'K' in args and pm.KingDanger(sqr, colour):
        return False
    if 'B' in args and pm.BigPieceDanger(sqr, colour):
        return False
    return True


# Gives a numerical value for how good colour's position is
def EvaluatePosition(colour):
    evalu = 0
    whiteMate, blackMate = pm.isMated(WHITE), pm.isMated(BLACK)
    BL = pm.boardlist

    # Check for draw
    if pm.isDraw():
        return 0
    if colour == BLACK and whiteMate == "STALEMATE":
        return 0
    if colour == WHITE and blackMate == "STALEMATE":
        return 0

    # Calculate material imbalances
    for y in pm.whitepieces:
        evalu += y.value * len(y.piecelist)
        for p in y.piecelist:
            # Make sure pieces are safe
            if y.name != PAWN and not(isSafe(p, WHITE)):
                evalu -= y.value/2 - 0.3
    for y in pm.blackpieces:
        evalu -= y.value * len(y.piecelist)
        #TODO: disregard king danger for isSafe here
        for p in y.piecelist:
            if y.name != PAWN and not(isSafe(p, BLACK)):
                evalu += y.value/2 - 0.3

    for p in wp.piecelist:
        # Make sure pawns are safe
        if not(isSafe(p, WHITE)) and isSafe(p, BLACK):
            evalu -= 0.4
        # Passed pawns are GREAT
        #TODO: improve alorithm for determining value of passed pawns
        if p > 32 and BL[p+8] == 0 and BL[p+9] != id(bp) and BL[p+7] != id(bp):
                evalu += p/8 - 3
    for p in bp.piecelist:
        if not(isSafe(p, BLACK)) and isSafe(p, WHITE):
            evalu += 0.4
        if p < 31 and BL[p-8] == 0 and BL[p-9] != id(wp) and BL[p-7] != id(wp):
                evalu -= 4 - p/8

    # Checkmate is the ultimate goal
    if isInCheck(WHITE):
        evalu -= 0.5
        if whiteMate == 'CHECKMATE':
            evalu -= Kval
    if isInCheck(BLACK):
        evalu += 0.5
        if blackMate == 'CHECKMATE':
            evalu += Kval

    if colour == BLACK:
        evalu *= -1

    if isEndgame():
        evalu += EvaluateEndgame(colour)
    else:
        evalu += EvaluateMiddleGame(colour)

    return evalu


def EvaluateMiddleGame(colour):
    evalu = 0

    for y in wp.piecelist:
        # Add incentives for centred pawns
        if y == 27 or y == 28:
            evalu += 0.4
        # Add incentives for making use of outposts for knights
        if y > 24 and y < 48:
            f = y % 8
            if pm.boardlist[y+9] == id(wn) or pm.boardlist[y+7] == id(wn):
                if f > 0 and f < 7:
                    evalu += 0.35
        # Doubled pawns are BAD
        if y < 56 and pm.boardlist[y + 8] == id(wp):
            evalu -= 0.5

    for y in bp.piecelist:
        if y == 35 or y == 36:
            evalu -= 0.4
        if y > 24 and y < 48:
            f = y % 8
            if pm.boardlist[y-9] == id(bn) or pm.boardlist[y-7] == id(bn):
                if f > 0 and f < 7:
                    evalu -= 0.35
        if y < 56 and pm.boardlist[y + 8] == id(bp):
            evalu += 0.5

    for y in wn.piecelist:
        # Add incentives for development
        if y == 18 or y == 21:
            evalu += 0.3
    for y in bn.piecelist:
        if y == 42 or y == 45:
            evalu -= 0.3

    for y in wb.piecelist:
        # Fianchetto
        if y == 9 or y == 14:
            evalu += 0.35
    for y in bb.piecelist:
        if y == 49 or y == 54:
            evalu -= 0.35

    for y in wr.piecelist:
        f, r = y%8, y/8
        # Centralize rooks
        if f == 3 or f == 4:
            evalu += 0.25
        # Rooks on open/semi-open files
        for x in [f+8, f+16, f+24, f+32, f+40, f+48]:
            if pm.boardlist[x] == id(wp):
                evalu -= 0.5
                break
        # Rook on seventh rank is good
        if r == 6:
            evalu += 0.35
    for y in br.piecelist:
        f, r = y%8, y/8
        if f == 3 or f == 4:
            evalu -= 0.25
        for x in [f+8, f+16, f+24, f+32, f+40, f+48]:
            if pm.boardlist[x] == id(bp):
                evalu += 0.5
                break
        # Rook on second rank is good
        if r == 1:
            evalu -= 0.35

    hs = wk.piecelist[0]
    ls = bk.piecelist[0]
    # Add incentives for castling
    if hs == 2 or hs == 6:
        evalu += 0.7
    # Discourage useless king marches
    elif not(pm.curState.wl or pm.curState.ws):
        evalu -= 0.3
    if ls == 57 or ls == 62:
        evalu -= 0.7
    elif not(pm.curState.bl or pm.curState.bs):
        evalu += 0.3

    # Keep the f2/f7 square safe
    if not(isSafe(53, BLACK)) and isSafeWithParams(53, WHITE, 'N', 'B'):
        evalu += 0.5
    if not(isSafe(13, WHITE)) and isSafeWithParams(13, BLACK, 'N', 'B'):
        evalu -= 0.5

    if colour == BLACK:
        evalu *= -1
        
    return evalu


class Position:
    evaluation = 0
    movestart = 0
    moveend = 0
    

# Returns the "best" move for colour
def FindBest(colour, plies=maxPlies, width=5):
    if width <= 0:
        width = 1
    
    if colour == WHITE:
        pieces = pm.whitepieces
        opp = BLACK
    elif colour == BLACK:
        pieces = pm.blackpieces
        opp = WHITE

    topMoves = []
    default = Position()
    default.evaluation = -1000

    def e(pos): return pos.evaluation

    for p in pieces:
        for start in p.piecelist:
            for end in PieceMovement(start):
                cur = Position()
                cur.movestart = start
                cur.moveend = end

                pm.MovePiece(start, end)
                cur.evaluation = EvaluatePosition(colour)
                pm.UndoMove()

                i = pm.pieceatsqr(end)
                # Don't hang pieces unless you need to
                if not(i) and not(isSafe(end, colour)) and isSafe(end, opp):
                    cur.evaluation -= p.value
                # No kamikaze allowed
                elif i and i.value < p.value and not(isSafe(end, colour)):
                    cur.evaluation -= p.value

                if len(topMoves) < width:
                    topMoves.append(cur)
                    topMoves.sort(key=e)
                elif cur.evaluation > topMoves[0].evaluation:
                    topMoves[0] = cur
                    topMoves.sort(key=e)

                # Return right away if a mate is found
                if cur.evaluation >= mateThreshold:
                    return cur
                    

    #TODO: Use a helper function or a loop instead
    if plies > 1:
        plies -= 1
        width -= 2
        for pos in topMoves:
            temp = pos.evaluation
            pm.MovePiece(pos.movestart, pos.moveend)
            oppTop = FindBest(opp, plies, width)
            pos.evaluation = (-1) * oppTop.evaluation
            if NOISY_LOGGING and plies == maxPlies - 1:
                print oppTop.moveend
                print pos.movestart, "->", pos.moveend
                print temp, ";", pos.evaluation
            pm.UndoMove()

    if NOISY_LOGGING and plies == maxPlies - 1:
        print "---------"

    if len(topMoves) == 0:
        topMoves.append(default)
    return max(topMoves, key=e)  


# returns True if kingpos has the opposition against the enemy king
def hasOpposition(kingpos, opp_pos):
    a, b = kingpos, opp_pos
    #TODO: check opposition for corners (if b in corners...)
    corners = [0, 7, 56, 63]
    if abs(a-b) == 16 or (a/8 == b/8 and abs(a-b) == 2):
        return True
    elif abs(a-b) == 32 or (a/8 == b/8 and abs(a-b) == 4):
        return True
    elif abs(a-b) == 48 or (a/8 == b/8 and abs(a-b) == 6):
        return True
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


def EvaluateEndgame(colour):
    evalu = 0
    if colour == WHITE:
        king, oppKing = wk.piecelist[0], bk.piecelist[0]
    else:
        king, oppKing = bk.piecelist[0], wk.piecelist[0]

    # Try to limit the enemy king's movement
    a = len(PieceMovement(oppKing))

    if a < 2:
        evalu += 3
    elif a < 3:
        evalu += 1.5
    elif a < 4:
        evalu += 1
    elif a < 5:
        evalu += 0.7
    elif a < 6:
        evalu += 0.5

    if hasOpposition(king, oppKing):
        evalu += 0.5

    return evalu
                

# Finds possible opening moves for black
def OpeningMoves(colour, movenum, randnum):
    #TODO: Place opening moves into a dictionary of some sort
    if movenum == 0 and colour == WHITE:
        if randnum < 0.3:
            return 11, 27 #d4
        elif randnum < 0.6:
            return 12, 28 #e4
        elif randnum < 0.9:
            return 10, 26 #c4
        else:
            return 14, 22 #g3

    if movenum == 1 and colour == BLACK:
        if pm.boardlist[26] == id(wp):
            if randnum < 0.75:
                return 50, 34 #c5
            else:
                return 52, 36 #e5
        elif pm.boardlist[27] == id(wp):
            if randnum < 0.25:
                return 62, 45 #Nf6
            else:
                return 51, 35 #d5
        elif pm.boardlist[28] == id(wp):
            if randnum < 0.5:
                return 50, 34
            else:
                return 52, 36

    elif movenum == 2 and colour == BLACK:
        if pm.boardlist[27] == id(wp) and pm.boardlist[26] == id(wp):
            if pm.boardlist[35] == id(bp):
                if randnum < 0.5:
                    return 35, 26 #dxc4
                else:
                    return 52, 44 #e6
            elif pm.boardlist[45] == id(bk):
                return 52, 44
        if pm.boardlist[28] == id(wp) and pm.boardlist[21] == id(wn):
            if pm.boardlist[51] == id(bp) and pm.boardlist[34] == id(bp):
                return 51, 43 #d6
            if pm.boardlist[57] == id(bn) and pm.boardlist[36] == id(bp):
                return 57, 42 #Nc6

    elif movenum >= 3 and colour == BLACK:
        if pm.boardlist[27] == id(wn) and pm.boardlist[62] == id(bn):
            if pm.boardlist[34] != id(bp) and pm.boardlist[36] != id(bp):
                return 62, 45
        if pm.boardlist[27] == id(wp) and pm.boardlist[26] == id(wp):
            if pm.boardlist[62] == id(bn):
                return 62, 45
    default = FindBest(colour)
    return default.movestart, default.moveend
    
