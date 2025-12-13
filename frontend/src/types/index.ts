// ============== User & Auth ==============
export interface User {
  id: number;
  email: string;
  name: string | null;
  created_at: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, inviteToken: string, name?: string) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
}

// ============== Family ==============
export interface Family {
  id: number;
  name: string | null;
  santa_code: string;  // Unique code for email routing
  santa_email: string | null;  // Full Santa email with family code
  language: string;
  budget_alert_threshold: number | null;
  moderation_strictness: string;
  data_retention_years: number;
  timezone: string;
  created_at: string;
}

export interface FamilyStats {
  total_children: number;
  total_letters: number;
  total_wish_items: number;
  pending_wish_items: number;
  approved_wish_items: number;
  denied_wish_items: number;
  total_estimated_budget: number | null;
  unread_notifications: number;
  pending_moderation_flags: number;
  completed_deeds: number;
  pending_deeds: number;
}

// ============== Children ==============
export interface Child {
  id: number;
  name: string;
  country: string | null;
  birth_year: number | null;
  avatar_url: string | null;
  language: string | null;
  created_at: string;
  letter_count?: number;
  wish_item_count?: number;
  pending_deeds?: number;
  completed_deeds?: number;
}

export interface ChildCreate {
  name: string;
  email: string;
  country?: string;
  birth_year?: number;
  avatar_url?: string;
  language?: string;
}

// ============== Letters ==============
export interface Letter {
  id: number;
  child_id: number;
  year: number;
  subject: string | null;
  body_text: string;
  received_at: string;
  status: string;
  processed_at: string | null;
  created_at: string;
  child_name?: string;
  wish_item_count?: number;
  wish_items?: WishItem[];
  santa_reply?: SantaReply;
  moderation_flags?: ModerationFlag[];
}

export interface LetterTimeline {
  year: number;
  letters: Letter[];
}

// ============== Wish Items ==============
export interface WishItem {
  id: number;
  letter_id: number;
  child_id?: number;  // Added for filtering display
  raw_text: string;
  normalized_name: string | null;
  category: string | null;
  status: string;
  denial_reason: string | null;
  denial_note: string | null;
  estimated_price: number | null;
  currency: string;
  product_url: string | null;
  product_image_url: string | null;
  product_description: string | null;
  created_at: string;
}

export interface WishlistSummary {
  total_items: number;
  by_status: Record<string, number>;
  by_category: Record<string, number>;
  total_estimated_cost: number | null;
  by_child: Record<string, number>;
}

// ============== Santa Replies ==============
export interface SantaReply {
  id: number;
  letter_id: number;
  body_text: string;
  suggested_deed: string | null;
  sent_at: string | null;
  delivery_status: string;
  created_at: string;
}

// ============== Good Deeds ==============
export interface GoodDeed {
  id: number;
  child_id: number;
  description: string;
  suggested_at: string;
  completed: boolean;
  completed_at: string | null;
  parent_note: string | null;
  child_name?: string;
}

// ============== Moderation ==============
export interface ModerationFlag {
  id: number;
  letter_id: number;
  flag_type: string;
  severity: 'low' | 'medium' | 'high';
  excerpt: string | null;
  ai_confidence: number | null;
  ai_explanation: string | null;
  reviewed: boolean;
  reviewed_at: string | null;
  action_taken: string | null;
  reviewer_note: string | null;
  created_at: string;
  child_name?: string;
  letter_subject?: string;
  letter_received_at?: string;
}

// ============== Notifications ==============
export interface Notification {
  id: number;
  type: string;
  title: string;
  message: string | null;
  read: boolean;
  related_letter_id: number | null;
  related_child_id: number | null;
  created_at: string;
}

// ============== Store States ==============
export interface FamilyState {
  family: Family | null;
  stats: FamilyStats | null;
  isLoading: boolean;
  fetchFamily: () => Promise<void>;
  createFamily: (name?: string) => Promise<void>;
  updateFamily: (updates: Partial<Family>) => Promise<void>;
  fetchStats: () => Promise<void>;
}

export interface ChildrenState {
  children: Child[];
  isLoading: boolean;
  fetchChildren: () => Promise<void>;
  addChild: (data: ChildCreate) => Promise<Child>;
  updateChild: (id: number, updates: Partial<Child>) => Promise<void>;
  deleteChild: (id: number) => Promise<void>;
}

export interface WishlistState {
  items: WishItem[];
  isLoading: boolean;
  fetchItems: (filters?: { child_id?: number; status?: string; year?: number }) => Promise<void>;
  updateItem: (id: number, updates: Partial<WishItem>) => Promise<void>;
}

export interface LettersState {
  letters: Letter[];
  isLoading: boolean;
  fetchLetters: (filters?: { child_id?: number; year?: number }) => Promise<void>;
  fetchLetter: (id: number) => Promise<Letter>;
}

export interface DeedsState {
  deeds: GoodDeed[];
  isLoading: boolean;
  fetchDeeds: (childId?: number, completed?: boolean) => Promise<void>;
  createDeed: (childId: number, description: string) => Promise<void>;
  completeDeed: (id: number, note?: string) => Promise<void>;
  deleteDeed: (id: number) => Promise<void>;
}

export interface NotificationsState {
  notifications: Notification[];
  unreadCount: number;
  isLoading: boolean;
  fetchNotifications: (unreadOnly?: boolean) => Promise<void>;
  fetchUnreadCount: () => Promise<void>;
  markAsRead: (id: number) => Promise<void>;
  markAllAsRead: () => Promise<void>;
}
