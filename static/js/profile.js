/**
 * Edumart - Profile JS
 * Handles Profile CRUD, Skills, and Avatar Upload
 */
document.addEventListener('DOMContentLoaded', () => {
    const fetchProfile = async () => {
        try {
            const res = await fetch('/auth/api/profile/', {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
            });
            const data = await res.json();
            renderProfile(data);
        } catch (err) {
            console.error('Failed to fetch profile:', err);
        }
    };

    const renderProfile = (profile) => {
        if (!profile) return;
        
        document.getElementById('profileName').textContent = profile.full_name;
        document.getElementById('profileHeadline').textContent = profile.headline || 'Add a headline to your profile';
        document.getElementById('profileBio').textContent = profile.bio || 'No bio added yet.';
        document.getElementById('profileEducation').textContent = profile.education || 'No education details.';
        document.getElementById('profileCareerInterests').textContent = profile.career_interests || 'No interests added.';
        
        // Stats
        document.getElementById('statResumes').textContent = profile.stats?.resumes_analyzed || 0;
        document.getElementById('statRoadmaps').textContent = profile.stats?.roadmaps_created || 0;
        document.getElementById('statInterviews').textContent = profile.stats?.interviews_completed || 0;
        document.getElementById('statCourses').textContent = profile.stats?.courses_saved || 0;

        // Completion
        const percent = profile.completion_percentage;
        document.getElementById('completionPercent').textContent = `${percent}%`;
        document.getElementById('completionFill').style.width = `${percent}%`;

        // Avatar
        if (profile.avatar) {
            const img = document.getElementById('avatarImage');
            img.src = profile.avatar;
            img.style.display = 'block';
            document.getElementById('avatarInitial').style.display = 'none';
        }

        // Skills
        renderSkills(profile.skills);
    };

    const renderSkills = (skills) => {
        const list = document.getElementById('skillsList');
        if (!skills || skills.length === 0) {
            list.innerHTML = '<p class="empty-state-text">No skills added yet</p>';
            return;
        }
        list.innerHTML = skills.map(s => `
            <div class="skill-tag">
                <span>${s.name}</span>
                <span class="skill-level">${s.proficiency}</span>
                <button class="skill-delete" onclick="deleteSkill(${s.id})"><i class="fas fa-times"></i></button>
            </div>
        `).join('');
    };

    // Edit Profile Modal
    const editBtn = document.getElementById('editProfileBtn');
    const modal = document.getElementById('editProfileModal');
    if (editBtn) {
        editBtn.onclick = () => modal.style.display = 'flex';
        document.getElementById('closeEditModal').onclick = () => modal.style.display = 'none';
        document.getElementById('cancelEditBtn').onclick = () => modal.style.display = 'none';
    }

    // Save Profile
    document.getElementById('saveProfileBtn')?.addEventListener('click', async () => {
        const formData = {
            first_name: document.getElementById('editFirstName').value,
            last_name: document.getElementById('editLastName').value,
            headline: document.getElementById('editHeadline').value,
            bio: document.getElementById('editBio').value,
            location: document.getElementById('editLocation').value,
            experience_level: document.getElementById('editExperience').value,
            education: document.getElementById('editEducation').value,
            career_interests: document.getElementById('editCareerInterests').value,
            linkedin_url: document.getElementById('editLinkedin').value,
            github_url: document.getElementById('editGithub').value,
        };

        try {
            const res = await fetch('/auth/api/profile/update/', {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': window.EDUMART.csrfToken,
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                },
                body: JSON.stringify(formData)
            });
            const result = await res.json();
            if (result.success) {
                window.showToast('Success', 'Profile updated!', 'success');
                modal.style.display = 'none';
                fetchProfile();
            }
        } catch (err) {
            window.showToast('Error', 'Update failed', 'error');
        }
    });

    if (window.EDUMART.isAuthenticated) {
        fetchProfile();
    }
});
