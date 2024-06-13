def cre_parameter_ipl(Ks:list,
              PHY:nx.DiGraph) -> pulp.LpProblem:


  #tạo các list xNode,xEdge
  xNode = dict()
  for s in Ks:
    s_index = Ks.index(s)
    xNode_s = dict()
    for k in s:
      k_index = s.index(k)
      xNode_k = pulp.LpVariable.dicts(
          name=f"xNode_{s_index}_{k_index}",
          indices =  ([i for i in PHY.nodes],[v for v in k.nodes]),
          cat='Binary'
      )
      xNode_s[k_index] = xNode_k
    xNode[s_index] = xNode_s
  xEdge = dict()
  for s in Ks:
      s_index = Ks.index(s)
      xEdge_s = dict()
      for k in s:
        k_index = s.index(k)
        xEdge_k = pulp.LpVariable.dicts(
            name=f"xEdge_{s_index}_{k_index}",
            indices = ([(i,j) for (i,j) in PHY.edges],[(v,w) for (v,w) in k.edges]),
            cat='Binary'
        )
        xEdge_s[k_index] = xEdge_k
      xEdge[s_index] = xEdge_s

  pi = pulp.LpVariable.dicts(name = "pi",
                             indices = [s for s in range(len(Ks))],
                             cat='Binary')

  phi = dict()
  for s in range(len(Ks)):
    for k in range(len(Ks[s])):
      phi_k = pulp.LpVariable.dicts(name=f"phi_{s}",
                                    indices = [k for k in range(len(Ks[s]))],
                                    cat='Binary')

    phi[s] = phi_k

  z = dict()
  for s in range(len(Ks)):
    for k in range(len(Ks[s])):
      z_k = pulp.LpVariable.dicts(name=f"z_{s}",
                                    indices = [k for k in range(len(Ks[s]))],
                                    cat='Binary')

    z[s] = z_k

  return xNode,xEdge,pi,phi,z
