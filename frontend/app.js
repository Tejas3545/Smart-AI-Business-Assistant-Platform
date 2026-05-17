const state = {
  apiBase: "https://smart-ai-business-assistant-platform.onrender.com",
  token: localStorage.getItem("token") || null,
  conversationId: null,
};

const elements = {
  authApp: document.getElementById("auth-app"),
  dashboardApp: document.getElementById("dashboard-app"),
  authTabs: document.querySelectorAll(".auth-tab"),
  authForms: document.querySelectorAll(".auth-form"),
  
  refreshDashboard: document.getElementById("refresh-dashboard"),
  signupName: document.getElementById("signup-name"),
  signupEmail: document.getElementById("signup-email"),
  signupPassword: document.getElementById("signup-password"),
  signupBtn: document.getElementById("signup-btn"),
  loginEmail: document.getElementById("login-email"),
  loginPassword: document.getElementById("login-password"),
  loginBtn: document.getElementById("login-btn"),
  authStatus: document.getElementById("auth-status"),
  logoutBtn: document.getElementById("logout-btn"),
  
  docFile: document.getElementById("doc-file"),
  uploadDoc: document.getElementById("upload-doc"),
  docStatus: document.getElementById("doc-status"),
  chatLog: document.getElementById("chat-log"),
  chatInput: document.getElementById("chat-input"),
  sendChat: document.getElementById("send-chat"),
  
  leadName: document.getElementById("lead-name"),
  leadEmail: document.getElementById("lead-email"),
  leadPhone: document.getElementById("lead-phone"),
  leadCompany: document.getElementById("lead-company"),
  leadInterest: document.getElementById("lead-interest"),
  createLead: document.getElementById("create-lead"),
  leadStatus: document.getElementById("lead-status"),
  leadList: document.getElementById("lead-list"),
  
  workflowType: document.getElementById("workflow-type"),
  workflowPayload: document.getElementById("workflow-payload"),
  runWorkflow: document.getElementById("run-workflow"),
  workflowStatus: document.getElementById("workflow-status"),
  workflowList: document.getElementById("workflow-list"),
  
  conversationList: document.getElementById("conversation-list"),
  auditList: document.getElementById("audit-list"),
  docList: document.getElementById("doc-list"),
  docListInline: document.getElementById("doc-list-inline"),
  
  kpiConversations: document.getElementById("kpi-conversations"),
  kpiMessages: document.getElementById("kpi-messages"),
  kpiLeads: document.getElementById("kpi-leads"),
  kpiHot: document.getElementById("kpi-hot"),
  kpiWorkflows: document.getElementById("kpi-workflows"),
  kpiDocs: document.getElementById("kpi-docs"),
  kpiAiTokens: document.getElementById("kpi-ai-tokens"),
  
  viewTitle: document.getElementById("view-title"),
  viewSubtitle: document.getElementById("view-subtitle"),
  navButtons: document.querySelectorAll(".nav-btn"),
  views: document.querySelectorAll(".view"),
};

const viewMeta = {
  overview: {
    title: "Overview",
    subtitle: "Live system pulse and business activity.",
  },
  assistant: {
    title: "Assistant",
    subtitle: "Grounded answers with document intelligence.",
  },
  leads: {
    title: "Leads",
    subtitle: "Capture, score, and follow up with prospects.",
  },
  automations: {
    title: "Automations",
    subtitle: "Trigger repeatable workflows in one click.",
  },
};

const headers = () => ({
  "Content-Type": "application/json",
  ...(state.token ? { Authorization: `Bearer ${state.token}` } : {}),
});

const updateAuthStatus = async () => {
  if (state.token) {
    elements.authApp.classList.remove("active");
    elements.dashboardApp.classList.add("active");
    await fetchUserProfile();
    refreshDashboard();
  } else {
    elements.authApp.classList.add("active");
    elements.dashboardApp.classList.remove("active");
  }
};

const fetchUserProfile = async () => {
  const response = await fetch(`${state.apiBase}/api/auth/me`, {
    headers: headers(),
  });
  if (response.ok) {
    const user = await response.json();
    const userNameEl = document.querySelector(".user-name");
    if (userNameEl) {
      userNameEl.textContent = user.full_name || user.email;
    }
  } else {
    logout();
  }
};

const showMessage = (element, message, isError = false) => {
  element.textContent = message;
  element.className = `status-msg ${isError ? "error" : "success"}`;
  setTimeout(() => {
    element.textContent = "";
    element.className = "status-msg";
  }, 4000);
};

const readErrorMessage = async (response) => {
  try {
    const payload = await response.json();
    if (payload.detail) {
      if (Array.isArray(payload.detail)) {
        return payload.detail.map((item) => item.msg).join(" ");
      }
      return payload.detail;
    }
  } catch (error) {
    return "";
  }
  return "";
};

const addChatBubble = (role, content) => {
  const bubble = document.createElement("div");
  bubble.className = `bubble ${role}`;
  bubble.textContent = content;
  elements.chatLog.appendChild(bubble);
  elements.chatLog.scrollTop = elements.chatLog.scrollHeight;
};

// --- DATA FETCHING ---

const fetchSummary = async () => {
  const response = await fetch(`${state.apiBase}/api/analytics/summary`, {
    headers: headers(),
  });
  if (!response.ok) {
    if (response.status === 401) logout();
    return;
  }
  const data = await response.json();
  elements.kpiConversations.textContent = data.total_conversations;
  elements.kpiMessages.textContent = data.total_messages;
  elements.kpiLeads.textContent = data.total_leads;
  elements.kpiHot.textContent = data.hot_leads;
  elements.kpiWorkflows.textContent = data.workflow_runs;
  elements.kpiDocs.textContent = data.documents_uploaded;
  if (elements.kpiAiTokens) {
    elements.kpiAiTokens.textContent = data.total_ai_tokens || 0;
  }
};

const fetchAuditLogs = async () => {
  const response = await fetch(`${state.apiBase}/api/analytics/audit`, {
    headers: headers(),
  });
  if (!response.ok) return;
  const data = await response.json();
  if (!data.length) {
    elements.auditList.innerHTML = `<div class="item empty-state">No activity yet.</div>`;
    return;
  }
  elements.auditList.innerHTML = data
    .slice(0, 8)
    .map(
      (log) =>
        `<div class="item activity-item">
           <div class="activity-content">
             <strong>${log.event_type}</strong>
             <span class="muted">${log.detail || ""}</span>
           </div>
         </div>`
    )
    .join("");
};

const renderDocuments = (documents) => {
  const html = documents
    .map(
      (doc) =>
        `<div class="item item-row">
           <div class="doc-info">
             <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
             <span>${doc.filename}</span>
           </div>
           <button class="icon-btn text-danger" data-doc-id="${doc.id}" title="Delete Document">
             <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
           </button>
         </div>`
    )
    .join("");
  elements.docList.innerHTML = html || `<div class="item empty-state">No documents uploaded.</div>`;
  elements.docListInline.innerHTML = html || `<div class="item empty-state">No documents uploaded.</div>`;

  document.querySelectorAll("button[data-doc-id]").forEach((button) => {
    button.addEventListener("click", async () => {
      await deleteDocument(button.dataset.docId);
    });
  });
};

const fetchDocuments = async () => {
  const response = await fetch(`${state.apiBase}/api/docs/`, { headers: headers() });
  if (!response.ok) return;
  const data = await response.json();
  renderDocuments(data);
};

const deleteDocument = async (documentId) => {
  const response = await fetch(`${state.apiBase}/api/docs/${documentId}`, {
    method: "DELETE",
    headers: headers(),
  });
  if (response.ok) {
    showMessage(elements.docStatus, "Document deleted.");
    refreshDashboard();
  } else {
    showMessage(elements.docStatus, "Delete failed.", true);
  }
};

const fetchLeads = async () => {
  const response = await fetch(`${state.apiBase}/api/leads/`, { headers: headers() });
  if (!response.ok) return;
  const data = await response.json();
  elements.leadList.innerHTML = data
    .map((lead) => {
      const badgeClass = lead.status === 'hot' ? 'success' : (lead.status === 'warm' ? 'warning' : 'neutral');
      return `<div class="item item-row lead-item">
        <div class="lead-info">
          <strong>${lead.name}</strong>
          <span class="muted">${lead.company || lead.email || "No company"}</span>
        </div>
        <div class="lead-meta">
          <span class="score">Score: ${lead.score}</span>
          <span class="badge ${badgeClass}">${lead.status}</span>
        </div>
      </div>`;
    })
    .join("");
};

const fetchWorkflows = async () => {
  const response = await fetch(`${state.apiBase}/api/workflows/`, { headers: headers() });
  if (!response.ok) return;
  const data = await response.json();
  elements.workflowList.innerHTML = data
    .map(
      (run) =>
        `<div class="item workflow-item">
           <strong>${run.workflow_type.replace('_', ' ').toUpperCase()}</strong>
           <span class="muted">${run.status} · ${run.output_summary || ""}</span>
         </div>`
    )
    .join("");
};

const fetchConversations = async () => {
  const response = await fetch(`${state.apiBase}/api/chat/conversations`, { headers: headers() });
  if (!response.ok) return;
  const conversations = await response.json();
  if (!conversations.length) {
    elements.conversationList.innerHTML = `<div class="item empty-state">No conversations yet.</div>`;
    return;
  }
  const latest = conversations[conversations.length - 1];
  const messagesResponse = await fetch(
    `${state.apiBase}/api/chat/${latest.id}/messages`,
    { headers: headers() }
  );
  if (!messagesResponse.ok) return;
  const messages = await messagesResponse.json();
  elements.conversationList.innerHTML = messages
    .slice(-6)
    .map(
      (msg) =>
        `<div class="item message-preview ${msg.role}">
           <strong class="capitalize">${msg.role}</strong>
           <span class="truncate">${msg.content}</span>
         </div>`
    )
    .join("");
};

const refreshDashboard = async () => {
  if (!state.token) return;
  await Promise.all([
    fetchSummary(),
    fetchLeads(),
    fetchWorkflows(),
    fetchConversations(),
    fetchAuditLogs(),
    fetchDocuments(),
  ]);
};

// --- AUTH ACTIONS ---

const signup = async () => {
  if (!elements.signupName.value || !elements.signupEmail.value || !elements.signupPassword.value) {
    showMessage(elements.authStatus, "Please complete all fields.", true);
    return;
  }
  elements.signupBtn.textContent = "Creating Account...";
  const payload = {
    full_name: elements.signupName.value,
    email: elements.signupEmail.value,
    password: elements.signupPassword.value,
  };
  const response = await fetch(`${state.apiBase}/api/auth/signup`, {
    method: "POST",
    headers: headers(),
    body: JSON.stringify(payload),
  });
  elements.signupBtn.textContent = "Create Account";
  
  if (response.ok) {
    showMessage(elements.authStatus, "Account created successfully. Please login.");
    // Auto switch to login tab
    document.querySelector('.auth-tab[data-tab="login"]').click();
  } else {
    const detail = await readErrorMessage(response);
    showMessage(elements.authStatus, detail || "Signup failed.", true);
  }
};

const login = async () => {
  if (!elements.loginEmail.value || !elements.loginPassword.value) {
    showMessage(elements.authStatus, "Please enter email and password.", true);
    return;
  }
  elements.loginBtn.textContent = "Signing In...";
  const payload = {
    email: elements.loginEmail.value,
    password: elements.loginPassword.value,
  };
  const response = await fetch(`${state.apiBase}/api/auth/login`, {
    method: "POST",
    headers: headers(),
    body: JSON.stringify(payload),
  });
  elements.loginBtn.textContent = "Sign In";
  
  if (!response.ok) {
    const detail = await readErrorMessage(response);
    showMessage(elements.authStatus, detail || "Login failed.", true);
    return;
  }
  const data = await response.json();
  state.token = data.access_token;
  localStorage.setItem("token", state.token);
  updateAuthStatus();
};

const logout = () => {
  state.token = null;
  localStorage.removeItem("token");
  updateAuthStatus();
};

// --- CORE ACTIONS ---

const uploadDocument = async () => {
  if (!elements.docFile.files.length) return;
  const formData = new FormData();
  formData.append("file", elements.docFile.files[0]);
  elements.uploadDoc.textContent = "Uploading...";
  const response = await fetch(`${state.apiBase}/api/docs/upload`, {
    method: "POST",
    headers: state.token ? { Authorization: `Bearer ${state.token}` } : {},
    body: formData,
  });
  elements.uploadDoc.textContent = "Browse Files";
  
  if (response.ok) {
    elements.docFile.value = "";
    showMessage(elements.docStatus, "Document uploaded and indexed successfully.");
    refreshDashboard();
  } else {
    showMessage(elements.docStatus, "Upload failed.", true);
  }
};

const sendChat = async () => {
  const message = elements.chatInput.value.trim();
  if (!message) return;
  addChatBubble("user", message);
  elements.chatInput.value = "";

  const response = await fetch(`${state.apiBase}/api/chat/`, {
    method: "POST",
    headers: headers(),
    body: JSON.stringify({ message, conversation_id: state.conversationId }),
  });
  if (!response.ok) {
    addChatBubble("assistant", "Unable to respond right now.");
    return;
  }
  const data = await response.json();
  state.conversationId = data.conversation_id;
  addChatBubble("assistant", data.assistant_message);
  if (data.lead_hint) {
    showMessage(elements.leadStatus, data.lead_hint);
  }
  refreshDashboard();
};

const createLead = async () => {
  const payload = {
    name: elements.leadName.value,
    email: elements.leadEmail.value || null,
    phone: elements.leadPhone.value || null,
    company: elements.leadCompany.value || null,
    interest: elements.leadInterest.value || null,
  };
  
  if (!payload.name) {
    showMessage(elements.leadStatus, "Lead Name is required.", true);
    return;
  }

  elements.createLead.textContent = "Scoring...";
  const response = await fetch(`${state.apiBase}/api/leads/`, {
    method: "POST",
    headers: headers(),
    body: JSON.stringify(payload),
  });
  elements.createLead.textContent = "Save & Score Lead";
  
  if (response.ok) {
    showMessage(elements.leadStatus, "Lead scored and saved to pipeline.");
    elements.leadName.value = "";
    elements.leadEmail.value = "";
    elements.leadPhone.value = "";
    elements.leadCompany.value = "";
    elements.leadInterest.value = "";
    refreshDashboard();
  } else {
    showMessage(elements.leadStatus, "Failed to save lead.", true);
  }
};

const runWorkflow = async () => {
  let payload = {};
  try {
    payload = JSON.parse(elements.workflowPayload.value || "{}");
  } catch (error) {
    showMessage(elements.workflowStatus, "Invalid JSON payload.", true);
    return;
  }
  elements.runWorkflow.textContent = "Executing...";
  const response = await fetch(`${state.apiBase}/api/workflows/run`, {
    method: "POST",
    headers: headers(),
    body: JSON.stringify({ workflow_type: elements.workflowType.value, payload }),
  });
  elements.runWorkflow.textContent = "Execute Workflow";
  
  if (response.ok) {
    showMessage(elements.workflowStatus, "Workflow executed successfully.");
    refreshDashboard();
  } else {
    showMessage(elements.workflowStatus, "Workflow execution failed.", true);
  }
};

const showView = (viewName) => {
  elements.views.forEach((view) => {
    view.classList.toggle("active", view.dataset.view === viewName);
  });
  elements.navButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.nav === viewName);
  });
  const meta = viewMeta[viewName];
  if (meta) {
    elements.viewTitle.textContent = meta.title;
    elements.viewSubtitle.textContent = meta.subtitle;
  }
};

const init = () => {
  // Auth Form Tabs Logic
  elements.authTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      elements.authTabs.forEach(t => t.classList.remove('active'));
      elements.authForms.forEach(f => f.classList.remove('active'));
      tab.classList.add('active');
      document.getElementById(`${tab.dataset.tab}-form`).classList.add('active');
    });
  });

  updateAuthStatus();
  
  // Event Listeners
  elements.refreshDashboard.addEventListener("click", refreshDashboard);
  elements.signupBtn.addEventListener("click", signup);
  elements.loginBtn.addEventListener("click", login);
  elements.logoutBtn.addEventListener("click", logout);
  elements.uploadDoc.addEventListener("click", () => {
    // If hidden file input is implemented, click it, else just trigger upload
    if(elements.docFile.files.length === 0) {
      elements.docFile.click();
    } else {
      uploadDocument();
    }
  });
  
  elements.docFile.addEventListener("change", uploadDocument);
  
  elements.sendChat.addEventListener("click", sendChat);
  elements.chatInput.addEventListener("keypress", (e) => {
    if (e.key === 'Enter') sendChat();
  });
  
  elements.createLead.addEventListener("click", createLead);
  elements.runWorkflow.addEventListener("click", runWorkflow);
  
  elements.navButtons.forEach((button) => {
    button.addEventListener("click", () => {
      showView(button.dataset.nav);
    });
  });
};

init();
