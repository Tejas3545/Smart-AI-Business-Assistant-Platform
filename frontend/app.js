const state = {
  apiBase: localStorage.getItem("apiBase") || "https://smart-ai-business-assistant-platform.onrender.com",
  token: localStorage.getItem("token") || null,
  conversationId: null,
};

const elements = {
  apiBase: document.getElementById("api-base"),
  saveApi: document.getElementById("save-api"),
  toggleConfig: document.getElementById("toggle-config"),
  configPanel: document.getElementById("config-panel"),
  refreshDashboard: document.getElementById("refresh-dashboard"),
  signupName: document.getElementById("signup-name"),
  signupEmail: document.getElementById("signup-email"),
  signupPassword: document.getElementById("signup-password"),
  signupBtn: document.getElementById("signup-btn"),
  loginEmail: document.getElementById("login-email"),
  loginPassword: document.getElementById("login-password"),
  loginBtn: document.getElementById("login-btn"),
  authStatus: document.getElementById("auth-status"),
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
  settings: {
    title: "Settings",
    subtitle: "Authentication and system configuration.",
  },
};

const headers = () => ({
  "Content-Type": "application/json",
  ...(state.token ? { Authorization: `Bearer ${state.token}` } : {}),
});

const updateAuthStatus = () => {
  elements.authStatus.textContent = state.token ? "Authenticated" : "Not authenticated";
};

const showMessage = (element, message) => {
  element.textContent = message;
  setTimeout(() => {
    element.textContent = "";
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

const fetchSummary = async () => {
  const response = await fetch(`${state.apiBase}/api/analytics/summary`, {
    headers: headers(),
  });
  if (!response.ok) return;
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
    elements.auditList.innerHTML = "<div class=\"item\">No activity yet.</div>";
    return;
  }
  elements.auditList.innerHTML = data
    .slice(0, 8)
    .map(
      (log) =>
        `<div class="item"><strong>${log.event_type}</strong><br/>${log.detail || ""}</div>`
    )
    .join("");
};

const renderDocuments = (documents) => {
  const html = documents
    .map(
      (doc) =>
        `<div class="item item-row"><span>${doc.filename}</span><button data-doc-id="${doc.id}">Delete</button></div>`
    )
    .join("");
  elements.docList.innerHTML = html || "<div class=\"item\">No documents yet.</div>";
  elements.docListInline.innerHTML = html || "<div class=\"item\">No documents yet.</div>";

  const buttons = document.querySelectorAll("button[data-doc-id]");
  buttons.forEach((button) => {
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
    showMessage(elements.docStatus, "Delete failed.");
  }
};

const fetchLeads = async () => {
  const response = await fetch(`${state.apiBase}/api/leads/`, { headers: headers() });
  if (!response.ok) return;
  const data = await response.json();
  elements.leadList.innerHTML = data
    .map(
      (lead) =>
        `<div class="item"><strong>${lead.name}</strong><br/>${lead.status} · score ${lead.score}</div>`
    )
    .join("");
};

const fetchWorkflows = async () => {
  const response = await fetch(`${state.apiBase}/api/workflows/`, { headers: headers() });
  if (!response.ok) return;
  const data = await response.json();
  elements.workflowList.innerHTML = data
    .map(
      (run) =>
        `<div class="item"><strong>${run.workflow_type}</strong><br/>${run.status} · ${run.output_summary || ""}</div>`
    )
    .join("");
};

const fetchConversations = async () => {
  const response = await fetch(`${state.apiBase}/api/chat/conversations`, { headers: headers() });
  if (!response.ok) return;
  const conversations = await response.json();
  if (!conversations.length) {
    elements.conversationList.innerHTML = "<div class=\"item\">No conversations yet.</div>";
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
        `<div class=\"item\"><strong>${msg.role}</strong><br/>${msg.content}</div>`
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

const signup = async () => {
  if (!elements.signupName.value || !elements.signupEmail.value || !elements.signupPassword.value) {
    showMessage(elements.authStatus, "Please enter name, email, and password.");
    return;
  }
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
  if (response.ok) {
    showMessage(elements.authStatus, "Account created. Please login.");
  } else {
    const detail = await readErrorMessage(response);
    showMessage(elements.authStatus, detail || "Signup failed.");
  }
};

const login = async () => {
  if (!elements.loginEmail.value || !elements.loginPassword.value) {
    showMessage(elements.authStatus, "Please enter email and password.");
    return;
  }
  const payload = {
    email: elements.loginEmail.value,
    password: elements.loginPassword.value,
  };
  const response = await fetch(`${state.apiBase}/api/auth/login`, {
    method: "POST",
    headers: headers(),
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const detail = await readErrorMessage(response);
    showMessage(elements.authStatus, detail || "Login failed.");
    return;
  }
  const data = await response.json();
  state.token = data.access_token;
  localStorage.setItem("token", state.token);
  updateAuthStatus();
  refreshDashboard();
};

const uploadDocument = async () => {
  if (!elements.docFile.files.length) return;
  const formData = new FormData();
  formData.append("file", elements.docFile.files[0]);
  const response = await fetch(`${state.apiBase}/api/docs/upload`, {
    method: "POST",
    headers: state.token ? { Authorization: `Bearer ${state.token}` } : {},
    body: formData,
  });
  if (response.ok) {
    showMessage(elements.docStatus, "Document uploaded.");
    refreshDashboard();
  } else {
    showMessage(elements.docStatus, "Upload failed.");
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
};

const createLead = async () => {
  const payload = {
    name: elements.leadName.value,
    email: elements.leadEmail.value || null,
    phone: elements.leadPhone.value || null,
    company: elements.leadCompany.value || null,
    interest: elements.leadInterest.value || null,
  };
  const response = await fetch(`${state.apiBase}/api/leads/`, {
    method: "POST",
    headers: headers(),
    body: JSON.stringify(payload),
  });
  if (response.ok) {
    showMessage(elements.leadStatus, "Lead saved.");
    refreshDashboard();
  } else {
    showMessage(elements.leadStatus, "Lead save failed.");
  }
};

const runWorkflow = async () => {
  let payload = {};
  try {
    payload = JSON.parse(elements.workflowPayload.value || "{}");
  } catch (error) {
    showMessage(elements.workflowStatus, "Invalid JSON payload.");
    return;
  }
  const response = await fetch(`${state.apiBase}/api/workflows/run`, {
    method: "POST",
    headers: headers(),
    body: JSON.stringify({ workflow_type: elements.workflowType.value, payload }),
  });
  if (response.ok) {
    showMessage(elements.workflowStatus, "Workflow executed.");
    refreshDashboard();
  } else {
    showMessage(elements.workflowStatus, "Workflow failed.");
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
  elements.apiBase.value = state.apiBase;
  updateAuthStatus();
  elements.saveApi.addEventListener("click", () => {
    state.apiBase = elements.apiBase.value.trim() || state.apiBase;
    localStorage.setItem("apiBase", state.apiBase);
  });
  elements.toggleConfig.addEventListener("click", () => {
    elements.configPanel.classList.toggle("active");
  });
  elements.refreshDashboard.addEventListener("click", refreshDashboard);
  elements.signupBtn.addEventListener("click", signup);
  elements.loginBtn.addEventListener("click", login);
  elements.uploadDoc.addEventListener("click", uploadDocument);
  elements.sendChat.addEventListener("click", sendChat);
  elements.createLead.addEventListener("click", createLead);
  elements.runWorkflow.addEventListener("click", runWorkflow);
  elements.navButtons.forEach((button) => {
    button.addEventListener("click", () => {
      showView(button.dataset.nav);
    });
  });
};

init();
