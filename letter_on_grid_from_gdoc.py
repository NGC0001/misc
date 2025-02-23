from bs4 import BeautifulSoup
import requests
import sys


# https://docs.google.com/document/d/e/2PACX-1vQGUck9HIFCyezsrBSnmENk5ieJuYwpt7YHYEzeNJkIb9OSDdx-ov2nRNReKQyey-cwJOoEKUhLmN9z/pub
# BOECWXH

# https://docs.google.com/document/d/e/2PACX-1vRMx5YQlZNa3ra8dYYxmv-QIQ3YJe8tbI3kqcuC7lQiZm-CSEznKfN_HYNSpoXcZIV3Y_O3YoUB1ecq/pub
# F


def fetch_grid_from_doc(url):
    # get html text from url
    res = requests.get(url)
    if res.status_code != 200:
        return None
    res.encoding = 'utf-8'
    # parsing html with bs4
    soup = BeautifulSoup(res.text, 'html.parser')
    tr_list = [tr for tr in soup.select('table tr')][1:]  # table header removed
    grid = []
    for tr in tr_list:
        # get each character and its grid coordinate, from corresponding tr
        tdx, tdc, tdy = tr.children
        c = next(iter(tdc.select('p span'))).string
        x = int(next(iter(tdx.select('p span'))).string)
        y = int(next(iter(tdy.select('p span'))).string)
        # y is row index but in reverse-print (bottom up) order; x is column index
        # i.e., the point x=0 y=0 is the bottom left corner
        # store coordinates in (-y, x) to be easily sorted into print order
        # i.e., top down, left to right
        grid.append((-y, x, c))
    grid.sort()
    return grid


def print_grid(grid):
    row, col = grid[0][0], 0
    for point in grid:
        y, x, c = point
        while row < y:
            sys.stdout.write('\n')
            row += 1
            col = 0
        while col < x:
            sys.stdout.write(' ')
            col += 1
        sys.stdout.write(c)
        col += 1
    sys.stdout.write('\n')


if __name__ == '__main__':
    if len(sys.argv) == 2:
        grid = fetch_grid_from_doc(sys.argv[1])
        if grid is not None:
            print_grid(grid)
