/**
 * GraphQL Queries for Search functionality
 */

import { gql } from 'graphql-request'

/**
 * Query to get city origin suggestions based on prefix
 */
export const CITY_ORIGINS = gql`
  query CityOrigins($prefix: String!, $limit: Int) {
    cityOrigins(prefix: $prefix, limit: $limit)
  }
`

/**
 * Query to get city destination suggestions based on prefix
 */
export const CITY_DESTINATIONS = gql`
  query CityDestinations($prefix: String!, $limit: Int) {
    cityDestinations(prefix: $prefix, limit: $limit)
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
