import json

def foreach(iterable, fn):
  for v in iterable:
    fn(v)

def filter_sols(best_draco, best_graphscape, name):
  best_draco_vl = set(json.dumps(c.props[name]) for c in best_draco)

  sols = list(filter(lambda c: json.dumps(c.props[name]) in best_draco_vl, best_graphscape))

  if (len(sols) > 0):
    return sols
  else:
    print('none')
    return best_draco
  # good = []
  # for v1 in sols:
  #   better = [v1.g <= v2.g or v1.d <= v2.d for v2 in sols]
  #   accept = all(better)
  #   if (accept): good.append(v1)

  # return good

def normalize(arr):
  hi = max(arr)
  lo = min(arr)

  return [(n - lo) / (hi - lo) for n in arr]

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