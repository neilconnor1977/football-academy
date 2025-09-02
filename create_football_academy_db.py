import sqlite3
import csv
import os
from datetime import datetime

# Create or connect to the database
conn = sqlite3.connect('football_academy.db')
cursor = conn.cursor()

# Create tables
def create_tables():
    # Player Types table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS player_types (
        type_code TEXT PRIMARY KEY,
        type_name TEXT NOT NULL
    )
    ''')
    
    # Age Groups table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS age_groups (
        group_id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_name TEXT NOT NULL UNIQUE
    )
    ''')
    
    # League Teams table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS league_teams (
        team_id INTEGER PRIMARY KEY AUTOINCREMENT,
        team_name TEXT NOT NULL UNIQUE
    )
    ''')
    
    # Players table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS players (
        player_id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        type_code TEXT,
        primary_age_group_id INTEGER,
        secondary_age_group_id INTEGER,
        birth_day INTEGER,
        birth_month INTEGER,
        birth_year INTEGER,
        jersey_number TEXT,
        league_team_id INTEGER,
        veo_member BOOLEAN DEFAULT 0,
        photos BOOLEAN DEFAULT 0,
        idp_meeting_sep BOOLEAN DEFAULT 0,
        idp_meeting_apr BOOLEAN DEFAULT 0,
        chat BOOLEAN DEFAULT 0,
        files BOOLEAN DEFAULT 0,
        FOREIGN KEY (type_code) REFERENCES player_types (type_code),
        FOREIGN KEY (primary_age_group_id) REFERENCES age_groups (group_id),
        FOREIGN KEY (secondary_age_group_id) REFERENCES age_groups (group_id),
        FOREIGN KEY (league_team_id) REFERENCES league_teams (team_id)
    )
    ''')
    
    # Academy Statistics table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS academy_statistics (
        stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
        age_group_id INTEGER,
        total INTEGER DEFAULT 0,
        budget INTEGER DEFAULT 0,
        net INTEGER DEFAULT 0,
        ft_players INTEGER DEFAULT 0,
        pt_players INTEGER DEFAULT 0,
        sc_players INTEGER DEFAULT 0,
        trial_players INTEGER DEFAULT 0,
        FOREIGN KEY (age_group_id) REFERENCES age_groups (group_id)
    )
    ''')
    
    conn.commit()

# Insert initial data
def insert_initial_data():
    # Insert player types
    player_types = [
        ('FT', 'Full Time'),
        ('SC', 'Scholarship'),
        ('PT', 'Part Time'),
        ('T', 'Trial')
    ]
    cursor.executemany('INSERT OR IGNORE INTO player_types (type_code, type_name) VALUES (?, ?)', player_types)
    
    # Insert age groups from the PDF
    age_groups = [
        ('B 11 & 12',),
        ('B 12 & 13',),
        ('B 13 & 14',),
        ('B 14 & 15',),
        ('B 15 & 16',),
        ('B 16 & 17',),
        ('B 17 & 18',),
        ('G 10 & 11',),
        ('G 12 & 13',)
    ]
    cursor.executemany('INSERT OR IGNORE INTO age_groups (group_name) VALUES (?)', age_groups)
    
    # Insert league teams
    league_teams = [
        ('League Team 1',),
        ('League Team 2',)
    ]
    cursor.executemany('INSERT OR IGNORE INTO league_teams (team_name) VALUES (?)', league_teams)
    
    conn.commit()

# Parse and insert player data from the text file
def insert_player_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    # Get age group IDs for reference
    cursor.execute('SELECT group_id, group_name FROM age_groups')
    age_group_map = {group_name: group_id for group_id, group_name in cursor.fetchall()}
    
    # Get league team IDs for reference
    cursor.execute('SELECT team_id, team_name FROM league_teams')
    team_map = {team_name: team_id for team_id, team_name in cursor.fetchall()}
    
    # Process each line that contains player data
    for line in lines:
        # Skip header lines and empty lines
        if not line.strip() or "PLAYER" in line or "TOT" in line:
            continue
            
        # Parse player data - this is a simplified version and might need adjustments
        parts = line.strip().split()
        if len(parts) < 5:  # Skip lines with insufficient data
            continue
            
        # Extract player name (which might contain multiple words)
        name_parts = []
        i = 0
        while i < len(parts) and parts[i] not in ["FT", "SC", "PT", "T"]:
            name_parts.append(parts[i])
            i += 1
        
        if i == len(parts):  # Skip if we can't find the player type
            continue
            
        full_name = " ".join(name_parts)
        type_code = parts[i]
        i += 1
        
        # Extract age group
        if i < len(parts) and "B" in parts[i] or "G" in parts[i]:
            primary_age_group = parts[i]
            i += 1
        else:
            primary_age_group = None
        
        # Extract birth day, month, year
        birth_day = None
        birth_month = None
        birth_year = None
        
        if i + 2 < len(parts):
            try:
                birth_day = int(parts[i])
                birth_month = int(parts[i+1])
                birth_year = int(parts[i+2])
                i += 3
            except (ValueError, IndexError):
                # If conversion fails, just continue with None values
                pass
        
        # Extract jersey number
        jersey_number = None
        if i < len(parts):
            try:
                jersey_number = parts[i]
                i += 1
            except (ValueError, IndexError):
                pass
        
        # Extract secondary age group if present
        secondary_age_group = None
        if i < len(parts) and ("B" in parts[i] or "G" in parts[i]):
            secondary_age_group = parts[i]
            i += 1
        
        # Extract boolean flags
        veo_member = "YES" in line[line.find(secondary_age_group if secondary_age_group else jersey_number):] if secondary_age_group or jersey_number else False
        photos = "YES" in line[line.find("YES" if veo_member else "NO"):] if veo_member or "NO" in line else False
        idp_meeting_sep = "YES" in line[line.find("YES" if photos else "NO"):] if photos or "NO" in line else False
        idp_meeting_apr = "YES" in line[line.find("YES" if idp_meeting_sep else "NO"):] if idp_meeting_sep or "NO" in line else False
        chat = "YES" in line[line.find("YES" if idp_meeting_apr else "NO"):] if idp_meeting_apr or "NO" in line else False
        files = "YES" in line[line.find("YES" if chat else "NO"):] if chat or "NO" in line else False
        
        # Get IDs for foreign keys
        primary_age_group_id = age_group_map.get(primary_age_group) if primary_age_group else None
        secondary_age_group_id = age_group_map.get(secondary_age_group) if secondary_age_group else None
        
        # Determine league team (simplified logic - would need refinement)
        league_team_id = None
        
        # Insert player data
        cursor.execute('''
        INSERT INTO players (
            full_name, type_code, primary_age_group_id, secondary_age_group_id,
            birth_day, birth_month, birth_year, jersey_number, league_team_id,
            veo_member, photos, idp_meeting_sep, idp_meeting_apr, chat, files
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            full_name, type_code, primary_age_group_id, secondary_age_group_id,
            birth_day, birth_month, birth_year, jersey_number, league_team_id,
            1 if veo_member else 0, 1 if photos else 0, 
            1 if idp_meeting_sep else 0, 1 if idp_meeting_apr else 0,
            1 if chat else 0, 1 if files else 0
        ))
    
    conn.commit()

# Insert academy statistics
def insert_academy_statistics():
    # Get age group IDs for reference
    cursor.execute('SELECT group_id, group_name FROM age_groups')
    age_groups = cursor.fetchall()
    
    # Extract statistics from the PDF data
    # This is a simplified version - in a real scenario, you would parse this data more carefully
    statistics = [
        # (age_group_id, total, budget, net, ft_players, pt_players, sc_players, trial_players)
        (age_groups[0][0], 12, 18, 6, 8, 2, 4, 0),  # B 11 & 12
        (age_groups[1][0], 20, 18, -2, 14, 0, 6, 0),  # B 12 & 13
        (age_groups[2][0], 17, 16, -1, 11, 0, 6, 0),  # B 13 & 14
        (age_groups[3][0], 24, 16, -8, 21, 0, 3, 0),  # B 14 & 15
        (age_groups[4][0], 0, 16, 16, 0, 0, 0, 0),  # B 15 & 16
        (age_groups[5][0], 1, 12, 11, 1, 0, 0, 0),  # B 16 & 17
        (age_groups[6][0], 7, 12, 5, 6, 0, 1, 0),  # B 17 & 18
        (age_groups[7][0], 0, 18, 18, 0, 0, 0, 0),  # G 10 & 11
        (age_groups[8][0], 2, 18, 16, 0, 0, 2, 0),  # G 12 & 13
    ]
    
    cursor.executemany('''
    INSERT INTO academy_statistics (
        age_group_id, total, budget, net, ft_players, pt_players, sc_players, trial_players
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', statistics)
    
    conn.commit()

# Main function to create and populate the database
def main():
    create_tables()
    insert_initial_data()
    insert_player_data('opa_database_content.txt')
    insert_academy_statistics()
    print("Database created and populated successfully!")
    
    # Display some sample data to verify
    print("\nSample Players:")
    cursor.execute('''
    SELECT p.full_name, pt.type_name, ag.group_name, p.birth_day, p.birth_month, p.birth_year, p.jersey_number
    FROM players p
    JOIN player_types pt ON p.type_code = pt.type_code
    JOIN age_groups ag ON p.primary_age_group_id = ag.group_id
    LIMIT 10
    ''')
    for row in cursor.fetchall():
        print(row)
    
    print("\nAge Group Statistics:")
    cursor.execute('''
    SELECT ag.group_name, s.total, s.budget, s.net, s.ft_players, s.pt_players, s.sc_players, s.trial_players
    FROM academy_statistics s
    JOIN age_groups ag ON s.age_group_id = ag.group_id
    ''')
    for row in cursor.fetchall():
        print(row)

if __name__ == "__main__":
    main()
    conn.close()