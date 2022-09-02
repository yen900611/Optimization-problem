from gurobipy import *

I, d = multidict({
    1: 28, 2: 20, 3: 24, 4: 24
})

J, M = multidict({
    1: 22, 2: 14, 3: 26
})

c = {
    (1, 1): 10, (1, 2): 24, (1, 3): 36,
    (2, 1): 20, (2, 2): 16, (2, 3): 14,
    (3, 1): 30, (3, 2): 22, (3, 3): 12,
    (4, 1): 40, (4, 2): 30, (4, 3): 8
}

f = {1: 23, 2: 12, 3: 18, 4: 32}

model = Model("transportation")
x = {}
y = {}
for i in I:
    for j in J:
        x[i, j] = model.addVar(vtype="C", name="x(%s, %s)" % (i, j))
        y[i] = model.addVar(vtype="B", name="y(%s)" % i)
model.update()
for i in I:
    model.addConstr(quicksum(x[i, j] for j in J) <= d[i] * y[i], name="Demand(%s)" % i)
for j in J:
    model.addConstr(quicksum(x[i, j] for i in I) >= M[j], name="Capacity(%s)" % j)
model.setObjective(quicksum(x[i, j] * c[i, j] for (i, j) in x) + quicksum(f[i] * y[i] for i in I), GRB.MINIMIZE)
# model.update()
model.optimize()
print("Optimal value:", model.Objval)
ESP = 1.e-6
for (i, j) in x:
    if x[i, j].X > ESP:
        print("send %10s from factory %3s to customer %3s" % (x[i, j].x, i, j))

model.update()
model.write("facility_location.lp")
