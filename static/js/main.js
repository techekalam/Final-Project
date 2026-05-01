document.addEventListener('DOMContentLoaded', () => {
    let currentUser = null;
    const loginView = document.getElementById('login-view');
    const dashboardView = document.getElementById('dashboard-view');
    const loginForm = document.getElementById('login-form');
    const loginError = document.getElementById('login-error');
    const logoutBtn = document.getElementById('logout-btn');
    const userRoleEl = document.getElementById('user-role');
    const navLinksEl = document.getElementById('nav-links');
    const dynamicContent = document.getElementById('dynamic-content');
    const pageTitle = document.getElementById('page-title');
    const pageSub = document.getElementById('page-subtitle');

    function formatUGX(a) { return 'UGX ' + Number(a).toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 }); }
    function injectTemplate(id) { const t = document.getElementById(id); dynamicContent.innerHTML = ''; dynamicContent.appendChild(t.content.cloneNode(true)); }
    function setPageHeader(t, s) { pageTitle.textContent = t; pageSub.textContent = s || ''; }

    // AUTH
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault(); loginError.textContent = '';
        const email = document.getElementById('email').value.trim(), password = document.getElementById('password').value;
        try {
            const res = await fetch('/api/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email, password }) });
            const data = await res.json();
            if (res.ok) { currentUser = data.user; initDashboard(); } else { loginError.textContent = data.error || 'Invalid credentials.'; }
        } catch (err) { loginError.textContent = 'Server error.'; }
    });
    logoutBtn.addEventListener('click', () => {
        currentUser = null; loginView.classList.add('active'); dashboardView.classList.remove('active');
        document.getElementById('email').value = ''; document.getElementById('password').value = ''; loginError.textContent = '';
    });

    function initDashboard() {
        loginView.classList.remove('active'); dashboardView.classList.add('active');
        document.getElementById('sidebar-user-name').textContent = currentUser.name || currentUser.email;
        document.getElementById('sidebar-user-role').textContent = currentUser.role;
        userRoleEl.textContent = currentUser.role;
        const initials = (currentUser.name || 'U').split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2);
        document.getElementById('user-avatar').textContent = initials;
        setupSidebar();
        if (currentUser.role === 'student') loadStudentDashboard(); else if (currentUser.role === 'lecturer') loadAdminDashboard(); else loadAdminDashboard();
    }

    function setupSidebar() {
        navLinksEl.innerHTML = '';
        let links = [];
        if (currentUser.role === 'student') {
            links = [
                { id: 'nav-dash', icon: '📊', text: 'Dashboard', action: loadStudentDashboard },
                { id: 'nav-profile', icon: '👤', text: 'My Profile', action: loadStudentProfile },
                { id: 'nav-enroll', icon: '📘', text: 'Enrollment', action: loadEnrollment },
                { id: 'nav-transcript', icon: '📜', text: 'Transcripts', action: loadTranscripts },
                { id: 'nav-tuition', icon: '💰', text: 'Tuition', action: loadTuition },
            ];
        } else if (currentUser.role === 'lecturer') {
            links = [
                { id: 'nav-dash', icon: '📊', text: 'Dashboard', action: loadAdminDashboard },
                { id: 'nav-profile', icon: '👤', text: 'My Profile', action: loadUserProfile },
                { id: 'nav-grades', icon: '📝', text: 'Input Grades', action: loadGradeInput },
                { id: 'nav-courses', icon: '📘', text: 'Courses', action: loadAdminCourses },
                {id:'nav-addcourse',icon:'➕',text:'Add Course',action:loadAddCourse},
                {id:'nav-students',icon:'👥',text:'Students',action:loadAllStudents},
                {id:'nav-transcript',icon:'📜',text:'Results',action:loadTranscripts},
            ];
        } else if (currentUser.role === 'finance') {
            links = [
                { id: 'nav-dash', icon: '📊', text: 'Dashboard', action: loadAdminDashboard },
                { id: 'nav-profile', icon: '👤', text: 'My Profile', action: loadUserProfile },
                { id: 'nav-students', icon: '👥', text: 'All Students', action: loadAllStudents },
                { id: 'nav-courses', icon: '📘', text: 'Courses', action: loadAdminCourses },
                { id: 'nav-tuition', icon: '💰', text: 'Finance', action: loadTuition },
                { id: 'nav-transcript', icon: '📜', text: 'Results', action: loadTranscripts },
                { id: 'nav-reports', icon: '📈', text: 'Reports', action: loadReports },
            ];
        } else {
            links = [
                { id: 'nav-dash', icon: '📊', text: 'Dashboard', action: loadAdminDashboard },
                { id: 'nav-profile', icon: '👤', text: 'My Profile', action: loadUserProfile },
                { id: 'nav-register', icon: '➕', text: 'Register Student', action: loadRegisterStudent },
                { id: 'nav-students', icon: '👥', text: 'All Students', action: loadAllStudents },
                { id: 'nav-courses', icon: '📘', text: 'Courses', action: loadAdminCourses },
                { id: 'nav-addcourse', icon: '📗', text: 'Add Course', action: loadAddCourse },
                { id: 'nav-grades', icon: '📝', text: 'Grade Input', action: loadGradeInput },
                { id: 'nav-tuition', icon: '💰', text: 'Finance', action: loadTuition },
                { id: 'nav-transcript', icon: '📜', text: 'Results', action: loadTranscripts },
                { id: 'nav-reports', icon: '📈', text: 'Reports', action: loadReports },
            ];
        }
        links.forEach(link => {
            const li = document.createElement('li'), a = document.createElement('a');
            a.href = '#'; a.id = link.id;
            a.innerHTML = '<span class="nav-icon">' + link.icon + '</span> ' + link.text;
            a.addEventListener('click', (e) => { e.preventDefault(); document.querySelectorAll('.sidebar-nav a').forEach(el => el.classList.remove('active')); a.classList.add('active'); link.action(); });
            li.appendChild(a); navLinksEl.appendChild(li);
        });
        if (navLinksEl.firstChild) navLinksEl.firstChild.querySelector('a').classList.add('active');
    }

    // MOBILE MENU LOGIC
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebar-overlay');

    function toggleSidebar() {
        menuToggle.classList.toggle('active');
        sidebar.classList.toggle('active');
        sidebarOverlay.classList.toggle('active');
    }

    menuToggle.addEventListener('click', toggleSidebar);
    sidebarOverlay.addEventListener('click', toggleSidebar);

    // Close sidebar when clicking links (mobile)
    navLinksEl.addEventListener('click', (e) => {
        if (window.innerWidth <= 850 && e.target.closest('a')) {
            toggleSidebar();
        }
    });

    // STUDENT DASHBOARD
    async function loadStudentDashboard() {
        setPageHeader('Student Dashboard', 'Welcome back, ' + currentUser.name + '!');
        injectTemplate('tpl-student-dashboard');
        try {
            const d = await (await fetch('/api/student/dashboard?user_id=' + currentUser.id)).json();
            document.getElementById('fee-balance').textContent = formatUGX(d.fee_balance);
            document.getElementById('enrolled-count').textContent = d.enrolled_count || d.upcoming_lessons.length || 3;
            const perf = d.performance, avg = perf.length ? (perf.reduce((a, b) => a + b, 0) / perf.length).toFixed(0) : 0;
            document.getElementById('avg-score').textContent = avg + '%';
            const list = document.getElementById('lesson-list');
            d.upcoming_lessons.forEach(l => { const li = document.createElement('li'); li.innerHTML = '<strong>' + l.course + '</strong><br><small>' + l.date + ' · ' + l.time + '</small>'; list.appendChild(li); });
            renderChart(perf);
        } catch (err) { console.error(err); }
    }

    function renderChart(data) {
        const ctx = document.getElementById('performanceChart').getContext('2d');
        new Chart(ctx, { type: 'bar', data: { labels: ['Sem 1', 'Sem 2', 'Sem 3', 'Sem 4', 'Sem 5'], datasets: [{ label: 'Score (%)', data: data, backgroundColor: ['rgba(0,168,157,0.7)', 'rgba(0,40,85,0.7)', 'rgba(0,168,157,0.5)', 'rgba(0,40,85,0.5)', 'rgba(0,168,157,0.6)'], borderColor: 'rgba(0,168,157,1)', borderWidth: 1, borderRadius: 6 }] }, options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, max: 100, grid: { color: 'rgba(0,0,0,0.04)' } }, x: { grid: { display: false } } } } });
    }

    // STUDENT PROFILE
    async function loadStudentProfile() {
        setPageHeader('My Profile', 'View and update your personal information.');
        injectTemplate('tpl-student-profile');
        try {
            const d = await (await fetch('/api/student/profile?user_id=' + currentUser.id)).json();
            const p = d.profile;
            document.getElementById('prof-id').value = p.student_id || p.id || '';
            document.getElementById('prof-name').value = p.name || '';
            document.getElementById('prof-email').value = p.email || '';
            document.getElementById('prof-phone').value = p.phone || '';
            if (p.faculty) document.getElementById('prof-faculty').value = p.faculty;
            if (p.program) document.getElementById('prof-program').value = p.program;
        } catch (err) { console.error(err); }
        document.getElementById('profile-form').addEventListener('submit', async (e) => {
            e.preventDefault(); const msgEl = document.getElementById('profile-msg'); msgEl.textContent = '';
            const profile = { name: document.getElementById('prof-name').value, phone: document.getElementById('prof-phone').value, faculty: document.getElementById('prof-faculty').value, program: document.getElementById('prof-program').value };
            try {
                const res = await fetch('/api/student/profile', { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ user_id: currentUser.id, profile }) });
                if (res.ok) { msgEl.textContent = '✓ Profile updated!'; msgEl.style.color = '#28a745'; currentUser.name = profile.name; document.getElementById('sidebar-user-name').textContent = profile.name; }
                else { msgEl.textContent = '✗ Update failed'; msgEl.style.color = '#e53e3e'; }
                setTimeout(() => { msgEl.textContent = ''; }, 4000);
            } catch (err) { console.error(err); }
        });
    }

    // USER PROFILE (non-student stakeholders)
    async function loadUserProfile() {
        setPageHeader('My Profile', 'View and update your profile.');
        injectTemplate('tpl-user-profile');
        try {
            const d = await (await fetch('/api/user/profile?user_id=' + currentUser.id)).json();
            const p = d.profile;
            document.getElementById('up-name').value = p.name || '';
            document.getElementById('up-email').value = p.email || currentUser.email || '';
            document.getElementById('up-phone').value = p.phone || '';
            document.getElementById('up-department').value = p.department || '';
            document.getElementById('up-role-display').textContent = currentUser.role;
        } catch (err) { console.error(err); }
        document.getElementById('user-profile-form').addEventListener('submit', async (e) => {
            e.preventDefault(); const msgEl = document.getElementById('up-msg'); msgEl.textContent = '';
            const profile = { name: document.getElementById('up-name').value, phone: document.getElementById('up-phone').value, department: document.getElementById('up-department').value };
            try {
                const res = await fetch('/api/user/profile', { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ user_id: currentUser.id, profile }) });
                if (res.ok) { msgEl.textContent = '✓ Profile updated!'; msgEl.style.color = '#28a745'; currentUser.name = profile.name; document.getElementById('sidebar-user-name').textContent = profile.name; }
                else { msgEl.textContent = '✗ Update failed'; msgEl.style.color = '#e53e3e'; }
                setTimeout(() => { msgEl.textContent = ''; }, 4000);
            } catch (err) { console.error(err); }
        });
    }

    // ENROLLMENT
    async function loadEnrollment() {
        setPageHeader('Course Enrollment', 'Browse and enroll in available courses.');
        injectTemplate('tpl-enrollment');
        try {
            let enrolledIds = [];
            if (currentUser.role === 'student') { const er = await (await fetch('/api/student/enrollments?user_id=' + currentUser.id)).json(); enrolledIds = er.enrollments || []; }
            const d = await (await fetch('/api/courses')).json();
            const tbody = document.getElementById('courses-tbody');
            d.courses.forEach(c => {
                const tr = document.createElement('tr'), isE = enrolledIds.includes(c.id);
                tr.innerHTML = '<td><strong>' + c.code + '</strong></td><td>' + c.name + '</td><td>' + c.credits + '</td><td>' + (c.faculty || '—') + '</td><td><button class="' + (isE ? 'btn-small enrolled' : 'btn-small enroll-btn') + '" data-id="' + c.id + '">' + (isE ? 'Enrolled ✓' : 'Enroll') + '</button></td>';
                tbody.appendChild(tr);
            });
            tbody.addEventListener('click', async (e) => {
                if (!e.target.classList.contains('enroll-btn')) return;
                const res = await fetch('/api/student/enroll', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ student_id: currentUser.id, course_id: e.target.dataset.id }) });
                if (res.ok) { e.target.textContent = 'Enrolled ✓'; e.target.classList.remove('enroll-btn'); e.target.classList.add('enrolled'); }
                else { const err = await res.json(); alert(err.error || 'Failed'); }
            });
        } catch (err) { console.error(err); }
    }

    async function loadTranscripts(targetUserId, studentName) {
        setPageHeader('Academic Transcript', studentName ? `Viewing results for: ${studentName}` : 'Official academic record.');
        injectTemplate('tpl-transcripts');

        const isStaff = currentUser.role === 'admin' || currentUser.role === 'registry' || currentUser.role === 'finance' || currentUser.role === 'lecturer';
        if (isStaff) {
            const container = document.getElementById('search-container-results');
            container.style.display = 'block';
            if (studentName) document.getElementById('student-search-results').value = studentName;
            const header = document.getElementById('transcript-action-header');
            if (header) header.style.display = 'table-cell';
        }

        const uid = targetUserId || (currentUser.role === 'student' ? currentUser.id : null);
        if (!uid && isStaff) return;

        try {
            const d = await (await fetch('/api/results?user_id=' + (uid || 5))).json();
            const tbody = document.getElementById('transcript-tbody');
            tbody.innerHTML = '';
            d.results.forEach(r => {
                const tr = document.createElement('tr');
                const cn = r.course ? r.course.name : r.courses ? r.courses.name : '—';
                const cc = r.course ? r.course.code : r.courses ? r.courses.code : '—';
                
                let actionTd = '';
                if (isStaff) {
                    actionTd = `<td><button class="btn-small" onclick="window.editResult(${r.id}, this)">Edit</button></td>`;
                }
                
                tr.innerHTML = '<td><strong>' + cc + '</strong></td><td>' + cn + '</td><td>' + r.score + '</td><td><strong>' + r.grade + '</strong></td><td>' + r.semester + '</td>' + actionTd;
                tbody.appendChild(tr);
            });
        } catch (err) { console.error(err); }
    }

    window.editResult = async function(id, btn) {
        const newScore = prompt('Enter new score:');
        if (newScore === null) return;
        try {
            const res = await fetch('/api/results', { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id, score: newScore }) });
            if (res.ok) { loadTranscripts(); } else { alert('Failed to update result'); }
        } catch (err) { console.error(err); }
    };

    async function loadTuition(targetUserId, studentName) {
        setPageHeader('Tuition Tracker', studentName ? `Financial records for: ${studentName}` : 'Fee balances and payment history.');
        injectTemplate('tpl-tuition');

        const isStaff = currentUser.role === 'admin' || currentUser.role === 'registry' || currentUser.role === 'finance';
        if (isStaff) {
            const container = document.getElementById('search-container-finance');
            container.style.display = 'block';
            if (studentName) document.getElementById('student-search-finance').value = studentName;
        }

        const uid = targetUserId || (currentUser.role === 'student' ? currentUser.id : null);
        if (!uid && isStaff) {
            document.getElementById('total-due').textContent = formatUGX(0);
            document.getElementById('total-paid').textContent = formatUGX(0);
            document.getElementById('tuition-balance').textContent = formatUGX(0);
            return;
        }

        try {
            const d = await (await fetch('/api/fees?user_id=' + (uid || 5))).json();
            let totalDue = 0, totalPaid = 0;
            const tbody = document.getElementById('fees-tbody');
            tbody.innerHTML = '';
            d.fees.forEach(f => {
                totalDue += parseFloat(f.amount_due); totalPaid += parseFloat(f.amount_paid);
                const tr = document.createElement('tr');
                tr.innerHTML = '<td>' + f.semester + '</td><td>' + formatUGX(f.amount_due) + '</td><td>' + formatUGX(f.amount_paid) + '</td><td>' + (f.due_date || '—') + '</td><td class="' + (f.status === 'paid' ? 'status-paid' : 'status-pending') + '">' + f.status.toUpperCase() + '</td>';
                tbody.appendChild(tr);
            });
            document.getElementById('total-due').textContent = formatUGX(totalDue);
            document.getElementById('total-paid').textContent = formatUGX(totalPaid);
            document.getElementById('tuition-balance').textContent = formatUGX(totalDue - totalPaid);
        } catch (err) { console.error(err); }
    }

    // ADMIN DASHBOARD
    async function loadAdminDashboard() {
        setPageHeader('Dashboard', 'System overview and recent activity.');
        injectTemplate('tpl-admin-dashboard');
        try {
            const d = await (await fetch('/api/admin/dashboard')).json();
            document.getElementById('admin-revenue').textContent = formatUGX(d.total_revenue);
            document.getElementById('admin-admissions').textContent = d.new_admissions;
            document.getElementById('admin-pending').textContent = d.pending_results;
            const tbody = document.getElementById('admin-activity-table');
            d.recent_activity.forEach(a => { const tr = document.createElement('tr'); tr.innerHTML = '<td>' + a.student + '</td><td>' + a.action + '</td><td>' + a.time + '</td>'; tbody.appendChild(tr); });
        } catch (err) { console.error(err); }
    }

    // REGISTER STUDENT
    function loadRegisterStudent() {
        setPageHeader('Register Student', 'Add a new student to the system.');
        injectTemplate('tpl-register-student');
        document.getElementById('register-form').addEventListener('submit', async (e) => {
            e.preventDefault(); const msgEl = document.getElementById('register-msg'); msgEl.textContent = '';
            const payload = { name: document.getElementById('reg-name').value, email: document.getElementById('reg-email').value, phone: document.getElementById('reg-phone').value, faculty: document.getElementById('reg-faculty').value, program: document.getElementById('reg-program').value };
            try {
                const res = await fetch('/api/student/register', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
                const data = await res.json();
                if (res.ok) { msgEl.textContent = '✓ ' + data.message; msgEl.style.color = '#28a745'; document.getElementById('register-form').reset(); }
                else { msgEl.textContent = '✗ ' + (data.error || 'Failed'); msgEl.style.color = '#e53e3e'; }
                setTimeout(() => { msgEl.textContent = ''; }, 5000);
            } catch (err) { console.error(err); }
        });
    }

    // ALL STUDENTS
    async function loadAllStudents() {
        setPageHeader('All Students', 'View all registered students.');
        injectTemplate('tpl-all-students');
        try {
            const d = await (await fetch('/api/students')).json();
            const tbody = document.getElementById('all-students-tbody');
            d.students.forEach(s => { const tr = document.createElement('tr'); tr.innerHTML = '<td><strong>' + (s.student_id || '—') + '</strong></td><td>' + (s.name || '—') + '</td><td>' + (s.email || '—') + '</td><td>' + (s.faculty || '—') + '</td><td>' + (s.program || '—') + '</td><td>' + (s.phone || '—') + '</td>'; tbody.appendChild(tr); });
        } catch (err) { console.error(err); }
    }

    // ADMIN COURSES
    async function loadAdminCourses() {
        setPageHeader('Course Catalog', 'All available courses.');
        injectTemplate('tpl-admin-courses');
        try {
            const d = await (await fetch('/api/courses')).json();
            const tbody = document.getElementById('admin-courses-tbody');

            const canDelete = currentUser.role === 'admin' || currentUser.role === 'registry';

            d.courses.forEach(c => {
                const tr = document.createElement('tr');
                let actionHtml = '<td>—</td>';
                if (canDelete) {
                    actionHtml = `<td><button class="btn-small" style="background:#e53e3e;" onclick="deleteCourse(${c.id}, this)">Delete</button></td>`;
                }
                tr.innerHTML = '<td><strong>' + c.code + '</strong></td><td>' + c.name + '</td><td>' + c.credits + '</td><td>' + (c.faculty || '—') + '</td>' + actionHtml;
                tbody.appendChild(tr);
            });
        } catch (err) { console.error(err); }
    }

    // Global delete function for simplicity in inline onclick
    window.deleteCourse = async function (id, btn) {
        if (!confirm('Are you sure you want to delete this course? All related enrollments and results will also be deleted.')) return;
        try {
            const res = await fetch(`/api/courses?id=${id}`, { method: 'DELETE' });
            if (res.ok) {
                btn.closest('tr').remove();
            } else {
                const data = await res.json();
                alert(data.error || 'Failed to delete course');
            }
        } catch (err) { console.error(err); }
    };

    // ADD COURSE
    function loadAddCourse() {
        setPageHeader('Add Course', 'Create a new course in the catalog.');
        injectTemplate('tpl-add-course');
        document.getElementById('add-course-form').addEventListener('submit', async (e) => {
            e.preventDefault(); const msgEl = document.getElementById('add-course-msg'); msgEl.textContent = '';
            const payload = { code: document.getElementById('course-code').value, name: document.getElementById('course-name').value, credits: parseInt(document.getElementById('course-credits').value), faculty: document.getElementById('course-faculty').value };
            try {
                const res = await fetch('/api/courses', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
                const data = await res.json();
                if (res.ok) { msgEl.textContent = '✓ ' + data.message; msgEl.style.color = '#28a745'; document.getElementById('add-course-form').reset(); }
                else { msgEl.textContent = '✗ ' + (data.error || 'Failed'); msgEl.style.color = '#e53e3e'; }
                setTimeout(() => { msgEl.textContent = ''; }, 5000);
            } catch (err) { console.error(err); }
        });
    }

    // GRADE INPUT
    async function loadGradeInput() {
        setPageHeader('Input Grades', 'Submit student grades for courses.');
        injectTemplate('tpl-grade-input');
        try {
            // Populate student dropdown
            const sd = await (await fetch('/api/students')).json();
            const stuSelect = document.getElementById('grade-student');
            sd.students.forEach(s => { const o = document.createElement('option'); o.value = s.student_id || s.id; o.textContent = (s.student_id || '') + ' — ' + (s.name || ''); stuSelect.appendChild(o); });
            // Populate course dropdown
            const cd = await (await fetch('/api/courses')).json();
            const crsSelect = document.getElementById('grade-course');
            cd.courses.forEach(c => { const o = document.createElement('option'); o.value = c.id; o.textContent = c.code + ' — ' + c.name; crsSelect.appendChild(o); });
            // Load existing grades table
            await refreshGradesTable();
        } catch (err) { console.error(err); }

        // Auto-select grade letter based on score
        document.getElementById('grade-score').addEventListener('input', (e) => {
            const s = parseInt(e.target.value), sel = document.getElementById('grade-letter');
            if (s >= 90) sel.value = 'A+'; else if (s >= 80) sel.value = 'A'; else if (s >= 75) sel.value = 'B+';
            else if (s >= 70) sel.value = 'B'; else if (s >= 65) sel.value = 'C+'; else if (s >= 60) sel.value = 'C';
            else if (s >= 50) sel.value = 'D'; else if (s >= 0) sel.value = 'F';
        });

        document.getElementById('grade-form').addEventListener('submit', async (e) => {
            e.preventDefault(); const msgEl = document.getElementById('grade-msg'); msgEl.textContent = '';
            const payload = { student_id: document.getElementById('grade-student').value, course_id: document.getElementById('grade-course').value, score: parseFloat(document.getElementById('grade-score').value), grade: document.getElementById('grade-letter').value, semester: document.getElementById('grade-semester').value };
            try {
                const res = await fetch('/api/grades', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
                const data = await res.json();
                if (res.ok) { msgEl.textContent = '✓ ' + data.message; msgEl.style.color = '#28a745'; document.getElementById('grade-form').reset(); await refreshGradesTable(); }
                else { msgEl.textContent = '✗ ' + (data.error || 'Failed'); msgEl.style.color = '#e53e3e'; }
                setTimeout(() => { msgEl.textContent = ''; }, 5000);
            } catch (err) { console.error(err); }
        });
    }

    async function refreshGradesTable() {
        try {
            const d = await (await fetch('/api/grades')).json();
            const tbody = document.getElementById('grades-tbody');
            const recentList = document.getElementById('recent-grades-list');
            if (tbody) {
                tbody.innerHTML = '';
                d.grades.forEach(g => { const tr = document.createElement('tr'); tr.innerHTML = '<td>' + (g.student_name || g.students?.name || '—') + '</td><td>' + (g.student_id || g.students?.student_id || '—') + '</td><td>' + (g.course_code || g.courses?.code || '—') + '</td><td>' + g.score + '</td><td><strong>' + g.grade + '</strong></td><td>' + g.semester + '</td>'; tbody.appendChild(tr); });
            }
            if (recentList) {
                recentList.innerHTML = '';
                d.grades.slice(-5).reverse().forEach(g => { const li = document.createElement('li'); li.innerHTML = '<strong>' + (g.student_name || '—') + '</strong> — ' + (g.course_code || '—') + ': ' + g.grade + ' (' + g.score + ')'; recentList.appendChild(li); });
            }
        } catch (err) { console.error(err); }
    }

    // REPORTS
    function loadReports() {
        setPageHeader('Reports', 'Generate system reports.');
        dynamicContent.innerHTML = '';
        const w = document.createElement('div'); w.className = 'grid-layout';
        w.innerHTML = '<div class="glass-card span-2"><h3>📈 Enrollment Summary</h3><canvas id="enrollmentChart" height="120"></canvas></div><div class="glass-card span-1"><h3>📊 Quick Stats</h3><div class="info-block"><p><strong>Total Students:</strong> 45</p><p><strong>Active Courses:</strong> 6</p><p><strong>Revenue (Sem 1):</strong> ' + formatUGX(125000000) + '</p><p><strong>Fee Collection Rate:</strong> 76%</p><p><strong>Avg. GPA:</strong> 3.6</p></div></div><div class="glass-card span-3"><h3>💰 Financial Health</h3><canvas id="financeChart" height="80"></canvas></div>';
        dynamicContent.appendChild(w);
        setTimeout(() => {
            const isMobile = window.innerWidth <= 500;
            new Chart(document.getElementById('enrollmentChart').getContext('2d'), { type: 'doughnut', data: { labels: ['Science and Technology', 'Business Admin', 'Law', 'Engineering', 'Medicine'], datasets: [{ data: [18, 12, 8, 4, 3], backgroundColor: ['rgba(0,168,157,0.8)', 'rgba(0,40,85,0.8)', 'rgba(40,167,69,0.8)', 'rgba(240,173,78,0.8)', 'rgba(108,117,125,0.8)'], borderWidth: 2, borderColor: '#fff' }] }, options: { responsive: true, plugins: { legend: { position: isMobile ? 'bottom' : 'right' } } } });
            new Chart(document.getElementById('financeChart').getContext('2d'), { type: 'bar', data: { labels: ['Sem 1 2025', 'Sem 2 2025', 'Sem 1 2026', 'Sem 2 2026'], datasets: [{ label: 'Fees Due', data: [95e6, 98e6, 105e6, 125e6], backgroundColor: 'rgba(0,40,85,0.6)', borderRadius: 4 }, { label: 'Fees Collected', data: [82e6, 90e6, 95e6, 95e6], backgroundColor: 'rgba(0,168,157,0.6)', borderRadius: 4 }] }, options: { responsive: true, scales: { y: { beginAtZero: true, ticks: { callback: v => 'UGX ' + (v / 1e6) + 'M' }, grid: { color: 'rgba(0,0,0,0.04)' } }, x: { grid: { display: false } } } } });
        }, 100);
    }

    // STUDENT SEARCH LOGIC
    window.performStudentSearch = async function (context) {
        const input = document.getElementById(`student-search-${context}`);
        const list = document.getElementById(`search-${context}-list`);
        const query = input.value.trim();
        if (!query) return;

        try {
            const res = await fetch(`/api/students/search?q=${query}`);
            const data = await res.json();
            list.innerHTML = '';
            if (data.students.length === 0) {
                list.innerHTML = '<div class="search-item" style="padding:10px; color:#e53e3e;">No students found.</div>';
            } else {
                // If there's only one result, or an exact ID match, load it automatically
                const isExactID = data.students.find(s => s.student_id.toLowerCase() === query.toLowerCase());
                
                if (isExactID || data.students.length === 1) {
                    const s = isExactID || data.students[0];
                    input.value = s.name;
                    list.innerHTML = '';
                    if (context === 'results') loadTranscripts(s.user_id, s.name);
                    else loadTuition(s.user_id, s.name);
                } else {
                    data.students.forEach(s => {
                        const div = document.createElement('div');
                        div.className = 'search-item';
                        div.style = "padding:10px; cursor:pointer; border-bottom:1px solid rgba(0,0,0,0.05); transition: 0.2s;";
                        div.innerHTML = `<strong>${s.student_id}</strong> — ${s.name} <span style="font-size: 0.8em; opacity: 0.7;">(${s.faculty})</span>`;
                        div.onmouseover = () => div.style.background = 'rgba(0,40,85,0.05)';
                        div.onmouseout = () => div.style.background = 'transparent';
                        div.onclick = () => {
                            input.value = s.name;
                            list.innerHTML = '';
                            if (context === 'results') loadTranscripts(s.user_id, s.name);
                            else loadTuition(s.user_id, s.name);
                        };
                        list.appendChild(div);
                    });
                }
            }
        } catch (err) { console.error(err); }
    };

    // EDIT RESULT
    window.editResult = async function(id, btn) {
        const tr = btn.closest('tr');
        const oldScore = tr.cells[2].textContent;
        const newScore = prompt('Enter new score (0-100):', oldScore);
        if (newScore === null || newScore === oldScore) return;
        
        const score = parseFloat(newScore);
        if (isNaN(score) || score < 0 || score > 100) { alert('Invalid score'); return; }
        
        let grade = 'F';
        if(score>=90) grade='A+'; else if(score>=80) grade='A'; else if(score>=75) grade='B+';
        else if(score>=70) grade='B'; else if(score>=65) grade='C+'; else if(score>=60) grade='C';
        else if(score>=50) grade='D';
        
        try {
            const res = await fetch('/api/results', {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({id, score, grade})
            });
            if (res.ok) {
                tr.cells[2].textContent = score;
                tr.cells[3].innerHTML = `<strong>${grade}</strong>`;
                alert('Result updated successfully!');
            } else {
                const data = await res.json();
                alert(data.error || 'Failed to update');
            }
        } catch (err) { console.error(err); }
    };
});
