/** 用户详细资料 API 类型定义 */
export interface UserDetails {
  id: string;
  user_id: string;
  real_name: string;
  grade: string | null;
  class_name: string | null;
  avatar_url: string | null;
  is_complete: boolean;
  created_at: string;
  update_at: string;
}

export interface UserDetailsPublic {
  real_name: string;
  grade: string | null;
  class_name: string | null;
  avatar_url: string | null;
}

export interface UserDetailsCompleteCheck {
  is_complete: boolean;
  missing_fields: string[];
  message: string | null;
}

export interface CompleteProfileRequest {
  real_name: string;
  grade: string;
  class_name: string;
  avatar_url: string;
}

export interface UserDetailsUpdate {
  real_name?: string;
  grade?: string;
  class_name?: string;
  avatar_url?: string;
}
