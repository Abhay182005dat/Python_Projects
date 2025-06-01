from player import HumanPlayer, RandomComputerPlayer 
# import player
import random


class Tictactoe:
    def __init__(self):
        self.board = [' ' for _ in range(9)]  # 3x3 board
        self.current_winner = None
    
    def print_board(self):   # '|'.join(['a', 'b', 'c'])  ->  'a|b|c'
        for row in [self.board[i*3 : (i+1)*3] for i in range(3)]:
            print('| '+' | '.join(row)+' |')


    @staticmethod # no need of self
    def print_board_nums():
        number_board = [[str(i) for i in range(j*3 , (j+1)*3)] for j in range(3)]
        for row in number_board:
            print('| '+'|'.join(row)+' |')

    def available_moves(self):
        return [i for i ,spot in enumerate(self.board) if spot == ' ']
        # moves = []
        # for (i, spot) in enumerate(self.board):
        #     #['x' , 'x' , 'o'] --> [(0,'x') , (1,'x') etc]
        #     if spot == ' ':
        #         moves.append(i)
        # return moves
    def empty_squares(self):
        return ' ' in self.board
    
    def num_empty_squares(self):
        return self.board.count(' ')
    
    def winner(self,square,letter):
        row_ind = square // 3            # assume square = 4 , then row_ind = 1
        # check row
        row = self.board[row_ind*3 : (row_ind+1)*3]    
        if all([spot == letter for spot in row]):
            return True
        
        # check column
        col_ind = square % 3
        column = [self.board[col_ind + i*3] for i in range(3)]
        
        if all([spot == letter for spot in column]):
            return True
        
        # check diagonals
        # that is if square is 0 , 2 , 4 , 6 , 8
        if square % 2 == 0:
            diagonal1 = [self.board[i] for i in [0, 4, 8]]
            diagonal2 = [self.board[i] for i in [2,4,6]]
            if all([spot == letter for spot in diagonal1]) or all([spot == letter for spot in diagonal2]):
                return True
        return False
    
    def make_move(self,square , letter):
        # if valid then only make the move 
        if self.board[square] == ' ':
            self.board[square] = letter
            if self.winner(square , letter):
                self.current_winner = letter
            return True
        return False
        


def play(game , x_player , o_player , print_game = True): # true means computer playing with human else computer playing with itself
    if print_game:
        game.print_board_nums()
    
    letter = 'X'
    while game.empty_squares():
        # get move from appropriate player
        if letter == 'O':
            square = o_player.get_move(game)
        else:
            square = x_player.get_move(game)
        
        # function to make a move
        if game.make_move(square , letter):
            if print_game:
                print(letter + f' makes a  move to square {square}')
                game.print_board()
                print(' ')
            
            if game.current_winner:
                if print_game:
                    print(letter + ' wins !')
                return letter
                
            # this is for next move that is we change the letters 
            letter = 'O' if letter == 'X' else 'X'

    if print_game:
        print('It\'s a Tie ')
        
if __name__ == '__main__':
    x_player = HumanPlayer('X')
    o_player = RandomComputerPlayer('O')
    t = Tictactoe()
    play(t , x_player,  o_player, print_game=True)


    