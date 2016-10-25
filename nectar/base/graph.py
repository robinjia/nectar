"""A directed graph."""
import collections
import copy
import numpy as np
import pygraphviz as pgz

class Graph(object):
  """A labeled, unweighted directed graph."""
  def __init__(self):
    self.nodes = []
    self.edges = []  # triples (i, j, label)
    self.label2index = collections.defaultdict(set)
    self.out_edges = collections.defaultdict(set)
    self.in_edges = collections.defaultdict(set)
    self.edge_to_label = {}
    self.conn_comps = []  # Connected components

  @classmethod
  def make_chain(cls, nodes):
    """Make a chain-structured graph from the list of nodes."""
    g = cls()
    for n in nodes:
      g.add_node(n)
    for i in range(len(nodes) - 1):
      g.add_edge(i, i+1)
    return g

  @classmethod
  def from_string(cls, s):
    """Load a Graph from a string generated by make_string()"""
    g = cls()
    toks = s.split(' ')
    nodes = toks[:-1]
    edges = [x.split(',') for x in toks[-1].split(';')]
    for n in nodes:
      g.add_node(n)
    for e in edges:
      e_new = [int(e[0]), int(e[1])] + e[2:]
      g.add_edge(*e_new)
    return g

  def make_string(self):
    """Serialize the graph as a string."""
    edge_str = ';'.join('%d,%d,%s' % (i, j, lab) for i, j, lab in self.edges)
    return '%s %s' % (' '.join(self.nodes), edge_str)

  def get_num_nodes(self):
    return len(self.nodes)

  def get_num_edges(self):
    return len(self.edges)

  def add_node(self, node_label):
    new_index = len(self.nodes)
    self.nodes.append(node_label)
    self.label2index[node_label].add(new_index)
    self.conn_comps.append(set([new_index]))

  def check_index_in_range(self, ind):
    if ind < 0 or ind >= len(self.nodes):
      raise ValueError('Index %d not in range (len(nodes) == %d)' % (
          ind, len(self.nodes)))

  def add_edge(self, start, end, label='_'):
    self.check_index_in_range(start)
    self.check_index_in_range(end)
    if (start, end) in self.edge_to_label:
      raise ValueError('Edge between %d and %d already exists' % (start, end))
    self.edges.append((start, end, label))
    self.out_edges[start].add(end)
    self.in_edges[end].add(start)
    self.edge_to_label[(start, end)] = label
    ind_start = self.find_conn_comp(start)
    ind_end = self.find_conn_comp(end)
    if ind_start != ind_end:
      self.conn_comps[ind_start] |= self.conn_comps[ind_end]
      self.conn_comps.pop(ind_end)

  def add_graph(self, other):
    base_index = len(self.nodes)
    for label in other.nodes:
      self.add_node(label)
    for i, j, label in other.edges:
      self.add_edge(base_index + i, base_index + j, label)

  def find_conn_comp(self, index):
    self.check_index_in_range(index)
    for i, cc in enumerate(self.conn_comps):
      if index in cc: return i
    raise ValueError('Connected components missing node index %d' % index)

  def has_edge(self, start, end, label=None):
    """Return if there exists an edge from start to end."""
    if end not in self.out_edges[start]: return False
    return (not label) or self.edge_to_label[(start, end)] == label

  def has_undirected_edge(self, start, end, label=None):
    """Return if there exists an edge from start to end or end to start."""
    return self.has_edge(start, end, label) or self.has_edge(end, start, label)

  def get_adjacency_matrix(self):
    """Get a matrix where mat[i,j] == 1 iff there is an i->j edge."""
    n = len(self.nodes)
    mat = np.zeros((n, n), dtype=np.int64)
    for i, j, label in self.edges:
      mat[i,j] = 1
    return mat

  def toposort(self, start_at_sink=False):
    """Return a topological sort of the nodes.

    In particular, finds a permutation topo_order of range(len(self.nodes))
    such that topo_order[i]'s parents are in topo_order[:i].
    In other words, the topological order starts with source nodes
    and ends with sink nodes.

    Args:
      start_at_sink: if True, start at sink nodes and end at source nodes.
    Returns:
      A topological ordering of the nodes, or None if the graph is not a DAG.
    """
    topo_order = []
    in_degrees = [len(self.in_edges[i]) for i in range(len(self.nodes))]
    source_nodes = [i for i, d in enumerate(in_degrees) if d == 0]
    while len(topo_order) < len(self.nodes):
      if len(source_nodes) == 0: 
        return None  # graph is not a DAG
      i = source_nodes.pop()
      topo_order.append(i)
      for j in self.out_edges[i]:
        in_degrees[j] -= 1
        if in_degrees[j] == 0:
          source_nodes.append(j)
    if start_at_sink:
      topo_order = topo_order[::-1]
    return topo_order

  def is_connected(self):
    return len(self.conn_comps) <= 1

  def __str__(self):
    node_str = ','.join(self.nodes)
    edge_str = ';'.join('(%s)' % ','.join(str(t) for t in e) for e in self.edges)
    return '(%s, nodes=[%s], edges=[%s])' % (self.__class__, node_str, edge_str)

  def to_agraph(self, id_prefix=''):
    """Return a pygraphviz AGraph representation of the graph."""
    def make_id(s):
      return '%s-%s' % (id_prefix, s) if id_prefix else s
    ag = pgz.AGraph(directed=True)
    for i, label in enumerate(self.nodes):
      ag.add_node(i, label=label, id=make_id('node%d' % i))
    for index, (i, j, label) in enumerate(self.edges):
      ag.add_edge(i, j, label=label, id=make_id('edge%d' % index))
    return ag

  def draw_svg(self, id_prefix='', filename=None, horizontal=False):
    """Render the graph as SVG, either to a string or to a file."""
    ag = self.to_agraph(id_prefix=id_prefix)
    args = '-Grankdir=LR' if horizontal else ''
    ag.layout('dot', args=args)
    if filename:
      # Write to file
      svg_str = ag.draw(filename)
    else:
      # Write to string, return the string
      svg_str = ag.draw(format='svg')
      start_ind = svg_str.index('<svg')  # Strip the header
      return svg_str[start_ind:]


class Subgraph(Graph):
  """A subgraph of a parent graph.

  The subgraph is constructed incrementally, and at each stage,
  it ensures that the current operation (adding a node or adding an edge)
  maintains the property that there is some injection from the 
  subgraph's nodes to the parent graph's nodes that makes it a subgraph.
  """
  def __init__(self, parent_graph):
    super(Subgraph, self).__init__()
    self.parent_graph = parent_graph
    self.funcs = [{}]  # All consistent maps from self.nodes to self.parent_graph.nodes
    self.counts_left = collections.Counter(parent_graph.nodes)

  def add_node(self, node_label):
    if not self.can_add_node(node_label):
      raise ValueError('Cannot add node "%s" to subgraph' % node_label)
    super(Subgraph, self).add_node(node_label)
    self.counts_left[node_label] -= 1
    i = len(self.nodes) - 1
    new_funcs = []
    for func in self.funcs:
      used_vals = set(func.values())
      free_vals = self.parent_graph.label2index[node_label] - used_vals
      for j in free_vals:
        new_func = func.copy()
        new_func[i] = j
        new_funcs.append(new_func)
    self.funcs = new_funcs

  def add_edge(self, start, end, label=None):
    if not self.can_add_edge(start, end, label):
      raise ValueError('Cannot add edge (%d, %d) to subgraph' % (start, end))
    super(Subgraph, self).add_edge(start, end, label)
    self.funcs = [func for func in self.funcs
                  if self.parent_graph.has_edge(func[start], func[end])]

  def add_graph(self, other):
    if not self.can_add_graph(other):
      raise ValueError('Cannot add graph %s to subgraph' % other)
    super(Subgraph, self).add_graph(other)
    # add_graph() calls add_node() and add_edge()
    # which will update funcs as appropriate.

  def can_add_node(self, node_label):
    return self.counts_left[node_label] > 0

  def can_add_edge(self, start, end, label):
    for func in self.funcs:
      if self.parent_graph.has_edge(func[start], func[end], label):
        return True
    return False

  def can_add_graph(self, other):
    base_index = len(self.nodes)
    for func in self.funcs:
      success = True
      g = copy.deepcopy(self)  # Need to deepcopy since we need to mutate
      for label in other.nodes:
        if g.can_add_node(label):
          g.add_node(label)
        else:
          success = False
          break
      if not success: continue
      for i, j, label in other.edges:
        if g.can_add_edge(base_index + i, base_index + j, label):
          g.add_edge(base_index + i, base_index + j, label)
        else:
          success = False
          break
      if not success: continue
      if success: return True
    return False

  def is_finished(self):
    return (len(self.nodes) == len(self.parent_graph.nodes) and
            len(self.edges) == len(self.parent_graph.edges))

  def get_valid_new_nodes(self):
    """Get a list of all node labels that can be added."""
    return list(x for x in self.counts_left if self.counts_left[x] > 0)