/**
 * GraphQL Client Configuration
 * 
 * Provides a configured GraphQL client instance with authentication support
 */

import { GraphQLClient } from 'graphql-request'
import Cookies from 'js-cookie'

const GRAPHQL_URL = process.env.NEXT_PUBLIC_GRAPHQL_URL || 'http://localhost:8000/graphql'

class AuthGraphQLClient {
  private client: GraphQLClient

  constructor() {
    this.client = new GraphQLClient(GRAPHQL_URL, {
      credentials: 'include',
      mode: 'cors',
    })
  }

  /**
   * Get the current access token from localStorage and cookies
   */
  private getAccessToken(): string | null {
    if (typeof window === 'undefined') return null
    // Try localStorage first, then cookies
    return localStorage.getItem('accessToken') || Cookies.get('accessToken') || null
  }

  /**
   * Update the authorization header with the current token
   */
  private updateAuthHeader() {
    const token = this.getAccessToken()
    if (token) {
      this.client.setHeader('Authorization', `Bearer ${token}`)
    } else {
      this.client.setHeader('Authorization', '')
    }
  }

  /**
   * Make a GraphQL request with automatic token injection
   */
  async request<T = any>(query: string, variables?: Record<string, any>): Promise<T> {
    this.updateAuthHeader()
    try {
      return await this.client.request<T>(query, variables)
    } catch (error: any) {
      // Handle authentication errors
      if (error.response?.errors?.[0]?.extensions?.code === 'UNAUTHENTICATED') {
        // Clear token on authentication error
        this.clearAccessToken()
      }
      throw error
    }
  }

  /**
   * Set the access token and update headers
   * Stores in both localStorage and cookies for SSR/middleware access
   */
  setAccessToken(token: string | null) {
    if (typeof window === 'undefined') return
    
    if (token) {
      localStorage.setItem('accessToken', token)
      // Also store in cookies for middleware access (7 days expiry)
      Cookies.set('accessToken', token, { 
        expires: 7,
        sameSite: 'lax',
        secure: process.env.NODE_ENV === 'production'
      })
      this.client.setHeader('Authorization', `Bearer ${token}`)
    } else {
      localStorage.removeItem('accessToken')
      Cookies.remove('accessToken')
      this.client.setHeader('Authorization', '')
    }
  }

  /**
   * Clear the access token
   */
  clearAccessToken() {
    this.setAccessToken(null)
  }
}

// Export singleton instance
export const graphqlClient = new AuthGraphQLClient()
