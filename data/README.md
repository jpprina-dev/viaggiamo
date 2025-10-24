# Mock Data for Viaggiamo Carpooling App

This directory contains realistic mock JSON datasets for the Viaggiamo carpooling application, generated based on the backend SQLAlchemy models and designed specifically for the Argentine market.

## 📁 Files Overview

### `users.json` (20 users)
Realistic Argentine users with authentic data:
- **Names**: Common Argentine first and last names
- **Contact**: Phone numbers in +54 format, email addresses with local domains
- **Identification**: DNI numbers in proper format
- **Profiles**: Bio descriptions, trip preferences, verification status
- **Authentication**: Mix of local and OAuth providers

### `vehicles.json` (12 vehicles)
Popular car models in Argentina:
- **Makes/Models**: Toyota, Ford, Chevrolet, Volkswagen, Honda, Peugeot, Renault, Nissan, Fiat, Hyundai
- **Details**: Realistic years (2017-2021), colors in Spanish, proper license plates
- **Ownership**: Linked to users who are drivers
- **Compliance**: Legal compliance acknowledgments for carpooling

### `trips.json` (25 trips)
Realistic carpooling routes across Argentina:
- **Routes**: Major cities (Buenos Aires, Córdoba, Rosario, Mar del Plata, La Plata, etc.)
- **Timing**: Future departure times (November-December 2025)
- **Pricing**: Realistic ARS amounts based on distance (2,000-15,000 ARS)
- **Capacity**: Proper seat availability and descriptions
- **Status**: Active trips with legal compliance

### `bookings.json` (40 bookings)
Diverse booking scenarios:
- **Statuses**: Confirmed, pending, and cancelled bookings
- **Pricing**: Correctly calculated (trip price × seats requested)
- **Notes**: Realistic passenger comments and requirements
- **Timing**: Proper booking timestamps
- **Relationships**: All linked to existing trips and users

### `ratings.json` (30 ratings)
Bidirectional ratings for completed trips:
- **Roles**: Both driver and passenger ratings
- **Scores**: 4-5 star ratings with detailed Spanish comments
- **Context**: Realistic feedback about punctuality, comfort, and experience
- **Relationships**: All linked to completed trips and valid users

## 🎯 Data Characteristics

### Argentina-Specific Features
- **Cities**: Real Argentine cities with proper Spanish names
- **Currency**: Prices in Argentine Pesos (ARS)
- **Phone Format**: +54 country code with proper formatting
- **Documents**: DNI identification numbers in correct format
- **Language**: Comments and descriptions in Spanish
- **Culture**: Realistic trip preferences and user behaviors

### Relational Integrity
- **Foreign Keys**: All relationships properly maintained
- **User IDs**: 1-20 range with consistent references
- **Vehicle Ownership**: Only users with vehicles can be drivers
- **Trip Participation**: Passengers cannot book their own trips
- **Rating Logic**: Only trip participants can rate each other
- **Price Accuracy**: Booking prices match trip prices × seats

### Data Quality
- **Timestamps**: ISO 8601 format with timezone
- **Future Dates**: All trip departures are in the future
- **Realistic Scenarios**: Plausible distances, prices, and timing
- **Diverse Content**: Mix of statuses, preferences, and user types
- **JSON Format**: Valid, well-formatted JSON ready for frontend use

## 🔗 Entity Relationships

```
Users (1-20)
├── Vehicles (owned by subset of users)
├── Trips (driven by users with vehicles)
├── Bookings (as passengers)
└── Ratings (as raters and rated users)

Trips (1-25)
├── Bookings (multiple passengers per trip)
└── Ratings (for completed trips)

Vehicles (1-12)
└── Trips (one vehicle per trip)
```

## 🚀 Usage

These mock datasets are designed to be used by the frontend for:
- **Development**: Testing UI components and user flows
- **Demo**: Showcasing the application with realistic data
- **Testing**: Validating data handling and display logic
- **Prototyping**: Building features without backend dependencies

## 📊 Data Statistics

- **Total Users**: 20 (mix of drivers and passengers)
- **Total Vehicles**: 12 (owned by 12 different users)
- **Total Trips**: 25 (covering major Argentine routes)
- **Total Bookings**: 40 (various statuses and scenarios)
- **Total Ratings**: 30 (bidirectional feedback)
- **Price Range**: 2,000 - 15,000 ARS per seat
- **Date Range**: November 2025 - December 2025

## ✅ Verification

All data has been verified for:
- ✅ Relational consistency across all files
- ✅ Price calculation accuracy
- ✅ Foreign key integrity
- ✅ Realistic Argentine context
- ✅ Valid JSON formatting
- ✅ Future date validation
- ✅ Proper data types and constraints

---

*Generated on: November 2024*
*For: Viaggiamo Carpooling Application*
*Context: Argentine Market*
