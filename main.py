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
def create_roster(staff_csv, jobs_csv, output_file):
    # Load data
    staff_df = pd.read_csv(staff_csv)
    jobs_df = pd.read_csv(jobs_csv)

    # Constants
    DAYS = list(range(7))  # 0 to 6 for a 7-day week
    MAX_HOURS_PER_DAY = 9  # Including travel time
    MAX_DAYS_PER_WEEK = 5

    # Initialize the problem
    problem = LpProblem("Staff_Rostering", LpMaximize)

    # Create decision variables for job assignments
    assignments = {
        (staff_id, job_id, day): LpVariable(f"assign_{staff_id}_{job_id}_{day}", 0, 1, cat="Binary")
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

    # Objective: Maximize total job assignments
    problem += lpSum(assignments[(staff_id, job_id, day)] for staff_id in staff_df['StaffID']
                     for job_id in jobs_df['JobID'] for day in DAYS)

    # Constraints

    # Staff must have the tools required for the job
    for _, job in jobs_df.iterrows():
        required_tools = set(job['ToolsRequired'].split(", "))
        for _, staff in staff_df.iterrows():
            staff_tools = set(staff['Tools'].split(", "))
            if not required_tools.issubset(staff_tools):
                for day in DAYS:
                    problem += lpSum(assignments[(staff['StaffID'], job['JobID'], day)] for day in DAYS) == 0

    # Link job assignments to working days
    for staff_id in staff_df['StaffID']:
        for day in DAYS:
            problem += lpSum(assignments[(staff_id, job_id, day)] for job_id in jobs_df['JobID']) <= working_days[(staff_id, day)] * len(jobs_df)

    # Limit staff to 9 hours per day including travel time
    for staff_id in staff_df['StaffID']:
        for day in DAYS:
            problem += lpSum(
                assignments[(staff_id, job_id, day)] *
                (jobs_df[jobs_df['JobID'] == job_id]['JobLength'].values[0] +
                 calculate_travel_time(staff_df[staff_df['StaffID'] == staff_id]['Location'].values[0],
                                       jobs_df[jobs_df['JobID'] == job_id]['Location'].values[0]))
                for job_id in jobs_df['JobID']
            ) <= MAX_HOURS_PER_DAY

    # Limit staff to 5 working days per week
    for staff_id in staff_df['StaffID']:
        problem += lpSum(working_days[(staff_id, day)] for day in DAYS) <= MAX_DAYS_PER_WEEK

    # Solve the problem
    status = problem.solve()

    # Output the roster
    if LpStatus[status] == "Optimal":
        print("Solution found. Generating output roster...")
        roster = []
        for staff_id in staff_df['StaffID']:
            for job_id in jobs_df['JobID']:
                for day in DAYS:
                    if assignments[(staff_id, job_id, day)].varValue == 1:
                        job_length = jobs_df[jobs_df['JobID'] == job_id]['JobLength'].values[0]
                        job_location = jobs_df[jobs_df['JobID'] == job_id]['Location'].values[0]
                        roster.append({
                            "JobID": job_id,
                            "JobLength": job_length,
                            "JobLocation": job_location,
                            "StaffAssigned": staff_id,
                            "Day": day
                        })
        roster_df = pd.DataFrame(roster)
        roster_df.to_csv(output_file, index=False)
        print(f"Roster saved to {output_file}.")
    else:
        print(f"Solution could not be found. Status: {LpStatus[status]}")

# Main execution
if __name__ == "__main__":
    # File paths (assuming files are in the same folder as this script)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    staff_csv = os.path.join(base_dir, "staff.csv")
    jobs_csv = os.path.join(base_dir, "jobs.csv")
    output_csv = os.path.join(base_dir, "7_day_roster.csv")

    # Generate the roster
    create_roster(staff_csv, jobs_csv, output_csv)
