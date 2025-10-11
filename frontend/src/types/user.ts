export interface User {
  id: number
  email: string
  username: string
  fullName: string
  name?: string
  lastName?: string
  phone?: string
  profilePicture?: string
  profileShortBio?: string
  isVerified: boolean
  isActive: boolean
  authProvider?: string
  createdAt: string
  updatedAt: string
}

export interface RegisterInput {
  email: string
  username: string
  fullName: string
  phone?: string
  password: string
}

export interface LoginInput {
  email: string
  password: string
}

export interface AuthResponse {
  accessToken: string
  tokenType: string
}
