import random
import math
import numpy as np
from scipy.special import softmax
from collections import defaultdict

def random_schedule():
    # dict activity -> (time, room, facilitator)
    sched = {}
    for act, info in ACTIVITIES.items():
        time = random.choice(TIMES)
        room = random.choice(list(ROOMS.keys()))
        fac = random.choice(FACILITATORS)
        sched[act] = (time, room, fac)
    return sched

# Fitness function
def activity_score(act, assignment, schedule):
    score = 0.0
    time, room, fac = assignment
    info = ACTIVITIES[act]
    # time-room conflict
    for other, asg in schedule.items():
        if other != act and asg[0]==time and asg[1]==room:
            score -= 0.5
    # room size
    cap = ROOMS[room]
    enroll = info['enroll']
    if cap < enroll:
        score -= 0.5
    elif cap > 6*enroll:
        score -= 0.4
    elif cap > 3*enroll:
        score -= 0.2
    else:
        score += 0.3
    # facilitator preference
    if fac in info['pref']:
        score += 0.5
    elif fac in info['other']:
        score += 0.2
    else:
        score -= 0.1
    return score

def overall_fitness(schedule):
    total = 0.0
    # base activity-level scores
    for act, asg in schedule.items():
        total += activity_score(act, asg, schedule)
    # facilitator load and specific adjustments
    # load per time slot
    fac_times = defaultdict(list)
    fac_total = defaultdict(int)
    for act, (t, _, fac) in schedule.items():
        fac_times[fac].append(t)
        fac_total[fac] += 1
    for fac, times in fac_times.items():
        counts = defaultdict(int)
        for t in times:
            counts[t] +=1
        for c in counts.values():
            if c==1: total += 0.2
            elif c>1: total -= 0.2
    for fac, tot in fac_total.items():
        if tot>4:
            total -=0.5
        elif tot<=2 and fac!='Tyler':
            total -=0.4


    # Specific SLA101/SLA191 adjustments
    def get(s): return schedule[s][0]

    # Compute time index
    def tindex(t): return TIMES.index(t)
    # SLA101
    if 'SLA100A' in schedule and 'SLA100B' in schedule:
        d = abs(tindex(get('SLA100A'))-tindex(get('SLA100B')))
        if d>4: total +=0.5
        if d==0: total -=0.5
    # SLA191
    if 'SLA191A' in schedule and 'SLA191B' in schedule:
        d = abs(tindex(get('SLA191A'))-tindex(get('SLA191B')))
        if d>4: total +=0.5
        if d==0: total -=0.5
    # cross-adjacent
    if all(k in schedule for k in ['SLA100A','SLA191A']):
        d = tindex(get('SLA100A'))-tindex(get('SLA191A'))
        if abs(d)==1:
            total +=0.5
            rooms = [schedule['SLA100A'][1], schedule['SLA191A'][1]]
            if (('Roman' in rooms[0] or 'Beach' in rooms[0]) ^ ('Roman' in rooms[1] or 'Beach' in rooms[1])):
                total -=0.4
        elif abs(d)==2:
            total +=0.25
        elif d==0:
            total -=0.25
    return total

# Genetic operators
def select_pair(pop, fitnesses):
    probs = softmax(fitnesses)
    i,j = np.random.choice(len(pop), size=2, p=probs, replace=False)
    return pop[i], pop[j]

def crossover(p1, p2):
    acts = list(ACTIVITIES)
    point = random.randint(1, len(acts)-1)
    child = {}
    for i,act in enumerate(acts): child[act] = p1[act] if i<point else p2[act]
    return child

def mutate(schedule, rate=0.01):
    for act in schedule:
        if random.random()<rate:
            field = random.choice(['time','room','fac'])
            if field=='time': schedule[act]=(random.choice(TIMES),schedule[act][1],schedule[act][2])
            elif field=='room': schedule[act]=(schedule[act][0],random.choice(list(ROOMS.keys())),schedule[act][2])
            else: schedule[act]=(schedule[act][0],schedule[act][1],random.choice(FACILITATORS))
    return schedule

# Genetic Algorithm
def run_genetic(pop_size=500, generations=100):
    pop = [random_schedule() for _ in range(pop_size)]
    best = None; best_fit=-math.inf
    for gen in range(generations):
        fits = [overall_fitness(ind) for ind in pop]
        # track best
        idx = fits.index(max(fits))
        if fits[idx]>best_fit: best_fit, best = fits[idx], pop[idx]
        # check convergence after 100
        if gen>=100:
            avg_now = sum(fits)/pop_size
            avg_prev = sum(prev_fits)/pop_size
            if (avg_now-avg_prev)/abs(avg_prev)<0.01:
                print(f"Converged at generation {gen}")
                break
        prev_fits = fits
        new_pop = []
        while len(new_pop)<pop_size:
            p1,p2 = select_pair(pop, fits)
            child = crossover(p1,p2)
            child = mutate(child)
            new_pop.append(child)
        pop = new_pop
    print(f"Best fitness: {best_fit}")
    return best

if __name__=='__main__':

    # Data
    ROOMS = {
        'Slater003': 45,
        'Roman216': 30,
        'Loft206': 75,
        'Roman201': 50,
        'Loft310': 108,
        'Beach201': 60,
        'Beach301': 75,
        'Logos325': 450,
        'Frank119': 60
    }

    TIMES = ["10 AM", "11 AM", "12 PM", "1 PM", "2 PM", "3 PM"]

    FACILITATORS = ['Lock', 'Glen', 'Banks', 'Richards', 'Shaw', 'Singer', 'Uther', 'Tyler', 'Numen', 'Zeldin']

    ACTIVITIES = {
        'SLA100A': {'enroll': 50, 'pref': ['Glen', 'Lock', 'Banks', 'Zeldin'], 'other': ['Numen', 'Richards']},
        'SLA100B': {'enroll': 50, 'pref': ['Glen', 'Lock', 'Banks', 'Zeldin'], 'other': ['Numen', 'Richards']},
        'SLA191A': {'enroll': 50, 'pref': ['Glen', 'Lock', 'Banks', 'Zeldin'], 'other': ['Numen', 'Richards']},
        'SLA191B': {'enroll': 50, 'pref': ['Glen', 'Lock', 'Banks', 'Zeldin'], 'other': ['Numen', 'Richards']},
        'SLA201': {'enroll': 50, 'pref': ['Glen', 'Banks', 'Zeldin', 'Shaw'], 'other': ['Numen', 'Richards', 'Singer']},
        'SLA291': {'enroll': 50, 'pref': ['Lock', 'Banks', 'Zeldin', 'Singer'], 'other': ['Numen', 'Richards', 'Shaw', 'Tyler']},
        'SLA303': {'enroll': 60, 'pref': ['Glen', 'Zeldin', 'Banks'], 'other': ['Numen', 'Singer', 'Shaw']},
        'SLA304': {'enroll': 25, 'pref': ['Glen', 'Banks', 'Tyler'], 'other': ['Numen', 'Singer', 'Shaw', 'Richards', 'Uther', 'Zeldin']},
        'SLA394': {'enroll': 20, 'pref': ['Tyler', 'Singer'], 'other': ['Richards', 'Zeldin']},
        'SLA449': {'enroll': 60, 'pref': ['Tyler', 'Singer', 'Shaw'], 'other': ['Zeldin', 'Uther']},
        'SLA451': {'enroll': 100, 'pref': ['Tyler', 'Singer', 'Shaw'], 'other': ['Zeldin', 'Uther', 'Richards', 'Banks']}
    }



    best_sched = run_genetic()
    for act,asg in best_sched.items():
        print(f"{act}: Time={asg[0]}, Room={asg[1]}, Facilitator={asg[2]}")
