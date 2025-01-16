import pandas as pd
from pulp import LpProblem, LpMaximize, LpVariable, lpSum, LpStatus
import os

# Calculate travel time between locations
def calculate_travel_time(from_loc, to_loc):
    if from_loc == to_loc:
        return 0
    elif {from_loc, to_loc} == {"East", "West"}:
        return 2
    elif {from_loc, to_loc} == {"North", "South"}:
        return 1
    else:
        return 0.5

# Create and solve the optimization model
def create_roster(staff_csv, jobs_csv, roster_file, uncompleted_jobs_file):
    # Load data
    staff_df = pd.read_csv(staff_csv)
    jobs_df = pd.read_csv(jobs_csv)

    # Constants
    DAYS = list(range(7))  # 0 to 6 for a 7-day week
    DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    MAX_HOURS_PER_DAY = 9  # Including travel time
    MAX_DAYS_PER_WEEK = 5

    # Initialize the problem
    problem = LpProblem("Staff_Rostering", LpMaximize)

    # Create decision variables for job assignments (hours worked on a job per staff per day)
    hours_worked = {
        (staff_id, job_id, day): LpVariable(f"hours_{staff_id}_{job_id}_{day}", 0, MAX_HOURS_PER_DAY, cat="Continuous")
        for staff_id in staff_df['StaffID']
        for job_id in jobs_df['JobID']
        for day in DAYS
    }

    # Create decision variables for working days
    working_days = {
        (staff_id, day): LpVariable(f"work_{staff_id}_{day}", 0, 1, cat="Binary")
        for staff_id in staff_df['StaffID']
        for day in DAYS
    }

    # Objective: Maximize total hours worked
    problem += lpSum(hours_worked[(staff_id, job_id, day)] for staff_id in staff_df['StaffID']
                     for job_id in jobs_df['JobID'] for day in DAYS)

    # Constraints

    # Job completion constraint: Ensure total assigned hours match the job's required hours
    for _, job in jobs_df.iterrows():
        job_id = job['JobID']
        job_length = job['JobLength']
        problem += lpSum(
            hours_worked[(staff_id, job_id, day)]
            for staff_id in staff_df['StaffID']
            for day in DAYS
        ) == job_length, f"Job_{job_id}_Completion"

    # Staff must have the tools required for the job
    for _, job in jobs_df.iterrows():
        required_tools = set(job['ToolsRequired'].split(", "))
        for _, staff in staff_df.iterrows():
            staff_tools = set(staff['Tools'].split(", "))
            if not required_tools.issubset(staff_tools):
                for day in DAYS:
                    problem += lpSum(hours_worked[(staff['StaffID'], job['JobID'], day)] for day in DAYS) == 0

    # Link hours worked to working days
    for staff_id in staff_df['StaffID']:
        for day in DAYS:
            problem += lpSum(hours_worked[(staff_id, job_id, day)] for job_id in jobs_df['JobID']) <= MAX_HOURS_PER_DAY * working_days[(staff_id, day)]

    # Limit staff to 9 hours per day including travel time
    for staff_id in staff_df['StaffID']:
        for day in DAYS:
            staff_location = staff_df[staff_df['StaffID'] == staff_id]['Location'].values[0]
            problem += (
                lpSum(hours_worked[(staff_id, job_id, day)] for job_id in jobs_df['JobID']) +
                lpSum(
                    calculate_travel_time(
                        staff_location,
                        jobs_df[jobs_df['JobID'] == job_id]['Location'].values[0]
                    )
                    for job_id in jobs_df['JobID']
                )
            ) <= MAX_HOURS_PER_DAY

    # Limit staff to 5 working days per week
    for staff_id in staff_df['StaffID']:
        problem += lpSum(working_days[(staff_id, day)] for day in DAYS) <= MAX_DAYS_PER_WEEK

    # Solve the problem
    status = problem.solve()

    # Separate completed and uncompleted jobs
    roster = []
    uncompleted_jobs = []

    for job_id in jobs_df['JobID']:
        total_hours_assigned = sum(
            hours_worked[(staff_id, job_id, day)].varValue or 0
            for staff_id in staff_df['StaffID']
            for day in DAYS
        )
        required_hours = jobs_df[jobs_df['JobID'] == job_id]['JobLength'].values[0]
        
        if total_hours_assigned == required_hours:
            for staff_id in staff_df['StaffID']:
                for day in DAYS:
                    hours = hours_worked[(staff_id, job_id, day)].varValue
                    if hours and hours > 0:
                        job_location = jobs_df[jobs_df['JobID'] == job_id]['Location'].values[0]
                        roster.append({
                            "JobID": job_id,
                            "JobLocation": job_location,
                            "StaffAssigned": staff_id,
                            "Day": DAY_NAMES[day],
                            "HoursWorked": hours
                        })
        else:
            uncompleted_jobs.append({
                "JobID": job_id,
                "Reason": f"Only {total_hours_assigned} hours assigned out of {required_hours}."
            })

    # Save completed jobs (roster) to CSV
    roster_df = pd.DataFrame(roster)
    roster_df.to_csv(roster_file, index=False)
    print(f"Roster saved to {roster_file}.")

    # Save uncompleted jobs to CSV
    uncompleted_jobs_df = pd.DataFrame(uncompleted_jobs)
    uncompleted_jobs_df.to_csv(uncompleted_jobs_file, index=False)
    print(f"Uncompleted jobs saved to {uncompleted_jobs_file}.")

# Main execution
if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    staff_csv = os.path.join(base_dir, "staff.csv")
    jobs_csv = os.path.join(base_dir, "jobs.csv")
    roster_file = os.path.join(base_dir, "7_day_roster.csv")
    uncompleted_jobs_file = os.path.join(base_dir, "uncompleted_jobs.csv")

    create_roster(staff_csv, jobs_csv, roster_file, uncompleted_jobs_file)
