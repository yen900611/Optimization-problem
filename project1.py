from gurobipy import *
# import numpy as np
import pandas as pd

df = {}
D_num = 100
df = pd.read_csv("prj1_test_data/Car_Demand_" + str(D_num) + ".csv")
K_d = {}
L_d = {}
T = {}
C = {}
for i in range(1, D_num + 1):  # -1是因為扣掉標題行
    L_d[i] = list()
    T[i] = list()
    K_d[i] = df.iloc[i - 1]["type"]
    L_d[i].append(df.iloc[i - 1]["Location_X"])
    L_d[i].append(df.iloc[i - 1]["Location_Y"])
    T[i].append(df.iloc[i - 1]["Time_H"])
    T[i].append(df.iloc[i - 1]["Time_E"])
    C[i] = df.iloc[i - 1]["Penalty"]

df2 = {}

S_num = 200  # 2
df2 = pd.read_csv("prj1_test_data/Space_" + str(S_num) + ".csv")

K_s = {}
L_s = {}
for i in range(1, S_num + 1):  # -1是因為扣掉標題行
    L_s[i] = list()
    K_s[i] = df2.iloc[i - 1]["type"]
    L_s[i].append(df2.iloc[i - 1]["Location_X"])
    L_s[i].append(df2.iloc[i - 1]["Location_Y"])

R = 20

model = Model("parking_problem")
d = {}
x = {}
y = {}
can_car_park = {}
r = {}
for i in range(1, D_num + 1):
    # d[i] = set()
    for j in range(1, S_num + 1):
        x[i, j] = model.addVar(vtype="B", name="x(%s %s)" % (i, j))  # 最後的結果
        y[i] = model.addVar(vtype="B", name="y(%s)" % i)
        r[i, j] = ((L_d[i][0] - L_s[j][0]) ** 2 + (L_d[i][1] - L_s[j][1]) ** 2) ** 0.5
        if K_d[i] <= K_s[j] and r[i, j] <= R:  # Type_s >= Type_d, r<=R
            # d[i].add(j)
            can_car_park[i, j] = 1
        else:
            can_car_park[i, j] = 0
# 判斷時間重疊：(Time_E1>Time_H2>=Time_H1 or Time_E2>Time_H1>=Time_H1)
t = {}
for i in range(1, D_num + 1):
    for j in range(i, D_num + 1):
        if i == j:
            continue
        else:
            if T[i][1] > T[j][0] >= T[i][0] or T[j][1] > T[i][0] >= T[j][0]:
                t[i, j] = 0  # i車與j車的停車時間重疊
            else:
                t[i, j] = 1

# s = {}
# for j in range(1, S_num + 1):
#     s[j] = set()
#     for i in range(1, D_num + 1):
#         if K_d[i] <= K_s[j] and r[i, j] <= R:
#             s[j].add(i)

model.update()
for i in range(1, D_num + 1):
    model.addConstr(quicksum(x[i, j] for j in range(1, S_num + 1)) <= 1, name="each car park")  # 每台車最多只能停一個停車格
    for j in range(1, S_num + 1):
        model.addConstr(x[i, j] <= can_car_park[i, j], name="y")
    model.addConstr((y[i] == quicksum(x[i, j] for j in range(1, S_num + 1))), name="y(%s)" % i)
for k in range(1, S_num + 1):
    for (i, j) in t:
        model.addConstr(x[i, k] * x[j, k] <= t[i, j], name="time window")

#     model.addConstrs((K_d[i] * x[i, j] <= K_s[j] * x[i, j] for j in range(1, S_num+1)), name="k(%s)" % i)
#     for j in range(1, S_num+1):
#         model.addConstr((r[i, j] * x[i, j] <= R), name="r")
# for j in range(1, S_num+1):
#     model.addConstr(quicksum(x[i, j] for i in range(1, D_num+1)) <= 1, name="each space park")  # 每個停車格最多只能停一台車
#
model.setObjective(
    quicksum(C[i] / r[i, j] * x[i, j] for (i, j) in x) - quicksum(
        C[i] * (1 - y[i]) for i in range(1, D_num + 1)),
    GRB.MAXIMIZE)
model.optimize()

print(model.Objval)

for (i, j) in x:
    if x[i, j].X == 1:
        print("park car %3s in space %3s" % (i, j))
