# Genetic Algorithm – Space Utilization Scheduler

A genetic algorithm that optimizes university course scheduling by assigning activities to time slots, rooms, and facilitators while satisfying multiple soft constraints.

## Problem Description

Given a set of 11 course sections (SLA100A through SLA451), the algorithm must assign each activity a **time slot**, **room**, and **facilitator** that collectively maximize a fitness score. The optimization balances several competing objectives:

- **Room capacity** – rooms should fit the enrollment without being excessively oversized.
- **Facilitator preference** – each activity has preferred and acceptable facilitators.
- **Time-room conflicts** – no two activities may share the same room at the same time.
- **Facilitator workload** – facilitators should teach 1 activity per time slot and carry a balanced total load (not too many, not too few).
- **Section spacing** – paired sections (e.g., SLA100A/B, SLA191A/B) should be spread across different time slots, and cross-listed sections (SLA100 ↔ SLA191) benefit from consecutive scheduling unless the rooms are far apart.

## How It Works

1. **Initialization** – A population of 500 random schedules is generated.
2. **Fitness Evaluation** – Each schedule is scored by summing per-activity rewards/penalties and global facilitator-load adjustments.
3. **Selection** – Parent pairs are chosen via softmax-weighted sampling over fitness scores.
4. **Crossover** – Single-point crossover combines two parents into a child schedule.
5. **Mutation** – Each gene (activity assignment) has a 1% chance of being randomly altered in one of its three fields (time, room, or facilitator).
6. **Convergence** – After generation 100, the algorithm halts when the average fitness improvement drops below 1%.

## Data

| Category | Details |
|---|---|
| **Rooms** | Slater 003 (45), Roman 216 (30), Loft 206 (75), Roman 201 (50), Loft 310 (108), Beach 201 (60), Beach 301 (75), Logos 325 (450), Frank 119 (60) |
| **Time Slots** | 10 AM, 11 AM, 12 PM, 1 PM, 2 PM, 3 PM |
| **Facilitators** | Lock, Glen, Banks, Richards, Shaw, Singer, Uther, Tyler, Numen, Zeldin |
| **Activities** | 11 sections with enrollments ranging from 20 to 100 students |

## Requirements

- Python 3.7+
- NumPy
- SciPy

Install dependencies:

```bash
pip install numpy scipy
```

## Usage

```bash
python Genetic_Algorithm.py
```

The program prints convergence information and the best schedule found:

```
Converged at generation 142
Best fitness: 5.85
SLA100A: Time=11 AM, Room=Loft206, Facilitator=Glen
SLA100B: Time=3 PM, Room=Beach201, Facilitator=Banks
...
```

## Project Structure

```
.
├── Genetic_Algorithm.py   # Main script: data, fitness function, GA operators, and runner
└── README.md
```

## Fitness Scoring Summary

| Condition | Score |
|---|---|
| Room fits enrollment well | +0.3 |
| Room too small | −0.5 |
| Room > 3× enrollment | −0.2 |
| Room > 6× enrollment | −0.4 |
| Preferred facilitator | +0.5 |
| Acceptable facilitator | +0.2 |
| Unqualified facilitator | −0.1 |
| Facilitator has 1 activity in a slot | +0.2 |
| Facilitator has > 1 activity in a slot | −0.2 |
| Facilitator teaches > 4 total | −0.5 |
| Facilitator teaches ≤ 2 total (except Tyler) | −0.4 |
| Paired sections > 4 slots apart | +0.5 |
| Paired sections at same time | −0.5 |
| Cross-listed sections consecutive | +0.5 |
| Cross-listed sections 2 slots apart | +0.25 |
| Cross-listed consecutive but buildings apart | −0.4 |

## License

This project is provided as-is for educational purposes.
