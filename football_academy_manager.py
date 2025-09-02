import sqlite3
import os
import sys
from datetime import datetime

class FootballAcademyManager:
    def __init__(self, db_path='football_academy.db'):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """Connect to the database"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # This enables column access by name
            self.cursor = self.conn.cursor()
            return True
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            return False
            
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            
    def execute_query(self, query, params=None):
        """Execute a query and return results"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
                
            if query.strip().upper().startswith(("SELECT", "PRAGMA")):
                return self.cursor.fetchall()
            else:
                self.conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Query execution error: {e}")
            print(f"Query: {query}")
            if params:
                print(f"Parameters: {params}")
            return None
            
    # Player Management
    def get_all_players(self):
        """Get all players with their basic information"""
        query = """
        SELECT 
            p.player_id,
            p.full_name,
            pt.type_name AS player_type,
            ag.group_name AS age_group,
            p.birth_day || '/' || p.birth_month || '/' || p.birth_year AS birth_date,
            p.jersey_number
        FROM players p
        JOIN player_types pt ON p.type_code = pt.type_code
        JOIN age_groups ag ON p.primary_age_group_id = ag.group_id
        ORDER BY ag.group_name, p.full_name
        """
        return self.execute_query(query)
        
    def get_players_by_age_group(self, age_group):
        """Get players in a specific age group"""
        query = """
        SELECT 
            p.player_id,
            p.full_name,
            pt.type_name AS player_type,
            p.birth_day || '/' || p.birth_month || '/' || p.birth_year AS birth_date,
            p.jersey_number
        FROM players p
        JOIN player_types pt ON p.type_code = pt.type_code
        JOIN age_groups ag ON p.primary_age_group_id = ag.group_id
        WHERE ag.group_name = ?
        ORDER BY p.full_name
        """
        return self.execute_query(query, (age_group,))
        
    def get_players_by_type(self, player_type):
        """Get players of a specific type"""
        query = """
        SELECT 
            p.player_id,
            p.full_name,
            ag.group_name AS age_group,
            p.birth_day || '/' || p.birth_month || '/' || p.birth_year AS birth_date,
            p.jersey_number
        FROM players p
        JOIN player_types pt ON p.type_code = pt.type_code
        JOIN age_groups ag ON p.primary_age_group_id = ag.group_id
        WHERE pt.type_name = ?
        ORDER BY ag.group_name, p.full_name
        """
        return self.execute_query(query, (player_type,))
        
    def search_players(self, search_term):
        """Search for players by name"""
        query = """
        SELECT 
            p.player_id,
            p.full_name,
            pt.type_name AS player_type,
            ag.group_name AS age_group,
            p.birth_day || '/' || p.birth_month || '/' || p.birth_year AS birth_date,
            p.jersey_number
        FROM players p
        JOIN player_types pt ON p.type_code = pt.type_code
        JOIN age_groups ag ON p.primary_age_group_id = ag.group_id
        WHERE p.full_name LIKE ?
        ORDER BY p.full_name
        """
        return self.execute_query(query, (f"%{search_term}%",))
        
    def add_player(self, full_name, type_code, age_group, birth_day, birth_month, birth_year, jersey_number):
        """Add a new player"""
        # Get age group ID
        age_group_query = "SELECT group_id FROM age_groups WHERE group_name = ?"
        age_group_result = self.execute_query(age_group_query, (age_group,))
        
        if not age_group_result:
            print(f"Age group '{age_group}' not found.")
            return False
            
        age_group_id = age_group_result[0]['group_id']
        
        # Insert player
        query = """
        INSERT INTO players (
            full_name, type_code, primary_age_group_id,
            birth_day, birth_month, birth_year, jersey_number
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        params = (full_name, type_code, age_group_id, birth_day, birth_month, birth_year, jersey_number)
        result = self.execute_query(query, params)
        
        if result:
            # Update statistics
            self.update_statistics(age_group_id)
            return True
        return False
        
    def update_player(self, player_id, **kwargs):
        """Update player information"""
        allowed_fields = {
            'full_name': 'full_name', 
            'type_code': 'type_code',
            'primary_age_group_id': 'primary_age_group_id',
            'secondary_age_group_id': 'secondary_age_group_id',
            'birth_day': 'birth_day',
            'birth_month': 'birth_month',
            'birth_year': 'birth_year',
            'jersey_number': 'jersey_number',
            'league_team_id': 'league_team_id',
            'veo_member': 'veo_member',
            'photos': 'photos',
            'idp_meeting_sep': 'idp_meeting_sep',
            'idp_meeting_apr': 'idp_meeting_apr',
            'chat': 'chat',
            'files': 'files'
        }
        
        # Check if player exists
        check_query = "SELECT player_id, primary_age_group_id FROM players WHERE player_id = ?"
        player = self.execute_query(check_query, (player_id,))
        
        if not player:
            print(f"Player with ID {player_id} not found.")
            return False
            
        old_age_group_id = player[0]['primary_age_group_id']
        new_age_group_id = kwargs.get('primary_age_group_id', old_age_group_id)
        
        # Build update query
        set_clauses = []
        params = []
        
        for key, value in kwargs.items():
            if key in allowed_fields:
                set_clauses.append(f"{allowed_fields[key]} = ?")
                params.append(value)
                
        if not set_clauses:
            print("No valid fields to update.")
            return False
            
        query = f"UPDATE players SET {', '.join(set_clauses)} WHERE player_id = ?"
        params.append(player_id)
        
        result = self.execute_query(query, params)
        
        if result:
            # Update statistics if age group changed
            if old_age_group_id != new_age_group_id:
                self.update_statistics(old_age_group_id)
                self.update_statistics(new_age_group_id)
            return True
        return False
        
    def delete_player(self, player_id):
        """Delete a player"""
        # Check if player exists and get age group
        check_query = "SELECT player_id, primary_age_group_id FROM players WHERE player_id = ?"
        player = self.execute_query(check_query, (player_id,))
        
        if not player:
            print(f"Player with ID {player_id} not found.")
            return False
            
        age_group_id = player[0]['primary_age_group_id']
        
        # Delete player
        query = "DELETE FROM players WHERE player_id = ?"
        result = self.execute_query(query, (player_id,))
        
        if result:
            # Update statistics
            self.update_statistics(age_group_id)
            return True
        return False
        
    # Age Group Management
    def get_all_age_groups(self):
        """Get all age groups"""
        query = "SELECT group_id, group_name FROM age_groups ORDER BY group_name"
        return self.execute_query(query)
        
    def add_age_group(self, group_name, budget=0):
        """Add a new age group"""
        # Insert age group
        query = "INSERT INTO age_groups (group_name) VALUES (?)"
        result = self.execute_query(query, (group_name,))
        
        if result:
            # Get the new age group ID
            id_query = "SELECT group_id FROM age_groups WHERE group_name = ?"
            id_result = self.execute_query(id_query, (group_name,))
            
            if id_result:
                age_group_id = id_result[0]['group_id']
                
                # Add statistics entry
                stats_query = """
                INSERT INTO academy_statistics (
                    age_group_id, total, budget, net, 
                    ft_players, pt_players, sc_players, trial_players
                ) VALUES (?, 0, ?, ?, 0, 0, 0, 0)
                """
                self.execute_query(stats_query, (age_group_id, budget, budget))
                return True
        return False
        
    def update_age_group(self, group_id, group_name=None, budget=None):
        """Update an age group"""
        if group_name:
            query = "UPDATE age_groups SET group_name = ? WHERE group_id = ?"
            self.execute_query(query, (group_name, group_id))
            
        if budget is not None:
            # Update budget and recalculate net
            query = """
            UPDATE academy_statistics 
            SET budget = ?, net = ? - total
            WHERE age_group_id = ?
            """
            self.execute_query(query, (budget, budget, group_id))
            
        return True
        
    def delete_age_group(self, group_id):
        """Delete an age group (only if no players are assigned to it)"""
        # Check if players are assigned
        check_query = """
        SELECT COUNT(*) as player_count 
        FROM players 
        WHERE primary_age_group_id = ? OR secondary_age_group_id = ?
        """
        result = self.execute_query(check_query, (group_id, group_id))
        
        if result and result[0]['player_count'] > 0:
            print(f"Cannot delete age group: {result[0]['player_count']} players are assigned to it.")
            return False
            
        # Delete statistics first (foreign key constraint)
        self.execute_query("DELETE FROM academy_statistics WHERE age_group_id = ?", (group_id,))
        
        # Delete age group
        query = "DELETE FROM age_groups WHERE group_id = ?"
        return self.execute_query(query, (group_id,))
        
    # Statistics Management
    def get_academy_statistics(self):
        """Get academy statistics"""
        query = """
        SELECT 
            ag.group_name AS age_group,
            s.total AS actual_players,
            s.budget AS budgeted_players,
            s.net AS difference,
            s.ft_players AS full_time,
            s.pt_players AS part_time,
            s.sc_players AS scholarship,
            s.trial_players AS trial
        FROM academy_statistics s
        JOIN age_groups ag ON s.age_group_id = ag.group_id
        ORDER BY ag.group_name
        """
        return self.execute_query(query)
        
    def update_statistics(self, age_group_id):
        """Update statistics for an age group"""
        query = """
        UPDATE academy_statistics
        SET 
            total = (SELECT COUNT(*) FROM players p WHERE p.primary_age_group_id = ?),
            ft_players = (SELECT COUNT(*) FROM players p WHERE p.primary_age_group_id = ? AND p.type_code = 'FT'),
            pt_players = (SELECT COUNT(*) FROM players p WHERE p.primary_age_group_id = ? AND p.type_code = 'PT'),
            sc_players = (SELECT COUNT(*) FROM players p WHERE p.primary_age_group_id = ? AND p.type_code = 'SC'),
            trial_players = (SELECT COUNT(*) FROM players p WHERE p.primary_age_group_id = ? AND p.type_code = 'T'),
            net = budget - (SELECT COUNT(*) FROM players p WHERE p.primary_age_group_id = ?)
        WHERE age_group_id = ?
        """
        params = (age_group_id,) * 7
        return self.execute_query(query, params)
        
    def update_all_statistics(self):
        """Update statistics for all age groups"""
        age_groups = self.get_all_age_groups()
        for age_group in age_groups:
            self.update_statistics(age_group['group_id'])
        return True
        
    # Player Type Management
    def get_all_player_types(self):
        """Get all player types"""
        query = "SELECT type_code, type_name FROM player_types ORDER BY type_name"
        return self.execute_query(query)
        
    # League Team Management
    def get_all_league_teams(self):
        """Get all league teams"""
        query = "SELECT team_id, team_name FROM league_teams ORDER BY team_name"
        return self.execute_query(query)
        
    def add_league_team(self, team_name):
        """Add a new league team"""
        query = "INSERT INTO league_teams (team_name) VALUES (?)"
        return self.execute_query(query, (team_name,))
        
    def update_league_team(self, team_id, team_name):
        """Update a league team"""
        query = "UPDATE league_teams SET team_name = ? WHERE team_id = ?"
        return self.execute_query(query, (team_name, team_id))
        
    def delete_league_team(self, team_id):
        """Delete a league team (only if no players are assigned to it)"""
        # Check if players are assigned
        check_query = "SELECT COUNT(*) as player_count FROM players WHERE league_team_id = ?"
        result = self.execute_query(check_query, (team_id,))
        
        if result and result[0]['player_count'] > 0:
            print(f"Cannot delete team: {result[0]['player_count']} players are assigned to it.")
            return False
            
        # Delete team
        query = "DELETE FROM league_teams WHERE team_id = ?"
        return self.execute_query(query, (team_id,))
        
    # Reports
    def get_players_with_birthdays_this_month(self):
        """Get players with birthdays in the current month"""
        current_month = datetime.now().month
        query = """
        SELECT 
            p.full_name,
            ag.group_name AS age_group,
            p.birth_day || '/' || p.birth_month || '/' || p.birth_year AS birth_date,
            p.jersey_number
        FROM players p
        JOIN age_groups ag ON p.primary_age_group_id = ag.group_id
        WHERE p.birth_month = ?
        ORDER BY p.birth_day
        """
        return self.execute_query(query, (current_month,))
        
    def get_players_with_idp_meetings(self, month='sep'):
        """Get players with IDP meetings"""
        field = 'idp_meeting_sep' if month.lower() == 'sep' else 'idp_meeting_apr'
        query = f"""
        SELECT 
            p.full_name,
            ag.group_name AS age_group,
            p.jersey_number
        FROM players p
        JOIN age_groups ag ON p.primary_age_group_id = ag.group_id
        WHERE p.{field} = 1
        ORDER BY ag.group_name, p.full_name
        """
        return self.execute_query(query)
        
    def get_players_with_secondary_age_group(self):
        """Get players with secondary age group assignments"""
        query = """
        SELECT 
            p.full_name,
            ag1.group_name AS primary_age_group,
            ag2.group_name AS secondary_age_group,
            p.jersey_number
        FROM players p
        JOIN age_groups ag1 ON p.primary_age_group_id = ag1.group_id
        JOIN age_groups ag2 ON p.secondary_age_group_id = ag2.group_id
        ORDER BY ag1.group_name, p.full_name
        """
        return self.execute_query(query)


# Command-line interface for the Football Academy Manager
def display_menu():
    print("\n===== Football Academy Database Manager =====")
    print("1. View all players")
    print("2. Search for players")
    print("3. View players by age group")
    print("4. View players by type")
    print("5. Add a new player")
    print("6. Update player information")
    print("7. Delete a player")
    print("8. View academy statistics")
    print("9. View players with birthdays this month")
    print("10. View players with IDP meetings")
    print("11. View players with secondary age group assignments")
    print("12. Manage age groups")
    print("13. Manage league teams")
    print("0. Exit")
    print("===========================================")
    
def display_age_group_menu():
    print("\n===== Age Group Management =====")
    print("1. View all age groups")
    print("2. Add a new age group")
    print("3. Update an age group")
    print("4. Delete an age group")
    print("0. Back to main menu")
    print("==============================")
    
def display_league_team_menu():
    print("\n===== League Team Management =====")
    print("1. View all league teams")
    print("2. Add a new league team")
    print("3. Update a league team")
    print("4. Delete a league team")
    print("0. Back to main menu")
    print("================================")
    
def display_results(results, headers=None):
    if not results:
        print("No results found.")
        return
        
    if not headers and isinstance(results[0], sqlite3.Row):
        headers = results[0].keys()
        
    if headers:
        # Print headers
        header_str = " | ".join(str(h) for h in headers)
        print(header_str)
        print("-" * len(header_str))
        
    # Print rows
    for row in results:
        if isinstance(row, sqlite3.Row):
            print(" | ".join(str(row[h]) for h in headers))
        else:
            print(" | ".join(str(r) for r in row))
            
def get_input(prompt, required=True):
    while True:
        value = input(prompt).strip()
        if value or not required:
            return value
        print("This field is required.")
        
def get_int_input(prompt, required=True, min_val=None, max_val=None):
    while True:
        value = input(prompt).strip()
        if not value and not required:
            return None
            
        try:
            int_value = int(value)
            if (min_val is None or int_value >= min_val) and (max_val is None or int_value <= max_val):
                return int_value
            else:
                if min_val is not None and max_val is not None:
                    print(f"Please enter a value between {min_val} and {max_val}.")
                elif min_val is not None:
                    print(f"Please enter a value greater than or equal to {min_val}.")
                else:
                    print(f"Please enter a value less than or equal to {max_val}.")
        except ValueError:
            print("Please enter a valid number.")
            
def get_bool_input(prompt):
    while True:
        value = input(f"{prompt} (y/n): ").strip().lower()
        if value in ('y', 'yes'):
            return 1
        elif value in ('n', 'no'):
            return 0
        print("Please enter 'y' or 'n'.")
        
def select_from_list(items, id_field, name_field, prompt):
    if not items:
        print("No items available.")
        return None
        
    print(f"\n{prompt}")
    for i, item in enumerate(items):
        print(f"{i+1}. {item[name_field]}")
        
    while True:
        try:
            choice = int(input("\nEnter your choice (0 to cancel): "))
            if choice == 0:
                return None
            elif 1 <= choice <= len(items):
                return items[choice-1][id_field]
            else:
                print(f"Please enter a number between 1 and {len(items)}.")
        except ValueError:
            print("Please enter a valid number.")
            
def main():
    manager = FootballAcademyManager()
    
    if not manager.connect():
        print("Failed to connect to the database. Make sure the database file exists.")
        print("Run create_football_academy_db.py first to create the database.")
        return
        
    while True:
        display_menu()
        choice = get_input("Enter your choice: ")
        
        if choice == '0':
            break
            
        elif choice == '1':  # View all players
            results = manager.get_all_players()
            print("\n=== All Players ===")
            display_results(results)
            
        elif choice == '2':  # Search for players
            search_term = get_input("Enter player name to search: ")
            results = manager.search_players(search_term)
            print(f"\n=== Search Results for '{search_term}' ===")
            display_results(results)
            
        elif choice == '3':  # View players by age group
            age_groups = manager.get_all_age_groups()
            age_group_id = select_from_list(age_groups, 'group_name', 'group_name', "Select an age group:")
            
            if age_group_id:
                results = manager.get_players_by_age_group(age_group_id)
                print(f"\n=== Players in {age_group_id} ===")
                display_results(results)
                
        elif choice == '4':  # View players by type
            player_types = manager.get_all_player_types()
            player_type = select_from_list(player_types, 'type_name', 'type_name', "Select a player type:")
            
            if player_type:
                results = manager.get_players_by_type(player_type)
                print(f"\n=== {player_type} Players ===")
                display_results(results)
                
        elif choice == '5':  # Add a new player
            print("\n=== Add New Player ===")
            full_name = get_input("Enter player name: ")
            
            # Select player type
            player_types = manager.get_all_player_types()
            type_code = select_from_list(player_types, 'type_code', 'type_name', "Select player type:")
            if not type_code:
                continue
                
            # Select age group
            age_groups = manager.get_all_age_groups()
            age_group = select_from_list(age_groups, 'group_name', 'group_name', "Select age group:")
            if not age_group:
                continue
                
            # Get birth date
            birth_day = get_int_input("Enter birth day (1-31): ", min_val=1, max_val=31)
            birth_month = get_int_input("Enter birth month (1-12): ", min_val=1, max_val=12)
            birth_year = get_int_input("Enter birth year (e.g., 2010): ", min_val=2000, max_val=2020)
            
            # Get jersey number
            jersey_number = get_input("Enter jersey number: ")
            
            if manager.add_player(full_name, type_code, age_group, birth_day, birth_month, birth_year, jersey_number):
                print(f"Player '{full_name}' added successfully.")
            else:
                print("Failed to add player.")
                
        elif choice == '6':  # Update player information
            search_term = get_input("Enter player name to update: ")
            players = manager.search_players(search_term)
            
            if not players:
                print(f"No players found matching '{search_term}'.")
                continue
                
            player_id = select_from_list(players, 'player_id', 'full_name', "Select player to update:")
            if not player_id:
                continue
                
            print("\n=== Update Player Information ===")
            print("Leave fields blank to keep current values.")
            
            updates = {}
            
            # Basic information
            full_name = get_input("Enter new name (or leave blank): ", required=False)
            if full_name:
                updates['full_name'] = full_name
                
            # Player type
            player_types = manager.get_all_player_types()
            type_code = select_from_list(player_types, 'type_code', 'type_name', "Select new player type (or cancel to keep current):")
            if type_code:
                updates['type_code'] = type_code
                
            # Age group
            age_groups = manager.get_all_age_groups()
            age_group_id = select_from_list(age_groups, 'group_id', 'group_name', "Select new age group (or cancel to keep current):")
            if age_group_id:
                updates['primary_age_group_id'] = age_group_id
                
            # Secondary age group
            secondary_age_group_id = select_from_list(age_groups, 'group_id', 'group_name', "Select secondary age group (or cancel for none):")
            if secondary_age_group_id is not None:  # Could be 0 which is falsy
                updates['secondary_age_group_id'] = secondary_age_group_id
                
            # Jersey number
            jersey_number = get_input("Enter new jersey number (or leave blank): ", required=False)
            if jersey_number:
                updates['jersey_number'] = jersey_number
                
            # Status flags
            update_flags = get_bool_input("Update status flags (VEO, photos, etc.)?")
            if update_flags:
                updates['veo_member'] = get_bool_input("VEO member?")
                updates['photos'] = get_bool_input("Has photos?")
                updates['idp_meeting_sep'] = get_bool_input("Has September IDP meeting?")
                updates['idp_meeting_apr'] = get_bool_input("Has April IDP meeting?")
                updates['chat'] = get_bool_input("Has chat access?")
                updates['files'] = get_bool_input("Has files?")
                
            if updates:
                if manager.update_player(player_id, **updates):
                    print("Player updated successfully.")
                else:
                    print("Failed to update player.")
            else:
                print("No changes made.")
                
        elif choice == '7':  # Delete a player
            search_term = get_input("Enter player name to delete: ")
            players = manager.search_players(search_term)
            
            if not players:
                print(f"No players found matching '{search_term}'.")
                continue
                
            player_id = select_from_list(players, 'player_id', 'full_name', "Select player to delete:")
            if not player_id:
                continue
                
            confirm = get_bool_input(f"Are you sure you want to delete this player?")
            if confirm and manager.delete_player(player_id):
                print("Player deleted successfully.")
            else:
                print("Player deletion cancelled or failed.")
                
        elif choice == '8':  # View academy statistics
            results = manager.get_academy_statistics()
            print("\n=== Academy Statistics ===")
            display_results(results)
            
        elif choice == '9':  # View players with birthdays this month
            results = manager.get_players_with_birthdays_this_month()
            current_month = datetime.now().strftime("%B")
            print(f"\n=== Players with Birthdays in {current_month} ===")
            display_results(results)
            
        elif choice == '10':  # View players with IDP meetings
            month = get_input("Enter month (sep/apr): ").lower()
            if month not in ('sep', 'apr'):
                print("Invalid month. Please enter 'sep' or 'apr'.")
                continue
                
            results = manager.get_players_with_idp_meetings(month)
            month_name = "September" if month == 'sep' else "April"
            print(f"\n=== Players with IDP Meetings in {month_name} ===")
            display_results(results)
            
        elif choice == '11':  # View players with secondary age group assignments
            results = manager.get_players_with_secondary_age_group()
            print("\n=== Players with Secondary Age Group Assignments ===")
            display_results(results)
            
        elif choice == '12':  # Manage age groups
            while True:
                display_age_group_menu()
                age_choice = get_input("Enter your choice: ")
                
                if age_choice == '0':
                    break
                    
                elif age_choice == '1':  # View all age groups
                    results = manager.get_all_age_groups()
                    print("\n=== All Age Groups ===")
                    display_results(results)
                    
                elif age_choice == '2':  # Add a new age group
                    group_name = get_input("Enter new age group name (e.g., 'B 18 & 19'): ")
                    budget = get_int_input("Enter player budget for this age group: ", min_val=0)
                    
                    if manager.add_age_group(group_name, budget):
                        print(f"Age group '{group_name}' added successfully.")
                    else:
                        print("Failed to add age group.")
                        
                elif age_choice == '3':  # Update an age group
                    age_groups = manager.get_all_age_groups()
                    group_id = select_from_list(age_groups, 'group_id', 'group_name', "Select age group to update:")
                    
                    if group_id:
                        group_name = get_input("Enter new name (or leave blank): ", required=False)
                        budget = get_int_input("Enter new budget (or leave blank): ", required=False, min_val=0)
                        
                        if (group_name or budget is not None) and manager.update_age_group(group_id, group_name, budget):
                            print("Age group updated successfully.")
                        else:
                            print("No changes made or update failed.")
                            
                elif age_choice == '4':  # Delete an age group
                    age_groups = manager.get_all_age_groups()
                    group_id = select_from_list(age_groups, 'group_id', 'group_name', "Select age group to delete:")
                    
                    if group_id:
                        confirm = get_bool_input(f"Are you sure you want to delete this age group?")
                        if confirm and manager.delete_age_group(group_id):
                            print("Age group deleted successfully.")
                        else:
                            print("Age group deletion cancelled or failed.")
                            
        elif choice == '13':  # Manage league teams
            while True:
                display_league_team_menu()
                team_choice = get_input("Enter your choice: ")
                
                if team_choice == '0':
                    break
                    
                elif team_choice == '1':  # View all league teams
                    results = manager.get_all_league_teams()
                    print("\n=== All League Teams ===")
                    display_results(results)
                    
                elif team_choice == '2':  # Add a new league team
                    team_name = get_input("Enter new league team name: ")
                    
                    if manager.add_league_team(team_name):
                        print(f"League team '{team_name}' added successfully.")
                    else:
                        print("Failed to add league team.")
                        
                elif team_choice == '3':  # Update a league team
                    teams = manager.get_all_league_teams()
                    team_id = select_from_list(teams, 'team_id', 'team_name', "Select league team to update:")
                    
                    if team_id:
                        team_name = get_input("Enter new name: ")
                        
                        if manager.update_league_team(team_id, team_name):
                            print("League team updated successfully.")
                        else:
                            print("League team update failed.")
                            
                elif team_choice == '4':  # Delete a league team
                    teams = manager.get_all_league_teams()
                    team_id = select_from_list(teams, 'team_id', 'team_name', "Select league team to delete:")
                    
                    if team_id:
                        confirm = get_bool_input(f"Are you sure you want to delete this league team?")
                        if confirm and manager.delete_league_team(team_id):
                            print("League team deleted successfully.")
                        else:
                            print("League team deletion cancelled or failed.")
                            
    manager.close()
    print("Thank you for using the Football Academy Database Manager!")

if __name__ == "__main__":
    main()