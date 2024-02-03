#Doron Heller 214422750
#Daniel Sharon 209993591

# This is O(nlogn)
def twoSum(nums: list[int], target: int) -> list[int]:
    ordered = sorted([(num, ind) for num, ind in zip(nums, range(len(nums)))])
    i1 = 0
    i2 = len(ordered) - 1
    while (ordered[i1][0] + ordered[i2][0] != target) and i1 != i2:
        if ordered[i1][0] + ordered[i2][0] > target:
            i2 -= 1
        elif ordered[i1][0] + ordered[i2][0] < target:
            i1 += 1
    if ordered[i1][0] + ordered[i2][0] == target:
        return [ordered[i1][1], ordered[i2][1]]
    else:
        return [-1, -1]


def max_profit(prices):
    best = 0
    lowest = prices[0]
    for price in prices:
        if price < lowest:
            lowest = price
        if price - lowest > best:
            best = price - lowest
    return best


class Node:
    def __init__(self, value, next_node=None):
        self.value = value
        self.next = next_node

    def __str__(self):
        return str(self.value)
    # def __str__(self):
    #     return str(self.value) +"->"+ str(self.next)


def read_file(file_path: str) -> Node:
    with open(file_path, 'r') as f:
        text = f.read()
        l = text.split(";")
        l = [int(num) for num in l]
    last = Node(l[-1])
    for num in reversed(l[:-1]):
        head = Node(num, last)
        last = head
    return last


def get_length(head: Node) -> int:
    if head is None:
        return 0
    lens = 1
    while not (head.next is None):
        lens += 1
        head = head.next
    return lens


def sort_in_place(head: Node) -> Node:
    for i in range(get_length(head) - 1):
        cur = head
        for j in range(get_length(head) - 1 - i):
            if cur.value > cur.next.value:
                temp = cur.value
                cur.value = cur.next.value
                cur.next.value = temp
            cur = cur.next
    return head

# This is O(n^2)
# It requires O(1) extra space
