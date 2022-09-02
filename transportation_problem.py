from gurobipy import *

I, d = multidict({
    1: 80, 2: 270, 3: 250, 4: 160, 5: 180
})
J, M = multidict({
    1: 500, 2: 500, 3: 500
})

c = {(1, 1): 4, (1, 2): 6, (1, 3): 9,
     (2, 1): 5, (2, 2): 4, (2, 3): 7,
     (3, 1): 6, (3, 2): 3, (3, 3): 4,
     (4, 1): 8, (4, 2): 5, (4, 3): 3,
     (5, 1): 10, (5, 2): 8, (5, 3): 4
     }

model = Model("transportation")
x = {}
for i in I:
    for j in J:
        x[i, j] = model.addVar(vtype="C", name="x(%s, %s)" % (i, j))

model.update()
for i in I:
    model.addConstr(quicksum(x[i, j] for j in J) == d[i], name="Demand(%s)" % i)
for j in J:
    model.addConstr(quicksum(x[i, j] for i in I) <= M[j], name="Capacity(%s)" % j)
model.setObjective(quicksum(c[i, j] * x[i, j] for (i, j) in x), GRB.MINIMIZE)
model.optimize()
print("Optimal value:", model.Objval)
EPS = 1.e-6 # 精確度（數值誤差）
for (i, j) in x:
    if x[i, j].X > EPS:
        print("sending quantity %10s from factory %3s to custoner %3s" % (x[i, j].x, j, i))
