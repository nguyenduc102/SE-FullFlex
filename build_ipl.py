from .cre_parameter_ipl import cre_parameter_ipl
def build_ipl(Ks:list,
              PHY:nx.DiGraph) -> pulp.LpProblem:

  #tạo các list xNode,xEdge
  xNode,xEdge,pi,phi,z = cre_parameter_ipl(Ks,PHY)

  #thiết lập bài toán
  problem=pulp.LpProblem("Exam",pulp.LpMaximize)

  #C1: Tổng tài nguyên phân bổ cho tất cả các slices tại từng node vật lý không được vượt quá tài nguyên có sẵn tại node vật lý đó
  for i in PHY.nodes:
    problem += (
        pulp.lpSum(
            xNode[s][k][i][v] * Ks[s][k].nodes[v]['r'] for s in range(len(Ks)) for k in range(len(Ks[s])) for v in Ks[s][k].nodes
        ) <= PHY.nodes[i]['a'],
        f"C1_{i}"
    )

  #C2: Tổng tài nguyên phân bổ cho tất cả các slices tại từng link vật lý không được vượt quá tài nguyên có sẵn tại link vật lý đó
  for (i,j) in PHY.edges:
    problem += (
        pulp.lpSum(
            xEdge[s][k][(i,j)][(v,w)] * Ks[s][k].edges[(v,w)]['r'] for s in range(len(Ks)) for k in range(len(Ks[s])) for (v,w) in Ks[s][k].edges
        ) <= PHY.edges[(i,j)]['a'],
        f"C2_{i}_{j}"
    )

  #C3: Với mỗi node vật lý, chỉ cho phép cài đặt tối đa một VNF của một slice
  for i in PHY.nodes:
    for s in range(len(Ks)):
      for k in range(len(Ks[s])):
        problem += (
            pulp.lpSum(
                xNode[s][k][i][v] for v in Ks[s][k].nodes
            ) <= z[s][k],
            f"C3_{i}_{s}_{k}"
        )

  #C4: Slice s nếu được accepted (i.e., πs = 1) thì tất cả các VNF của nó phải được ánh xạ (cài đặt) vào một node vật lý i nào đó
  for s in range(len(Ks)):
    for k in range(len(Ks[s])):
      for v in Ks[s][k].nodes:
        problem += (
            pulp.lpSum(
                xNode[s][k][i][v] for i in PHY.nodes
            ) == z[s][k],
            f"C4_{s}_{k}_{v}"
        )

  #C5 (flow conservation): Nếu ánh xạ 2 VNFs v và w của một slice s lần lượt vào hai node vật lý i và j, thì virtual link vw cũng phải được ánh xạ vào một path vật lý (có thể có nút trung gian) nằm giữa i và j
  M = 100
  for i in PHY.nodes:
    for s in range(len(Ks)):
      for k in range(len(Ks[s])):
        for (v,w) in Ks[s][k].edges:


                problem += (
                    pulp.lpSum(
                        (xEdge[s][k][(i,j)][(v,w)] - xEdge[s][k][(j,i)][(v,w)])
                        - (xNode[s][k][i][v] - xNode[s][k][i][w]) for j in PHY.nodes if (i,j) in PHY.edges and (j,i) in PHY.edges
                    ) <= M * (1-phi[s][k]),
                    f"C5_{s}_{k}_{i}_{(v,w)}_1"
                )
                problem +=(
                    pulp.lpSum(
                        (xEdge[s][k][(i,j)][(v,w)] - xEdge[s][k][(j,i)][(v,w)])
                        - (xNode[s][k][i][v] - xNode[s][k][i][w]) for j in PHY.nodes if (i,j) in PHY.edges and (j,i) in PHY.edges
                    ) >= -M * (1-phi[s][k]),
                    f"C5_{s}_{k}_{i}_{(v,w)}_2"
                )

  #C6: Mỗi slice s chỉ được chọn một cấu hình k
  for s in range(len(Ks)):
    for k in range(len(Ks[s])):
      problem += (
          pulp.lpSum(
              phi[s][k]
          ) == pi[s],
          f"C6_{s}_{k}"
          )

  #C7: Thể hiện mối ràng buộc về giá trị giữa zsk, πk, và Φk s (sao cho zsk = πsΦk s)
  for i in PHY.nodes:
    for s in range(len(Ks)):
      for k in range(len(Ks[s])):
        problem += (
            pulp.lpSum(
                z[s][k]
            ) <= pi[s],
            f"C7_{s}_{k}_{i}_1"
        )
        problem += (
            pulp.lpSum(
                z[s][k]
            ) <= phi[s][k],
            f"C7_{s}_{k}_{i}_2"
        )
        problem += (
            pulp.lpSum(
                z[s][k]
            ) >= (pi[s] + phi[s][k] - 1),
            f"C7_{s}_{k}_{i}_3"
        )

  gamma = 0.9999
  problem += gamma * pulp.lpSum(pi[s] for s in range(len(Ks)))- (1-gamma)*pulp.lpSum(xEdge[s][k][(i,j)][(v,w)]
                                 for s in range(len(Ks))
                                 for k in range(len(Ks[s]))
                                 for (i,j) in PHY.edges
                                 for (v,w) in Ks[s][k].edges)
  return problem


