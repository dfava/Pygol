'''Game of life'''
import sys
import copy
import random
import argparse
import time
import curses

class Cell():
    '''Represents a cell in a grid.  It has a coordinate and a weight'''
    def __init__(self, coordinate : tuple, weight : float):
        self.coordinate = coordinate
        self.weight = weight

    def __getitem__(self, key):
        return self.coordinate[key]

    def __repr__(self):
        return '(%s, %s)' % (self.coordinate, self.weight)

class Grid():
    neighbors_offset = [(r_idx, c_idx) for r_idx in range(-1,2) for c_idx in range(-1,2) if (r_idx, c_idx) != (0,0)]

    def __init__(self, arg):
        '''Constructor for a Grid.  Either initialize the grid randomly when arg is a float, interpreting arg 
as the probability of the cell being alive, or read the grid from a file when arg is a string with the filename.'''
        self.cells = None
        if type(arg) == tuple:
            (size, prob) = arg
            self.size = size
            self.cells = [[('X' if random.random() < prob else '.') for r_idx in range(0,self.size)] for c_idx in range(0,self.size)]
            return
        assert(type(arg) == str)
        with open(arg, 'r') as f:
            lines = f.readlines()
        self.cells = [list(l.strip()) for l in lines]
        # Validate the size of the grid
        self.size = len(self.cells)
        for idx,row in enumerate(self.cells):
            if len(row) != self.size:
                print('Row %d does not have the expected number (%d) of cells!' % (idx+1, self.size))

    def __getitem__(self, key):
        if type(key) == tuple:
            return self.cells[key[0]][key[1]]
        return self.cells[key]

    def getNeighbors(self, cell : Cell):
        '''Compute all the neighbors of a cell'''
        ret = []
        for offset in Grid.neighbors_offset:
            coordinate = (cell[0] + offset[0], cell[1] + offset[1])
            if -1 in coordinate or self.size in coordinate:
                continue
            ret.append(Cell(coordinate, 1)) # All neighbors have the same weight of 1
        return ret

    def update(self, debug=False):
        '''Update cells given the current configuration.'''
        new_cells = copy.deepcopy(self.cells)
        for row in range(0,self.size):
            for col in range(0,self.size):
                cell = (row,col)
                if debug: print('Cell %s' % (cell,))
                # Score neighbors
                score = 0
                neighbors = self.getNeighbors(cell)
                if debug: print(neighbors)
                score = sum([((0 if self[n.coordinate] == '.' else 1) * n.weight) for n in neighbors])
                if debug: print('Score: %f' % score)
                live = self.live(self[cell], score)
                new_cells[cell[0]][cell[1]] = 'X' if live else '.'
        self.cells = new_cells

    def live(self, cell_val, neighbor_score):
        '''Implements the rule that decides whether a cell is suposed to be dead or alive on the next iteration.'''
        return True if (cell_val == 'X' and neighbor_score in [2, 3]) or (cell_val == '.' and neighbor_score == 3) else False

    def __repr__(self):
        return ('\n'.join([''.join(self.cells[r_idx]) for r_idx in range(0,self.size)]))

class HexGrid6(Grid):
    '''A hex grid with the 6 neighbor rule'''
    common_neighbors_offset = [(-1,0),(0,-1),(0,1),(1,0)]
    neighbors_offset = [common_neighbors_offset + [(-1,-1), (1,-1)], common_neighbors_offset + [(-1,1), (1,1)]]

    def getNeighbors(self, cell : Cell):
        '''Compute all the neighbors of a cell'''
        ret = []
        (row,col) = cell
        for offset in HexGrid6.neighbors_offset[row%2==1]:
            coordinate = (row + offset[0], col + offset[1])
            if -1 in coordinate or self.size in coordinate:
                continue
            ret.append(Cell(coordinate, 1)) # All neighbors have the same weight of 1
        return ret

    def __repr__(self):
        '''Print the hex version of the grid'''
        offsets = [('' if idx % 2 == 0 else ' ') for idx in range(0,self.size)]
        rows = [' '.join(self.cells[r_idx]) for r_idx in range(0,self.size)]
        return ('\n'.join([_[0] + _[1] for _ in zip(offsets, rows)]))

class HexGrid12(HexGrid6):
    '''A hex grid with the 12 neighbor rule'''
    common_neighbors_offset = [(-2,0),(2,0)]
    neighbors_offset = [common_neighbors_offset + [(-1,-2), (-1,1), (1,1), (1,-2)], common_neighbors_offset + [(-1,2), (-1,-1), (1,-1), (1,2)]]

    def getNeighbors(self, cell : Cell):
        ret = super(HexGrid12, self).getNeighbors(cell)
        (row,col) = cell
        for offset in HexGrid12.neighbors_offset[row%2==1]:
            coordinate = (row + offset[0], col + offset[1])
            if -1 in coordinate or -2 in coordinate or self.size in coordinate or self.size+1 in coordinate:
                continue
            ret.append(Cell(coordinate, 0.3))
        return ret

    def live(self, cell_val, neighbor_score):
        '''Implements the rule in http://www.well.com/~dgb/hexrules.html'''
        return True if (cell_val == 'X' and (2.0 < neighbor_score < 3.3)) or (cell_val == '.' and (2.3 < neighbor_score < 2.9)) else False

def gridBuilder(grid_type, args):
    if grid_type == 8:
        return Grid(args)
    elif grid_type == 6:
        return HexGrid6(args)
    elif grid_type == 12:
        return HexGrid12(args)

def parse_args():
    '''Parse and validate command line args'''
    parser = argparse.ArgumentParser(description="Game of Live", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-6', nargs='?', dest='neighbor_rules', const='6', type=int, default=6,
        help='use 6 neighbor rules on hex grid')
    parser.add_argument('-8', nargs='?', dest='neighbor_rules', const='8', type=int, default=6,
        help='use 8 neighbor rules on rectangular grid')
    parser.add_argument('-12', nargs='?', dest='neighbor_rules', const='12', type=int, default=6,
        help='use 12 neighbor rules on hex grid')
    parser.add_argument('-size', dest='size', default=100, type=int,
        help='set grid size to SIZE by SIZE')
    parser.add_argument('-f', dest='fname',
        help='read initial configuration from file')
    parser.add_argument('-g', dest='gens', default=10, type=int,
        help='number of generations to simulate')
    parser.add_argument('-p', dest='gen_print', default=1, type=int,
        help='print every nth generation')
    parser.add_argument('-i', dest='prob', default=0.5, type=float,
        help='probabilty of alive cell initially')
    parser.add_argument('-nc', nargs='?', dest='ncurses', default=False, const=True, type=bool,
        help='use ncurses for output')
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    grid = gridBuilder(args.neighbor_rules, args.fname) if args.fname != None \
            else gridBuilder(args.neighbor_rules, (args.size, args.prob))

    def main_curses(stdscr):
        pad = curses.newpad(args.size*2+5, args.size*2+5)
        for gen in range(0,args.gens+1):
            pad.addstr(0,0, 'Gen%d' % gen)
            pad.addstr(1,0, grid.__repr__())
            pad.refresh(0,0, 5,5, 20,75)
            time.sleep(0.1)
            grid.update()

    if args.ncurses:
        curses.wrapper(main_curses)
    else:
        print(grid)
        for gen in range(1,args.gens+1):
            print('Gen %d' % gen)
            grid.update()
            if gen % args.gen_print == 0:
                print(grid)
    return 0


if __name__ == "__main__":
    sys.exit(main())
