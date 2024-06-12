#------------------------------------------------------------------------------------------------
# Created time: 2024_06_01
# Created by: Pao Chang, Chiu
#------------------------------------------------------------------------------------------------

# Import modules
import gurobipy as gp
from gurobipy import GRB


# Create a new model
model = gp.Model('team01_4_4_model')


# Set parameters
P = [21, 31, 5, 15, 10, 12] # process time
J = len(P) # job
T = len(P) # time
N = len(P) # number of job
M = 1000000


# Create decision variables
x = model.addVars(J, T, vtype=GRB.BINARY, name='x') 
s = model.addVars(J, lb=0, vtype=GRB.INTEGER, name='s') # start time
f = model.addVars(J, lb=0, vtype=GRB.INTEGER, name='f') # finish time
c = model.addVars(J, T, lb=0, vtype=GRB.INTEGER, name='c') # completion time of each job at each time
pt = model.addVars(T, lb=0, vtype=GRB.INTEGER, name='pt')


# Computational formula
SP = [0] * N
for j in range(N):
    SP[j] = pt[j]


# Set objective function
model.setObjective(gp.quicksum(c[j, t] for j in range(N) for t in range(N)) / N, GRB.MINIMIZE) 


# Add constraints
# Completion time of each job at each time
for j in range(N):
    for t in range(N):
        model.addConstr(c[j, t] >= f[j] + M * (x[j, t] - 1), 'c1_%d_%d' % (j, t)) 

# Completion time of each job
for j in range(N):
    model.addConstr(f[j] >= s[j] + gp.quicksum(SP[j] * x[j, t] for t in range(N)), 'c2_%d' % j) 

# Start time of each job
model.addConstr(s[0] == 0, 'c3')
for j in range(N-1):
    model.addConstr(s[j+1] >= s[j] + gp.quicksum(SP[j] * x[j, t] for t in range(N)), 'c4_%d' % j) 

# Each job can only be processed once
for j in range(N):
    model.addConstr(gp.quicksum(x[j, t] for t in range(N)) == 1, 'c5_%d' % j)

# Only one job can be processed at any given time
for t in range(N):
    model.addConstr(gp.quicksum(x[j, t] for j in range(N)) == 1, 'c6_%d' % t)


'''------------- Sort processing time by LPT -------------'''
for t in range(N):
    model.addConstr(pt[t] == gp.quicksum(P[i] * x[i, t] for i in range(N)), 'c7_%d' % t)

for t in range(N-1):
    model.addConstr(pt[t] >= pt[t+1], 'c8_%d' % t)
'''-------------------------------------------------------'''


# Update the model
model.update()

# Optimize the model
model.optimize()

# Create .lp file
model.write('team01_4_4_model.lp')

# Print the solution
if model.status == GRB.OPTIMAL:
    print('Number of variables: ', model.numVars, end=' ')
    variables = model.getVars()
    int_vars = len([v for v in variables if v.vType == GRB.INTEGER])
    cont_vars = len([v for v in variables if v.vType == GRB.CONTINUOUS])
    bin_vars = len([v for v in variables if v.vType == GRB.BINARY])
    
    print('(integer: %d, continuous: %d, binary: %d)' % (int_vars, cont_vars, bin_vars))
    print('Number of constraints: ', model.numConstrs)
    print('Objective value: ', round(model.objVal, 2))
    for v in model.getVars():
        print('%s = %d' % (v.varName, v.x))
        #if v.x != 0:
        #    print('%s = %d' % (v.varName, v.x))

else:
    print('No solution found.')



'''
# Plot the scheduling
import pandas as pd
import plotly.figure_factory as ff
import datetime, os

# Collecting data
tasks = []
for t in range(N):
    start_time = s[t].x
    finish_time = f[t].x
    for j in range(N):
        if x[j, t].x > 0:
            job_sequence = j
    tasks.append(dict(Task='Machine', Start=start_time, Finish=finish_time, Resource=f'Job {job_sequence+1}'))

# Creating a DataFrame
df = pd.DataFrame(tasks)

# Converting start time and finish time to datetime
df['Start'] = pd.to_datetime(df['Start'], unit='m', origin=pd.Timestamp.now())
df['Finish'] = pd.to_datetime(df['Finish'], unit='m', origin=pd.Timestamp.now())

# Plotting
fig = ff.create_gantt(df, index_col='Resource', show_colorbar=True, group_tasks=True, showgrid_x=True, title='Single-Machine Scheduling: Minimum Average Completion Time (LPT)')
fig.update_layout(margin=dict(l=60, r=50, t=100, b=300))

output_dir = "Gantt_Chart"
os.makedirs(output_dir, exist_ok=True)

output_file = os.path.join(output_dir, "team01_4_4_LPT.html")
fig.write_html(output_file)
fig.write_html("Gantt_Chart/team01_4_4_LPT.html")

fig.show()
'''