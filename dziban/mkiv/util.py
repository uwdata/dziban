def foreach(iterable, fn):
  for v in iterable:
    fn(v)

def filter_sols(sols):
  good = []
  for v1 in sols:
    better = [v1.g <= v2.g or v1.d <= v2.d for v2 in sols]
    accept = all(better)
    if (accept): good.append(v1)

  return good

def construct_graph(sols):
  sols.sort(key = lambda v : len(v.graphscape_list))

  foreach(sols, lambda v : v.graphscape_list.sort())
  
  start = 'start'
  nodes = { () : start }
  graph = { start: {} }

  seen = set()
  seen_vis = set()
  for v in sols:
    # print(v.graphscape_list)
    i = -1
    while (i + len(v.graphscape_list) >= 0 and tuple(v.graphscape_list[:i]) not in nodes): i -= 1
    prev_rules = tuple(v.graphscape_list[:i])
    edit = v.graphscape_list[-1]
    parent = nodes[prev_rules]

    new_rules = tuple(v.graphscape_list)

    # if (new_rules in seen):
    #   if (tuple(v.props) in seen_vis):
        # print('error')
    seen.add(new_rules)
    seen_vis.add(tuple(v.props))

    nodes[new_rules] = v
    graph[parent][edit] = v
    graph[v] = {}

    # print(nodes.keys())

  return graph