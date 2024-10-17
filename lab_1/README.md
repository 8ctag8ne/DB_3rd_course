# Anime Database

This project contains scripts and schema for an anime database, designed to store and manage information about various anime series, characters, studios, and related data.

## Overview

The Anime Database is a comprehensive system for tracking and managing information related to anime series. It includes details about anime shows, characters, voice actors, studios, user reviews, and more. This database can serve as a foundation for building anime-related applications, such as a content management system for an anime streaming platform or a fan community website.

## Project Structure

The project consists of several SQL scripts, each serving a specific purpose:

1. `CreateDB.sql`: Creates the database and defines the schema (tables and relationships).
2. `FillDB.sql`: Populates the database with sample data.
3. `SoftDeleteProcedures.sql`: Implements soft delete functionality for relevant tables.
4. `Views.sql`: Creates database views for simplified data access and reporting.
5. `UpdateTriggers.sql`: Defines triggers for maintaining data integrity during updates.
6. `UserFunctions.sql`: Contains user-defined functions for common operations or calculations.

## Database Schema

The database consists of the following main tables:

1. `Anime`: Stores information about anime series, including title, year, synopsis, and episode count.
2. `Users`: Contains user account information.
3. `Character`: Stores details about anime characters.
4. `VoiceActor`: Information about voice actors.
5. `Studio`: Details about animation studios.
6. `Genre`: Anime genres.
7. `Review`: User reviews for anime series.
8. `Episode`: Information about individual episodes of anime series.
9. `Soundtrack`: Details about anime soundtracks.
10. `Merchandise`: Information about anime-related merchandise.
11. `Award`: Records of awards won by anime series.
12. `ForumThread` and `ForumPost`: For managing forum discussions.
13. `WatchStatus`: Tracks users' watching progress for different anime.
14. `Recommendation`: Stores anime recommendations.

There are also junction tables to manage many-to-many relationships, such as `AnimeGenre`, `AnimeStudio`, and `CharacterVoiceActor`.

## Features

- Comprehensive anime information storage
- User management system
- Review and rating system
- Forum functionality for user discussions
- Tracking of user watch status
- Merchandise and soundtrack information
- Award tracking for anime series
- Soft delete functionality for data preservation
- Custom views for simplified data access
- Update triggers for maintaining data integrity
- User-defined functions for common operations

## Setup

1. Ensure you have SQL Server installed and running.
2. Run the scripts in the following order:
   a. `CreateDB.sql` to create the database and tables.
   b. `FillDB.sql` to populate the database with sample data.
   c. `SoftDeleteProcedures.sql` to implement soft delete functionality.
   d. `Views.sql` to create database views.
   e. `UpdateTriggers.sql` to set up update triggers.
   f. `UserFunctions.sql` to add user-defined functions.

## Usage

After setting up the database, you can use it as a backend for various anime-related applications. Some potential use cases include:

- Building an anime streaming platform
- Creating a community website for anime fans
- Developing a mobile app for tracking watched anime
- Analyzing trends in anime production and popularity

### Using Views

The views defined in `Views.sql` provide simplified access to commonly needed data. For example, you might have views for:
- Popular anime by user ratings
- Most active forum threads
- Top voice actors by number of roles

### Soft Delete

The soft delete procedures allow you to mark records as deleted without physically removing them from the database. This is useful for maintaining data history and potentially recovering deleted records.

### Update Triggers

The triggers defined in `UpdateTriggers.sql` help maintain data integrity by automatically updating related records or timestamps when certain data changes.

### User Functions

The functions in `UserFunctions.sql` can be used to perform common calculations or data manipulations. These might include functions for calculating average ratings, determining watch progress, or generating recommendations.

## Contributing

Contributions to improve the database schema, add more sample data, or enhance the provided SQL scripts are welcome. Please submit a pull request with your proposed changes.

## License

This project is open-source and available under the MIT License.