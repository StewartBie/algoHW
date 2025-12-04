// 最小费用最大流（MCMF）实现
// 残量图用并行数组实现；每条边同时插入反向边（容量0，费用取负）。
// 输入：
//   n m
//   u v cap cost  （m 行，0-based）
//   s t
// 输出：`flow cost`

#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef long long ll;
const ll INF = (ll)9e18;

// Graph storage (adjacency list using parallel arrays)
// N: number of vertices
int N; // number of vertices
int head_alloc = 0; // reserved for future dynamic alloc (unused)
int *head;           // head[u] = index of first edge from u, -1 if none

// Edge arrays: for each edge index e
//   to_[e]   - destination vertex
//   next_[e] - next edge index from the same source
//   cap_[e]  - remaining capacity on this directed edge
//   cost_[e] - per-unit cost (reverse edge stores -original_cost)
int edge_cnt = 0;
int *to_, *next_, *cap_;
ll *cost_;

// 为边数组分配一次性空间（2*m2 条记录）
void ensure_edge_alloc(int m2) {
  if (edge_cnt == 0) {
    int sz = (m2 * 2 + 5);
    to_ = malloc(sizeof(int) * sz);
    next_ = malloc(sizeof(int) * sz);
    cap_ = malloc(sizeof(int) * sz);
    cost_ = malloc(sizeof(ll) * sz);
  }
}

// 添加有向边 u->v（cap c，cost w）及反向边（cap 0，cost -w）。
void add_edge(int u, int v, int c, ll w) {
  // forward edge
  to_[edge_cnt] = v;
  cap_[edge_cnt] = c;
  cost_[edge_cnt] = w;
  next_[edge_cnt] = head[u];
  head[u] = edge_cnt++;
  // reverse edge (initially zero capacity)
  to_[edge_cnt] = u;
  cap_[edge_cnt] = 0;
  cost_[edge_cnt] = -w;
  next_[edge_cnt] = head[v];
  head[v] = edge_cnt++;
}

// 二叉堆（保留供 Dijkstra 使用）。不支持 decrease-key，采用重复入堆并在弹出时跳过过时条目。
typedef struct {
  ll d; // distance
  int v; // vertex
} Pair;
Pair *heap_arr;
int heap_sz = 0;

// 将 (d, v) 插入堆中
void heap_push(ll d, int v) {
  int i = ++heap_sz;
  heap_arr[i].d = d;
  heap_arr[i].v = v;
  while (i > 1) {
    int p = i >> 1;
    if (heap_arr[p].d <= heap_arr[i].d)
      break;
    Pair tmp = heap_arr[p];
    heap_arr[p] = heap_arr[i];
    heap_arr[i] = tmp;
    i = p;
  }
}

// 弹出最小的 (d, v)。调用方需通过与最新的 dist[v] 比较来判断条目是否过时。
Pair heap_pop() {
  Pair ret = heap_arr[1];
  heap_arr[1] = heap_arr[heap_sz--];
  int i = 1;
  while (1) {
    int l = i << 1, r = l + 1, smallest = i;
    if (l <= heap_sz && heap_arr[l].d < heap_arr[smallest].d)
      smallest = l;
    if (r <= heap_sz && heap_arr[r].d < heap_arr[smallest].d)
      smallest = r;
    if (smallest == i)
      break;
    Pair tmp = heap_arr[i];
    heap_arr[i] = heap_arr[smallest];
    heap_arr[smallest] = tmp;
    i = smallest;
  }
  return ret;
}

// 主算法（每轮用 SPFA 找最小费用增广路径并增广）
// 参数：s 源点，t 汇点，out_flow/out_cost 为输出指针
void min_cost_max_flow(int s, int t, long long *out_flow, long long *out_cost) {
  // 使用队列（SPFA）在残量图中寻找每轮的最小费用路径并增广
  ll flow = 0, cost = 0;
  ll *dist = malloc(sizeof(ll) * N);     // 最短费用距离
  int *prevv = malloc(sizeof(int) * N);  // 前驱顶点
  int *preve = malloc(sizeof(int) * N);  // 前驱边索引
  int *inqueue = malloc(sizeof(int) * N); // 队列内标记

  // 每次找到一条最小费用路径并增广
  while (1) {
    for (int i = 0; i < N; ++i) {
      dist[i] = INF;
      prevv[i] = -1;
      preve[i] = -1;
      inqueue[i] = 0;
    }

    // 环形缓冲区实现 SPFA 队列，容量设为 N*5+5（足够避免频繁溢出）
    int capq = N * 5 + 5;
    int *queue = malloc(sizeof(int) * capq);
    int qhead = 0, qtail = 0;
    dist[s] = 0;
    queue[qtail++] = s;
    if (qtail == capq) qtail = 0;
    inqueue[s] = 1;

    while (qhead != qtail) {
      int v = queue[qhead++];
      if (qhead == capq) qhead = 0;
      inqueue[v] = 0;
      for (int e = head[v]; e != -1; e = next_[e]) {
        if (cap_[e] <= 0) continue;
        int to = to_[e];
        if (dist[to] > dist[v] + cost_[e]) {
          dist[to] = dist[v] + cost_[e];
          prevv[to] = v;
          preve[to] = e;
          if (!inqueue[to]) {
            inqueue[to] = 1;
            queue[qtail++] = to;
            if (qtail == capq) qtail = 0;
          }
        }
      }
    }
    free(queue);

    // 若汇点不可达则结束
    if (prevv[t] == -1) break;

    // 计算路径的最小残量
    int d = INT_MAX;
    for (int v = t; v != s; v = prevv[v]) {
      int e = preve[v];
      if (e == -1) { d = 0; break; }
      if (cap_[e] < d) d = cap_[e];
    }
    if (d == 0) break;

    // 沿路径增广并累加费用
    for (int v = t; v != s; v = prevv[v]) {
      int e = preve[v];
      cap_[e] -= d;
      cap_[e ^ 1] += d;
      cost += (ll)d * cost_[e];
    }
    flow += d;
  }

  *out_flow = flow;
  *out_cost = cost;

  free(dist);
  free(prevv);
  free(preve);
  free(inqueue);
}

int main() {
  int n, m;
  if (scanf("%d %d", &n, &m) != 2)
    return 0;
  N = n;
  head = malloc(sizeof(int) * N);
  for (int i = 0; i < N; i++)
    head[i] = -1;
  ensure_edge_alloc(m);
  int s, t;
  // we'll read edges then read s t on next line or last two inputs
  // assume next m lines: u v cap cost, then a line: s t
  for (int i = 0; i < m; i++) {
    int u, v, c;
    ll w;
    scanf("%d %d %d %lld", &u, &v, &c, &w);
    add_edge(u, v, c, w);
  }
  if (scanf("%d %d", &s, &t) != 2)
    return 0;
  long long flow = 0, cost = 0;
  min_cost_max_flow(s, t, &flow, &cost);
  printf("%lld %lld\n", flow, cost);
  return 0;
}
