import pulp
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import random
import pulp
import pickle

from build_ipl import build_ipl

#tạo PHY với 5 nodes, 8 links
PHY=nx.DiGraph()
for i in range(5):
  PHY.add_node(i, a=20)
for i in range(4):
  PHY.add_edge(i,i+1,a=15)
  PHY.add_edge(i+1,i,a=15)


def K_list():
  K=list()
  def PHY_graph():
    PHYs=nx.DiGraph()
    # Tạo các nút ngẫu nhiên
    for i in range(3):
        r_value = random.randint(1, 10)
        PHYs.add_node(i, r=r_value)

    # Tạo các cạnh ngẫu nhiên
    for i in list(PHYs.nodes)[:-1]:
        a_value=random.randint(1,10)
        PHYs.add_edge(i, i+1, r=a_value)
        PHYs.add_edge(i+1, i, r=a_value)

    return PHYs

  K=list()
  for i in range(3):
    K.append(PHY_graph())
  return K

Ks=list()
for i in range(10):
  Ks.append(K_list())

problem = build_ipl(Ks,PHY)
problem.writeLP("problem.lp")


# Giải bài toán sử dụng GLPK
problem.solve(solver=pulp.GLPK_CMD())

# In trạng thái và mục tiêu của bài toán
print(f"Status: {problem.status}, {pulp.LpStatus[problem.status]}")
print(f"\nObjective: {problem.objective.value()}")
print('\nVariables:')
variables = {var.name: var.value() for var in problem.variables()}
for var_name, var_value in variables.items():
    print(f"\t{var_name}: \t {var_value}")

# Lưu kết quả vào file sử dụng pickle
with open('problem_solution.pkl', 'wb') as f:
    pickle.dump({
        'status': problem.status,
        'objective': pulp.value(problem.objective),
        'variables': variables
    }, f)

# Đọc lại kết quả từ file pickle
with open('problem_solution.pkl', 'rb') as f:
    solution = pickle.load(f)

print(f"Status from pickle: {solution['status']}, {pulp.LpStatus[solution['status']]}")
print(f"\nObjective from pickle: {solution['objective']}")
print('\nVariables from pickle:')
for var_name, var_value in solution['variables'].items():
    print(f"\t{var_name}: \t {var_value}")

# Thực hiện kiểm tra ràng buộc với giá trị của biến từ problem.variables()
variables = {var.name: var.value() for var in problem.variables()}
feasible = validate(PHY,Ks,variables)

if feasible:
    print("Solution satisfies all constraints.")
else:
    print("Solution violates some constraints.")
