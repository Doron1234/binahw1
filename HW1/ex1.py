import itertools
import copy
import search
import random
import math
import heapq
from search import astar_search
import time
from collections import Counter

def ords_to_check(treasures):
    tot = []
    if len(treasures)%2 == 1:
        for t1 in treasures:
            new = treasures.copy()
            new.remove(t1)
            if len(new)==0:
                return [[t1,"base"]]
            else:
                tot+=([[t1,"base"] + x for x in ords_to_check(new)])
    for t1 in treasures:
        for t2 in treasures:
            if t2 > t1:
                continue
            if t2==t1:
                continue
            new = treasures.copy()
            new.remove(t1)
            new.remove(t2)
            if len(new)==0:
                return [sorted([t1,t2]) + ["base"]]
            else:
                tot+=[sorted([t1,t2]) + ["base"] + x for x in ords_to_check(new)]
    return tot
def multiplyList(myList):
    # Multiply elements one by one
    result = 1
    for x in myList:
        result = result * x
    return result

def largest_num(numbers):
    lst = []
    for number in numbers:
        f = factors(number)
        lst = list((Counter(f) | Counter(lst)).elements())
    return multiplyList(lst)

ids = ["209993591", "Doron's id"]

def manh_dist(x, y):
    distance = 0
    for i in range(2):
        distance += abs(x[i] - y[i])
    return distance

def biased_manh_dist(x, y):
    return abs(x[0] - y[0])+ abs(x[1] - y[1]) + 1

def zipafy(list_of_lists):
    if not list_of_lists:
        return []  # Return an empty list if the input list is empty

    num_elements = len(list_of_lists[0])
    result_list = []

    for i in range(num_elements):
        tuple_from_each_list = tuple(inner_list[i][0] for inner_list in list_of_lists)
        result_list.append(tuple_from_each_list)

    return result_list

def create_neighboring_list(coord):
    x, y = coord
    result_list = [(x + 1, y), (x - 1, y), (x, y - 1), (x, y + 1)]
    return result_list

def divide_list_into_k_sublists(lst, k):
    if k==1:
        return [[lst]]
    n = len(lst)
    first = [lst.pop(0)]
    all = []
    for i in range(n-k+1):
        for l in itertools.combinations(lst,i):
            cur = first.copy()
            use = lst.copy()
            for a in l:
                cur.append(a)
                use.remove(a)
            x = divide_list_into_k_sublists(use,k-1)
            all += [[cur] + p for p in x]
    return all

from math import sqrt
def factors(n):    # (cf. https://stackoverflow.com/a/15703327/849891)
    j = 2
    while n > 1:
        for i in range(j, int(sqrt(n+0.05)) + 1):
            if n % i == 0:
                n //= i ; j = i
                yield i
                break
        else:
            if n > 1:
                yield n; break

class miniproblem(search.Problem):
    def __init__(self, initial, h_chosen="follow_sol", map=None, offset=0):
        if map is not None:
            self.map = map
        else:
            self.map = initial["map"]
        self.state = {}
        self.state["offset"] = offset
        for key in initial["pirate_ships"].keys():
            self.pirate_name = key
        self.state["pirate_ships"] = initial["pirate_ships"][key]
        self.state["finished"] = 0
        self.marine_ships = initial["marine_ships"]
        self.mod = largest_num([len(path) for path in self.marine_ships.values()])
        self.state["damaged"] = False
        self.initial = initial
        for x in range(len(self.map)):
            for y in range(len(self.map[0])):
                if self.map[x][y] == "B":
                    self.base = (x, y)
        self.treasures = initial["treasures"] + [self.base]
        self.treasure_names = initial["treasure_names"]
        self.state["cur_treasures"] = 0



    def actions(self, state):
        """Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""
        pirates_actions = []
        for data in [state["pirate_ships"]]:
            actions = [("wait",self.pirate_name)]
            pos = data[0]
            #sail actions:
            for i in range(4):
                if i==1:
                    new_pos = (pos[0],pos[1]+1)
                elif i==2:
                    new_pos = (pos[0],pos[1]-1)
                elif i==3:
                    new_pos = (pos[0]+1,pos[1])
                elif i==0:
                    new_pos = (pos[0]-1,pos[1])
                if new_pos[0]>=0 and new_pos[0]<len(self.map) and new_pos[1]>=0 and new_pos[1]<len(self.map[0]) and self.map[new_pos[0]][new_pos[1]]!="I":
                    actions.append(("sail",self.pirate_name,new_pos))
            #collecting actions
            if state["pirate_ships"][1]<2:
                counter = 0
                for i,treasure in enumerate(self.treasures[:-1]):
                    if state["pirate_ships"][1] == 0:
                        if manh_dist(treasure,pos)==1 and self.map[pos[0]][pos[1]] == "S" and counter == 0: #and i==0:
                            actions.append(("collect_treasure",self.pirate_name, self.treasure_names[i]))
                    elif state["pirate_ships"][1]<2:
                        if manh_dist(treasure, pos) == 1 and self.map[pos[0]][pos[1]] == "S" and counter == 1: # and i==1:
                            actions.append(("collect_treasure", self.pirate_name, self.treasure_names[i]))
                    counter += 1
            #deposit
            if self.map[pos[0]][pos[1]]=="B": # and state["pirate_ships"][1] == len(self.treasure_names):
                if state["cur_treasures"]>0:
                    actions.append(("deposit_treasure",self.pirate_name))
            pirates_actions.append(actions)

        return list(itertools.product(*pirates_actions))

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        #print(state["last_move"])
        ships_num = 1
        new_state = copy.deepcopy(state)
        for i in range(ships_num):
            act = action[i]
            if act[0] == "sail":
                new_state["pirate_ships"][0] = act[2]
            elif act[0] == "collect_treasure":
                #new_state["seen"] +=1
                new_state["pirate_ships"][1]+=1
                new_state["cur_treasures"] += 1
            elif act[0] == "deposit_treasure":
                new_state["cur_treasures"] = 0
                if len(self.treasure_names) == new_state["pirate_ships"][1]:
                    new_state["finished"] = 1
                #new_state["pirate_ships"][1]=0

        #move marines
        new_state["offset"] = (state["offset"] + 1)%self.mod

        # print(new_state["order"])
        new_state = self.check_collision(new_state)

        # if self.order_bol:
            # print("from: "+str(state["id"]))
            # print(self.h_order_state(state))
            # print("to: "+str(new_state["id"]))
            # print(new_state["pirate_ships"]["pirate_ship_1"])
            # print(new_state["treasures"])
            # print(new_state["order"])
            # print(action)
            # print(self.h_order_state(new_state))
            # print()

        return new_state

    def check_collision(self,state):
        for data in [state["pirate_ships"]]:
            pos = data[0]
            for marine,path in self.marine_ships.items():
                if manh_dist(path[state["offset"]%len(path)],pos)==0:
                    if state["cur_treasures"] > 0:
                        state["damaged"] = True
        return state

    def goal_test(self, state):
        """ Given a state, checks if this is the goal state.
         Returns True if it is, False otherwise."""
        if state["finished"] == 1:
            return True
        return False

    def h(self, node):
        s = node.state
        if s["damaged"]:
            return float('inf')
        sum = 0
        old_pos = [s["pirate_ships"][0]]
        for treasure in self.treasures[s["pirate_ships"][1]:]:
            new_old = []
            if treasure[0] == self.base[0] and treasure[1] == self.base[1]:
                pos = [self.base]
            else:
                pos = create_neighboring_list(treasure)
            cur_min = float('inf')
            for x in old_pos:
                for y in pos:
                    d = biased_manh_dist(x, y)
                    if d < cur_min:
                        cur_min = d
                        new_old = [y]
                    elif d == cur_min:
                        new_old.append(y)
            sum += cur_min
            old_pos = new_old
        return sum + len(self.treasures) - s["finished"] - s["pirate_ships"][1]




class OnePieceProblem(search.Problem):
    """This class implements a medical problem according to problem description file"""


    def __init__(self, initial, order = None, prebuilt = False, h_chosen="follow_sol",map = None):
        """Don't forget to implement the goal test
        You should change the initial to your own representation.
        search.Problem.__init__(self, initial) creates the root node"""
        search.Problem.__init__(self, initial)
        self.start = True
        self.id = 0
        #self.h_chosen = "normal"
        self.h_chosen = h_chosen
        self.state = initial
        if map is not None:
            self.map= map
        else:
            self.map = initial["map"]
            del self.state["map"]
        self.state["damaged"] = False
        self.state["id"] = self.assign_id()
        if self.h_chosen == "follow_sol":
            self.state["last_move"] = "start"
        if not prebuilt:
            for key,value in self.state["pirate_ships"].items():
                self.state["pirate_ships"][key] = [value,0]

            treasures = self.state["treasures"]
            for key, value in treasures.items():
                treasures[key] = [value,{ship:0 for ship in self.state["pirate_ships"].keys()}]
                treasures[key][1]["base"]=0

            marines = self.state["marine_ships"]
            for key, value in marines.items():
                marines[key]+=reversed(marines[key][1:-1])
        self.base = self.state["pirate_ships"][list(self.state["pirate_ships"].keys())[0]][0]

        self.order_bol = False
        if order is not None:
            self.order_bol = True
            self.state["order"] = order
            self.full_path = order
            self.costs = []

    def assign_id(self):
        #self.id+=1
        return self.id

    def solutionafy(self, solutions, length):
        for i,sol in enumerate(solutions):
            while len(sol)<length:
                sol.append((("wait",f"pirate_ship_{i+1}"),))
        # solutions += ["" for x in range(length)]
        #print(solutions)
        res = zipafy(solutions)
        #print(res)
        return res

    def actions(self, state):
        """Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""
        pirates_actions = []
        for pirate,data in state["pirate_ships"].items():
            actions = [("wait",pirate)]
            pos = data[0]
            #sail actions:
            for i in range(4):
                if i==1:
                    new_pos = (pos[0],pos[1]+1)
                elif i==2:
                    new_pos = (pos[0],pos[1]-1)
                elif i==3:
                    new_pos = (pos[0]+1,pos[1])
                elif i==0:
                    new_pos = (pos[0]-1,pos[1])
                if new_pos[0]>=0 and new_pos[0]<len(self.map) and new_pos[1]>=0 and new_pos[1]<len(self.map[0]) and self.map[new_pos[0]][new_pos[1]]!="I":
                    actions.append(("sail",pirate,new_pos))
            #collecting actions
            if state["pirate_ships"][pirate][1]<2:
                for treasure,t_data in state["treasures"].items():
                    if self.order_bol:
                        # print(state["pirate_ships"]["pirate_ship_1"])
                        # print(state["treasures"])
                        # print(state["order"])
                        # print()
                        if state["order"][0] == "base":
                            break
                        else:
                            if treasure != state["order"][0]:
                                continue
                    t_pos = t_data[0]
                    if manh_dist(t_pos,pos)==1:
                        actions.append(("collect_treasure",pirate,treasure))
            #deposit
            if self.map[pos[0]][pos[1]]=="B" and state["pirate_ships"][pirate][1] > 0:
                actions.append(("deposit_treasure",pirate))
            pirates_actions.append(actions)

        return list(itertools.product(*pirates_actions))

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        #print(state["last_move"])
        ships_num = len(state["pirate_ships"])
        new_state = copy.deepcopy(state)
        new_state["id"] = self.assign_id()
        if self.order_bol:
            new_state["order"] = new_state["order"].copy()
        if self.h_chosen == "follow_sol":
            new_state["last_move"] = action
        for i in range(ships_num):
            act = action[i]
            if act[0] == "sail":
                new_state["pirate_ships"][act[1]][0] = act[2]
            elif act[0] == "collect_treasure":
                new_state["treasures"][act[2]][1][act[1]]+=1
                new_state["pirate_ships"][act[1]][1]+=1
                if self.order_bol:
                    #print("removing from order")
                    new_state["order"].pop(0)
                    #print(state["order"])
            elif act[0] == "deposit_treasure":
                treasures = new_state["treasures"]
                if self.order_bol:
                    #print("removing from order")
                    new_state["order"].pop(0)
                for name,data in treasures.items():
                    if data[1][act[1]]>=1:
                        new_state["treasures"][name][1][act[1]] = 0
                        new_state["treasures"][name][1]["base"] += 1
                        new_state["pirate_ships"][act[1]][1] = 0
        #move marines

        for marine,data in new_state["marine_ships"].items():
            new_state["marine_ships"][marine].append(new_state["marine_ships"][marine].pop(0))

        # print(new_state["order"])
        new_state = self.check_collision(new_state)

        # if self.order_bol:
            # print("from: "+str(state["id"]))
            # print(self.h_order_state(state))
            # print("to: "+str(new_state["id"]))
            # print(new_state["pirate_ships"]["pirate_ship_1"])
            # print(new_state["treasures"])
            # print(new_state["order"])
            # print(action)
            # print(self.h_order_state(new_state))
            # print()

        return new_state


    def check_collision(self,state):
        for pirate,data in state["pirate_ships"].items():
            pos = data[0]
            for marine,path in state["marine_ships"].items():
                if manh_dist(path[0],pos)==0:
                    if state["pirate_ships"][pirate][1] > 0:
                        state["damaged"] = True
                        state["pirate_ships"][pirate][1] = 0
                        for treasure,not_needed in state["treasures"].items():
                            state["treasures"][treasure][1][pirate]=0
        return state

    def goal_test(self, state):
        """ Given a state, checks if this is the goal state.
         Returns True if it is, False otherwise."""
        for treasure,data in state["treasures"].items():
            if data[1]["base"] == 0:
                return False
        return True

    def h1(self, node):
        count = 0
        s = node.state
        for t_name,value in s["treasures"].items():
            count+=1
            for ship,num in value[1].items():
                if num==1:
                    count-=1
                break
        return count/len(s["pirate_ships"])

    def h2(self,node):
        s = node.state
        sum = 0
        for t_name, value in s["treasures"].items():
            pos = value[0]
            posses = []
            for i in range(4):
                if i == 1:
                    new_pos = (pos[0], pos[1] + 1)
                elif i == 2:
                    new_pos = (pos[0], pos[1] - 1)
                elif i == 3:
                    new_pos = (pos[0] + 1, pos[1])
                elif i == 0:
                    new_pos = (pos[0] - 1, pos[1])
                if new_pos[0] >= 0 and new_pos[0] < len(s["map"]) and new_pos[1] >= 0 and new_pos[1] < len(
                        s["map"][0]) and s["map"][new_pos[0]][new_pos[1]] == "S":
                    posses.append(new_pos)
            if value[1]["base"]==1:
                sum+=1
                break
            for pirate,value in value[1].items():
                if pirate == "base":
                    continue
                elif value == 1:
                    pos = s["pirate_ships"][pirate][0]
                    for i in range(4):
                        if i == 1:
                            new_pos = (pos[0], pos[1] + 1)
                        elif i == 2:
                            new_pos = (pos[0], pos[1] - 1)
                        elif i == 3:
                            new_pos = (pos[0] + 1, pos[1])
                        elif i == 0:
                            new_pos = (pos[0] - 1, pos[1])
                        if new_pos[0] >= 0 and new_pos[0] < len(s["map"]) and new_pos[1] >= 0 and new_pos[1] < len(
                                s["map"][0]) and s["map"][new_pos[0]][new_pos[1]] == "S":
                            posses.append(new_pos)
            if len(posses)==0:
                return float('inf')
            sum+= min([manh_dist(x, self.base) for x in posses])
        return sum/len(s["pirate_ships"])

    def h_follow_sol(self,node):
        # print("last move " + str(node.state["last_move"]))
        # print(self.solution[node.path_cost-1])
        # print(node.state["damaged"])
        # print()
        # print(self.solution)
        if self.solution == "unsolvable":
            return float('inf')
        if node.state["last_move"] == self.solution[node.path_cost-1]:
            return 0
        else:
            return float('inf')

    def h_order(self,node):
        s = node.state
        if s["damaged"]:
            return float('inf')
        sum = 0
        old_pos = [s["pirate_ships"][list(s["pirate_ships"].keys())[0]][0]]
        for treasure in s["order"]:
            new_old = []
            if treasure == "base":
                pos = [self.base]
            else:
                pos = create_neighboring_list(s["treasures"][treasure][0])
            cur_min = float('inf')
            for x in old_pos:
                for y in pos:
                    d = biased_manh_dist(x,y)
                    if d<cur_min:
                        cur_min = d
                        new_old = [y]
                    elif d==cur_min:
                        new_old.append(y)
            sum+=cur_min
            old_pos = new_old
        return sum

    def h_order_state(self,node):
        s = node
        if s["damaged"]:
            return float('inf')
        sum = 0
        old_pos = [s["pirate_ships"][list(s["pirate_ships"].keys())][0]]
        for treasure in s["order"]:
            new_old = []
            if treasure == "base":
                pos = [self.base]
            else:
                pos = create_neighboring_list(s["treasures"][treasure][0])
            cur_min = float('inf')
            for x in old_pos:
                for y in pos:
                    d = biased_manh_dist(x, y)
                    if d < cur_min:
                        cur_min = d
                        new_old = [y]
                    elif d == cur_min:
                        new_old.append(y)
            sum += cur_min
            old_pos = new_old
        return sum


    def h(self, node):
        """ This is the heuristic. It gets a node (not a state,
        state can be accessed via node.state)
        and returns a goal distance estimate"""
        if self.start:
            if self.h_chosen == "follow_sol":
                ships_num = len(self.state["pirate_ships"])
                treasures = list(self.state["treasures"].keys())
                partitions = divide_list_into_k_sublists(treasures, ships_num)
                optimal_solution = None
                min_len = float('inf')
                t0 = time.time()
                for partition in partitions:
                    max_len = 0
                    solutions = []
                    for i in range(1, ships_num + 1):
                        send_state = copy.deepcopy(self.state)
                        send_state["pirate_ships"] = {
                            f"pirate_ship_{i}": send_state["pirate_ships"][f"pirate_ship_{i}"]}
                        send_state["treasures"] = {}
                        for treasure in partition[i - 1]:
                            send_state["treasures"][treasure] = self.state["treasures"][treasure]
                        p = OnePieceProblem(send_state, prebuilt=True, h_chosen="solo_ship",map = self.map)
                        ass = astar_search(p)
                        if ass is not None:
                            plan = ass.solution()
                            l = len(plan)
                            if l > max_len:
                                max_len = l
                            solutions.append(plan)
                        else:
                            self.start = False
                            self.solution = "unsolvable"
                            return float('inf')
                    if max_len < min_len:
                        min_len = max_len
                        optimal_solution = solutions
                if min_len == float('inf'):
                    self.solution = "Unsolvable"
                else:
                    self.solution = (self.solutionafy(optimal_solution, min_len))
                # print()
                # print(f"time: {time.time() - t0}")

            # h special stuff:
            if self.h_chosen == "solo_ship":
                chosen_plan = None
                shortest = float('inf')
                temp = ords_to_check(list(self.state["treasures"].keys()))
                for i, ord in enumerate(temp):
                    # print(ord)
                    # print(i/len(temp))
                    t1 = time.time()
                    temp_len = 0
                    temp_plan = []
                    # print()
                    #print(ord)
                    for lst in split_list_by_base(ord):
                        #print(lst)
                        mini_state = {}
                        mini_state["map"] = self.map
                        # print(f"org {lst}")
                        mini_state["treasures"] = []
                        for treas in lst:
                            if treas != "base":
                                mini_state["treasures"] += self.state["treasures"][treas][:-1]
                        mini_state["marine_ships"] = self.state["marine_ships"]
                        pirate_name = list(self.state["pirate_ships"].keys())[0]
                        mini_state["pirate_ships"] = {pirate_name: copy.deepcopy(self.state["pirate_ships"][pirate_name])}
                        mini_state["treasure_names"] = lst[:-1]
                        p = miniproblem(copy.deepcopy(mini_state), offset=temp_len)
                        ass = astar_search(p)
                        #print(ass.solution())
                        ass2 = ass
                        #print("on to as2")
                        if len(lst) == 3:
                            mini_state["treasures"] = []
                            for treas in lst[::-1]:
                                if treas != "base":
                                    mini_state["treasures"] += self.state["treasures"][treas][:-1]
                            mini_state["treasure_names"] = list(reversed(lst))[1:]
                            #print(mini_state["treasure_names"])
                            p2 = miniproblem(mini_state, offset = temp_len)
                            ass2 = astar_search(p2)
                            #print(ass2.solution())
                        #print(ass == None)
                        if ass is not None:
                            if len(ass2.solution())<len(ass.solution()):
                                ass = ass2
                            temp_plan += ass.solution()
                            temp_len = len(temp_plan)
                        else:
                            self.solution = "unsolvable"
                            return float('inf')
                    if temp_len < shortest:
                        chosen_plan = temp_plan
                        #print(chosen_plan)
                        #print(len(chosen_plan))
                        shortest = temp_len
                    # t2 = time.time()
                    # print(t2-t1)
                if chosen_plan is None:
                    self.solution = "unsolvable"
                else:
                    self.solution = chosen_plan
                #print(self.solution)
            if self.h_chosen == "solo_ship":
                self.h_chosen = "follow_sol"
            self.start = False

        if self.h_chosen=="follow_sol":
            return self.h_follow_sol(node)
        if self.h_chosen=="order":
            return self.h_order(node)
        return self.h2(node)

    """Feel free to add your own functions
    (-2, -2, None) means there was a timeout"""




def split_list_by_base(input_list):
    sublists = []
    current_sublist = []

    for item in input_list:
        if current_sublist:
            if current_sublist[-1] == "base":
                sublists.append(current_sublist)
                current_sublist = []
        current_sublist.append(item)

    if current_sublist:
        sublists.append(current_sublist)

    return sublists

def create_onepiece_problem(game):
    return OnePieceProblem(game)

