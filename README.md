# 7-Day Staff Roster Generator

## Overview

The **7-Day Staff Roster Generator** is a Python program designed to create an optimal weekly schedule for assigning staff members to jobs based on predefined constraints. It uses the `Pulp` library for linear programming to maximize job assignments while respecting tool requirements, travel times, and daily/weekly work limits.

---

## Prerequisites

### Python Dependencies
The program requires the following Python libraries:
- `pandas`: For data manipulation.
- `pulp`: For optimization.

Install these libraries using:

pip install pandas pulp


Input Files
-----------

### 1\. **Staff File (`staff.csv`)**

A CSV file containing details about staff members.

| Column Name | Description | Example |
| --- | --- | --- |
| `StaffID` | Unique identifier for each staff member | S001 |
| `StaffName` | Name of the staff member | John Doe |
| `Location` | Base location of the staff member | North |
| `Tools` | Comma-separated list of tools the staff member owns | Shovel, Lawnmower, Rake |

### 2\. **Jobs File (`jobs.csv`)**

A CSV file containing details about jobs.

| Column Name | Description | Example |
| --- | --- | --- |
| `JobID` | Unique identifier for each job | J001 |
| `Location` | Location of the job | East |
| `ToolsRequired` | Comma-separated list of tools required for the job | Shovel, Lawnmower |
| `JobLength` | Length of the job in hours | 5 |

* * * * *

Output File
-----------

### Roster File (`7_day_roster.csv`)

A CSV file containing the generated schedule.

| Column Name | Description | Example |
| --- | --- | --- |
| `JobID` | ID of the job assigned | J001 |
| `JobLength` | Length of the job in hours | 5 |
| `JobLocation` | Location where the job is performed | East |
| `StaffAssigned` | ID of the staff assigned to the job | S001 |
| `Day` | Day of the week (0 for Sunday, 6 for Saturday) | 2 |

* * * * *

Constraints
-----------

1.  **Tool Requirements**:

    -   A staff member can only be assigned to a job if they have all the required tools.
2.  **Daily Working Hours**:

    -   A staff member can work a maximum of **9 hours per day**, including travel time.
3.  **Travel Time**:

    -   Travel times between locations are defined as:
        -   **East ↔ West**: 2 hours
        -   **North ↔ South**: 1 hour
        -   **East/West ↔ North/South**: 0.5 hours
4.  **Weekly Working Days**:

    -   A staff member can work a maximum of **5 days** in a 7-day week.
5.  **Maximizing Assignments**:

    -   The objective is to maximize the total number of job assignments while respecting the constraints.

* * * * *

How It Works
------------

### Step 1: Initialize Variables

-   **Assignments**: Binary variables (`assign_{staff_id}_{job_id}_{day}`) indicating if a staff member is assigned to a job on a particular day.
-   **Working Days**: Binary variables (`work_{staff_id}_{day}`) indicating if a staff member works on a particular day.

### Step 2: Define Constraints

-   Ensure staff have the required tools.
-   Ensure job assignments respect daily and weekly working limits.
-   Link job assignments to working days.

### Step 3: Solve the Problem

-   Use the `Pulp` library to solve the linear optimization problem and determine the optimal assignments.

### Step 4: Generate Output

-   Save the generated schedule as a CSV file.

* * * * *

Running the Program
-------------------

### Step 1: Prepare the Files

Place the following files in the same directory as the program:

-   `main.py` (the program file)
-   `staff.csv` (staff details)
-   `jobs.csv` (job details)

### Step 2: Execute the Program

Run the program in the terminal:

`python3 main.py`

### Step 3: Check the Output

The generated roster will be saved as `7_day_roster.csv` in the same directory.

---

## Future Upgrades

The current version of the 7-Day Staff Roster Generator is functional but can be further enhanced with the following upgrades:

### 1. Dynamic Prioritization of Jobs
- Add support for assigning priorities to jobs, allowing critical tasks to be scheduled first.
- Introduce a "Job Priority" column in the `jobs.csv` file and modify the objective function to maximize priority-weighted assignments.

### 2. Break Scheduling
- Include mandatory break periods for staff members working over a certain number of hours in a day.
- Add constraints to ensure break compliance.

### 3. Flexibility for Part-Time Staff
- Allow different maximum working hours for full-time and part-time staff.
- Add a "MaxHoursPerDay" column in the `staff.csv` file to account for individual variations.

### 4. Enhanced Travel Time Modeling
- Use actual distances or travel time matrices between locations instead of predefined fixed values.
- Integrate a mapping API like Google Maps or OpenStreetMap for accurate travel times.

### 5. Improved Output Visualization
- Generate a graphical representation of the weekly schedule (e.g., a Gantt chart).
- Use libraries like `matplotlib` or `plotly` to create visual outputs.

### 6. Configurable Constraints
- Provide a configuration file (e.g., `config.json`) where users can adjust constraints like maximum working hours, days per week, and travel limits without modifying the code.

### 7. Error Handling and Logging
- Add detailed error messages for missing or improperly formatted input files.
- Implement logging to track assignment issues, solver errors, and constraint violations.

### 8. Multi-Objective Optimization
- Enable balancing multiple objectives, such as minimizing travel time while maximizing assignments.
- Use weighted coefficients in the objective function to allow trade-offs.

### 9. User Interface
- Create a simple web-based or desktop UI for users to upload input files, set constraints, and view results interactively.
- Use frameworks like Flask or Streamlit for implementation.

### 10. Machine Learning Integration
- Use machine learning models to predict staff availability and job durations based on historical data, further optimizing assignments.
- Implement clustering algorithms to group jobs and reduce travel distances.

These upgrades aim to enhance the functionality, flexibility, and user experience of the tool, ensuring it can handle more complex operational planning scenarios.

---
