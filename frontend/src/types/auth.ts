export interface AuthUser {
  token: string;
  user_id: number;
  name: string;
  email: string;
}

export interface LoginData {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  name: string;
  session_id?: string;
}

