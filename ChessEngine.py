"""
Current State of Chess game
Current State Valid moves
Move log
"""


class GameState:
    def __init__(self):
        """
        8 x 8 2D list
        """
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.moveFunctions = {"p": self.getPawnMoves, "R": self.getRookMoves, "N": self.getKnightMoves,
                              "B": self.getBishopMoves, "Q": self.getQueenMoves, "K": self.getKingMoves}
        self.white_to_move = True
        self.move_log = []
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.checkmate = False
        self.stalemate = False
        self.in_check = False
        self.pins = []
        self.checks = []
        self.enpassant_possible = ()  # coordinates for the square where en-passant capture is possible
        self.enpassant_possible_log = [self.enpassant_possible]
        self.current_castling_rights = CastleRights(True, True, True, True)
        self.castle_rights_log = [CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                               self.current_castling_rights.wqs, self.current_castling_rights.bqs)]

    def makeMove(self, move):
        """
        Moves executions
        (this will not work for castling, pawn promotion and en-passant)
        """
        
        """
        Update pieces positions after making a move
        """
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        
        self.move_log.append(move)  # log the move so we can undo it later
        self.swap_player()  # switch players
        
        
        """
        Update king's position after making a move
        """
        if move.piece_moved == "wK":
            self.white_king_location = (move.end_row, move.end_col)
        elif move.piece_moved == "bK":
            self.black_king_location = (move.end_row, move.end_col)

        """
        Hanlding Pawn Promotion rule after making a move
        """
        if move.is_pawn_promotion:
            # if not is_AI:
            #    promoted_piece = input("Promote to Q, R, B, or N:") #take this to UI later
            #    self.board[move.end_row][move.end_col] = move.piece_moved[0] + promoted_piece
            # else:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + "Q"

        """
        Hanlding En Passant rule after making a move
        """
        if move.is_enpassant_move:
            self.board[move.start_row][move.end_col] = "--"  # capturing the pawn

        """
        Update En Passant possible position after making a move
        """
        if move.piece_moved[1] == "p" and abs(move.start_row - move.end_row) == 2:  # only on 2 square pawn advance
            self.enpassant_possible = ((move.start_row + move.end_row) // 2, move.start_col)
        else:
            self.enpassant_possible = ()

        """
        Handle castle move after making a move
        """
        if move.is_castle_move:
            if move.end_col - move.start_col == 2:  # king-side castle move
                self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][
                    move.end_col + 1]  # moves the rook to its new square
                self.board[move.end_row][move.end_col + 1] = '--'  # erase old rook
            else:  # queen-side castle move
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][
                    move.end_col - 2]  # moves the rook to its new square
                self.board[move.end_row][move.end_col - 2] = '--'  # erase old rook

        self.enpassant_possible_log.append(self.enpassant_possible)

        """
        Log current castle rights after making a move
        """
        self.updateCastleRights(move)
        self.castle_rights_log.append(CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                                   self.current_castling_rights.wqs, self.current_castling_rights.bqs))
  
    def swap_player(self):
        """
        Swap to other player
        """
        self.white_to_move = not self.white_to_move  
        
    def undoMove(self):
        """
        Undo the last move
        """
        if len(self.move_log) != 0:  # Make sure there's move to undo
            move = self.move_log.pop()
            
            """
            Restore Position of a piece after undoing the move
            """
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            
            self.swap_player()  # switch players
            
            
            """
            Update King's position after undoing the move
            """
            if move.piece_moved == "wK":
                self.white_king_location = (move.start_row, move.start_col)
            elif move.piece_moved == "bK":
                self.black_king_location = (move.start_row, move.start_col)
            
            """
            En Passant handling after undoing the move
            """
            if move.is_enpassant_move:
                self.board[move.end_row][move.end_col] = "--"  # leave landing square blank
                self.board[move.start_row][move.end_col] = move.piece_captured

            self.enpassant_possible_log.pop()
            self.enpassant_possible = self.enpassant_possible_log[-1]

            """
            Castle rights handling after undoing the move
            """
            self.castle_rights_log.pop()  # get rid of the new castle rights from the move we are undoing
            self.current_castling_rights = self.castle_rights_log[
                -1]  # set the current castle rights to the last one in the list
            
            """
            Castle moves handling after undoing the move
            """
            if move.is_castle_move:
                if move.end_col - move.start_col == 2:  # king-side
                    self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 1]
                    self.board[move.end_row][move.end_col - 1] = '--'
                else:  # queen-side
                    self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][move.end_col + 1]
                    self.board[move.end_row][move.end_col + 1] = '--'
            self.checkmate = False
            self.stalemate = False

    def updateCastleRights(self, move):
        """
        Update the castle rights given the move
        """
        # Mapping piece moved and captured to corresponding castle rights
        rights_map = {
            "wR": ("wqs", "wks"),
            "bR": ("bqs", "bks"),
            "wK": ("wqs", "wks"),
            "bK": ("bqs", "bks")
        }

        if move.piece_moved in rights_map:
            self.current_castling_rights.__dict__[rights_map[move.piece_moved][0]] = False
            self.current_castling_rights.__dict__[rights_map[move.piece_moved][1]] = False

        if move.piece_captured in rights_map:
            if move.end_col == 0:  # left rook
                self.current_castling_rights.__dict__[rights_map[move.piece_captured][0]] = False
            elif move.end_col == 7:  # right rook
                self.current_castling_rights.__dict__[rights_map[move.piece_captured][1]] = False

    def getValidMoves(self):
        """
        All moves considering checks.
        """
        temp_castle_rights = CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                          self.current_castling_rights.wqs, self.current_castling_rights.bqs)
        # advanced algorithm
        moves = []
        self.in_check, self.pins, self.checks = self.checkForPinsAndChecks()

        if self.white_to_move:
            king_row = self.white_king_location[0]
            king_col = self.white_king_location[1]
        else:
            king_row = self.black_king_location[0]
            king_col = self.black_king_location[1]
        if self.in_check:
            if len(self.checks) == 1:  # only 1 check, block the check or move the king
                moves = self.getAllPossibleMoves()
                # to block the check you must put a piece into one of the squares between the enemy piece and your king
                check = self.checks[0]  # check information
                check_row = check[0]
                check_col = check[1]
                piece_checking = self.board[check_row][check_col]
                valid_squares = []  # squares that pieces can move to
                # if knight, must capture the knight or move your king, other pieces can be blocked
                if piece_checking[1] == "N":
                    valid_squares = [(check_row, check_col)]
                else:
                    for i in range(1, 8):
                        valid_square = (king_row + check[2] * i,
                                        king_col + check[3] * i)  # check[2] and check[3] are the check directions
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[
                            1] == check_col:  # once you get to piece and check
                            break
                # get rid of any moves that don't block check or move king
                for i in range(len(moves) - 1, -1, -1):  # iterate through the list backwards when removing elements
                    if moves[i].piece_moved[1] != "K":  # move doesn't move king so it must block or capture
                        if not (moves[i].end_row,
                                moves[i].end_col) in valid_squares:  # move doesn't block or capture piece
                            moves.remove(moves[i])
            else:  # double check, king has to move
                self.getKingMoves(king_row, king_col, moves)
        else:  # not in check - all moves are fine
            moves = self.getAllPossibleMoves()
            if self.white_to_move:
                self.getCastleMoves(self.white_king_location[0], self.white_king_location[1], moves)
            else:
                self.getCastleMoves(self.black_king_location[0], self.black_king_location[1], moves)

        if len(moves) == 0:
            if self.inCheck():
                self.checkmate = True
            else:
                # TODO stalemate on repeated moves
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        self.current_castling_rights = temp_castle_rights
        return moves

    def inCheck(self):
        """
        Determine if a current player is in check
        """
        if self.white_to_move:
            return self.squareUnderAttack(self.white_king_location[0], self.white_king_location[1])
        else:
            return self.squareUnderAttack(self.black_king_location[0], self.black_king_location[1])

    def squareUnderAttack(self, row, col):
        """
        Determine if enemy can attack the square row col
        """
        self.swap_player()
        opponents_moves = self.getAllPossibleMoves()
        self.swap_player()
        for move in opponents_moves:
            if move.end_row == row and move.end_col == col:  # square is under attack
                return True
        return False

    def getAllPossibleMoves(self):
        """
        All moves without considering checks.
        """
        moves = []
        ally_color = 'w' if self.white_to_move else 'b'
        positions_to_evaluate = [(r, c) for r, row in enumerate(self.board) for c, cell in enumerate(row) if cell and cell[0] == ally_color]

        for row, col in positions_to_evaluate:
            piece = self.board[row][col][1]
            self.moveFunctions[piece](row, col, moves)

        return moves

    def checkForPinsAndChecks(self):
        pins, checks = [], []
        ally_color, enemy_color, start_row, start_col = ('w', 'b', *self.white_king_location) if self.white_to_move else ('b', 'w', *self.black_king_location)
        
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for direction in directions:
            possible_pin = ()
            for i in range(1, 8):
                end_row, end_col = start_row + direction[0] * i, start_col + direction[1] * i
                if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally_color and end_piece[1] != "K":
                        if not possible_pin: possible_pin = (end_row, end_col, *direction)
                        else: break
                    elif end_piece[0] == enemy_color:
                        if ((0 <= directions.index(direction) <= 3 and end_piece[1] == "R") or 
                            (4 <= directions.index(direction) <= 7 and end_piece[1] == "B") or 
                            (i == 1 and end_piece[1] == "p" and ((enemy_color == "w" and 6 <= directions.index(direction) <= 7) or 
                            (enemy_color == "b" and 4 <= directions.index(direction) <= 5))) or 
                            (end_piece[1] == "Q") or (i == 1 and end_piece[1] == "K")):
                            if not possible_pin: 
                                checks.append((end_row, end_col, *direction))
                            else: # piece blocking pinned
                                pins.append(possible_pin)
                            break
                        else: # Enemy piece not applying check
                            break
                else: # Off board
                    break
        # Check for knight checks
        knight_moves = ((-2, -1), (-2, 1), (-1, 2), (1, 2), (2, -1), (2, 1), (-1, -2), (1, -2))
        for move in knight_moves:
            end_row, end_col = start_row + move[0], start_col + move[1]
            if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color and end_piece[1] == "N":
                    checks.append((end_row, end_col, *move))

        return bool(checks), pins, checks

    def getPawnMoves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][:2] == (r, c):
                piece_pinned = True
                pin_direction = self.pins[i][2:]
                del self.pins[i]
                break

        if self.white_to_move:
            direction = -1
            start_row = 6
            enemy_color = "b"
            king_loc = self.white_king_location
        else:
            direction = 1
            start_row = 1
            enemy_color = "w"
            king_loc = self.black_king_location

        if self.board[r + direction][c] == "--":
            if not piece_pinned or pin_direction == (direction, 0):
                moves.append(Move((r, c), (r + direction, c), self.board))
                if r == start_row and self.board[r + 2 * direction][c] == "--":
                    moves.append(Move((r, c), (r + 2 * direction, c), self.board))

        # Capture Moves
        for new_c in [c - 1, c + 1]:
            if 0 <= new_c <= 7:  # Ensure within board
                if not piece_pinned or pin_direction == (direction, new_c - c):
                    if self.board[r + direction][new_c][0] == enemy_color:
                        moves.append(Move((r, c), (r + direction, new_c), self.board))
                    if (r + direction, new_c) == self.enpassant_possible:
                        blocking_piece = attacking_piece = False
                        if king_loc[0] == r:
                            inside_range = range(min(c, king_loc[1]) + 1, max(c, king_loc[1]))
                            outside_range = range(c + 2 if c < king_loc[1] else c - 2, -1 if c < king_loc[1] else 8)
                            if any(self.board[r][i] != "--" for i in inside_range):
                                blocking_piece = True
                            for i in outside_range:
                                square = self.board[r][i]
                                if square[0] == enemy_color and (square[1] == "R" or square[1] == "Q"):
                                    attacking_piece = True
                                elif square != "--":
                                    blocking_piece = True
                        if not attacking_piece or blocking_piece:
                            moves.append(Move((r, c), (r + direction, new_c), self.board, is_enpassant_move=True))

    def getRookMoves(self, row, col, moves):
        """
        Get all the rook moves for the rook located at row, col and add the moves to the list.
        """
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if self.board[row][col][
                    1] != "Q":  # can't remove queen from pin on rook moves, only remove it on bishop moves
                    self.pins.remove(self.pins[i])
                break

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # up, left, down, right
        enemy_color = "b" if self.white_to_move else "w"
        for direction in directions:
            for i in range(1, 8):
                end_row = row + direction[0] * i
                end_col = col + direction[1] * i
                if 0 <= end_row <= 7 and 0 <= end_col <= 7:  # check for possible moves only in boundaries of the board
                    if not piece_pinned or pin_direction == direction or pin_direction == (
                            -direction[0], -direction[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "--":  # empty space is valid
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color:  # capture enemy piece
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                            break
                        else:  # friendly piece
                            break
                else:  # off board
                    break

    def getKnightMoves(self, row, col, moves):
        """
        Get all the knight moves for the knight located at row col and add the moves to the list.
        """
        piece_pinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                self.pins.remove(self.pins[i])
                break

        knight_moves = ((-2, -1), (-2, 1), (-1, 2), (1, 2), (2, -1), (2, 1), (-1, -2),
                        (1, -2))  # up/left up/right right/up right/down down/left down/right left/up left/down
        ally_color = "w" if self.white_to_move else "b"
        for move in knight_moves:
            end_row = row + move[0]
            end_col = col + move[1]
            if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                if not piece_pinned:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] != ally_color:  # so its either enemy piece or empty square
                        moves.append(Move((row, col), (end_row, end_col), self.board))

    def getBishopMoves(self, row, col, moves):
        """
        Get all the bishop moves for the bishop located at row col and add the moves to the list.
        """
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = ((-1, -1), (-1, 1), (1, 1), (1, -1))  # diagonals: up/left up/right down/right down/left
        enemy_color = "b" if self.white_to_move else "w"
        for direction in directions:
            for i in range(1, 8):
                end_row = row + direction[0] * i
                end_col = col + direction[1] * i
                if 0 <= end_row <= 7 and 0 <= end_col <= 7:  # check if the move is on board
                    if not piece_pinned or pin_direction == direction or pin_direction == (
                            -direction[0], -direction[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "--":  # empty space is valid
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color:  # capture enemy piece
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                            break
                        else:  # friendly piece
                            break
                else:  # off board
                    break

    def getQueenMoves(self, row, col, moves):
        """
        Get all the queen moves for the queen located at row col and add the moves to the list.
        """
        self.getBishopMoves(row, col, moves)
        self.getRookMoves(row, col, moves)

    def getKingMoves(self, row, col, moves):
        """
        Get all the king moves for the king located at row col and add the moves to the list.
        """
        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        col_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
        ally_color = "w" if self.white_to_move else "b"
        for i in range(8):
            end_row = row + row_moves[i]
            end_col = col + col_moves[i]
            if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:  # not an ally piece - empty or enemy
                    # place king on end square and check for checks
                    if ally_color == "w":
                        self.white_king_location = (end_row, end_col)
                    else:
                        self.black_king_location = (end_row, end_col)
                    in_check, pins, checks = self.checkForPinsAndChecks()
                    if not in_check:
                        moves.append(Move((row, col), (end_row, end_col), self.board))
                    # place king back on original location
                    if ally_color == "w":
                        self.white_king_location = (row, col)
                    else:
                        self.black_king_location = (row, col)

    def getCastleMoves(self, row, col, moves):
        """
        Generate all valid castle moves for the king at (row, col) and add them to the list of moves.
        """
        if self.squareUnderAttack(row, col):
            return  # can't castle while in check
        castle_rights = self.current_castling_rights.wks if self.white_to_move else self.current_castling_rights.bks
        if castle_rights:
            self.getCastleMove(row, col, 2, moves, True)
        castle_rights = self.current_castling_rights.wqs if self.white_to_move else self.current_castling_rights.bqs
        if castle_rights:
            self.getCastleMove(row, col, -2, moves, False)

    def getCastleMove(self, row, col, d, moves, is_king_side):
        """
        Generate a valid castle move and add it to the list of moves.
        """
        for i in range(1, abs(d) + 1):
            if self.board[row][col + i] != '--' or self.squareUnderAttack(row, col + i):
                return
        moves.append(Move((row, col), (row, col + d), self.board, is_castle_move=True))

class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs



class Move:
    ranks_to_rows = {str(i): 8-i for i in range(1, 9)}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {chr(i+97): i for i in range(8)}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_square, end_square, board, is_enpassant_move=False, is_castle_move=False):
        self.start_row, self.start_col = start_square
        self.end_row, self.end_col = end_square
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.is_pawn_promotion = (self.piece_moved[1] == 'p' and self.end_row in [0, 7])
        self.is_enpassant_move = is_enpassant_move
        self.is_castle_move = is_castle_move
        self.is_capture = self.piece_captured != '--'
        self.moveID = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col

        if self.is_enpassant_move:
            self.piece_captured = 'wp' if self.piece_moved == 'bp' else 'bp'

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getRankFile(self, row, col):
        return f'{self.cols_to_files[col]}{self.rows_to_ranks[row]}'

    def getChessNotation(self):
        end_square = self.getRankFile(self.end_row, self.end_col)
        if self.is_pawn_promotion:
            return f'{end_square}Q'
        if self.is_castle_move:
            return '0-0-0' if self.end_col == 1 else '0-0'
        if self.is_enpassant_move:
            return f'{self.getRankFile(self.start_row, self.start_col)[0]}x{end_square} e.p.'
        if self.is_capture:
            if self.piece_moved[1] == 'p':
                return f'{self.getRankFile(self.start_row, self.start_col)[0]}x{end_square}'
            else:
                return f'{self.piece_moved[1]}x{end_square}'
        else:
            return f'{self.piece_moved[1]}{end_square}'

    def __str__(self):
        if self.is_castle_move:
            return '0-0' if self.end_col == 6 else '0-0-0'

        end_square = self.getRankFile(self.end_row, self.end_col)
        move_string = self.piece_moved[1]

        if self.piece_moved[1] == 'p':
            move_string = f'{self.cols_to_files[self.start_col]}x{end_square}' if self.is_capture else end_square
            move_string += 'Q' if self.is_pawn_promotion else ''
        else:
            move_string += f'x{end_square}' if self.is_capture else end_square

        return move_string

