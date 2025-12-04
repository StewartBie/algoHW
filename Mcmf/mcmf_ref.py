#!/usr/bin/env python3
"""
Reference Min-Cost Max-Flow implementation for correctness testing.
Uses Bellman-Ford (O(VE) per augmentation) for simplicity and reliability.

Input format:
 n m
 u v cap cost  (m lines, 0-based)
 s t

Outputs: prints two integers: flow cost
"""
import sys
from collections import deque


class Edge:
    def __init__(self, u, v, cap, cost):
        self.u = u
        self.v = v
        self.cap = cap
        self.cost = cost
        self.rev = None


def read_input(fp):
    data = fp.read().strip().split()
    if not data:
        return None
    it = iter(data)
    n = int(next(it))
    m = int(next(it))
    edges = []
    for _ in range(m):
        u = int(next(it)); v = int(next(it)); c = int(next(it)); w = int(next(it))
        edges.append((u, v, c, w))
    s = int(next(it)); t = int(next(it))
    return n, m, edges, s, t


def min_cost_max_flow(n, edges, s, t):
    # build residual graph
    G = [[] for _ in range(n)]
    def add_edge(u, v, cap, cost):
        a = Edge(u, v, cap, cost)
        b = Edge(v, u, 0, -cost)
        a.rev = b
        b.rev = a
        G[u].append(a)
        G[v].append(b)

    for (u, v, c, w) in edges:
        add_edge(u, v, c, w)

    flow = 0
    cost = 0
    INF = 10**30
    # augment until no path
    while True:
        # Bellman-Ford
        dist = [INF]*n
        inq = [False]*n
        prev = [None]*n  # store edge
        dist[s] = 0
        q = deque([s]); inq[s]=True
        while q:
            u = q.popleft(); inq[u]=False
            for e in G[u]:
                if e.cap>0 and dist[e.v] > dist[u] + e.cost:
                    dist[e.v] = dist[u] + e.cost
                    prev[e.v] = e
                    if not inq[e.v]:
                        inq[e.v] = True
                        q.append(e.v)

        if prev[t] is None:
            break

        # find bottleneck
        d = 10**18
        v = t
        while v != s:
            e = prev[v]
            if e is None:
                d = 0; break
            d = min(d, e.cap)
            v = e.u
        if d==0: break

        # augment
        v = t
        while v != s:
            e = prev[v]
            e.cap -= d
            e.rev.cap += d
            cost += d * e.cost
            v = e.u
        flow += d

    return flow, cost


def main():
    inp = read_input(sys.stdin)
    if inp is None:
        return
    n,m,edges,s,t = inp
    flow,cost = min_cost_max_flow(n, edges, s, t)
    print(flow, cost)


if __name__=='__main__':
    main()
