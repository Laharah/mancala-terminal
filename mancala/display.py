def show_board(board):
    top = board.top
    bottom = board.bottom
    print(' ' * 6, end='')
    for i in range(5, -1, -1):
        print('{:^5}'.format(i), end='')
    print()
    h_border = '-' * 43
    print(h_border)
    print(construct_bins(top[-2::-1]))
    print('|' + ' {:>2}  '.format(top[-1]) + '-' * 31 + ' ' * 5 + '|')
    print('|' + ' '*5 + '-' * 31 + ' {:>2}  '.format(bottom[-1])  + '|')
    print(construct_bins(bottom[:-1]))
    print(h_border)
    print(' ' * 6, end='')
    for i in range(6):
        print('{:^5}'.format(i), end='')

def construct_bins(values):
    glyf = [' ']
    glyf.extend(chr(o) for o in range(ord('\u2460'), ord('\u2474')))
    bins = ''.join('| {}  '.format(glyf[v]) for v in values)
    return '|     '+ bins+ '|     |'
