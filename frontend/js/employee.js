
// EMPLOYEE DASHBOARD

function employeeEscapeHTML(value) {
    return String(value ?? "").replace(/[&<>"']/g, character => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[character]);
}


// LOAD EMPLOYEE DASHBOARD

async function loadEmployeeDashboard() {

    try {
        const [profile, tasks] = await Promise.all([
            apiRequest("/employee/profile"),
            apiRequest("/employee/tasks")
        ]);

        // EMPLOYEE PROFILE

        document.getElementById("employeeName").textContent =
            profile.name;

        document.getElementById("employeeEmail").textContent =
            profile.email;

        // TASK STATISTICS

        const totalTasks = tasks.length;

        const pendingTasks = tasks.filter(
            task => task.status.toLowerCase() === "pending"
        ).length;

        const progressTasks = tasks.filter(
            task => task.status.toLowerCase() === "in_progress"
        ).length;

        const completedTasks = tasks.filter(
            task => task.status.toLowerCase() === "completed"
        ).length;

        document.getElementById("employeeTotalTasks").textContent =
            totalTasks;

        document.getElementById("employeePendingTasks").textContent =
            pendingTasks;

        document.getElementById("employeeProgressTasks").textContent =
            progressTasks;

        document.getElementById("employeeCompletedTasks").textContent =
            completedTasks;

        // RECENT TASKS TABLE

        const table = document.getElementById("employeeRecentTasks");

        if (tasks.length === 0) {
            table.innerHTML = `
                <tr>
                    <td colspan="5">No assigned tasks found.</td>
                </tr>
            `;
            return;
        }

        table.innerHTML = tasks.map(task => `
            <tr>
                <td>${task.id}</td>
                <td>${employeeEscapeHTML(task.title)}</td>
                <td>${employeeEscapeHTML(task.priority)}</td>
                <td>${employeeEscapeHTML(task.status)}</td>
                <td>${task.due_date || "Not specified"}</td>
            </tr>
        `).join("");

    } catch (error) {
        console.error("Employee dashboard error:", error);

        document.getElementById("employeeName").textContent =
            "Unable to load";

        document.getElementById("employeeEmail").textContent =
            "Unable to load";

        document.getElementById("employeeRecentTasks").innerHTML = `
            <tr>
                <td colspan="5">${employeeEscapeHTML(error.message)}</td>
            </tr>
        `;
    }
}


// PAGE INITIALIZATION

document.addEventListener("DOMContentLoaded", () => {

    if (document.getElementById("employeeTotalTasks")) {
        loadEmployeeDashboard();
    }

    const logoutButton = document.getElementById("logoutButton");

    if (logoutButton) {
        logoutButton.addEventListener("click", () => {
            localStorage.removeItem("access_token");
            localStorage.removeItem("user");

            window.location.href = "../login.html";
        });
    }

    if (document.getElementById("employeeTasksTable")) {
    loadEmployeeTasks();}

    if (document.getElementById("detailTaskId")) {
    loadEmployeeTaskDetails();}

    if (document.getElementById("employeeTimeLogsTable")) {
    loadEmployeeTimeLogs();}

});



// LOAD EMPLOYEE MY TASKS

async function loadEmployeeTasks() {

    const table = document.getElementById("employeeTasksTable");
    const message = document.getElementById("employeeTasksMessage");

    if (!table) return;

    try {
        table.innerHTML = `
            <tr>
                <td colspan="6">Loading tasks...</td>
            </tr>
        `;

        const tasks = await apiRequest("/employee/tasks");

        if (!Array.isArray(tasks) || tasks.length === 0) {
            table.innerHTML = `
                <tr>
                    <td colspan="6">No assigned tasks found.</td>
                </tr>
            `;
            return;
        }

        table.innerHTML = tasks.map(task => `
            <tr>
                <td>${task.id}</td>
                <td>${employeeEscapeHTML(task.title)}</td>
                <td>${employeeEscapeHTML(task.priority)}</td>
                <td>${employeeEscapeHTML(task.status)}</td>
                <td>${task.due_date || "Not specified"}</td>
                <td>
                    <a
                        href="task-details.html?id=${task.id}"
                        class="action-btn view-btn"
                        style="text-decoration:none;">
                        View Details
                    </a>
                </td>
            </tr>
        `).join("");

        if (message) {
            message.textContent =
                `Successfully loaded ${tasks.length} assigned tasks.`;
            message.style.color = "green";
        }

    } catch (error) {

        table.innerHTML = `
            <tr>
                <td colspan="6">Unable to load tasks.</td>
            </tr>
        `;

        if (message) {
            message.textContent = error.message;
            message.style.color = "red";
        }

        console.error("Employee tasks error:", error);
    }
}



// LOAD EMPLOYEE TASK DETAILS

async function loadEmployeeTaskDetails() {

    const params = new URLSearchParams(window.location.search);
    const taskId = params.get("id");

    if (!taskId || !/^\d+$/.test(taskId)) {
        alert("Invalid task ID.");
        return;
    }

    try {
        const task = await apiRequest(`/employee/tasks/${taskId}`);

        document.getElementById("detailTaskId").textContent = task.id;
        document.getElementById("detailTaskTitle").textContent = task.title;
        document.getElementById("detailTaskDescription").textContent = task.description;
        document.getElementById("detailTaskPriority").textContent = task.priority;
        document.getElementById("detailTaskDueDate").textContent =
            task.due_date || "Not specified";
        document.getElementById("detailTaskStatus").textContent = task.status;

        document.getElementById("newTaskStatus").value = task.status;

    } catch (error) {

        document.getElementById("detailTaskTitle").textContent =
            "Unable to load task";

        console.error("Task details error:", error);
    }
}



// UPDATE EMPLOYEE TASK STATUS

const updateTaskStatusForm = document.getElementById("updateTaskStatusForm");

if (updateTaskStatusForm) {

    updateTaskStatusForm.addEventListener("submit", async function(event) {

        event.preventDefault();

        const params = new URLSearchParams(window.location.search);
        const taskId = params.get("id");

        const newStatus = document.getElementById("newTaskStatus").value;
        const message = document.getElementById("statusUpdateMessage");

        if (!newStatus) {
            message.textContent = "Please select a status.";
            message.style.color = "red";
            return;
        }

        try {

            message.textContent = "Updating task status...";
            message.style.color = "blue";

            await apiRequest(`/employee/tasks/${taskId}/status`, {
                method: "PATCH",
                body: JSON.stringify({
                    status: newStatus
                })
            });

            message.textContent = "Task status updated successfully!";
            message.style.color = "green";

            // Refresh task information
            await loadEmployeeTaskDetails();

        } catch (error) {

            message.textContent = error.message;
            message.style.color = "red";

            console.error("Status update error:", error);
        }

    });

}


// EMPLOYEE SUBMIT WORKING HOURS

const employeeTimeLogForm = document.getElementById("employeeTimeLogForm");

if (employeeTimeLogForm) {
    employeeTimeLogForm.addEventListener("submit", async function(event) {
        event.preventDefault();

        const params = new URLSearchParams(window.location.search);
        const taskId = params.get("id");

        const hoursWorked = Number(
            document.getElementById("hoursWorked").value
        );

        const workDate = document.getElementById("workDate").value;

        const description = document.getElementById("workDescription").value.trim();

        const message = document.getElementById("timeLogMessage");

        if (!taskId || !hoursWorked || hoursWorked <= 0 || !workDate || !description) {
            message.textContent = "Please complete all fields correctly.";
            message.style.color = "red";
            return;
        }

        try {
            message.textContent = "Submitting time log...";
            message.style.color = "blue";

            const response = await apiRequest(
                `/employee/tasks/${taskId}/time-logs`,
                {
                    method: "POST",
                    body: JSON.stringify({
                        hours_worked: hoursWorked,
                        work_date: workDate,
                        description: description
                    })
                }
            );

            message.textContent = response.message ||
                "Working hours logged successfully!";

            message.style.color = "green";

            employeeTimeLogForm.reset();

        } catch (error) {
            message.textContent = error.message;
            message.style.color = "red";

            console.error("Time log submission error:", error);
        }
    });
}



// LOAD EMPLOYEE TIME LOGS

async function loadEmployeeTimeLogs() {

    const table = document.getElementById("employeeTimeLogsTable");
    const message = document.getElementById("employeeTimeLogsMessage");

    if (!table) return;

    try {
        table.innerHTML = `
            <tr>
                <td colspan="6">Loading time logs...</td>
            </tr>
        `;

        const timeLogs = await apiRequest("/employee/time-logs");

        if (!Array.isArray(timeLogs) || timeLogs.length === 0) {
            table.innerHTML = `
                <tr>
                    <td colspan="6">No time logs found.</td>
                </tr>
            `;
            return;
        }

        table.innerHTML = timeLogs.map(log => `
            <tr>
                <td>${log.id}</td>
                <td>${log.task_id}</td>
                <td>${employeeEscapeHTML(log.task_title || "Task")}</td>
                <td>${log.hours_worked} hours</td>
                <td>${employeeEscapeHTML(log.description || "No description")}</td>
                <td>${log.work_date || "Not available"}</td>
            </tr>
        `).join("");

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

        console.error("Employee time logs error:", error);
    }
}
