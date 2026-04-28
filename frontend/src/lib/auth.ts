/**
 * Authentication Library
 * 
 * Handles user authentication, registration, and session management
 */

import { gql, ClientError } from 'graphql-request'
import { graphqlClient } from './graphql-client'
import type { User, RegisterInput, AuthResponse } from '@/types'
import { mapGraphQLUserToUser } from '@/types/user'
import type { GraphQLUser } from '@/types/user'

// GraphQL Mutations
const LOGIN_MUTATION = gql`
  mutation Login($loginInput: LoginInput!) {
    login(loginInput: $loginInput) {
      accessToken
      tokenType
    }
  }
`

const REGISTER_MUTATION = gql`
  mutation Register($userInput: UserCreateInput!) {
    register(userInput: $userInput) {
      id
      email
      username
      name
      lastName
      status
    }
  }
`

const LOGIN_WITH_OAUTH_MUTATION = gql`
  mutation LoginWithOAuth($oauthInput: OAuthLoginInput!) {
    loginWithOauth(oauthInput: $oauthInput) {
      accessToken
      tokenType
    }
  }
`

// GraphQL Queries
const GET_CURRENT_USER_QUERY = gql`
  query GetCurrentUser {
    me {
      id
      email
      username
      name
      lastName
      status
      emailVerified
      phone
      phoneVerified
      profilePicture
      profileShortBio
      authProvider
      createdAt
      updatedAt
    }
  }
`

/**
 * Login with email and password
 */
export async function login(email: string, password: string): Promise<AuthResponse> {
  try {
    const response = await graphqlClient.request<{ login: AuthResponse }>(
      LOGIN_MUTATION,
      { 
        loginInput: {
          email,
          password
        }
      }
    )

    // Store the access token
    graphqlClient.setAccessToken(response.login.accessToken)

    return response.login
  } catch (error: unknown) {
    const errorMessage = error instanceof ClientError
      ? (error.response?.errors?.[0]?.message ?? 'Error al iniciar sesión')
      : 'Error al iniciar sesión'
    throw new Error(errorMessage)
  }
}

/**
 * Register a new user
 */
export async function register(input: RegisterInput): Promise<User> {
  try {
    const response = await graphqlClient.request<{ register: GraphQLUser }>(
      REGISTER_MUTATION,
      { 
        userInput: {
          email: input.email,
          username: input.username,
          name: input.name,
          last_name: input.last_name,
          password: input.password,
          phone: input.phone,
          profile_picture: input.profile_picture,
        }
      }
    )

    // Map the response to User type
    return mapGraphQLUserToUser(response.register)
  } catch (error: unknown) {
    const errorMessage = error instanceof ClientError
      ? (error.response?.errors?.[0]?.message ?? 'Error al registrarse')
      : 'Error al registrarse'
    throw new Error(errorMessage)
  }
}

/**
 * Login with Google OAuth
 */
export async function loginWithGoogle(credential: string): Promise<AuthResponse> {
  try {
    const response = await graphqlClient.request<{ loginWithOauth: AuthResponse }>(
      LOGIN_WITH_OAUTH_MUTATION,
      { 
        oauthInput: {
          provider: 'google',
          token: credential
        }
      }
    )

    // Store the access token
    graphqlClient.setAccessToken(response.loginWithOauth.accessToken)

    return response.loginWithOauth
  } catch (error: unknown) {
    const errorMessage = error instanceof ClientError
      ? (error.response?.errors?.[0]?.message ?? 'Error al iniciar sesión con Google')
      : 'Error al iniciar sesión con Google'
    throw new Error(errorMessage)
  }
}

/**
 * Get the current authenticated user
 */
export async function getCurrentUser(): Promise<User> {
  try {
    const response = await graphqlClient.request<{ me: GraphQLUser }>(GET_CURRENT_USER_QUERY)
    
    // Map GraphQL response to User type
    return mapGraphQLUserToUser(response.me)
  } catch (error: unknown) {
    if (error instanceof ClientError && error.response?.errors?.[0]?.extensions?.code === 'UNAUTHENTICATED') {
      graphqlClient.clearAccessToken()
      throw new Error('No authenticated user')
    }
    throw error
  }
}

/**
 * Logout the current user
 */
export function logout(): void {
  graphqlClient.clearAccessToken()
}

/**
 * Check if user is authenticated (has a valid token)
 */
export function isAuthenticated(): boolean {
  if (typeof window === 'undefined') return false
  return !!localStorage.getItem('accessToken')
}

// Re-export User type for convenience
export type { User }
