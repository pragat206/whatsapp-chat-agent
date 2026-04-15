export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_verified: boolean;
  roles: Role[];
  created_at: string;
}

export interface Role {
  id: string;
  name: string;
  description?: string;
}

export interface Contact {
  id: string;
  phone_number: string;
  display_name?: string;
  city?: string;
  language: string;
}

export interface Tag {
  id: string;
  name: string;
  color: string;
}

export interface Conversation {
  id: string;
  contact: Contact;
  status: string;
  state: string;
  is_ai_active: boolean;
  assigned_to?: string;
  language: string;
  message_count: number;
  last_message_at?: string;
  tags: Tag[];
  created_at: string;
  messages?: Message[];
}

export interface Message {
  id: string;
  conversation_id: string;
  direction: 'inbound' | 'outbound';
  message_type: string;
  content: string;
  status: string;
  is_ai_generated: boolean;
  created_at: string;
}

export interface Product {
  id: string;
  name: string;
  sku?: string;
  description?: string;
  is_active: boolean;
  categories: Category[];
  created_at: string;
}

export interface Category {
  id: string;
  name: string;
  description?: string;
  is_active: boolean;
}

export interface KnowledgeSource {
  id: string;
  title: string;
  source_type: string;
  status: string;
  file_size?: number;
  original_filename?: string;
  chunk_count: number;
  version: number;
  is_active: boolean;
  error_message?: string;
  created_at: string;
}

export interface DashboardKPIs {
  total_conversations: number;
  active_conversations: number;
  resolved_conversations: number;
  total_inbound_messages: number;
  total_outbound_messages: number;
  ai_handled_count: number;
  human_handled_count: number;
  ai_resolution_rate: number;
  leads_captured: number;
  escalated_count: number;
  failed_messages: number;
}

export interface ConversationTrend {
  date: string;
  inbound: number;
  outbound: number;
  ai_handled: number;
  human_handled: number;
}

export interface AuditLog {
  id: string;
  user_id?: string;
  action: string;
  resource_type: string;
  resource_id?: string;
  details?: Record<string, unknown>;
  ip_address?: string;
  created_at: string;
}

export interface Setting {
  id: string;
  key: string;
  value?: string;
  value_json?: Record<string, unknown>;
  category: string;
  description?: string;
}

export interface Note {
  id: string;
  conversation_id: string;
  author_id: string;
  content: string;
  created_at: string;
}
