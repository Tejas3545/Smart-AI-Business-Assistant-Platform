const state = {
  apiBase: "https://smart-ai-business-assistant-platform.onrender.com",
  token: localStorage.getItem("token") || null,
  conversationId: null,
  conversationsCache: [],
  conversationsFetchedAt: 0,
  userRole: null,
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
  newChat: document.getElementById("new-chat"),
  deleteChat: document.getElementById("delete-chat"),
  deleteAllChats: document.getElementById("delete-all-chats"),
  chatHistory: document.getElementById("chat-history"),
  
  leadName: document.getElementById("lead-name"),
  leadEmail: document.getElementById("lead-email"),
  leadPhone: document.getElementById("lead-phone"),
  leadCompany: document.getElementById("lead-company"),
  leadInterest: document.getElementById("lead-interest"),
  createLead: document.getElementById("create-lead"),
  leadStatus: document.getElementById("lead-status"),
  leadList: document.getElementById("lead-list"),
  
  newWfName: document.getElementById("new-workflow-name"),
  newWfTrigger: document.getElementById("new-workflow-trigger"),
  newWfNodes: document.getElementById("new-workflow-nodes"),
  createWfBtn: document.getElementById("create-workflow"),
  createWfStatus: document.getElementById("create-workflow-status"),

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
  kpiConversion: document.getElementById("kpi-conversion"),
  kpiWorkflows: document.getElementById("kpi-workflows"),
  kpiResponse: document.getElementById("kpi-response"),
  kpiDocs: document.getElementById("kpi-docs"),
  kpiAiTokens: document.getElementById("kpi-ai-tokens"),

  adminUsers: document.getElementById("admin-users"),
  adminWorkspaces: document.getElementById("admin-workspaces"),
  adminAutomationLogs: document.getElementById("admin-automation-logs"),
  adminAuditLogs: document.getElementById("admin-audit-logs"),
  adminIntegrations: document.getElementById("admin-integrations"),
  adminNavButton: document.querySelector('[data-nav="admin"]'),
  
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
  admin: {
    title: "Admin",
    subtitle: "Client settings, workflows, and operational visibility.",
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
    state.userRole = user.role || null;
    const userNameEl = document.querySelector(".user-name");
    if (userNameEl) {
      userNameEl.textContent = user.full_name || user.email;
    }
    if (elements.adminNavButton) {
      elements.adminNavButton.style.display = state.userRole === "admin" ? "" : "none";
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

const formatAssistantMessage = (message) => {
  if (!message) return "I couldn't generate a response.";
  const withoutMemory = message.split("\n\nSaved memory:")[0];
  return withoutMemory.replace(/\n{3,}/g, "\n\n").trim();
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
  if (elements.kpiConversion) {
    elements.kpiConversion.textContent = `${data.conversion_rate || 0}%`;
  }
  elements.kpiWorkflows.textContent = data.workflow_runs;
  if (elements.kpiResponse) {
    elements.kpiResponse.textContent = data.avg_response_seconds || 0;
  }
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

const fetchAdminData = async () => {
  if (state.userRole !== "admin") return;
  const [usersRes, workspacesRes, logsRes, auditRes, integrationsRes] = await Promise.all([
    fetch(`${state.apiBase}/api/admin/users`, { headers: headers() }),
    fetch(`${state.apiBase}/api/admin/workspaces`, { headers: headers() }),
    fetch(`${state.apiBase}/api/admin/automation-logs`, { headers: headers() }),
    fetch(`${state.apiBase}/api/admin/audit-logs`, { headers: headers() }),
    fetch(`${state.apiBase}/api/admin/integrations`, { headers: headers() }),
  ]);
  if ([usersRes, workspacesRes, logsRes, auditRes, integrationsRes].some((res) => res.status === 401)) {
    logout();
    return;
  }
  if (usersRes.ok) {
    const users = await usersRes.json();
    elements.adminUsers.innerHTML = users.length
      ? users
          .map(
            (user) => `<div class="item item-row">
              <div class="lead-info">
                <strong>${user.full_name || user.email}</strong>
                <span class="muted">${user.email}</span>
              </div>
              <span class="badge neutral">${user.role}</span>
            </div>`
          )
          .join("")
      : `<div class="item empty-state">No users found.</div>`;
  }
  if (workspacesRes.ok) {
    const workspaces = await workspacesRes.json();
    elements.adminWorkspaces.innerHTML = workspaces.length
      ? workspaces
          .map(
            (workspace) => `<div class="item item-row">
              <div class="lead-info">
                <strong>${workspace.name}</strong>
                <span class="muted">Workspace ID: ${workspace.id}</span>
              </div>
              <span class="badge ${workspace.is_active ? "success" : "neutral"}">${workspace.is_active ? "Active" : "Paused"}</span>
            </div>`
          )
          .join("")
      : `<div class="item empty-state">No workspaces found.</div>`;
  }
  if (logsRes.ok) {
    const logs = await logsRes.json();
    elements.adminAutomationLogs.innerHTML = logs.length
      ? logs
          .map(
            (log) => `<div class="item">
              <strong>${log.status}</strong>
              <span class="muted">Workflow ID: ${log.workflow_id || "n/a"} · Retries: ${log.retry_count}</span>
            </div>`
          )
          .join("")
      : `<div class="item empty-state">No automation logs.</div>`;
  }
  if (auditRes.ok) {
    const audits = await auditRes.json();
    elements.adminAuditLogs.innerHTML = audits.length
      ? audits
          .slice(0, 20)
          .map(
            (log) => `<div class="item">
              <strong>${log.event_type}</strong>
              <span class="muted">${log.detail || ""}</span>
            </div>`
          )
          .join("")
      : `<div class="item empty-state">No audit activity yet.</div>`;
  }
  if (integrationsRes.ok) {
    const integrations = await integrationsRes.json();
    elements.adminIntegrations.innerHTML = integrations.length
      ? integrations
          .map(
            (integration) => `<div class="item item-row">
              <div class="lead-info">
                <strong>${integration.provider}</strong>
                <span class="muted">Workspace ID: ${integration.workspace_id}</span>
              </div>
              <span class="badge ${integration.status === "active" ? "success" : "neutral"}">${integration.status}</span>
            </div>`
          )
          .join("")
      : `<div class="item empty-state">No integrations configured.</div>`;
  }
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
  elements.workflowList.innerHTML = data.length ? data
    .map(
      (run) =>
        `<div class="item workflow-item">
           <strong>${run.workflow_type.replace('_', ' ').toUpperCase()}</strong>
           <span class="muted">${run.status} · ${run.output_summary || ""}</span>
         </div>`
    )
    .join("") : `<div class="item empty-state">No workflows executed yet.</div>`;
};

const createWorkflowDef = async () => {
  if (!elements.newWfName.value || !elements.newWfNodes.value) {
    showMessage(elements.createWfStatus, "Please complete fields.", true);
    return;
  }
  let parsedNodes = [];
  try {
    parsedNodes = JSON.parse(elements.newWfNodes.value);
  } catch (e) {
    showMessage(elements.createWfStatus, "Invalid JSON in logic nodes.", true);
    return;
  }

  const payload = {
    name: elements.newWfName.value,
    trigger_type: elements.newWfTrigger.value,
    nodes: parsedNodes
  };

  elements.createWfBtn.textContent = "Saving...";
  const res = await fetch(`${state.apiBase}/api/workflows/definitions`, {
    method: "POST",
    headers: headers(),
    body: JSON.stringify(payload)
  });

  elements.createWfBtn.textContent = "Save Workflow";

  if (res.ok) {
    showMessage(elements.createWfStatus, "Workflow Saved!");
    elements.newWfName.value = "";
    elements.newWfNodes.value = "";
  } else {
    const detail = await readErrorMessage(res);
    showMessage(elements.createWfStatus, detail || "Failed to save", true);
  }
};

const fetchConversations = async (force = false) => {
  const now = Date.now();
  if (!force && state.conversationsCache.length && now - state.conversationsFetchedAt < 30000) {
    return state.conversationsCache;
  }
  const response = await fetch(`${state.apiBase}/api/chat/conversations`, { headers: headers() });
  if (!response.ok) return [];
  const conversations = await response.json();
  state.conversationsCache = conversations;
  state.conversationsFetchedAt = now;
  return conversations;
};

const renderChatHistory = (conversations) => {
  if (!conversations.length) {
    elements.chatHistory.innerHTML = `<div class="item empty-state">No chat history.</div>`;
    return;
  }

  elements.chatHistory.innerHTML = conversations
    .map(
      (conversation) => `
      <div class="item history-item ${state.conversationId === conversation.id ? "active" : ""}" data-conversation-id="${conversation.id}">
        <div class="history-item-header">
          <span class="history-title">${conversation.title || `Conversation #${conversation.id}`}</span>
          <button class="icon-btn text-danger" data-delete-conversation-id="${conversation.id}" title="Delete chat">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"></path></svg>
          </button>
        </div>
      </div>`
    )
    .join("");

  document.querySelectorAll("[data-conversation-id]").forEach((item) => {
    item.addEventListener("click", async (event) => {
      if (event.target.closest("[data-delete-conversation-id]")) return;
      const id = Number(item.dataset.conversationId);
      await loadConversation(id);
    });
  });

  document.querySelectorAll("[data-delete-conversation-id]").forEach((button) => {
    button.addEventListener("click", async (event) => {
      event.stopPropagation();
      await deleteConversation(Number(button.dataset.deleteConversationId));
    });
  });
};

const fetchOverviewConversations = async () => {
  const conversations = await fetchConversations();
  if (!conversations.length) {
    elements.conversationList.innerHTML = `<div class="item empty-state">No conversations yet.</div>`;
    renderChatHistory([]);
    return;
  }
  renderChatHistory(conversations);
  const latest = conversations[0];
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

const loadConversation = async (conversationId) => {
  const response = await fetch(`${state.apiBase}/api/chat/${conversationId}/messages`, { headers: headers() });
  if (!response.ok) return;
  const messages = await response.json();
  state.conversationId = conversationId;
  elements.chatLog.innerHTML = "";
  if (!messages.length) {
    addChatBubble("assistant", "This chat is empty. Ask me anything.");
  } else {
    messages.forEach((message) => addChatBubble(message.role, message.content));
  }
  renderChatHistory(state.conversationsCache);
};

const refreshChatHistory = async (force = false) => {
  const conversations = await fetchConversations(force);
  renderChatHistory(conversations);
};

const refreshDashboard = async () => {
  if (!state.token) return;
  await Promise.all([
    fetchSummary(),
    fetchLeads(),
    fetchWorkflows(),
    fetchOverviewConversations(),
    fetchAuditLogs(),
    fetchDocuments(),
  ]);
  await fetchAdminData();
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
  state.userRole = null;
  localStorage.removeItem("token");
  if (elements.adminNavButton) {
    elements.adminNavButton.style.display = "none";
  }
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
    const detail = await readErrorMessage(response);
    showMessage(elements.docStatus, detail || "Upload failed.", true);
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
  addChatBubble("assistant", formatAssistantMessage(data.assistant_message));
  if (data.lead_hint) {
    showMessage(elements.leadStatus, data.lead_hint);
  }
  state.conversationsFetchedAt = 0;
  await refreshChatHistory(true);
  refreshDashboard();
};

const startNewChat = async () => {
  state.conversationId = null;
  elements.chatLog.innerHTML = "";
  addChatBubble("assistant", "New chat started. How can I help you?");
  await refreshChatHistory();
};

const deleteConversation = async (conversationId) => {
  const response = await fetch(`${state.apiBase}/api/chat/conversations/${conversationId}`, {
    method: "DELETE",
    headers: headers(),
  });
  if (!response.ok) return;

  if (state.conversationId === conversationId) {
    state.conversationId = null;
    elements.chatLog.innerHTML = "";
    addChatBubble("assistant", "Chat deleted. Start a new conversation.");
  }
  state.conversationsFetchedAt = 0;
  await refreshChatHistory(true);
  await fetchOverviewConversations();
};

const deleteCurrentChat = async () => {
  if (!state.conversationId) {
    showMessage(elements.leadStatus, "No active chat to delete.", true);
    return;
  }
  await deleteConversation(state.conversationId);
};

const deleteAllChats = async () => {
  const response = await fetch(`${state.apiBase}/api/chat/conversations`, {
    method: "DELETE",
    headers: headers(),
  });
  if (!response.ok) return;
  state.conversationId = null;
  state.conversationsCache = [];
  state.conversationsFetchedAt = 0;
  elements.chatLog.innerHTML = "";
  addChatBubble("assistant", "All chats deleted. Start a new conversation.");
  renderChatHistory([]);
  await fetchOverviewConversations();
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
    const detail = await readErrorMessage(response);
    showMessage(elements.leadStatus, detail || "Failed to save lead.", true);
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
  if (viewName === "admin" && state.userRole !== "admin") {
    showView("overview");
    return;
  }
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
  if (viewName === "assistant") {
    refreshChatHistory();
  }
  if (viewName === "admin") {
    fetchAdminData();
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
  elements.createWfBtn.addEventListener("click", createWorkflowDef);
  elements.newChat.addEventListener("click", startNewChat);
  elements.deleteChat.addEventListener("click", deleteCurrentChat);
  elements.deleteAllChats.addEventListener("click", deleteAllChats);
  
  elements.navButtons.forEach((button) => {
    button.addEventListener("click", () => {
      showView(button.dataset.nav);
    });
  });
};

init();
