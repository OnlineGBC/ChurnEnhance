// General app utilities
document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss flash messages after 5 seconds
    document.querySelectorAll('[data-auto-dismiss]').forEach(el => {
        setTimeout(() => el.remove(), 5000);
    });
});
