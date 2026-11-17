
document.addEventListener("DOMContentLoaded", () => {
    loadAdminDashboard();

    const logoutButton = document.getElementById("logoutButton");

    logoutButton.addEventListener("click", () => {
        localStorage.removeItem("access_token");
        localStorage.removeItem("user");

        window.location.href = "../login.html";
    });
});

async function loadAdminDashboard() {
    const message = document.getElementById("dashboardMessage");

    try {
        const user = JSON.parse(localStorage.getItem("user") || "null");

        // Check whether the user is logged in as Admin
        if (!user || user.role !== "admin") {
            window.location.href = "../login.html";
            return;
        }

        document.getElementById("adminName").textContent = user.name;

        // Fetch dashboard statistics from FastAPI
        const stats = await apiRequest("/admin/dashboard");

        // Display statistics
        document.getElementById("totalManagers").textContent =
            stats.total_managers;

        document.getElementById("activeManagers").textContent =
            stats.active_managers;

        document.getElementById("totalEmployees").textContent =
            stats.total_employees;

        document.getElementById("totalTasks").textContent =
            stats.total_tasks;

        document.getElementById("pendingTasks").textContent =
            stats.pending_tasks;

        document.getElementById("inProgressTasks").textContent =
            stats.in_progress_tasks;

        document.getElementById("completedTasks").textContent =
            stats.completed_tasks;

        message.textContent = "Dashboard statistics loaded successfully.";
        message.style.color = "green";

    } catch (error) {
        message.textContent = error.message;
        message.style.color = "red";

        if (error.message.includes("credentials")) {
            localStorage.removeItem("access_token");
            localStorage.removeItem("user");
            window.location.href = "../login.html";
        }
    }
}




/* Load all managers */


/* Load all managers */

async function loadManagers() {
    const tableBody = document.getElementById("managersTableBody");
    const message = document.getElementById("managersMessage");

    try {
        const user = JSON.parse(localStorage.getItem("user") || "null");

        if (!user || user.role !== "admin") {
            window.location.href = "../login.html";
            return;
        }

        const managers = await apiRequest("/managers/");

        tableBody.innerHTML = "";

        if (managers.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="5">No managers found.</td>
                </tr>
            `;
            return;
        }

        managers.forEach(manager => {
            const row = document.createElement("tr");

            const statusClass = manager.is_active
                ? "status-active"
                : "status-inactive";

            const statusText = manager.is_active
                ? "Active"
                : "Inactive";

            const actionText = manager.is_active
                ? "Deactivate"
                : "Reactivate";

            const actionClass = manager.is_active
                ? "deactivate-btn"
                : "activate-btn";

            row.innerHTML = `
                <td>${manager.id}</td>
                <td>${escapeHTML(manager.name)}</td>
                <td>${escapeHTML(manager.email)}</td>
                <td>
                    <span class="status-badge ${statusClass}">
                        ${statusText}
                    </span>
                </td>
                <td>
                    <button
                        class="action-btn view-btn"
                        data-action="view"
                        data-manager-id="${manager.id}">
                        View
                    </button>

                    <button
                        class="action-btn ${actionClass}"
                        data-action="toggle"
                        data-manager-id="${manager.id}"
                        data-active="${manager.is_active}">
                        ${actionText}
                    </button>
                </td>
            `;

            tableBody.appendChild(row);
        });

        message.textContent = "Managers loaded successfully.";
        message.style.color = "green";

    } catch (error) {
        message.textContent = error.message;
        message.style.color = "red";
    }
}

/* Handle Manager actions */

if (!tableBodyActionHandlerAdded()) {
    document.addEventListener("click", handleManagerAction);
}

function tableBodyActionHandlerAdded() {
    return window.managerActionHandlerAdded === true;
}

window.managerActionHandlerAdded = true;

async function handleManagerAction(event) {
    const button = event.target.closest(".action-btn");

    if (!button || !document.getElementById("managersTableBody")?.contains(button)) {
        return;
    }

    const managerId = button.dataset.managerId;
    const action = button.dataset.action;

    if (action === "view") {
        window.location.href =
            `manager-details.html?id=${managerId}`;
        return;
    }

    if (action === "toggle") {
        const currentlyActive = button.dataset.active === "true";

        const newStatus = !currentlyActive;

        const confirmation = confirm(
            `Are you sure you want to ${
                newStatus ? "reactivate" : "deactivate"
            } this manager?`
        );

        if (!confirmation) return;

        try {
            await apiRequest(`/admin/managers/${managerId}`, {
                method: "PATCH",
                body: JSON.stringify({
                    is_active: newStatus
                })
            });

            alert(
                `Manager ${
                    newStatus ? "reactivated" : "deactivated"
                } successfully!`
            );

            await loadManagers();

        } catch (error) {
            alert(error.message);
        }
    }
}


function escapeHTML(value) {
    const element = document.createElement("div");
    element.textContent = value ?? "";
    return element.innerHTML;
}

/* Run manager loader only on the Managers page */

if (document.getElementById("managersTableBody")) {
    document.addEventListener("DOMContentLoaded", loadManagers);
}



/* Load selected manager details */

async function loadManagerDetails() {
    const managerInfo = document.getElementById("managerInfo");
    const employeesTable = document.getElementById("employeesTableBody");
    const message = document.getElementById("detailsMessage");

    try {
        const user = JSON.parse(localStorage.getItem("user") || "null");

        if (!user || user.role !== "admin") {
            window.location.href = "../login.html";
            return;
        }

        const params = new URLSearchParams(window.location.search);
        const managerId = params.get("id");

        if (!managerId || !/^\d+$/.test(managerId)) {
            throw new Error("Invalid manager ID");
        }

        const manager = await apiRequest(
            `/admin/managers/${managerId}`
        );


// Edit Manager button functionality

const editButton = document.getElementById("editManagerButton");
const editForm = document.getElementById("editManagerForm");

editButton.addEventListener("click", function () {

    // Fill form with existing manager details
    document.getElementById("editName").value = manager.name;

    document.getElementById("editEmail").value = manager.email;

    document.getElementById("editPassword").value = "";

    // Show edit form
    editForm.style.display = "block";

    editForm.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
});

// Cancel button functionality

document.getElementById("cancelEditButton").addEventListener(
    "click",
    function () {
        editForm.style.display = "none";
    }
);

// Update Manager Details

document.getElementById("managerUpdateForm").addEventListener(
    "submit",
    async function (event) {

        event.preventDefault();

        const updateMessage =
            document.getElementById("editManagerMessage");

        const updatedData = {
            name: document.getElementById("editName").value.trim(),
            email: document.getElementById("editEmail").value.trim()
        };

        const newPassword =
            document.getElementById("editPassword").value;

        if (newPassword.trim() !== "") {
            updatedData.password = newPassword;
        }

        try {
            await apiRequest(`/admin/managers/${managerId}`, {
                method: "PATCH",
                body: JSON.stringify(updatedData)
            });

            updateMessage.style.color = "green";
            updateMessage.textContent =
                "Manager updated successfully!";

            setTimeout(() => {
                window.location.reload();
            }, 1000);

        } catch (error) {
            updateMessage.style.color = "red";
            updateMessage.textContent = error.message;
        }
    }
);


        managerInfo.innerHTML = `
            <p><strong>Name:</strong> ${escapeHTML(manager.name)}</p>
            <p><strong>Email:</strong> ${escapeHTML(manager.email)}</p>
            <p><strong>Status:</strong>
                ${manager.is_active ? "Active" : "Inactive"}
            </p>
        `;

        document.getElementById("totalEmployees").textContent =
            `Total Employees: ${manager.total_employees}`;

        employeesTable.innerHTML = "";

        if (manager.employees.length === 0) {
            employeesTable.innerHTML = `
                <tr>
                    <td colspan="4">No employees found.</td>
                </tr>
            `;
        } else {
            manager.employees.forEach(employee => {
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
                `;

                employeesTable.appendChild(row);
            });
        }

        message.textContent = "Manager details loaded successfully.";
        message.style.color = "green";

    } catch (error) {
        managerInfo.textContent = error.message;
        employeesTable.innerHTML = "";
        message.textContent = error.message;
        message.style.color = "red";
    }
}

/* Run only on Manager Details page */

if (document.getElementById("managerInfo")) {
    document.addEventListener("DOMContentLoaded", loadManagerDetails);
}


/* Load all employees for Admin */

async function loadAllEmployees() {
    const tableBody = document.getElementById("employeesTableBody");
    const message = document.getElementById("employeesMessage");

    try {
        const user = JSON.parse(localStorage.getItem("user") || "null");

        if (!user || user.role !== "admin") {
            window.location.href = "../login.html";
            return;
        }

        const employees = await apiRequest("/admin/employees");

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
                <td>${employee.manager_id ?? "Not assigned"}</td>
                <td>
                    <span class="status-badge ${
                        employee.is_active
                            ? "status-active"
                            : "status-inactive"
                    }">
                        ${employee.is_active ? "Active" : "Inactive"}
                    </span>
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

/* Run only on Admin Employees page */

if (
    document.getElementById("employeesTableBody") &&
    document.getElementById("employeesMessage")
) {
    document.addEventListener("DOMContentLoaded", loadAllEmployees);
}
