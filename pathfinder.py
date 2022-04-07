from os import times
from queue import Queue, PriorityQueue
import re
import numpy as np
import sys

class coordinate(object):
    def __init__(self,key, timestamp, x, y):
        self.x = x
        self.y = y
        self.key = key
        self.timestamp = timestamp
    def __lt__(self, other):
        if self.key != other.key:
            return self.key < other.key
        else:
            # print("equal", self.x,self.y, other.x, other.y)
            return self.timestamp < other.timestamp


def get_input(filename):
    rows, columns = 0, 0
    sx, sy = 0, 0
    ex, ey = 0, 0
    with open(filename, 'r') as f:
        iter = 0
        file_lines = f.readlines()
        rows, columns = list(map(int, file_lines[iter].strip().split(" ")))
        iter += 1
        sx, sy = list(map(int, file_lines[iter].strip().split(" ")))
        iter += 1
        ex, ey = list(map(int, file_lines[iter].strip().split(" ")))
        iter += 1
        mat = np.zeros((rows, columns))
        for i in range(rows):
            row = list(map(lambda x: float(x) if x != "X" else float('inf'), file_lines[iter].strip().split(" ")))
            iter += 1
            mat[i, :] = row
        
    return (rows, columns, sx-1, sy-1, ex-1, ey-1, mat)


def forward(mat, x, y):
    row, column = mat.shape
    up = (x - 1, y) if x - 1 >= 0 else None
    down = (x + 1, y) if x + 1 < row else None
    left = (x, y - 1) if y - 1 >= 0 else None
    right = (x, y + 1) if y + 1 < column else None
    return up, down, left, right

def draw_road(mat, pre, x, y):
    road_map = []
    for i in range(mat.shape[0]):
        road_map.append([])
        for j in range(mat.shape[1]):
            road_map[i].append(str(int(mat[i, j])) if mat[i, j] != np.inf else "X")
    while pre["%d %d" % (x, y)] != "terminate":
        road_map[x][y] = "*"
        tmp = pre["%d %d" % (x, y)].split(" ")
        x = int(tmp[0])
        y = int(tmp[1])
    road_map[x][y] = "*"
    return road_map

def get_dis(mat, a, b):
    return 1 + max(0, mat[b[0], b[1]] - mat[a[0], a[1]])


def bfs(mat, sx, sy, ex, ey):
    pre = {}
    queue = Queue()
    queue.put((sx, sy))
    pre["%d %d" % (sx, sy)] = "terminate"
    record = np.zeros((mat.shape))
    record[sx, sy] = 1
    while not queue.empty():
        head = queue.get()
        # record[head[0], head[1]] = 0
        if head[0] == ex and head[1] == ey:
            return draw_road(mat, pre, ex, ey)

        for direct in forward(mat, head[0], head[1]):
            if direct != None and record[direct[0], direct[1]] == 0 and mat[direct[0], direct[1]] != np.inf:
                pre["%d %d" % (direct[0], direct[1])] = "%d %d" % (head[0], head[1])
                queue.put(direct)
                record[direct[0], direct[1]] = 1
    return None


def euclidean_est(f, t):
    return np.sqrt((f[0] - t[0])**2 + (f[1] - t[1])**2)


def manhattan_est(f, t):
    return abs(f[0] - t[0]) + abs(f[1] - t[1])


def ucs(mat, sx, sy, ex, ey):
    pre = {}
    queue = PriorityQueue()
    queue.put(coordinate(0, 0, sx, sy))
    pre["%d %d" % (sx, sy)] = "terminate"
    record = np.zeros((mat.shape))
    dis = np.full(mat.shape, np.inf)
    dis[sx, sy] = 0
    timestamp = 0
    while not queue.empty():
        head = queue.get()
        # print((head.key, head.timestamp, head.x, head.y))
        head = [head.x, head.y]
        # print("to:")
        for index, direct in enumerate(forward(mat, head[0], head[1])) :
            if direct != None and dis[head[0], head[1]] + get_dis(mat, head, direct) < dis[direct[0], direct[1]]:
                pre["%d %d" % (direct[0], direct[1])] = "%d %d" % (head[0], head[1])
                dis[direct[0], direct[1]] = dis[head[0], head[1]] + get_dis(mat, head, direct)
                if record[direct[0], direct[1]] == 0:
                    timestamp += 1
                    queue.put(coordinate(dis[direct[0], direct[1]], timestamp, direct[0], direct[1]))
                    # print(direct)
                    record[direct[0], direct[1]] = 1
                if direct[0] == ex and direct[1] == ey:
                    # print(dis)
                    return draw_road(mat, pre, ex, ey)
    
    return None


def Astar(heuristic, mat, sx, sy, ex, ey):
    pre = {}
    queue = PriorityQueue()
    queue.put(coordinate(0, 0, sx, sy))
    pre["%d %d" % (sx, sy)] = "terminate"
    record = np.zeros((mat.shape))
    dis = np.full(mat.shape, np.inf)
    dis[sx, sy] = 0
    timestamp = 0
    while not queue.empty():
        head = queue.get()
        head = [head.x, head.y]
        record[head[0], head[1]] = 0
        
        for direct in forward(mat, head[0], head[1]):
            if direct != None and dis[head[0], head[1]] + get_dis(mat, head, direct) < dis[direct[0], direct[1]]:
                pre["%d %d" % (direct[0], direct[1])] = "%d %d" % (head[0], head[1])
                dis[direct[0], direct[1]] = dis[head[0], head[1]] + get_dis(mat, head, direct)
                if record[direct[0], direct[1]] == 0:
                    timestamp += 1
                    queue.put(coordinate(dis[direct[0], direct[1]] + heuristic(direct, [ex,ey]), timestamp, direct[0], direct[1]))
                    record[direct[0], direct[1]] = 1
                if direct[0] == ex and direct[1] == ey:
                    return draw_road(mat, pre, ex, ey)

    return None


def show(str_mat):
    for i in str_mat:
        for j in i:
            print(j, end=' ')
        print()

if __name__ == '__main__':
    file_name = sys.argv[1]
    if len(sys.argv) > 2: algorithm = sys.argv[2]
    if len(sys.argv) > 3: heuristic = sys.argv[3]
    rows, columns, sx, sy, ex, ey, mat = get_input(file_name)
    if algorithm == "bfs":
        ans = bfs(mat,sx,sy,ex,ey)
    elif algorithm == "ucs":
        ans = ucs(mat, sx, sy, ex, ey)
    else:
        heuristic_func = euclidean_est if heuristic == "euclidean" else manhattan_est
        ans = Astar(heuristic_func, mat, sx, sy, ex, ey)

    if ans != None:
        show(ans)
        # print(coordinate(0,2,3) < coordinate(1,3,2))
    else:
        print("null")
    