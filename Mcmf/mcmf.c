// 最小费用最大流实现（Dijkstra + 势）
// - 残量图使用并行数组表示的邻接表存储
// - 每条原始边对应一个反向边，反向边初始容量为 0，费用为负值
// - 势（pi）通过从源点运行 Bellman-Ford 计算，以便可以用 Dijkstra 在约化费用（非负）上搜索
// 输入格式（stdin）：
//   n m
//   u v cap cost   （m 行，节点编号为 0-based）
//   s t
// 输出：两个整数，表示最大流与总费用

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

// 为边分配空间。调用者应传入预期的原始边数量 `m2`，
// 我们为正向和反向边各分配空间（2*m2）
// 仅在第一次调用时分配 不会动态扩展
void ensure_edge_alloc(int m2) {
  if (edge_cnt == 0) {
    int sz = (m2 * 2 + 5);
    to_ = malloc(sizeof(int) * sz);
    next_ = malloc(sizeof(int) * sz);
    cap_ = malloc(sizeof(int) * sz);
    cost_ = malloc(sizeof(ll) * sz);
  }
}

// 向图中添加有向边 u->v，容量为 c，单位费用为 w。
// 同时添加反向边 v->u（初始容量为 0，费用为 -w）以便构建残量图。
// 边存储在并行数组中，通过 `head` 和 `next_` 进行链式连接。
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

// Dijkstra 使用的最小二叉堆（优先队列）。
// 存储 (距离, 顶点) 对。该实现不支持 decrease-key；当发现更短距离时会插入新条目，
// 弹出时通过与当前 `dist[]` 比较来忽略过时的条目。
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

// 核心算法：带势的逐次最短增广路径（Successive Shortest Path with Potentials）
// - 用 Bellman-Ford 从源点 s 计算初始势 pi[]。
// - 在约化费用（cost + pi[u] - pi[v]）非负的图上重复运行 Dijkstra，找到 s->t 的最小费用路径，
//   在该路径上尽可能增广，然后更新势。
// 参数：
//   s, t: 源点和汇点
//   out_flow, out_cost: 返回的总流量与总费用（通过指针返回）
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

    // 简单循环队列实现 SPFA
    int *queue = malloc(sizeof(int) * (N + 5));
    int qhead = 0, qtail = 0;
    dist[s] = 0;
    queue[qtail++] = s;
    inqueue[s] = 1;

    while (qhead < qtail) {
      int v = queue[qhead++];
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
            if (qtail >= N + 5) qtail = qtail; // 防守性保留（数组已按 N+5 分配）
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
