/**
 * AI-POWERED SKILL GAP ANALYZER & CAREER GUIDANCE
 * Frontend JavaScript Controller
 */

document.addEventListener('DOMContentLoaded', function () {
    // 1. Initialize Bootstrap Tooltips & Popovers
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // 2. Interactive Topic Progress Checkboxes (AJAX)
    const topicCheckboxes = document.querySelectorAll('.topic-progress-toggle');
    topicCheckboxes.forEach(function (checkbox) {
        checkbox.addEventListener('change', function () {
            const topicId = this.dataset.topicId;
            const careerId = this.dataset.careerId || null;
            const titleEl = document.getElementById(`topic-title-${topicId}`);
            const cardEl = document.getElementById(`topic-card-${topicId}`);

            // Optimistic UI update
            if (this.checked) {
                if (titleEl) titleEl.classList.add('topic-completed-strike');
                if (cardEl) cardEl.classList.add('bg-light');
            } else {
                if (titleEl) titleEl.classList.remove('topic-completed-strike');
                if (cardEl) cardEl.classList.remove('bg-light');
            }

            // AJAX call to backend
            fetch(`/api/toggle_topic/${topicId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({ career_id: careerId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update progress display counters
                    const completedEl = document.getElementById('stat-completed-topics');
                    const pendingEl = document.getElementById('stat-pending-topics');
                    const progressPercentEl = document.getElementById('stat-progress-percent');
                    const progressBarEl = document.getElementById('stat-progress-bar');

                    if (completedEl) completedEl.textContent = data.completed_topics;
                    if (pendingEl) pendingEl.textContent = data.pending_topics;
                    if (progressPercentEl) progressPercentEl.textContent = `${data.progress_percentage}%`;
                    if (progressBarEl) {
                        progressBarEl.style.width = `${data.progress_percentage}%`;
                        progressBarEl.setAttribute('aria-valuenow', data.progress_percentage);
                    }
                } else {
                    // Revert state if failed
                    this.checked = !this.checked;
                    alert('Could not update topic progress. Please try again.');
                }
            })
            .catch(err => {
                console.error('Progress update error:', err);
                this.checked = !this.checked;
            });
        });
    });

    // 3. Auto-dismiss alerts after 6 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            try {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            } catch (e) {}
        }, 6000);
    });
});
