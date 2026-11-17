
document.addEventListener("DOMContentLoaded", () => {

    // Manager Dashboard page
    if (document.getElementById("managerName")) {
        loadManagerDashboard();
    }

    // Manager Employees page
    if (document.getElementById("managerEmployeesTable")) {
        loadManagerEmployees();
    }

    if (document.getElementById("managerTasksTable")) {
    loadManagerTasks();}

    if (document.getElementById("assignedEmployee")) {
    loadTaskEmployees();}

    if (document.getElementById("managerTimeLogsTable")) {
    loadManagerTimeLogs();}


    // Logout functionality
    const logoutButton = document.getElementById("logoutButton");

    if (logoutButton) {
        logoutButton.addEventListener("click", () => {
            localStorage.removeItem("access_token");
            localStorage.removeItem("user");
            window.location.href = "../login.html";
        });
    }

});



async function loadManagerDashboard() {
    const message = document.getElementById("managerMessage");

    try {
        // Check logged-in user
        const user = JSON.parse(
            localStorage.getItem("user") || "null"
        );

        if (!user || user.role !== "manager") {
            window.location.href = "../login.html";
            return;
        }

        // Display manager name
        document.getElementById("managerName").textContent =
            user.name;

        // Fetch employees and tasks
        const [employees, tasks] = await Promise.all([
            apiRequest("/managers/employees"),
            apiRequest("/managers/tasks")
        ]);

        // Employee statistics
        const totalEmployees = employees.length;

        const activeEmployees = employees.filter(
            employee => employee.is_active
        ).length;

        // Task statistics
        const totalTasks = tasks.length;

        const pendingTasks = tasks.filter(
            task => task.status === "pending"
        ).length;

        const inProgressTasks = tasks.filter(
            task => task.status === "in_progress"
        ).length;

        const completedTasks = tasks.filter(
            task => task.status === "completed"
        ).length;

        // Display statistics
        document.getElementById("totalEmployees").textContent =
            totalEmployees;

        document.getElementById("activeEmployees").textContent =
            activeEmployees;

        document.getElementById("totalTasks").textContent =
            totalTasks;

        document.getElementById("pendingTasks").textContent =
            pendingTasks;

        document.getElementById("inProgressTasks").textContent =
            inProgressTasks;

        document.getElementById("completedTasks").textContent =
            completedTasks;

        message.textContent =
            "Manager dashboard loaded successfully.";

        message.style.color = "green";

    } catch (error) {
        message.textContent = error.message;
        message.style.color = "red";
    }
}


/* Load employees belonging to the logged-in Manager */

async function loadManagerEmployees() {
    const tableBody = document.getElementById("managerEmployeesTable");
    const message = document.getElementById("managerEmployeesMessage");

    try {
        const user = JSON.parse(
            localStorage.getItem("user") || "null"
        );

        if (!user || user.role !== "manager") {
            window.location.href = "../login.html";
            return;
        }

        const employees = await apiRequest("/managers/employees");

        tableBody.innerHTML = "";

        if (employees.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="5">No employees found.</td>
                </tr>
            `;
            return;
        }

        employees.forEach(employee => {
            const row = document.createElement("tr");

            row.innerHTML = `
                <td>${employee.id}</td>
                <td>${escapeHTML(employee.name)}</td>
                <td>${escapeHTML(employee.email)}</td>
                <td>
                    <span class="status-badge ${
                        employee.is_active
                            ? "status-active"
                            : "status-inactive"
                    }">
                        ${employee.is_active ? "Active" : "Inactive"}
                    </span>
                </td>
                <td>
                    <button
                        class="action-btn view-btn"
                        data-employee-id="${employee.id}">
                        View
                    </button>
                    <button

                    class="action-btn ${employee.is_active ? 'deactivate-btn' : 'view-btn'}"
                    data-status-id="${employee.id}"
                    data-active="${employee.is_active}">
                    ${employee.is_active ? 'Deactivate' : 'Reactivate'}

                    </button>

                </td>
            `;

            tableBody.appendChild(row);
        });

        message.textContent = "Employees loaded successfully.";
        message.style.color = "green";

    } catch (error) {
        message.textContent = error.message;
        message.style.color = "red";
    }
}

/* Run only on Manager Employees page */

if (document.getElementById("managerEmployeesTable")) {
    document.addEventListener("DOMContentLoaded", loadManagerEmployees);
}


/* Helper function to safely display text */

function escapeHTML(value) {
    const element = document.createElement("div");
    element.textContent = value ?? "";
    return element.innerHTML;
}


/* Create Employee Form */

const createEmployeeButton =
    document.getElementById("showCreateEmployeeButton");

const createEmployeeForm =
    document.getElementById("createEmployeeForm");

if (createEmployeeButton && createEmployeeForm) {

    createEmployeeButton.addEventListener("click", () => {
        createEmployeeForm.style.display = "block";

        createEmployeeForm.scrollIntoView({
            behavior: "smooth"
        });
    });

    document.getElementById("cancelEmployeeForm")
        .addEventListener("click", () => {
            createEmployeeForm.style.display = "none";
        });

    document.getElementById("employeeForm")
        .addEventListener("submit", async function(event) {

            event.preventDefault();

            const message =
                document.getElementById("employeeFormMessage");

            const employeeData = {
                name: document.getElementById("employeeName").value.trim(),
                email: document.getElementById("employeeEmail").value.trim(),
                password: document.getElementById("employeePassword").value
            };

            try {
                await apiRequest("/managers/employees", {
                    method: "POST",
                    body: JSON.stringify(employeeData)
                });

                message.style.color = "green";
                message.textContent =
                    "Employee created successfully!";

                this.reset();

                await loadManagerEmployees();

            } catch (error) {
                message.style.color = "red";
                message.textContent = error.message;
            }
        });
}


/* View Employee Button */

document.addEventListener("click", function(event) {

    console.log("Click event detected:", event.target);

    const button = event.target.closest(
        "#managerEmployeesTable .view-btn"
    );

    console.log("View button found:", button);

    if (!button) {
        return;
    }

    const employeeId = button.dataset.employeeId;

    if (!employeeId) {
        console.error("Employee ID not found");
        return;
    }

    const row = button.closest("tr");

    if (!row) {
        console.error("Employee table row not found");
        return;
    }

    const cells = row.querySelectorAll("td");

    const editForm = document.getElementById("editEmployeeForm");

    if (!editForm) {
        console.error("Edit Employee form not found");
        return;
    }

    document.getElementById("editEmployeeId").value =
        employeeId;

    document.getElementById("editEmployeeName").value =
        cells[1].textContent.trim();

    document.getElementById("editEmployeeEmail").value =
        cells[2].textContent.trim();

    document.getElementById("editEmployeePassword").value = "";

    editForm.style.display = "block";

    editForm.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });

});



/* UPDATE EMPLOYEE DETAILS */

const employeeUpdateForm = document.getElementById(
    "employeeUpdateForm"
);

if (employeeUpdateForm) {

    employeeUpdateForm.addEventListener("submit", async function(event) {

        event.preventDefault();

        const employeeId =
            document.getElementById("editEmployeeId").value;

        const message =
            document.getElementById("editEmployeeMessage");

        const updatedData = {
            name: document.getElementById("editEmployeeName").value.trim(),
            email: document.getElementById("editEmployeeEmail").value.trim()
        };

        const newPassword =
            document.getElementById("editEmployeePassword").value;

        if (newPassword.trim() !== "") {
            updatedData.password = newPassword;
        }

        try {

            message.textContent = "Updating employee...";
            message.style.color = "blue";

            await apiRequest(
                `/managers/employees/${employeeId}`,
                {
                    method: "PATCH",
                    body: JSON.stringify(updatedData)
                }
            );

            message.textContent =
                "Employee updated successfully!";

            message.style.color = "green";

            // Refresh employee directory
            await loadManagerEmployees();

            // Clear password field
            document.getElementById("editEmployeePassword").value = "";

        } catch (error) {

            message.textContent = error.message;
            message.style.color = "red";

        }

    });

}


/* CANCEL EDIT EMPLOYEE */

const cancelEditEmployee = document.getElementById(
    "cancelEditEmployee"
);

if (cancelEditEmployee) {

    cancelEditEmployee.addEventListener("click", function() {

        document.getElementById("editEmployeeForm").style.display =
            "none";

    });

}


// DEACTIVATE / REACTIVATE EMPLOYEE

document.addEventListener("click", async function(event) {
    const button = event.target.closest("[data-status-id]");

    if (!button) return;

    const employeeId = button.dataset.statusId;
    const currentStatus = button.dataset.active === "true";
    const newStatus = !currentStatus;

    const action = newStatus ? "reactivate" : "deactivate";

    const confirmed = confirm(
        `Are you sure you want to ${action} this employee?`
    );

    if (!confirmed) return;

    try {
        button.disabled = true;

        await apiRequest(`/managers/employees/${employeeId}`, {
            method: "PATCH",
            body: JSON.stringify({
                is_active: newStatus
            })
        });

        alert(`Employee ${action}d successfully!`);

        await loadManagerEmployees();

    } catch (error) {
        alert(error.message);
        button.disabled = false;
    }
});



// LOAD MANAGER TASKS

async function loadManagerTasks() {
    const table = document.getElementById("managerTasksTable");
    const message = document.getElementById("tasksMessage");

    if (!table) return;

    try {
        table.innerHTML = `
            <tr>
                <td colspan="7">Loading tasks...</td>
            </tr>
        `;

        const [tasks, employees] = await Promise.all([
            apiRequest("/managers/tasks"),
            apiRequest("/managers/employees")
        ]);

        if (!Array.isArray(tasks) || tasks.length === 0) {
            table.innerHTML = `
                <tr>
                    <td colspan="7">No tasks found.</td>
                </tr>
            `;
            return;
        }

        const employeeMap = new Map(
            employees.map(employee => [
                employee.id,
                employee.name
            ])
        );

        table.innerHTML = tasks.map(task => {
            const employeeName =
                employeeMap.get(task.assigned_to_id) || "Unknown";


            return `
                <tr>
                    <td>${task.id}</td>
                    <td>${escapeHTML(task.title)}</td>
                    <td>${escapeHTML(employeeName)}</td>
                    <td>${escapeHTML(task.priority)}</td>
                    <td>${escapeHTML(task.status)}</td>
                    <td>${task.due_date || "Not specified"}</td>
                    <td>
                        <button
                            class="action-btn view-btn"
                            data-reassign-task="${task.id}"
                            data-current-employee="${task.assigned_to_id}">
                            Reassign
                        </button>
                    </td>
                </tr>
            `;


        }).join("");

        if (message) {
            message.textContent = "";
        }

    } catch (error) {
        table.innerHTML = `
            <tr>
                <td colspan="7">Unable to load tasks.</td>
            </tr>
        `;

        if (message) {
            message.textContent = error.message;
            message.style.color = "red";
        }

        console.error("Error loading manager tasks:", error);
    }
}



// LOAD ACTIVE EMPLOYEES IN CREATE TASK DROPDOWN

async function loadTaskEmployees() {
    const employeeSelect = document.getElementById("assignedEmployee");

    if (!employeeSelect) return;

    try {
        const employees = await apiRequest("/managers/employees");

        const activeEmployees = employees.filter(
            employee => employee.is_active === true
        );

        employeeSelect.innerHTML =
            '<option value="">Select Employee</option>';

        activeEmployees.forEach(employee => {
            const option = document.createElement("option");

            option.value = employee.id;
            option.textContent = employee.name;

            employeeSelect.appendChild(option);
        });

        if (activeEmployees.length === 0) {
            employeeSelect.innerHTML =
                '<option value="">No active employees available</option>';
        }

    } catch (error) {
        console.error("Unable to load employees:", error);
        employeeSelect.innerHTML =
            '<option value="">Unable to load employees</option>';
    }
}



// CREATE TASK - FORM SUBMISSION

const createTaskForm = document.getElementById("createTaskForm");

if (createTaskForm) {
    createTaskForm.addEventListener("submit", async function(event) {
        event.preventDefault();

        const message = document.getElementById("createTaskMessage");

        const taskData = {
            title: document.getElementById("taskTitle").value.trim(),
            description: document.getElementById("taskDescription").value.trim(),
            assigned_to_id: Number(
                document.getElementById("assignedEmployee").value
            ),
            priority: document.getElementById("taskPriority").value,
            due_date: document.getElementById("taskDueDate").value
        };

        try {
            message.textContent = "Creating task...";
            message.style.color = "blue";

            await apiRequest("/managers/tasks", {
                method: "POST",
                body: JSON.stringify(taskData)
            });

            message.textContent = "Task created successfully!";
            message.style.color = "green";

            createTaskForm.reset();

            console.log("Task created successfully:", taskData);

        } catch (error) {
            message.textContent = error.message;
            message.style.color = "red";

            console.error("Task creation failed:", error);
        }
    });
}




// LOAD TASKS IN HISTORY DROPDOWN

async function loadHistoryTasks() {
    const select = document.getElementById("historyTaskSelect");

    if (!select) return;

    try {
        const tasks = await apiRequest("/managers/tasks");

        select.innerHTML = '<option value="">Select Task</option>';

        tasks.forEach(task => {
            const option = document.createElement("option");
            option.value = task.id;
            option.textContent = `#${task.id} - ${task.title}`;
            select.appendChild(option);
        });

    } catch (error) {
        console.error("Error loading history tasks:", error);
        select.innerHTML =
            '<option value="">Unable to load tasks</option>';
    }
}



// LOAD SELECTED TASK HISTORY

async function loadTaskHistory() {
    const taskId = document.getElementById("historyTaskSelect").value;
    const table = document.getElementById("taskHistoryTable");
    const message = document.getElementById("historyMessage");

    if (!taskId) {
        message.textContent = "Please select a task first.";
        message.style.color = "red";
        return;
    }

    try {
        message.textContent = "Loading task history...";
        message.style.color = "blue";

        table.innerHTML = `
            <tr><td colspan="4">Loading history...</td></tr>
        `;

        const [history, employees] = await Promise.all([
            apiRequest(`/managers/tasks/${taskId}/history`),
            apiRequest("/managers/employees")
        ]);

        const employeeMap = new Map(
            employees.map(employee => [
                employee.id,
                employee.name
            ])
        );

        if (!history || history.length === 0) {
            table.innerHTML = `
                <tr>
                    <td colspan="4">No history available for this task.</td>
                </tr>
            `;
            message.textContent = "";
            return;
        }

        table.innerHTML = history.map(record => {
            let details = record.remarks || "No additional details";

            if (record.action === "reassigned") {
                const oldName =
                    employeeMap.get(record.old_assignee_id) || "Unknown";

                const newName =
                    employeeMap.get(record.new_assignee_id) || "Unknown";

                details = `Reassigned from ${oldName} to ${newName}. ${details}`;
            }

            if (record.old_status || record.new_status) {
                details += ` | Status: ${record.old_status || "None"} → ${record.new_status || "None"}`;
            }

            const changedAt = record.changed_at
                ? new Date(record.changed_at).toLocaleString()
                : "Not available";

            return `
                <tr>
                    <td>${record.id}</td>
                    <td>${escapeHTML(record.action)}</td>
                    <td>${escapeHTML(details)}</td>
                    <td>${escapeHTML(changedAt)}</td>
                </tr>
            `;
        }).join("");

        message.textContent = "Task history loaded successfully!";
        message.style.color = "green";

    } catch (error) {
        table.innerHTML = `
            <tr><td colspan="4">Unable to load task history.</td></tr>
        `;

        message.textContent = error.message;
        message.style.color = "red";

        console.error("Task history error:", error);
    }
}



// TASK HISTORY PAGE EVENTS

const historyTaskSelect = document.getElementById("historyTaskSelect");

if (historyTaskSelect) {
    loadHistoryTasks();
}

const loadHistoryButton = document.getElementById("loadHistoryButton");

if (loadHistoryButton) {
    loadHistoryButton.addEventListener("click", loadTaskHistory);
}




// OPEN TASK REASSIGNMENT FORM

document.addEventListener("click", async function(event) {
    const button = event.target.closest("[data-reassign-task]");

    if (!button) return;

    const taskId = button.dataset.reassignTask;
    const currentEmployeeId = Number(button.dataset.currentEmployee);

    const section = document.getElementById("reassignTaskSection");
    const employeeInput = document.getElementById("currentEmployee");
    const employeeSelect = document.getElementById("newAssignedEmployee");
    const taskIdInput = document.getElementById("reassignTaskId");
    const message = document.getElementById("reassignMessage");

    try {
        const employees = await apiRequest("/managers/employees");

        const activeEmployees = employees.filter(
            employee => employee.is_active === true
        );

        const currentEmployee = activeEmployees.find(
            employee => employee.id === currentEmployeeId
        );

        employeeInput.value = currentEmployee
            ? currentEmployee.name
            : "Unknown";

        taskIdInput.value = taskId;

        employeeSelect.innerHTML =
            '<option value="">Select Employee</option>';

        activeEmployees.forEach(employee => {
            const option = document.createElement("option");
            option.value = employee.id;
            option.textContent = employee.name;

            if (employee.id === currentEmployeeId) {
                option.disabled = true;
                option.textContent += " (Currently Assigned)";
            }

            employeeSelect.appendChild(option);
        });

        message.textContent = "";

        section.style.display = "block";

        section.scrollIntoView({
            behavior: "smooth",
            block: "center"
        });

    } catch (error) {
        alert(error.message);
    }
});



// CANCEL TASK REASSIGNMENT

const cancelReassignment = document.getElementById("cancelReassignment");

if (cancelReassignment) {
    cancelReassignment.addEventListener("click", function() {
        document.getElementById("reassignTaskSection").style.display = "none";
        document.getElementById("reassignTaskForm").reset();
        document.getElementById("reassignMessage").textContent = "";
    });
}


// CONFIRM TASK REASSIGNMENT

const reassignTaskForm = document.getElementById("reassignTaskForm");

if (reassignTaskForm) {
    reassignTaskForm.addEventListener("submit", async function(event) {
        event.preventDefault();

        const taskId = document.getElementById("reassignTaskId").value;
        const employeeId = Number(
            document.getElementById("newAssignedEmployee").value
        );

        const message = document.getElementById("reassignMessage");

        if (!employeeId) {
            message.textContent = "Please select an employee.";
            message.style.color = "red";
            return;
        }

        try {
            message.textContent = "Reassigning task...";
            message.style.color = "blue";

            await apiRequest(
                `/managers/tasks/${taskId}/reassign`,
                {
                    method: "PATCH",
                    body: JSON.stringify({
                        assigned_to_id: employeeId
                    })
                }
            );

            message.textContent = "Task reassigned successfully!";
            message.style.color = "green";

            // Refresh task table with updated employee name
            await loadManagerTasks();

            // Close and reset the form
            reassignTaskForm.reset();

            setTimeout(() => {
                document.getElementById("reassignTaskSection").style.display = "none";
            }, 1200);

        } catch (error) {
            message.textContent = error.message;
            message.style.color = "red";
        }
    });
}



// LOAD MANAGER TIME LOGS

async function loadManagerTimeLogs() {
    const table = document.getElementById("managerTimeLogsTable");
    const message = document.getElementById("timeLogsMessage");

    if (!table) return;

    try {
        table.innerHTML = `
            <tr>
                <td colspan="6">Loading time logs...</td>
            </tr>
        `;

        const timeLogs = await apiRequest("/managers/time-logs");

        if (!Array.isArray(timeLogs) || timeLogs.length === 0) {
            table.innerHTML = `
                <tr>
                    <td colspan="6">No time logs found.</td>
                </tr>
            `;
            return;
        }

        table.innerHTML = timeLogs.map(log => {
            const formattedDate = log.work_date
                ? new Date(log.work_date + "T00:00:00").toLocaleDateString()
                : "Not available";

            return `
                <tr>
                    <td>${log.id}</td>
                    <td>${escapeHTML(log.employee_name)}</td>
                    <td>
                        ${log.task_id} - ${escapeHTML(log.task_title)}
                    </td>
                    <td>${log.hours_worked} hours</td>
                    <td>${escapeHTML(log.description || "No description")}</td>
                    <td>${formattedDate}</td>
                </tr>
            `;
        }).join("");

        if (message) {
            message.textContent =
                `Successfully loaded ${timeLogs.length} time logs.`;
            message.style.color = "green";
        }

    } catch (error) {
        table.innerHTML = `
            <tr>
                <td colspan="6">Unable to load time logs.</td>
            </tr>
        `;

        if (message) {
            message.textContent = error.message;
            message.style.color = "red";
        }

        console.error("Time logs error:", error);
    }
}
