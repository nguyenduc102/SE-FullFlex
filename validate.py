from cre_parameteripl import cre_parameter_ipl

def validate(PHY: nx.DiGraph, Ks: list[list[nx.DiGraph]],solution: dict[str,float]):
    xNode,xEdge,pi,phi,z = cre_parameter_ipl(Ks,PHY)
    # C1: Tổng tài nguyên phân bổ cho tất cả các slices tại từng node vật lý không được vượt quá tài nguyên có sẵn tại node vật lý đó
    if not all(
        sum(variables.get(f"xNode_{s}_{k}_{i}_{v}", 0) * Ks[s][k].nodes[v]['r'] for v in Ks[s][k].nodes) <= PHY.nodes[i]['a']
        for i in PHY.nodes for s in range(len(Ks)) for k in range(len(Ks[s]))
    ):
        print("Constraint C1 violated")
        return False

    # C2: Tổng tài nguyên phân bổ cho tất cả các slices tại từng link vật lý không được vượt quá tài nguyên có sẵn tại link vật lý đó
    if not all(
        sum(variables.get(f"xEdge_{s}_{k}_{(i,j)}_{(v,w)}", 0) * Ks[s][k].edges[(v,w)]['r'] for (v,w) in Ks[s][k].edges) <= PHY.edges[(i,j)]['a']
        for (i,j) in PHY.edges for s in range(len(Ks)) for k in range(len(Ks[s]))
    ):
        print("Constraint C2 violated")
        return False

    # C3: Với mỗi node vật lý, chỉ cho phép cài đặt tối đa một VNF của một slice
    if not all(
        sum(variables.get(f"xNode_{s}_{k}_{i}_{v}", 0) for v in Ks[s][k].nodes) <= variables.get(f"z_{s}_{k}", 0)
        for i in PHY.nodes for s in range(len(Ks)) for k in range(len(Ks[s]))
    ):
        print("Constraint C3 violated")
        return False

    # C4: Slice s nếu được accepted (i.e., πs = 1) thì tất cả các VNF của nó phải được ánh xạ (cài đặt) vào một node vật lý i nào đó
    if not all(
        sum(variables.get(f"xNode_{s}_{k}_{i}_{v}", 0) for i in PHY.nodes) == variables.get(f"z_{s}_{k}", 0)
        for s in range(len(Ks)) for k in range(len(Ks[s])) for v in Ks[s][k].nodes
    ):
        print("Constraint C4 violated")
        return False

    # C5 (flow conservation): Nếu ánh xạ 2 VNFs v và w của một slice s lần lượt vào hai node vật lý i và j, thì virtual link vw cũng phải được ánh xạ vào một path vật lý (có thể có nút trung gian) nằm giữa i và j
    M = 100
    if not all(
        -M * (1 - variables.get(f"phi_{s}_{k}", 0)) <= (
            sum(variables.get(f"xEdge_{s}_{k}_{(i,j)}_{(v,w)}", 0) - variables.get(f"xEdge_{s}_{k}_{(j,i)}_{(v,w)}", 0) for j in PHY.nodes if (i, j) in PHY.edges and (j, i) in PHY.edges)
            - (variables.get(f"xNode_{s}_{k}_{i}_{v}", 0) - variables.get(f"xNode_{s}_{k}_{i}_{w}", 0))
        ) <= M * (1 - variables.get(f"phi_{s}_{k}", 0))
        for i in PHY.nodes for s in range(len(Ks)) for k in range(len(Ks[s])) for (v,w) in Ks[s][k].edges
    ):
        print("Constraint C5 violated")
        return False

    # C6: Mỗi slice s chỉ được chọn một cấu hình k
    if not all(
        sum(variables.get(f"phi_{s}_{k}", 0) for k in range(len(Ks[s]))) == variables.get(f"pi_{s}", 0)
        for s in range(len(Ks))
    ):
        print("Constraint C6 violated")
        return False

    # C7: Thể hiện mối ràng buộc về giá trị giữa zsk, πk, và Φk s (sao cho zsk = πsΦk s)
    if not all(
        variables.get(f"z_{s}_{k}", 0) <= variables.get(f"pi_{s}", 0) and
        variables.get(f"z_{s}_{k}", 0) <= variables.get(f"phi_{s}_{k}", 0) and
        variables.get(f"z_{s}_{k}", 0) >= (variables.get(f"pi_{s}", 0) + variables.get(f"phi_{s}_{k}", 0) - 1)
        for s in range(len(Ks)) for k in range(len(Ks[s]))
    ):
        print("Constraint C7 violated")
        return False

    return True


