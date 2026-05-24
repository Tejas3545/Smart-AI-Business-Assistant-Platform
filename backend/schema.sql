
CREATE TABLE users (
	id SERIAL NOT NULL, 
	workspace_id INTEGER, 
	email VARCHAR(255) NOT NULL, 
	full_name VARCHAR(255) NOT NULL, 
	hashed_password VARCHAR(255) NOT NULL, 
	role VARCHAR(50) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);


CREATE TABLE audit_logs (
	id SERIAL NOT NULL, 
	user_id INTEGER, 
	event_type VARCHAR(80) NOT NULL, 
	detail TEXT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);


CREATE TABLE conversations (
	id SERIAL NOT NULL, 
	user_id INTEGER NOT NULL, 
	title VARCHAR(255) DEFAULT 'New Conversation' NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);


CREATE TABLE documents (
	id SERIAL NOT NULL, 
	user_id INTEGER NOT NULL, 
	filename VARCHAR(255) NOT NULL, 
	content_type VARCHAR(120), 
	source VARCHAR(255), 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);


CREATE TABLE leads (
	id SERIAL NOT NULL, 
	user_id INTEGER NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	email VARCHAR(255), 
	phone VARCHAR(50), 
	company VARCHAR(255), 
	interest TEXT, 
	score INTEGER NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	notes TEXT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);


CREATE TABLE user_memory (
	id SERIAL NOT NULL, 
	user_id INTEGER NOT NULL, 
	key VARCHAR(120) NOT NULL, 
	value TEXT NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);


CREATE TABLE workflow_runs (
	id SERIAL NOT NULL, 
	user_id INTEGER NOT NULL, 
	workflow_type VARCHAR(80) NOT NULL, 
	status VARCHAR(40) NOT NULL, 
	input_summary TEXT, 
	output_summary TEXT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);


CREATE TABLE workspaces (
	id SERIAL NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	owner_id INTEGER NOT NULL, 
	settings JSON NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(owner_id) REFERENCES users (id)
);


CREATE TABLE integrations (
	id SERIAL NOT NULL, 
	workspace_id INTEGER NOT NULL, 
	provider VARCHAR(50) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	credentials JSON NOT NULL, 
	config JSON NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(workspace_id) REFERENCES workspaces (id)
);


CREATE TABLE messages (
	id SERIAL NOT NULL, 
	conversation_id INTEGER NOT NULL, 
	role VARCHAR(20) NOT NULL, 
	content TEXT NOT NULL, 
	tokens INTEGER DEFAULT '0' NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(conversation_id) REFERENCES conversations (id)
);


CREATE TABLE workflows (
	id SERIAL NOT NULL, 
	workspace_id INTEGER NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	description TEXT, 
	is_active BOOLEAN NOT NULL, 
	trigger_type VARCHAR(50) NOT NULL, 
	trigger_config JSON NOT NULL, 
	nodes JSON NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(workspace_id) REFERENCES workspaces (id)
);


CREATE TABLE automation_tasks (
	id SERIAL NOT NULL, 
	workspace_id INTEGER NOT NULL, 
	workflow_id INTEGER, 
	trigger_source VARCHAR(100), 
	payload JSON NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	step_index INTEGER NOT NULL, 
	retry_count INTEGER NOT NULL, 
	max_retries INTEGER NOT NULL, 
	error_log TEXT, 
	next_run_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(workspace_id) REFERENCES workspaces (id), 
	FOREIGN KEY(workflow_id) REFERENCES workflows (id)
);

