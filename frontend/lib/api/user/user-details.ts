/** 用户详细资料 API 类型定义 */
export interface UserDetails {
  id: string;
  userId: string;
  realName: string;
  grade: string | null;
  className: string | null;
  avatarUrl: string | null;
  isComplete: boolean;
  createdAt: string;
  updateAt: string;
}

export interface UserDetailsPublic {
  realName: string;
  grade: string | null;
  className: string | null;
  avatarUrl: string | null;
}

export interface UserDetailsCompleteCheck {
  isComplete: boolean;
  missingFields: string[];
  message: string | null;
}

export interface CompleteProfileRequest {
  realName: string;
  grade: string;
  className: string;
  avatarUrl: string;
}

export interface UserDetailsUpdate {
  realName?: string;
  grade?: string;
  className?: string;
  avatarUrl?: string;
}
