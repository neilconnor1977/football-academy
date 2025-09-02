# Football Academy Database System

A comprehensive database management system for football academies to track players, teams, and academy statistics.

## Overview

This system was created to help football academies manage their player information, team assignments, and various status indicators. It provides tools for tracking players across different age groups, monitoring participation in various activities, and generating useful reports.

## Features

- **Player Management**: Add, update, delete, and search for players
- **Age Group Management**: Organize players by age categories
- **Team Assignments**: Track league team participation
- **Status Tracking**: Monitor player participation in various activities (VEO, photos, IDP meetings, etc.)
- **Statistics**: Automatically calculate and display academy statistics by age group
- **Reports**: Generate useful reports such as birthday lists and IDP meeting participants

## System Components

1. **SQLite Database** (`football_academy.db`) - Core data storage
2. **Database Creation Script** (`create_football_academy_db.py`) - Initializes the database
3. **Management Application** (`football_academy_manager.py`) - User interface for database operations
4. **Sample Queries** (`sample_queries.sql`) - Example SQL queries for custom reporting
5. **User Guide** (`user_guide.md`) - Comprehensive documentation

## Getting Started

### Prerequisites

- Python 3.6 or higher
- SQLite3 (included with Python)

### Installation

1. Clone or download this repository to your local machine
2. Navigate to the project directory

### Setup

1. Run the database creation script to set up the database:

```bash
python create_football_academy_db.py
```

2. Once the database is created, launch the management application:

```bash
python football_academy_manager.py
```

3. Follow the on-screen prompts to interact with the database

## Database Structure

The database consists of the following main tables:

- **players**: Individual player information
- **player_types**: Player classification (Full Time, Scholarship, Part Time, Trial)
- **age_groups**: Age categories
- **league_teams**: Teams for competitions
- **academy_statistics**: Summary statistics by age group

For a detailed explanation of the database structure, refer to the User Guide.

## Usage Examples

### Adding a New Player

1. Select option 5 from the main menu
2. Enter the player's full name
3. Select the player type
4. Select the primary age group
5. Enter birth date information
6. Enter jersey number

### Generating Reports

The system offers several built-in reports:
- Academy statistics by age group (option 8)
- Players with birthdays in the current month (option 9)
- Players with IDP meetings (option 10)
- Players with secondary age group assignments (option 11)

## Advanced Usage

For advanced users who want to create custom reports, the `sample_queries.sql` file provides examples of SQL queries that can be run directly against the database using a tool like SQLite Browser or the SQLite command-line interface.

## Documentation

For detailed instructions on using the system, refer to the `user_guide.md` file.

## Future Enhancements

Potential future enhancements include:
- Training session tracking
- Match records and performance metrics
- Financial information management
- Medical records
- Parent/Guardian contact information

## Support

For any issues or questions, please refer to the troubleshooting section in the User Guide.