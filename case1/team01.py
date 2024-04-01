'''
Created time: 2024_03_31
Created by: Pao Chang, Chiu


Class code:
  | 國文 - 0  | 英文 - 1  | 數學 - 2  | 理化- 3   | 歷史 - 4  | 地理 - 5  | 公民 - 6  |
  | 健康 - 7  | 體育 - 8  | 音樂 - 9  | 藝術 - 10 | 表藝 - 11 | 童軍 - 12 | 家政 - 13 |
  | 輔導 - 14 | 閱讀 - 15 | 週會 - 16 | 社團 - 17 | 選數 - 18 | 選自 - 19 | 科技 - 20 |

Teaching instructor and number of courses taught:
  | 教師 0   | 教師 1   | 教師 2   | 教師 3   | 教師 4   | 教師 5   | 教師 6   | 教師 7   | 教師 8   | 教師 9  | 教師 10  | 教師 11  | 教師 12  | 教師 13  | 教師 14  |
  | 國文 (5) | 英語 (4) | 數學 (4) | 理化 (3) | 歷史 (1) | 地理 (1) | 公民 (2) | 健康 (1) | 體育 (2) | 音樂 (1) | 藝術 (1) | 表藝 (1) | 童軍 (1) | 家政 (1) | 輔導 (1) |
  | 閱讀 (1) |         | 選數 (1) | 選自 (1) |         |         |         |         |         |         |         |         |         |         |         |
  | 週會 (1) |         |         | 科技 (1) |         |         |         |         |         |         |         |         |         |         |         |
  | 社團 (1) |         |         |         |         |         |         |         |         |         |         |         |         |         |         |

'''

import gurobipy as gp
from gurobipy import GRB
import numpy as np

# Create a new model
model = gp.Model('team01')


# Set parameters
D = 5 # 排班天數
T = 7 # 每天節數(4, 3)
C = 1 # 班級數
S = 21 # 課程數
N = np.array([5, 4, 4, 3, 1,
              1, 2, 1, 2, 1,
              1, 1, 1, 1, 1,
              1, 1, 1, 1, 1,
              1]) # 課程 S 每週節數
M = 1000000


# Create decision varibles
x = model.addVars(D, T, C, S, vtype=GRB.BINARY, name='x') # 排課程 S 
y = model.addVars(D, T, C, vtype=GRB.BINARY, name='y') # 排課程 S 實驗


# Set objective function
obj = gp.quicksum(x[d, t, c, s] for d in range(D) for t in range(T) for c in range(C) for s in range(S))
model.setObjective(obj, GRB.MINIMIZE)


# Add constraints
# 每天每班每節只能排一門課
for d in range(D):
    for t in range(T): 
        for c in range(C): 
            model.addConstr(gp.quicksum(x[d, t, c, s] for s in range(S)) == 1, 'c1_%d_%d_%d' % (d, t, c)) 

#----------- 科目不排課的時段 -----------#
# 週一：下午不排英文 
for c in range(C): 
    model.addConstr(gp.quicksum(x[0, t, c, 1] for t in range(4, T)) == 0, 'c3.1_%d' % c) 

# 週二：上午不排綜合活動 
for c in range(C): 
    for s in [12, 13, 14]:
        model.addConstr(gp.quicksum(x[1, t, c, s] for t in range(0, 4)) == 0, 'c3.2_%d_%d' % (c, s)) 
# 週二：下午不排國文 
for c in range(C): 
    model.addConstr(gp.quicksum(x[1, t, c, 0] for t in range(4, T)) == 0, 'c3.3_%d' % c) 

# 週三：上午不排藝術、健康 
for c in range(C): 
    for s in [8, 9, 10, 11]:
        model.addConstr(gp.quicksum(x[2, t, c, s] for t in range(0, 4)) == 0, 'c3.4_%d_%d' % (c, s)) 
# 週三：下午不排數學 
for c in range(C): 
    for s in [2, 18]:
        model.addConstr(gp.quicksum(x[2, t, c, s] for t in range(4, T)) == 0, 'c3.5_%d_%d' % (c, s)) 

# 週五：上午不排社會 
for c in range(C): 
    for s in [4, 5, 6]:
        model.addConstr(gp.quicksum(x[4, t, c, s] for t in range(0, 4)) == 0, 'c3.6_%d_%d' % (c, s)) 
# 週五：下午不排自然、科技 
for c in range(C): 
    for s in [3, 19, 20]:
        model.addConstr(gp.quicksum(x[4, t, c, s] for t in range(4, T)) == 0, 'c3.7_%d_%d' % (c, s)) 

#----------- 教師不排課的時段 -----------#
# 週一：教師 8 下午不排課 
for c in range(C):
    model.addConstr(gp.quicksum(x[0, t, c, 7] for t in range(4, T)) == 0, 'c5.1_%d' % c) 

# 週五：教師 7 和 13 下午不排課 
for c in range(C):
    for s in [6, 12]:
        model.addConstr(gp.quicksum(x[4, t, c, s] for t in range(4, T)) == 0, 'c5.2_%d_%d' % (c, s)) 
#-------------------------------------#

# 必須相連的課（輔導完，上公民）
for d in range(D):
    for t in range(T-1):
        for c in range(C):
            model.addConstr(x[d, t+1, c, 6] == x[d, t, c, 14], 'c6_%d_%d_%d' % (d, t, c)) 

#----------- 課連上，不行跨中午 -----------#
for d in range(D):
    for t in range(T):
        for c in range(C):
            model.addConstr(y[d, t, c] <= M * x[d, t, c, 3], 'c7.1_%d_%d_%d' % (d, t, c)) 

for d in range(D):
    for t in range(T-1):
        if t not in [3]:
            for c in range(C):
                model.addConstr(y[d, t, c] <= M * y[d, t+1, c], 'c7.2_%d_%d_%d' % (d, t, c)) # 理化三節，其中兩節連上 

model.addConstr(gp.quicksum(y[d, t, c] for d in range(D) for t in range(T) if t not in [3] for c in range(C)) == 2, 'c7.3') 
#-------------------------------------#

# 一天只能一節課（國文、英文、數學、公民、體育）
for d in range(D):
    for c in range(C):
        for s in [0, 1, 2, 6, 8]: 
            model.addConstr(gp.quicksum(x[d, t, c, s] for t in range(T)) <= 1, 'c9_%d_%d_%d' % (d, c, s)) 

# 固定課程時段（週四：六節為週會，七節為社團）
for c in range(C):
    model.addConstr(x[3, 5, c, 16] == 1, 'c11.1_%d' % c)
    model.addConstr(x[3, 6, c, 17] == 1, 'c11.2_%d' % c)

#------------ 主科排課限制 -------------#
# 五門：上午至少三節，下午至少二節（國文） 
for c in range(C):
    model.addConstr(gp.quicksum(x[d, t, c, 0] for d in range(D) for t in range(0, 4)) >= 3, 'c12.1.1_%d' % c) 

for c in range(C):
    model.addConstr(gp.quicksum(x[d, t, c, 0] for d in range(D) for t in range(4, T)) >= 2, 'c12.1.2_%d' % c) 

# 四門：上午至少二節，下午至少一節（英文、數學） 
for c in range(C):
    for s in [1, 2]:
        model.addConstr(gp.quicksum(x[d, t, c, s] for d in range(D) for t in range(0, 4)) >= 2, 'c12.2.1_%d_%d' % (c, s)) 

for c in range(C):
    for s in [1, 2]:
        model.addConstr(gp.quicksum(x[d, t, c, s] for d in range(D) for t in range(4, T)) >= 1, 'c12.2.2_%d_%d' % (c, s)) 
#-------------------------------------#

# 每種課一週的排課數
for s in range(S):
    model.addConstr(gp.quicksum(x[d, t, c, s] for d in range(D) for t in range(T) for c in range(C)) <= N[s], 'c15_%d' % s) 


# Update the model
model.update()

# Optimize the model
model.optimize()

# Create .lp file
model.write('team01.lp')

# Print the solution
if model.status == GRB.OPTIMAL:
    print('Number of variables: ', model.numVars)
    print('Number of constraints: ', model.numConstrs)
    print('Objective value: ', model.objVal)
    #for v in model.getVars():
        #print('%s = %.4f' % (v.varName, v.x))
else:
    print('No solution found.')


print('\n\n')

on_duty = model.getAttr("x", x)
days_of_week = ['Mon.', 'Tue.', 'Wed.', 'Thu.', 'Fri.']
class_name = ['國文', '英文', '數學', '理化', '歷史',
               '地理', '公民', '健康', '體育', '音樂',
               '藝術', '表藝', '童軍', '家政', '輔導',
               '閱讀', '週會', '社團', '選數', '選自',
               '科技']


for c in range(C):
    print('班級 %d 的班表: \n' % (c+1))
    for d, day in enumerate(days_of_week):
        print(day.ljust(8), end=' ')
        for t in range(T):
            for s, shift_name in enumerate(class_name):
                if on_duty[d, t, c, s] == 1:
                    print(shift_name.ljust(8), end=' ')
        print('\n')
    print('\n')
