import type { AuthUser, LoginData, RegisterData } from '../types/auth';
import { apiRequest } from './client';

export async function login(data: LoginData): Promise<AuthUser> {
  return apiRequest<AuthUser>('/auth/login', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function register(data: RegisterData): Promise<AuthUser> {
  return apiRequest<AuthUser>('/auth/register', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getMe(token: string): Promise<AuthUser> {
  return apiRequest<AuthUser>('/auth/me', {
    method: 'GET',
    headers: { Authorization: `Bearer ${token}` },
  });
}

export interface MyProfileOut {
  user_id: number;
  name: string;
  email: string;
  session_id: string | null;
  selected_profession: string | null;
}

export async function getMyProfile(token: string): Promise<MyProfileOut> {
  return apiRequest<MyProfileOut>('/auth/my-profile', {
    method: 'GET',
    headers: { Authorization: `Bearer ${token}` },
  });
}

