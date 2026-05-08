/**
 * Edumart - Dashboard JS
 * Fetches and displays user stats and activity
 */
document.addEventListener('DOMContentLoaded', () => {
    const fetchStats = async () => {
        try {
            const res = await fetch('/auth/api/dashboard/', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                }
            });
            const data = await res.json();
            
            if (data) {
                // Update stats
                document.getElementById('dashResumes').textContent = data.stats.resumes_analyzed;
                document.getElementById('dashRoadmaps').textContent = data.stats.roadmaps_created;
                document.getElementById('dashInterviews').textContent = data.stats.interviews_completed;
                document.getElementById('dashScore').textContent = data.stats.overall_score;
                document.getElementById('dashStreak').textContent = data.user.streak;
                
                // Update completion banner
                const percent = data.user.completion;
                document.getElementById('dashCompletionFill').style.width = `${percent}%`;
                if (percent === 100) {
                    document.getElementById('completionBanner').style.display = 'none';
                }

                // Update activity
                const feed = document.getElementById('dashActivityFeed');
                if (data.recent_activity.length > 0) {
                    feed.innerHTML = data.recent_activity.map(act => `
                        <div class="notif-item">
                            <div class="notif-item-icon" style="background:rgba(79,140,255,0.1);color:var(--accent-blue);">
                                <i class="fas fa-history"></i>
                            </div>
                            <div class="notif-item-content">
                                <strong>${act.title}</strong>
                                <p>${act.description}</p>
                            </div>
                            <div class="notif-item-time">${new Date(act.created_at).toLocaleDateString()}</div>
                        </div>
                    `).join('');
                }
            }
        } catch (err) {
            console.error('Failed to load dashboard stats:', err);
        }
    };

    if (window.EDUMART.isAuthenticated) {
        fetchStats();
    }
});
