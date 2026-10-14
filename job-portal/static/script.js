
document.addEventListener("DOMContentLoaded", () => {
    // Open the edit form for the selected application.
    document.querySelectorAll(".edit-button").forEach((button) => {
        button.addEventListener("click", () => {
            const jobId = button.dataset.jobId;
            const detailsRow = document.getElementById(`details-${jobId}`);

            if (!detailsRow) return;

            // Close other open edit forms.
            document.querySelectorAll(".details-row").forEach((row) => {
                if (row !== detailsRow) {
                    row.hidden = true;
                }
            });

            detailsRow.hidden = !detailsRow.hidden;

            if (!detailsRow.hidden) {
                detailsRow.scrollIntoView({
                    behavior: "smooth",
                    block: "nearest"
                });
            }
        });
    });

    // Close the edit form when Cancel is clicked.
    document.querySelectorAll(".cancel-edit").forEach((button) => {
        button.addEventListener("click", () => {
            const jobId = button.dataset.jobId;
            const detailsRow = document.getElementById(`details-${jobId}`);

            if (detailsRow) {
                detailsRow.hidden = true;
            }
        });
    });

    // Automatically hide flash messages after a short delay.
    document.querySelectorAll(".flash").forEach((message) => {
        window.setTimeout(() => {
            message.style.transition = "opacity 0.4s ease";
            message.style.opacity = "0";

            window.setTimeout(() => message.remove(), 400);
        }, 4500);
    });
});
