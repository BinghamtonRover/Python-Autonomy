import sys
from queue import PriorityQueue
import math
import time

#https://mat.uab.cat/~alseda/MasterOpt/AStar-Algorithm.pdf

def main():
    is_blocked = set([])

    ## TESTING
    #for i in range(-10, 11):
    #    is_blocked.add((2, i))
    #for i in range(-1, 10):
    #    is_blocked.add((i, 5))
    #for i in range(-20, 5):
    #    is_blocked.add((i, -5))

    # Here will be the "main loop"
    start_node = (0, 0)
    goal_node = (10, 0)

    path = a_star((lambda a, b : (abs(b[0] - a[0]) + abs(b[1] - a[1]))), is_blocked, start_node, goal_node)
    dir = (get_direction(path, is_blocked, start_node, goal_node)) * (180.0 / (math.pi))
    # send "dir" to where it is needed
    # update "is_blocked"

    print(dir)

def get_direction(path, is_blocked, start_node, goal_node):
    x_delta = 0
    y_delta = 0

    prev_node = start_node
    for node in path:
        if x_delta == 0:
            if (node[0] > start_node[0]):
                x_delta = 1
            elif (node[0] < start_node[0]):
                x_delta = -1
        if y_delta == 0:
            if (node[1] > start_node[1]):
                y_delta = 1
            elif (node[1] < start_node[1]):
                y_delta = -1
        if (set_contains((node[0], node[1] - y_delta), is_blocked) or set_contains((node[0] - x_delta, node[1]), is_blocked)):
            print(prev_node)
            return math.atan2(prev_node[1] - start_node[1], prev_node[0] - start_node[0])
        prev_node = node
    return math.atan2(goal_node[1] - start_node[1], goal_node[0] - start_node[0])

def a_star(h_func, is_blocked, start_node, goal_node):
    #start_time = time.time()
    open_queue = PriorityQueue()
    closed_nodes = set([])
    parent = {}
    g_func = {}

    open_queue.put((0, start_node))
    g_func[start_node] = 0
    goal_found = False
    while (not open_queue.empty() and not goal_found):
        current_node = open_queue.get()[1]
        if set_contains(current_node, closed_nodes):
            continue
        elif current_node == goal_node:
            goal_found = True
        else:
            g_val = g_func[current_node] + 1
            for adj_node in get_adjacent_nodes(current_node):
                f_val = g_val + (h_func(adj_node, goal_node))
                if (set_contains(adj_node, is_blocked)):
                    continue
                elif (set_contains(adj_node, closed_nodes)):
                    continue
                else:                    
                    if (adj_node in g_func and g_func[adj_node] <= g_val):
                        continue
                    else:
                        open_queue.put((f_val, adj_node))
                        g_func[adj_node] = g_val
                        parent[adj_node] = current_node
            closed_nodes.add(current_node)
    
    if (not goal_found):
        print("No solution found")
        return None
    else:
        path = []
        parent_node = goal_node
        while (parent_node != start_node):
            path.insert(0, parent_node)
            parent_node = parent[parent_node]
        path.insert(0, start_node)
        ## TESTING
        #delta_time = (time.time() - start_time)
        #print("Closed")
        #print(closed_nodes)
        #print("Blocked")
        #print(is_blocked)
        #print("Path")
        #print(path)
        #print("--- %s seconds ---" % (delta_time))
        return path

def get_adjacent_nodes(node):
    return [(node[0], node[1] + 1),
        (node[0], node[1] - 1),
        (node[0] + 1, node[1]),
        (node[0] - 1, node[1])]
    
def set_contains(val, set):
    return val in set

if __name__ == "__main__":
    sys.exit(main())