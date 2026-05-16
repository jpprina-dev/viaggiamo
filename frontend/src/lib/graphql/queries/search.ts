/**
 * GraphQL Queries for Search functionality
 */

import { gql } from 'graphql-request'

export const SEARCH_LOCALITIES = gql`
  query SearchLocalities($q: String!, $limit: Int) {
    searchLocalities(q: $q, limit: $limit) {
      id
      name
      province
      department
      displayName
    }
  }
`

/**
 * Query to search for trips with filters
 */
export const SEARCH_TRIPS = gql`
  query SearchTrips(
    $origin: String!
    $destination: String!
    $departureDate: Date
    $minSeats: Int
    $maxPrice: Decimal
    $limit: Int
    $offset: Int
  ) {
    searchTrips(
      search: {
        origin: $origin
        destination: $destination
        departureDate: $departureDate
        minSeats: $minSeats
        maxPrice: $maxPrice
        limit: $limit
        offset: $offset
      }
    ) {
      trip {
        id
        origin
        destination
        departureTime
        pricePerSeat
        availableSeats
        totalSeats
        description
        isActive
        tripPreferences
      }
      driver {
        id
        name
        lastName
        username
        profilePicture
        profileShortBio
        status
      }
      vehicle {
        id
        make
        model
        year
        color
        licensePlate
        seats
      }
      relevanceScore
    }
  }
`
