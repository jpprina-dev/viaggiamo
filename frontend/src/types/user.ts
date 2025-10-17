export interface User {
  id: number
  email: string
  username: string
  name: string
  last_name: string
  status: string
  email_verified: boolean
  phone?: string
  phone_verified?: boolean
  profile_picture?: string
  profile_short_bio?: string
  auth_provider?: string
  created_at: string
  updated_at: string
}

export interface RegisterInput {
  email: string
  username: string
  name: string
  last_name: string
  phone?: string
  password: string
  profile_picture?: string
}

export interface LoginInput {
  email: string
  password: string
}

export interface AuthResponse {
  accessToken: string
  tokenType: string
}

// Helper function to map GraphQL UserType to User interface
export function mapGraphQLUserToUser(gqlUser: any): User {
  return {
    id: gqlUser.id,
    email: gqlUser.email,
    username: gqlUser.username,
    name: gqlUser.name,
    last_name: gqlUser.lastName,
    status: gqlUser.status,
    email_verified: gqlUser.emailVerified,
    phone: gqlUser.phone,
    phone_verified: gqlUser.phoneVerified,
    profile_picture: gqlUser.profilePicture,
    profile_short_bio: gqlUser.profileShortBio,
    auth_provider: gqlUser.authProvider,
    created_at: gqlUser.createdAt,
    updated_at: gqlUser.updatedAt,
  }
}
