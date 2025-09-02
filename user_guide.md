# Football Academy Database - User Guide

## Introduction

This database system is designed to help manage your football academy's player information, team assignments, and various status indicators. The system allows you to track players across different age groups, monitor their participation in various activities, and generate useful reports.

## System Components

The database system consists of the following components:

1. **SQLite Database** (`football_academy.db`) - Stores all your academy data
2. **Database Creation Script** (`create_football_academy_db.py`) - Creates and initializes the database
3. **Management Application** (`football_academy_manager.py`) - User-friendly interface for database operations
4. **Sample Queries** (`sample_queries.sql`) - Examples of SQL queries for custom reporting
5. **User Guide** (this document) - Instructions for using the system

## Getting Started

### Initial Setup

1. First, run the database creation script to set up the database:

```bash
python create_football_academy_db.py
```

This script will:
- Create the database file (`football_academy.db`)
- Set up all necessary tables
- Import player data from the PDF file
- Initialize statistics for each age group

2. Once the database is created, you can use the management application:

```bash
python football_academy_manager.py
```

## Database Structure

The database consists of the following tables:

1. **players** - Contains all player information
   - player_id: Unique identifier
   - full_name: Player's full name
   - type_code: Player type (FT, SC, PT, T)
   - primary_age_group_id: Main age group assignment
   - secondary_age_group_id: Optional secondary age group
   - birth_day, birth_month, birth_year: Date of birth
   - jersey_number: Player's jersey number
   - league_team_id: Team assignment
   - veo_member, photos, idp_meeting_sep, idp_meeting_apr, chat, files: Status flags

2. **player_types** - Player classification types
   - type_code: Short code (FT, SC, PT, T)
   - type_name: Full description (Full Time, Scholarship, Part Time, Trial)

3. **age_groups** - Age categories
   - group_id: Unique identifier
   - group_name: Age group name (e.g., "B 11 & 12")

4. **league_teams** - Teams for competitions
   - team_id: Unique identifier
   - team_name: Team name

5. **academy_statistics** - Summary statistics by age group
   - stat_id: Unique identifier
   - age_group_id: Associated age group
   - total: Total players in the age group
   - budget: Target number of players
   - net: Difference between budget and actual
   - ft_players, pt_players, sc_players, trial_players: Counts by player type

## Using the Management Application

The management application provides a user-friendly interface for common database operations. Here's how to use it:

### Main Menu Options

1. **View all players** - Displays a complete list of all players in the academy
2. **Search for players** - Find players by name
3. **View players by age group** - List players in a specific age category
4. **View players by type** - List players of a specific type (FT, SC, PT, T)
5. **Add a new player** - Register a new player in the system
6. **Update player information** - Modify existing player details
7. **Delete a player** - Remove a player from the database
8. **View academy statistics** - See summary statistics for each age group
9. **View players with birthdays this month** - Useful for planning celebrations
10. **View players with IDP meetings** - Track individual development plan meetings
11. **View players with secondary age group assignments** - See players assigned to multiple groups
12. **Manage age groups** - Add, update, or delete age categories
13. **Manage league teams** - Add, update, or delete teams

### Common Tasks

#### Adding a New Player

1. Select option 5 from the main menu
2. Enter the player's full name
3. Select the player type (Full Time, Scholarship, Part Time, Trial)
4. Select the primary age group
5. Enter birth date information
6. Enter jersey number
7. The system will automatically update statistics

#### Updating Player Information

1. Select option 6 from the main menu
2. Search for the player by name
3. Select the player from the search results
4. Enter new information (leave fields blank to keep current values)
5. Optionally update status flags (VEO, photos, etc.)

#### Generating Reports

The system offers several built-in reports:
- Academy statistics by age group (option 8)
- Players with birthdays in the current month (option 9)
- Players with IDP meetings (option 10)
- Players with secondary age group assignments (option 11)

## Advanced Usage: Custom Queries

For advanced users who want to create custom reports, the `sample_queries.sql` file provides examples of SQL queries that can be run directly against the database using a tool like SQLite Browser or the SQLite command-line interface.

Examples include:
- Finding players born in a specific year
- Comparing actual vs. budgeted players for each age group
- Listing players with specific status flags

## Data Maintenance

### Regular Maintenance Tasks

1. **Update Statistics**: The system automatically updates statistics when players are added, updated, or deleted. However, if you suspect any discrepancies, you can manually update statistics through the database.

2. **Backup**: Regularly back up your database file (`football_academy.db`) to prevent data loss.

3. **Age Group Transitions**: At the end of each season, you may need to move players to new age groups. This can be done by updating each player's primary_age_group_id.

## Troubleshooting

### Common Issues

1. **Database Connection Error**: Ensure the database file exists in the same directory as the management application. If not, run the creation script first.

2. **Cannot Delete Age Group**: Age groups with assigned players cannot be deleted. You must first reassign or delete all players in that group.

3. **Statistics Mismatch**: If statistics seem incorrect, try updating all statistics by modifying and saving a player record.

## Extending the System

The database can be extended to include additional features such as:

1. **Training Sessions**: Track attendance and performance at training sessions
2. **Match Records**: Record match participation and performance metrics
3. **Financial Information**: Track fees, payments, and expenses
4. **Medical Records**: Monitor injuries and fitness information
5. **Parent/Guardian Information**: Store contact details for parents/guardians

To extend the system, you would need to:
1. Add new tables to the database schema
2. Update the creation script
3. Add new functionality to the management application

## Conclusion

This football academy database system provides a comprehensive solution for managing player information, team assignments, and academy statistics. By using this system, you can efficiently track player development, monitor age group distributions, and generate useful reports for academy management.

For any additional assistance or custom modifications, please contact your database administrator.