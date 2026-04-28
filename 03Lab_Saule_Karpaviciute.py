import os

import pandas as pd 


base_dir = os.path.dirname(__file__)
file_path = os.path.join(base_dir, "duomenys", "athlete_events.csv")

df = pd.read_csv(file_path).sample(n=50_000, random_state=42)

base_dir = os.path.dirname(__file__)
file_path = os.path.join(base_dir, "athlete_events.csv")
df.to_csv("athlete_events.csv", index=False)


import time
import random
import matplotlib.pyplot as plt

df = pd.read_csv("athlete_events.csv")

EXACT_KEY = "ID"
BST_KEY = "Year"
TOPK_KEY = "Age"

df = df.dropna(subset=[EXACT_KEY, BST_KEY, TOPK_KEY])
data = df.to_dict("records")



def linear_search(arr, key, value):
    for item in arr:
        if item[key] == value:
            return item
    return None


def binary_search(arr, key, value):
    low, high = 0, len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid][key] == value:
            return arr[mid]
        elif arr[mid][key] < value:
            low = mid + 1
        else:
            high = mid - 1
    return None


def jump_search(arr, key, value):
    n = len(arr)
    step = int(n ** 0.5)
    prev = 0

    while arr[min(step, n) - 1][key] < value:
        prev = step
        step += int(n ** 0.5)
        if prev >= n:
            return None

    for i in range(prev, min(step, n)):
        if arr[i][key] == value:
            return arr[i]
    return None


def interpolation_search(arr, key, value):
    low, high = 0, len(arr) - 1

    while low <= high and arr[low][key] <= value <= arr[high][key]:
        if arr[high][key] == arr[low][key]:
            break

        pos = low + int(
            (high - low)
            * (value - arr[low][key])
            / (arr[high][key] - arr[low][key])
        )

        if arr[pos][key] == value:
            return arr[pos]
        elif arr[pos][key] < value:
            low = pos + 1
        else:
            high = pos - 1

    return None

def benchmark_search():
    sizes = [1000, 10000, 50000]
    results = {"linear": [], "binary": [], "jump": [], "interp": []}

    for n in sizes:
        subset = data[:n]
        subset_sorted = sorted(subset, key=lambda x: x[EXACT_KEY])

        target = random.choice(subset_sorted)[EXACT_KEY]

        for name, func, arr in [
            ("linear", linear_search, subset),
            ("binary", binary_search, subset_sorted),
            ("jump", jump_search, subset_sorted),
            ("interp", interpolation_search, subset_sorted),
        ]:
            times = []
            for _ in range(3):
                start = time.perf_counter()
                func(arr, EXACT_KEY, target)
                end = time.perf_counter()
                times.append((end - start) * 1000)

            results[name].append(sum(times) / 3)

    return sizes, results


class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.left = None
        self.right = None


class BST:
    def __init__(self):
        self.root = None

    def insert(self, key, value):
        def _insert(node, key, value):
            if not node:
                return Node(key, value)
            if key < node.key:
                node.left = _insert(node.left, key, value)
            else:
                node.right = _insert(node.right, key, value)
            return node

        self.root = _insert(self.root, key, value)

    def search(self, key):
        node = self.root
        while node:
            if key == node.key:
                return node.value
            node = node.left if key < node.key else node.right
        return None

    def inorder(self):
        res = []

        def _in(node):
            if node:
                _in(node.left)
                res.append(node.key)
                _in(node.right)

        _in(self.root)
        return res

    def range_query(self, low, high):
        res = []

        def _range(node):
            if not node:
                return
            if low < node.key:
                _range(node.left)
            if low <= node.key <= high:
                res.append(node.value)
            if node.key < high:
                _range(node.right)

        _range(self.root)
        return res
    
    def test_bst(): 
        tree = BST()

        for row in data[:50000]:
            tree.insert(row[BST_KEY], row)

        low, high = 2000, 2010

        start = time.perf_counter()
        res_tree = tree.range_query(low, high)
        t1 = (time.perf_counter() - start) * 1000

        start = time.perf_counter()
        res_naive = [r for r in data[:50000] if low <= r[BST_KEY] <= high]
        t2 = (time.perf_counter() - start) * 1000

        print("BST:", t1, "ms")
        print("Naive:", t2, "ms")
        print("Count:", len(res_tree))


class MinHeap:
    def __init__(self):
        self.heap = []

    def insert(self, val):
        self.heap.append(val)
        self._up(len(self.heap) - 1)

    def _up(self, i):
        while i > 0:
            p = (i - 1) // 2
            if self.heap[p][TOPK_KEY] <= self.heap[i][TOPK_KEY]:
                break
            self.heap[p], self.heap[i] = self.heap[i], self.heap[p]
            i = p

    def _down(self, i):
        n = len(self.heap)
        while True:
            l, r = 2 * i + 1, 2 * i + 2
            smallest = i

            if l < n and self.heap[l][TOPK_KEY] < self.heap[smallest][TOPK_KEY]:
                smallest = l
            if r < n and self.heap[r][TOPK_KEY] < self.heap[smallest][TOPK_KEY]:
                smallest = r

            if smallest == i:
                break

            self.heap[i], self.heap[smallest] = self.heap[smallest], self.heap[i]
            i = smallest

    def replace_root(self, val):
        self.heap[0] = val
        self._down(0)


def top_k():
    k = 10
    heap = MinHeap()

    for row in data[:50000]:
        if len(heap.heap) < k:
            heap.insert(row)
        elif row[TOPK_KEY] > heap.heap[0][TOPK_KEY]:
            heap.replace_root(row)

    print("Top 10:", [r[TOPK_KEY] for r in heap.heap])


def plot_results(sizes, results):
    for key in results:
        plt.plot(sizes, results[key], label=key)

    plt.xlabel("n")
    plt.ylabel("ms")
    plt.legend()
    plt.show()

def test_bst():
    print("BST veikia")
    
if __name__ == "__main__":
    sizes, results = benchmark_search()
    plot_results(sizes, results)

    test_bst()
    top_k()