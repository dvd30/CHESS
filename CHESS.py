import sys
import pygame

pygame.init()
width = height = 512
dimension = 8
cell_size = height//dimension
fps = 60
images = {}
font = pygame.font.Font("freesansbold.ttf", 48)


class GameState:
    def __init__(self):
        self.board = [
            ['br', 'bh', 'bb', 'bq', 'bk', 'bb', 'bh', 'br'],
            ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
            ['wr', 'wh', 'wb', 'wq', 'wk', 'wb', 'wh', 'wr']
            ]
        self.white_moves = True
        self.move_log = []
        self.command = {'p': self.get_pawn_moves, 'r': self.get_rook_moves, 'h': self.get_knight_moves, 'q':
                        self.get_queen_moves, 'k': self.get_king_moves, 'b': self.get_bishop_moves}
        self.chance = {'p': "pawn_moves", 'r': "rook_moves", 'h': "knight_moves", 'q': "queen_moves", 'k': "king_moves",
                       'b': "bishop_moves"}

    def make_move(self, move):
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)
        self.white_moves = not self.white_moves

    def undo_move(self):
        if len(self.move_log) != 0:
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_moves = not self.white_moves

    def get_valid_moves(self):
        return self.all_possible_moves()

    def all_possible_moves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == "w" and self.white_moves) or (turn == "b" and not self.white_moves):
                    piece = self.board[r][c][1]
                    self.command[piece](r, c, moves)

        return moves

    def get_pawn_moves(self, r, c, moves):
        if self.white_moves:
            if self.board[r - 1][c] == '--':
                moves.append(Move((r, c), (r - 1, c), self.board))
                if r == 6 and self.board[r - 2][c] == '--':
                    moves.append(Move((r, c), (r - 2, c), self.board))
            if c-1 >= 0:
                if self.board[r-1][c-1][0] == 'b':
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
            if c+1 <= 7:
                if self.board[r - 1][c + 1][0] == 'b':
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
        else:
            if self.board[r+1][c] == '--':
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r+2][c] == '--':
                    moves.append(Move((r, c), (r + 2, c), self.board))
            if c - 1 >= 0:
                if self.board[r+1][c-1][0] == 'w':
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
            if c + 1 <= 7:
                if self.board[r+1][c+1][0] == 'w':
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))

    def get_rook_moves(self, r, c, moves):
        direction = [(-1, 0), (1, 0), (0, 1), (0, -1)]
        enemy_color = 'b' if self.white_moves else 'w'
        for d in direction:
            for i in range(1, 8):
                end_row = r + d[0]*i
                end_col = c + d[1]*i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    piece_captured = self.board[end_row][end_col]
                    if piece_captured == '--':
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif piece_captured[0] == enemy_color:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else:
                        break
                else:
                    break

    def get_knight_moves(self, r, c, moves):
        knight_moves = [(-2, -1), (-2, 1), (-1, 2), (-1, -2), (1, 2), (1, -2), (2, -1), (2, 1)]
        ally_color = 'w' if self.white_moves else 'b'
        for m in knight_moves:
            end_row = r + m[0]
            end_col = c + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                piece_captured = self.board[end_row][end_col]
                if piece_captured[0] != ally_color:
                    moves.append(Move((r, c), (end_row, end_col), self.board))

    def get_bishop_moves(self, r, c, moves):
        camels_moves = [(1, -1), (-1, -1), (-1, 1), (1, 1)]
        ally_color = 'w' if self.white_moves else 'b'
        for m in camels_moves:
            for i in range(1, 8):
                end_row = r + m[0]*i
                end_col = c + m[1]*i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    piece_captured = self.board[end_row][end_col]
                    if piece_captured[0] != ally_color:
                        moves.append(Move((r, c), (end_row, end_col), self.board))

    def get_queen_moves(self, r, c, moves):
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)

    def get_king_moves(self, r, c, moves):
        queen_moves = [(-1, 1), (-1, 0), (-1, -1), (0, 1), (0, -1), (1, 1), (1, 0), (1, -1)]
        ally_color = 'w' if self.white_moves else 'b'
        for q in range(8):
            end_row = r + queen_moves[q][0]
            end_col = c + queen_moves[q][1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                piece_captured = self.board[end_row][end_col]
                if piece_captured[0] != ally_color:
                    moves.append(Move((r, c), (end_row, end_col), self.board))


class Move:
    ranks_to_row = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    row_to_ranks = {v: k for k, v in ranks_to_row.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    col_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_pos, end_pos, board):
        self.start_row = start_pos[0]
        self.start_col = start_pos[1]
        self.end_row = end_pos[0]
        self.end_col = end_pos[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.MoveId = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.MoveId == other.MoveId
        return False

    def get_chess_notation(self):
        return self.get_file_rank(self.start_row, self.start_col) + self.get_file_rank(self.end_row, self.end_col)

    def get_file_rank(self, r, c):
        return self.col_to_files[c] + self.row_to_ranks[r]


def load_img():
    pieces = ['br', 'bh', 'bb', 'bq', 'bk', 'bp', 'wp', 'wr', 'wh', 'wb', 'wk', 'wq']
    for piece in pieces:
        images[piece] = pygame.transform.scale(pygame.image.load("CHESS/" + piece + ".png"), (cell_size, cell_size))


def main():
    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    screen.fill((114, 114, 0))
    load_img()
    gs = GameState()
    valid_move = gs.get_valid_moves()
    move_made = False
    sq_selected = ()
    player_clicks = []
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                location = pygame.mouse.get_pos()
                row = location[1]//cell_size
                col = location[0]//cell_size
                if sq_selected == (row, col):
                    sq_selected = ()
                    player_clicks = []
                else:
                    sq_selected = (row, col)
                    player_clicks.append(sq_selected)
                
                if len(player_clicks) == 2:
                    move = Move(player_clicks[0], player_clicks[1], gs.board)
                    if move in valid_move:
                        print(Move.get_chess_notation(move))
                        gs.make_move(move)
                        move_made = True
                    player_clicks = []
                    sq_selected = ()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:
                    gs.undo_move()
                    move_made = True

        if move_made:
            valid_move = gs.get_valid_moves()
            move_made = False

        draw_board(screen)
        draw_pieces(screen, gs)
        clock.tick(fps)
        pygame.display.update()


def draw_board(surface):
    color = [(118, 150, 86), (186, 202, 68)]
    for r in range(dimension):
        for c in range(dimension):
            pygame.draw.rect(surface, color[(r+c) % 2], pygame.Rect(c*cell_size, r*cell_size, cell_size, cell_size))


def draw_pieces(surface, state):
    for r in range(dimension):
        for c in range(dimension):
            piece = state.board[r][c]
            if piece != '--':
                surface.blit(images[piece], pygame.Rect(c*cell_size, r*cell_size, cell_size, cell_size))


if __name__ == '__main__':
    main()
