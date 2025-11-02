
from collections import deque, defaultdict
import csv

class MaxFlowEKTracked:
    def __init__(self):
        self.graph = defaultdict(dict)
        self.original_cap = defaultdict(dict)

    def add_edge(self, u, v, capacity):
        if capacity < 0:
            raise ValueError("Capacity must be non-negative")
        if v not in self.graph[u]:
            self.graph[u][v] = 0
        if u not in self.graph[v]:
            self.graph[v][u] = 0
        self.graph[u][v] += capacity
        self.original_cap[u][v] = self.original_cap[u].get(v, 0) + capacity

    def _bfs(self, s, t, parent):
        parent.clear()
        parent[s] = None
        q = deque([s])
        while q:
            u = q.popleft()
            for v, cap in self.graph[u].items():
                if v not in parent and cap > 0:
                    parent[v] = u
                    if v == t:
                        return True
                    q.append(v)
        return False

    def max_flow(self, s, t):
        parent = {}
        flow_value = 0
        while self._bfs(s, t, parent):
            v = t
            bottleneck = float('inf')
            while v != s:
                u = parent[v]
                bottleneck = min(bottleneck, self.graph[u][v])
                v = u
            v = t
            while v != s:
                u = parent[v]
                self.graph[u][v] -= bottleneck
                self.graph[v][u] += bottleneck
                v = u
            flow_value += bottleneck
        return flow_value

    def edge_flow(self, u, v):
        orig = self.original_cap.get(u, {}).get(v, 0)
        res = self.graph.get(u, {}).get(v, 0)
        return max(0, orig - res)

    def flows(self):
        f = defaultdict(dict)
        for u, d in self.original_cap.items():
            for v in d:
                f[u][v] = self.edge_flow(u, v)
        return f

def build_and_solve():
    ek = MaxFlowEKTracked()
    terminals = ["Термінал 1", "Термінал 2"]
    warehouses = ["Склад 1", "Склад 2", "Склад 3", "Склад 4"]
    stores = ["Магазин 1","Магазин 2","Магазин 3","Магазин 4","Магазин 5","Магазин 6",
              "Магазин 7","Магазин 8","Магазин 9","Магазин 10","Магазин 11","Магазин 12","Магазин 13","Магазин 14"]

    edges_tw = [
        ("Термінал 1","Склад 1",25),
        ("Термінал 1","Склад 2",20),
        ("Термінал 1","Склад 3",15),
        ("Термінал 2","Склад 3",15),
        ("Термінал 2","Склад 4",30),
        ("Термінал 2","Склад 2",10),
    ]
    edges_ws = [
        ("Склад 1","Магазин 1",15),
        ("Склад 1","Магазин 2",10),
        ("Склад 1","Магазин 3",20),
        ("Склад 2","Магазин 4",15),
        ("Склад 2","Магазин 5",10),
        ("Склад 2","Магазин 6",25),
        ("Склад 3","Магазин 7",20),
        ("Склад 3","Магазин 8",15),
        ("Склад 3","Магазин 9",10),
        ("Склад 4","Магазин 10",20),
        ("Склад 4","Магазин 11",10),
        ("Склад 4","Магазин 12",15),
        ("Склад 4","Магазин 13",5),
        ("Склад 4","Магазин 14",10),
    ]

    SRC = "Джерело"
    SNK = "Сток"

    # Source→terminals capacities = sum of outgoing from each terminal
    cap_out_t = defaultdict(int)
    for u,v,c in edges_tw:
        cap_out_t[u] += c
    for t in terminals:
        ek.add_edge(SRC, t, cap_out_t[t])

    for u,v,c in edges_tw:
        ek.add_edge(u,v,c)
    for u,v,c in edges_ws:
        ek.add_edge(u,v,c)

    cap_in_s = defaultdict(int)
    for u,v,c in edges_ws:
        cap_in_s[v] += c
    for s in stores:
        ek.add_edge(s, SNK, cap_in_s[s])

    max_val = ek.max_flow(SRC, SNK)
    f = ek.flows()
    return ek, f, max_val, terminals, warehouses, stores

def decompose_terminal_store(f, terminals, warehouses, stores, warehouse):
    # Build a bipartite flow per-warehouse to assign terminal→store portions
    ekw = MaxFlowEKTracked()
    SRC = "SRC"
    SNK = "SNK"
    inflows = [(t, warehouse, f.get(t, {}).get(warehouse, 0)) for t in terminals]
    inflows = [(t, w, cap) for t,w,cap in inflows if cap>0]
    outflows = [(warehouse, s, f.get(warehouse, {}).get(s, 0)) for s in stores]
    outflows = [(w,s,cap) for w,s,cap in outflows if cap>0]

    for t,_,cap in inflows:
        ekw.add_edge(SRC, t, cap)
    for t,_,_ in inflows:
        for _,s,_ in outflows:
            ekw.add_edge(t, s, 10**9)
    for _,s,cap in outflows:
        ekw.add_edge(s, SNK, cap)

    val = ekw.max_flow(SRC, SNK)
    tf = ekw.flows()
    ts = defaultdict(int)
    for t in [x[0] for x in inflows]:
        for _,s,_ in outflows:
            ts[(t,s)] += tf.get(t, {}).get(s, 0)
    return ts, val

if __name__ == "__main__":
    ek, flows, max_val, terminals, warehouses, stores = build_and_solve()
    # Save edge flows
    with open("edge_flows.csv","w",newline="",encoding="utf-8") as fcsv:
        w = csv.writer(fcsv)
        w.writerow(["Від","До","Потік","Ємність","Насичено?"])
        for u, d in ek.original_cap.items():
            for v, cap in d.items():
                if u=="Джерело" or v=="Сток":
                    continue
                used = flows.get(u,{}).get(v,0)
                w.writerow([u, v, used, cap, "так" if used==cap else "ні"])

    # Decompose terminal→store
    ts_total = defaultdict(int)
    for wname in warehouses:
        ts, val = decompose_terminal_store(flows, terminals, warehouses, stores, wname)
        for k, v in ts.items():
            ts_total[k] += v

    with open("terminal_store_flow.csv","w",newline="",encoding="utf-8") as fcsv:
        w = csv.writer(fcsv)
        w.writerow(["Термінал","Магазин","Фактичний Потік (од.)"])
        for (t,s), flow in sorted(ts_total.items()):
            w.writerow([t,s,flow])

    print("Максимальний потік:", max_val)
