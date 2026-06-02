// ===== Config =====
const API = 'http://localhost:5000/api';

// ===== Token helpers =====
function getToken() { return localStorage.getItem('st_token'); }
function setToken(t) { localStorage.setItem('st_token', t); }
function clearToken() { localStorage.removeItem('st_token'); localStorage.removeItem('st_user'); }
function getUser() { const u = localStorage.getItem('st_user'); return u ? JSON.parse(u) : null; }
function setUser(u) { localStorage.setItem('st_user', JSON.stringify(u)); }

// ===== API wrapper =====
async function apiFetch(endpoint, method = 'GET', body = null, auth = true) {
    const headers = { 'Content-Type': 'application/json' };
    if (auth && getToken()) headers['Authorization'] = 'Bearer ' + getToken();
    const opts = { method, headers };
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(API + endpoint, opts);
    const data = await res.json();
    if (auth && res.status === 401) {
        clearToken();
        if (getPage() !== 'login' && getPage() !== 'signup') {
            navigate('login');
        }
    }
    return { ok: res.ok, status: res.status, data };
}

// ===== Toast =====
function showToast(message, type = 'info', duration = 3200) {
    const existing = document.getElementById('toast');
    if (existing) existing.remove();
    const toast = document.createElement('div');
    toast.id = 'toast';
    toast.className = 'toast ' + type;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), duration);
}

// ===== Router =====
function getPage() {
    return window.location.hash.replace('#', '') || 'home';
}

function navigate(page) {
    window.location.hash = page;
}

// ===== Render Navbar =====
function renderNavbar() {
    const token = getToken();
    const user = getUser();
    const nav = document.getElementById('navbar');
    if (!nav) return;
    if (!token) {
        nav.innerHTML = `
        <div class="logo">Skill<span>Tree</span></div>
        <div class="nav-links">
            <a href="#login">Login</a>
            <a href="#signup">Sign Up</a>
        </div>`;
    } else {
        nav.innerHTML = `
        <div class="logo">Skill<span>Tree</span></div>
        <div class="nav-links">
            <a href="#dashboard" id="nav-dashboard">Dashboard</a>
            <a href="#skills" id="nav-skills">Skills</a>
            <a href="#badges" id="nav-badges">Badges</a>
        </div>
        <div class="nav-user">
            <span class="xp-pill" id="nav-xp">XP: --</span>
            <span>${user ? user.username : ''}</span>
            <button class="btn btn-secondary btn-sm" onclick="logout()">Logout</button>
        </div>`;
        loadXP();
        highlightNav();
    }
}

function highlightNav() {
    const page = getPage();
    document.querySelectorAll('.nav-links a').forEach(a => {
        a.classList.remove('active');
        if (a.getAttribute('href') === '#' + page) a.classList.add('active');
    });
}

async function loadXP() {
    const res = await apiFetch('/auth/profile');
    if (res.ok) {
        const xpEl = document.getElementById('nav-xp');
        if (xpEl) xpEl.textContent = 'XP: ' + (res.data.xp ? res.data.xp.total_xp : 0);
    }
}

function logout() {
    clearToken();
    navigate('login');
    renderApp();
}

// ===== Auth: Signup =====
function renderSignup() {
    return `
    <div class="auth-container">
        <div class="auth-card">
            <h1>Create Account</h1>
            <p class="subtitle">Start your learning journey today</p>
            <div class="form-group">
                <label>Username</label>
                <input type="text" id="su-username" placeholder="e.g. coder123">
            </div>
            <div class="form-group">
                <label>Email</label>
                <input type="email" id="su-email" placeholder="you@example.com">
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" id="su-password" placeholder="at least 6 characters">
            </div>
            <div id="su-msg"></div>
            <button class="btn btn-primary" onclick="doSignup()">Create Account</button>
            <p class="auth-switch">Already have an account? <a href="#login">Login here</a></p>
        </div>
    </div>`;
}

async function doSignup() {
    const username = document.getElementById('su-username').value.trim();
    const email = document.getElementById('su-email').value.trim();
    const password = document.getElementById('su-password').value.trim();
    const msgEl = document.getElementById('su-msg');

    if (!username || !email || !password) {
        msgEl.innerHTML = '<div class="msg-error">Please fill in all fields.</div>';
        return;
    }

    const res = await apiFetch('/auth/signup', 'POST', { username, email, password }, false);
    if (res.ok) {
        setToken(res.data.token);
        setUser(res.data.user);
        showToast('Welcome! Account created.', 'success');
        navigate('dashboard');
        renderApp();
    } else {
        msgEl.innerHTML = `<div class="msg-error">${res.data.error || 'Signup failed'}</div>`;
    }
}

// ===== Auth: Login =====
function renderLogin() {
    return `
    <div class="auth-container">
        <div class="auth-card">
            <h1>Welcome Back</h1>
            <p class="subtitle">Log in to continue learning</p>
            <div class="form-group">
                <label>Email</label>
                <input type="email" id="li-email" placeholder="you@example.com">
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" id="li-password" placeholder="your password">
            </div>
            <div id="li-msg"></div>
            <button class="btn btn-primary" onclick="doLogin()">Login</button>
            <p class="auth-switch">Don't have an account? <a href="#signup">Sign up</a></p>
        </div>
    </div>`;
}

async function doLogin() {
    const email = document.getElementById('li-email').value.trim();
    const password = document.getElementById('li-password').value.trim();
    const msgEl = document.getElementById('li-msg');

    if (!email || !password) {
        msgEl.innerHTML = '<div class="msg-error">Please fill in all fields.</div>';
        return;
    }

    const res = await apiFetch('/auth/login', 'POST', { email, password }, false);
    if (res.ok) {
        setToken(res.data.token);
        setUser(res.data.user);
        showToast('Logged in successfully!', 'success');
        navigate('dashboard');
        renderApp();
    } else {
        msgEl.innerHTML = `<div class="msg-error">${res.data.error || 'Login failed'}</div>`;
    }
}

// ===== Dashboard =====
async function renderDashboard() {
    const [profileRes, skillsRes, badgesRes] = await Promise.all([
        apiFetch('/auth/profile'),
        apiFetch('/skills/my'),
        apiFetch('/badges/my')
    ]);

    const xp = profileRes.ok ? (profileRes.data.xp || {}) : {};
    const skills = skillsRes.ok ? skillsRes.data.user_skills : [];
    const badges = badgesRes.ok ? badgesRes.data.user_badges : [];

    const completed = skills.filter(s => s.status === 'completed').length;
    const assigned = skills.filter(s => s.status === 'assigned').length;

    return `
    <div class="page-wrapper">
        <h1 class="page-title">My Dashboard</h1>
        <p class="page-subtitle">Track your progress and keep learning</p>

        <div class="stats-row">
            <div class="stat-box">
                <div class="stat-number">${xp.total_xp || 0}</div>
                <div class="stat-label">Total XP</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">${xp.level || 1}</div>
                <div class="stat-label">Level</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">${completed}</div>
                <div class="stat-label">Skills Completed</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">${assigned}</div>
                <div class="stat-label">In Progress</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">${badges.length}</div>
                <div class="stat-label">Badges Earned</div>
            </div>
        </div>

        <h2 style="font-size:18px; margin-bottom:12px;">Recent Badges</h2>
        <div style="display:flex; gap:12px; flex-wrap:wrap; margin-bottom:28px;">
            ${badges.length === 0
                ? '<p style="color:#8a8480; font-family:Arial,sans-serif; font-size:14px;">No badges yet. Complete a skill to earn one!</p>'
                : badges.slice(0, 5).map(b =>
                    `<div style="background:#fff; border:1px solid #d5cfc4; border-radius:8px; padding:12px 16px; text-align:center; min-width:100px;">
                        <div style="font-size:28px;">${b.badge_icon || '⭐'}</div>
                        <div style="font-size:13px; color:#2c2c2c;">${b.badge_name}</div>
                    </div>`
                ).join('')
            }
        </div>

        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
            <h2 style="font-size:18px;">My Skills</h2>
            <a href="#skills" class="btn btn-secondary btn-sm">View All Skills</a>
        </div>
        ${skills.length === 0
            ? '<p style="color:#8a8480; font-family:Arial,sans-serif; font-size:14px;">No skills yet.</p>'
            : `<div class="skills-grid">
                ${skills.slice(0, 6).map(us => miniSkillCard(us)).join('')}
            </div>`
        }
    </div>`;
}

function miniSkillCard(us) {
    return `
    <div class="skill-card ${us.status}">
        <div class="skill-card-header">
            <span class="skill-status-badge status-${us.status}">${us.status}</span>
        </div>
        <div class="skill-name">${us.skill_name || 'Skill #' + us.skill_id}</div>
        ${us.status === 'assigned'
            ? `<button class="btn btn-secondary btn-sm" onclick="navigate('skills')">Do Assignment</button>`
            : ''
        }
    </div>`;
}

// ===== Skills Page =====
let allSkills = [];
let activeCategory = 'All';
let activeAssignmentSkillId = null;
let activeSkillQuestions = [];
let activeQuestionIndex = 0;

async function renderSkillsPage() {
    const res = await apiFetch('/skills/');
    allSkills = res.ok ? res.data.skills : [];

    const categories = ['All', ...new Set(allSkills.map(s => s.category))];

    return `
    <div class="page-wrapper">
        <h1 class="page-title">Skill Tree</h1>
        <p class="page-subtitle">Assign skills, complete assignments, and unlock new abilities</p>
        <div class="filter-row" id="cat-filters">
            ${categories.map(c =>
                `<button class="filter-btn ${c === activeCategory ? 'active' : ''}"
                    onclick="filterCategory('${c}')">${c}</button>`
            ).join('')}
        </div>
        <div class="skills-grid" id="skills-grid">
            ${renderSkillCards()}
        </div>
        <div id="assignment-area"></div>
    </div>`;
}

function renderSkillCards() {
    const filtered = activeCategory === 'All'
        ? allSkills
        : allSkills.filter(s => s.category === activeCategory);

    return filtered.map(skill => {
        const status = skill.user_status || 'locked';
        return `
        <div class="skill-card ${status}" id="skill-card-${skill.id}">
            <div class="skill-card-header">
                <span class="skill-category ${skill.category}">${skill.category}</span>
                <span class="skill-status-badge status-${status}">${status}</span>
            </div>
            <div class="skill-name">${skill.name}</div>
            <div class="skill-desc">${skill.description}</div>
            <div class="skill-meta">
                <span>Level ${skill.level}</span>
                <span class="skill-xp">+${skill.xp_reward} XP</span>
                ${skill.attempts > 0 ? `<span>${skill.attempts} attempt${skill.attempts > 1 ? 's' : ''}</span>` : ''}
            </div>
            <div class="skill-actions">
                ${status === 'locked'
                    ? `<button class="btn btn-secondary btn-sm" onclick="assignSkill(${skill.id})">Assign</button>`
                    : ''
                }
                ${status === 'assigned'
                    ? `<button class="btn btn-primary btn-sm" onclick="openAssignment(${skill.id})">Do Assignment</button>`
                    : ''
                }
                ${status === 'completed'
                    ? `<span style="color:#2e7d32; font-size:13px; font-family:Arial,sans-serif;">✓ Completed</span>`
                    : ''
                }
            </div>
        </div>`;
    }).join('');
}

function filterCategory(cat) {
    activeCategory = cat;
    document.getElementById('cat-filters').innerHTML =
        ['All', ...new Set(allSkills.map(s => s.category))].map(c =>
            `<button class="filter-btn ${c === activeCategory ? 'active' : ''}"
                onclick="filterCategory('${c}')">${c}</button>`
        ).join('');
    document.getElementById('skills-grid').innerHTML = renderSkillCards();
    document.getElementById('assignment-area').innerHTML = '';
}

async function assignSkill(skillId) {
    const res = await apiFetch('/skills/assign', 'POST', { skill_id: skillId });
    if (res.ok) {
        showToast('Skill assigned! Complete the assignment to earn XP.', 'success');
        await refreshSkills();
    } else {
        showToast(res.data.error || 'Could not assign skill', 'error');
    }
}

async function refreshSkills() {
    const res = await apiFetch('/skills/');
    if (res.ok) {
        allSkills = res.data.skills;
        document.getElementById('skills-grid').innerHTML = renderSkillCards();
        loadXP();
    }
}

function openAssignment(skillId) {
    const skill = allSkills.find(s => s.id === skillId);
    if (!skill) return;
    activeAssignmentSkillId = skillId;

    // parse question bank if present
    activeSkillQuestions = [];
    activeQuestionIndex = 0;
    try {
        const parsed = JSON.parse(skill.assignment_question);
        if (Array.isArray(parsed) && parsed.length > 0) {
            activeSkillQuestions = parsed;
        } else {
            activeSkillQuestions = [{ type: 'short', question: skill.assignment_question, answer: skill.assignment_answer }];
        }
    } catch (e) {
        activeSkillQuestions = [{ type: 'short', question: skill.assignment_question, answer: skill.assignment_answer }];
    }

    renderQuestionPanel(skill);
    document.getElementById('assignment-area').scrollIntoView({ behavior: 'smooth' });
}

function renderQuestionPanel(skill) {
    const q = activeSkillQuestions[activeQuestionIndex];
    const qHtml = q.type === 'mcq'
        ? `<div class="mcq-choices">${q.choices.map((c, i) => `<label style="display:block;margin:6px 0;"><input type="radio" name="mcq-${skill.id}" value="${c}"> ${c}</label>`).join('')}</div>`
        : (q.type === 'coding'
            ? `<textarea id="ans-input-${skill.id}" class="assignment-input" placeholder="Write your code here..." style="min-height:120px;width:100%;padding:8px;border:1px solid #ddd;border-radius:4px;"></textarea>`
            : `<input type="text" class="assignment-input" id="ans-input-${skill.id}" placeholder="Type your answer here...">`);

    const progressHtml = typeof skill.correct_count !== 'undefined'
        ? `<div style="font-size:13px;margin-bottom:8px;color:#2e7d32;">Progress: ${skill.correct_count}/${skill.required_correct} correct answers</div>`
        : '';
    document.getElementById('assignment-area').innerHTML = `
    <div class="assignment-panel" id="assignment-panel-${skill.id}">
        <h3>Assignment: ${skill.name}</h3>
        <div style="font-size:14px;margin-bottom:8px;">Question ${activeQuestionIndex + 1} of ${activeSkillQuestions.length}</div>
        ${progressHtml}
        <div class="assignment-question" id="assignment-question-${skill.id}">${q.question}</div>
        ${qHtml}
        <div id="ans-msg-${skill.id}"></div>
        <div style="display:flex; gap:10px; margin-top:8px;">
            <button class="btn btn-primary btn-sm" onclick="submitAssignment(${skill.id})">Submit Answer</button>
            <button class="btn btn-secondary btn-sm" onclick="closeAssignment()">Cancel</button>
            <button class="btn btn-secondary btn-sm" onclick="prevQuestion(${skill.id})">Prev</button>
            <button class="btn btn-secondary btn-sm" onclick="nextQuestion(${skill.id})">Next</button>
        </div>
    </div>`;
    const inputEl = document.getElementById('ans-input-' + skill.id);
    if (inputEl) inputEl.focus();
}

function prevQuestion(skillId) {
    if (activeQuestionIndex > 0) {
        activeQuestionIndex -= 1;
        const skill = allSkills.find(s => s.id === skillId);
        renderQuestionPanel(skill);
    }
}

function nextQuestion(skillId) {
    if (activeQuestionIndex < activeSkillQuestions.length - 1) {
        activeQuestionIndex += 1;
        const skill = allSkills.find(s => s.id === skillId);
        renderQuestionPanel(skill);
    }
}

function closeAssignment() {
    document.getElementById('assignment-area').innerHTML = '';
    activeAssignmentSkillId = null;
}

async function submitAssignment(skillId) {
    const q = activeSkillQuestions[activeQuestionIndex] || null;
    let answer = '';
    const msgEl = document.getElementById('ans-msg-' + skillId);
    if (q && q.type === 'mcq') {
        const radios = document.getElementsByName('mcq-' + skillId);
        for (let r of radios) if (r.checked) answer = r.value;
    } else {
        const input = document.getElementById('ans-input-' + skillId);
        answer = input ? input.value.trim() : '';
    }

    if (!answer) {
        msgEl.innerHTML = '<div class="msg-error">Please type or select an answer.</div>';
        return;
    }

    const res = await apiFetch('/skills/submit', 'POST', { skill_id: skillId, answer, question_index: activeQuestionIndex });

    if (res.ok) {
        let html = `<div class="msg-success">${res.data.message}</div>`;
        if (res.data.xp_earned) html += `<div class="msg-success">+${res.data.xp_earned} XP earned!</div>`;
        if (res.data.skills_unlocked && res.data.skills_unlocked.length > 0) {
            html += `<div class="msg-success">Unlocked: ${res.data.skills_unlocked.join(', ')}</div>`;
        }
        if (res.data.badges_earned && res.data.badges_earned.length > 0) {
            res.data.badges_earned.forEach(b => {
                showToast(`Badge earned: ${b.icon} ${b.name}!`, 'success', 4000);
            });
        }
        if (res.data.progress) {
            html += `<div class="msg-success">Progress: ${res.data.progress.correct_count}/${res.data.progress.required_correct}</div>`;
        }
        msgEl.innerHTML = html;
        await refreshSkills();
        if (res.data.xp_earned) {
            setTimeout(() => closeAssignment(), 2000);
        }
    } else {
        let html = `<div class="msg-error">${res.data.message || 'Wrong answer, try again!'}</div>`;
        if (res.data.progress) {
            html += `<div class="msg-error">Progress: ${res.data.progress.correct_count}/${res.data.progress.required_correct}</div>`;
        }
        msgEl.innerHTML = html;
    }
}

// ===== Badges Page =====
async function renderBadgesPage() {
    const res = await apiFetch('/badges/');
    const badges = res.ok ? res.data.badges : [];

    const earned = badges.filter(b => b.earned);
    const notEarned = badges.filter(b => !b.earned);

    return `
    <div class="page-wrapper">
        <h1 class="page-title">Badges</h1>
        <p class="page-subtitle">Earn badges by completing skills. You have ${earned.length} of ${badges.length} badges.</p>

        <div class="tabs">
            <button class="tab-btn active" id="tab-all" onclick="switchTab('all')">All Badges</button>
            <button class="tab-btn" id="tab-earned" onclick="switchTab('earned')">Earned (${earned.length})</button>
        </div>

        <div id="badge-content">
            <div class="badges-grid">
                ${badges.map(b => badgeCard(b)).join('')}
            </div>
        </div>
    </div>`;
}

function badgeCard(b) {
    return `
    <div class="badge-card ${b.earned ? '' : 'not-earned'}">
        <div class="badge-icon">${b.icon || '⭐'}</div>
        <div class="badge-name">${b.name}</div>
        <div class="badge-desc">${b.description}</div>
        ${b.earned ? `<div class="badge-earned-date">Earned ${new Date(b.earned_at).toLocaleDateString()}</div>` : '<div style="font-size:11px;color:#aaa;margin-top:6px;font-family:Arial,sans-serif;">Not yet earned</div>'}
    </div>`;
}

function switchTab(tab) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.getElementById('tab-' + tab).classList.add('active');
}

// ===== Home/Landing =====
function renderHome() {
    return `
    <div style="min-height: 100vh; background: #f5f0e8;">
        <div style="max-width:700px; margin:0 auto; padding: 80px 24px; text-align:center;">
            <div style="font-size:56px; margin-bottom:16px;"></div>
            <h1 style="font-size:38px; color:#2c2c2c; margin-bottom:14px;">SkillTree Platform</h1>
            <p style="font-size:16px; color:#5a5550; font-family:Arial,sans-serif; margin-bottom:36px; line-height:1.7;">
                Learn programming skills step by step. Complete assignments, earn XP, and collect badges as you grow your knowledge tree.
            </p>
            <div style="display:flex; gap:16px; justify-content:center; flex-wrap:wrap;">
                <a href="#signup" class="btn btn-primary" style="width:auto; padding:12px 32px; font-size:16px;">Get Started</a>
                <a href="#login" class="btn btn-secondary" style="padding:12px 32px; font-size:16px;">Login</a>
            </div>
            <div style="margin-top:60px; display:flex; gap:24px; justify-content:center; flex-wrap:wrap;">
                <div style="background:#fff; border:1px solid #d5cfc4; border-radius:8px; padding:20px 24px; min-width:160px;">
                    <div style="font-size:28px;">📚</div>
                    <div style="font-size:14px; color:#5a5550; font-family:Arial,sans-serif; margin-top:6px;">10 Skills to Master</div>
                </div>
                <div style="background:#fff; border:1px solid #d5cfc4; border-radius:8px; padding:20px 24px; min-width:160px;">
                    <div style="font-size:28px;">🏆</div>
                    <div style="font-size:14px; color:#5a5550; font-family:Arial,sans-serif; margin-top:6px;">10 Badges to Earn</div>
                </div>
                <div style="background:#fff; border:1px solid #d5cfc4; border-radius:8px; padding:20px 24px; min-width:160px;">
                    <div style="font-size:28px;">⚡</div>
                    <div style="font-size:14px; color:#5a5550; font-family:Arial,sans-serif; margin-top:6px;">Earn XP & Level Up</div>
                </div>
            </div>
        </div>
    </div>`;
}

// ===== Main App Router =====
async function renderApp() {
    renderNavbar();
    highlightNav();

    const page = getPage();
    const token = getToken();
    const main = document.getElementById('main-content');
    main.innerHTML = '<div style="padding:60px;text-align:center;color:#8a8480;font-family:Arial,sans-serif;">Loading...</div>';

    // Auth guard
    const protectedPages = ['dashboard', 'skills', 'badges'];
    if (protectedPages.includes(page) && !token) {
        navigate('login');
        main.innerHTML = renderLogin();
        return;
    }
    if ((page === 'login' || page === 'signup') && token) {
        navigate('dashboard');
        main.innerHTML = await renderDashboard();
        return;
    }

    switch (page) {
        case 'signup':
            main.innerHTML = renderSignup();
            break;
        case 'login':
            main.innerHTML = renderLogin();
            break;
        case 'dashboard':
            main.innerHTML = await renderDashboard();
            break;
        case 'skills':
            main.innerHTML = await renderSkillsPage();
            break;
        case 'badges':
            main.innerHTML = await renderBadgesPage();
            break;
        default:
            main.innerHTML = renderHome();
    }
}

// ===== Bootstrap =====
window.addEventListener('hashchange', renderApp);
window.addEventListener('DOMContentLoaded', renderApp);
