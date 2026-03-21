// Healthcare Form Logic with API Integration
document.addEventListener('DOMContentLoaded', async () => {
    const form = document.getElementById('healthcare-form');
    let currentStep = 1;
    let formData = {
        department: null,
        doctor: null,
        priority: null
    };

    // Load departments from API
    async function loadDepartments() {
        const departments = [
            { id: 'opd', name: 'OPD', icon: '🩺', queue: 0 },
            { id: 'emergency', name: 'Emergency', icon: '🚨', queue: 0 },
            { id: 'lab', name: 'Laboratory', icon: '🔬', queue: 0 },
            { id: 'pharmacy', name: 'Pharmacy', icon: '💊', queue: 0 },
            { id: 'radiology', name: 'Radiology', icon: '📷', queue: 0 },
            { id: 'cardiology', name: 'Cardiology', icon: '❤️', queue: 0 }
        ];

        try {
            const queueData = await api.getHealthcareQueue();
            // Update queue counts if available
            departments.forEach(dept => {
                const queueInfo = queueData.find(q => q.department === dept.id);
                if (queueInfo) dept.queue = queueInfo.count || 0;
            });
        } catch (error) {
            console.log('Using default department data');
        }

        const grid = document.getElementById('department-grid');
        grid.innerHTML = departments.map(dept => `
            <div class="department-card" data-department="${dept.id}">
                <div class="department-icon">${dept.icon}</div>
                <div class="department-name">${dept.name}</div>
                <div class="department-queue">Current Queue: <strong>${dept.queue}</strong></div>
            </div>
        `).join('');

        attachDepartmentListeners();
    }

    // Load doctors based on department
    async function loadDoctors(department) {
        const doctors = [
            { id: 'any', name: 'Any Available Doctor', specialty: 'Fastest Queue', wait: 8, avatar: '👤' },
            { id: 'dr-sharma', name: 'Dr. Rajesh Sharma', specialty: 'General Medicine', wait: 15, avatar: '👨‍⚕️' },
            { id: 'dr-patel', name: 'Dr. Priya Patel', specialty: 'Internal Medicine', wait: 25, avatar: '👩‍⚕️' },
            { id: 'dr-kumar', name: 'Dr. Anil Kumar', specialty: 'Family Medicine', wait: 12, avatar: '👨‍⚕️' }
        ];

        const grid = document.getElementById('doctor-grid');
        grid.innerHTML = doctors.map(doc => `
            <div class="doctor-card" data-doctor="${doc.id}">
                <div class="doctor-avatar">${doc.avatar}</div>
                <div class="doctor-info">
                    <div class="doctor-name">${doc.name}</div>
                    <div class="doctor-specialty">${doc.specialty}</div>
                    <div class="doctor-status">
                        <span class="status-indicator ${doc.wait > 20 ? 'busy' : ''}"></span>
                        <span>~${doc.wait} min wait</span>
                    </div>
                </div>
            </div>
        `).join('');

        attachDoctorListeners();
    }

    // Step navigation
    function updateStep(step) {
        currentStep = step;
        document.querySelectorAll('.form-section').forEach((section, idx) => {
            section.classList.toggle('active', idx + 1 === step);
        });
        document.querySelectorAll('.step-dot').forEach((dot, idx) => {
            dot.classList.remove('active', 'completed');
            if (idx + 1 < step) dot.classList.add('completed');
            if (idx + 1 === step) dot.classList.add('active');
        });
        document.querySelectorAll('.step-line').forEach((line, idx) => {
            line.classList.toggle('completed', idx + 1 < step);
        });
        document.querySelector('.queue-form-container').scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    // Department selection
    function attachDepartmentListeners() {
        document.querySelectorAll('.department-card').forEach(card => {
            card.addEventListener('click', () => {
                document.querySelectorAll('.department-card').forEach(c => c.classList.remove('selected'));
                card.classList.add('selected');
                formData.department = card.dataset.department;
                document.querySelector('[data-step="1"] .next-step').disabled = false;
                document.getElementById('summary-department').textContent = card.querySelector('.department-name').textContent;
                loadDoctors(formData.department);
            });
        });
    }

    // Doctor selection
    function attachDoctorListeners() {
        document.querySelectorAll('.doctor-card').forEach(card => {
            card.addEventListener('click', () => {
                document.querySelectorAll('.doctor-card').forEach(c => c.classList.remove('selected'));
                card.classList.add('selected');
                formData.doctor = card.dataset.doctor;
                document.querySelector('[data-step="2"] .next-step').disabled = false;
                document.getElementById('summary-doctor').textContent = card.querySelector('.doctor-name').textContent;
            });
        });
    }

    // Priority selection
    document.querySelectorAll('.priority-card').forEach(card => {
        card.addEventListener('click', () => {
            document.querySelectorAll('.priority-card').forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');
            formData.priority = card.dataset.priority;
            document.querySelector('[data-step="3"] .next-step').disabled = false;
            document.getElementById('summary-priority').textContent = card.querySelector('.priority-name').textContent;

            const times = { emergency: '~2', senior: '~8', normal: '~15' };
            document.getElementById('estimated-time').textContent = times[formData.priority];

            // ── Emergency fraud warning ──────────────────────────────────────
            // Remove old warning if any
            const oldWarning = document.getElementById('emergency-fraud-warning');
            if (oldWarning) oldWarning.remove();

            if (formData.priority === 'emergency') {
                const warning = document.createElement('div');
                warning.id = 'emergency-fraud-warning';
                warning.style.cssText = `
                    background: rgba(239,71,111,0.12);
                    border: 1px solid rgba(239,71,111,0.5);
                    border-radius: 10px;
                    padding: 14px 16px;
                    margin-top: 16px;
                    font-size: 0.88rem;
                    color: #ef476f;
                    line-height: 1.5;
                `;
                warning.innerHTML = `
                    <strong>⚠️ Emergency Declaration Notice</strong><br>
                    Emergency status gives you immediate priority but will be <strong>verified by staff on arrival</strong>.
                    If your claim is rejected, your token will be moved to the <strong>back of the normal queue</strong> as a penalty.
                    Please only select Emergency if you have a genuine medical emergency.
                `;
                // Insert warning after priority grid
                card.closest('.priority-grid').insertAdjacentElement('afterend', warning);
            }
        });
    });

    // Navigation buttons
    document.querySelectorAll('.next-step').forEach(btn => {
        btn.addEventListener('click', () => updateStep(currentStep + 1));
    });
    document.querySelectorAll('.prev-step').forEach(btn => {
        btn.addEventListener('click', () => updateStep(currentStep - 1));
    });

    // Form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const name = document.getElementById('patient-name').value.trim();
        const phone = document.getElementById('patient-phone').value.trim();
        const age = document.getElementById('patient-age').value;
        const gender = document.getElementById('patient-gender').value;
        const reason = document.getElementById('patient-reason').value.trim();

        if (!name || !phone) {
            alert('Please fill in your name and phone number.');
            return;
        }

        const submitBtn = document.getElementById('submit-btn');
        submitBtn.disabled = true;
        submitBtn.textContent = '⏳ Creating Token...';

        try {
            const tokenData = {
                name,
                phone,
                department: formData.department,
                doctor: formData.doctor,
                priority: formData.priority,
                age: age ? parseInt(age) : null,
                gender: gender || null,
                reason: reason || null
            };

            const response = await api.createHealthcareToken(tokenData);

            // Store token data for display
            localStorage.setItem('currentToken', JSON.stringify({
                id: response.token_id,
                type: 'healthcare',
                ...tokenData,
                position: response.position,
                estimatedWait: response.estimated_wait_time,
                timestamp: Date.now()
            }));

            window.location.href = 'token.html';
        } catch (error) {
            console.error('Error creating token:', error);
            alert('Failed to create token. Please try again.');
            submitBtn.disabled = false;
            submitBtn.textContent = '🎫 Get My Token';
        }
    });

    // Initialize
    await loadDepartments();
});
