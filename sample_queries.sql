-- Football Academy Database Sample Queries

-- 1. Get all players with their basic information
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
ORDER BY ag.group_name, p.full_name;

-- 2. Count players by age group
SELECT 
    ag.group_name AS age_group,
    COUNT(*) AS player_count
FROM players p
JOIN age_groups ag ON p.primary_age_group_id = ag.group_id
GROUP BY ag.group_name
ORDER BY ag.group_name;

-- 3. Count players by type
SELECT 
    pt.type_name AS player_type,
    COUNT(*) AS player_count
FROM players p
JOIN player_types pt ON p.type_code = pt.type_code
GROUP BY pt.type_name
ORDER BY player_count DESC;

-- 4. Find players with IDP meetings in September
SELECT 
    p.full_name,
    ag.group_name AS age_group,
    p.jersey_number
FROM players p
JOIN age_groups ag ON p.primary_age_group_id = ag.group_id
WHERE p.idp_meeting_sep = 1
ORDER BY ag.group_name, p.full_name;

-- 5. Find players with IDP meetings in April
SELECT 
    p.full_name,
    ag.group_name AS age_group,
    p.jersey_number
FROM players p
JOIN age_groups ag ON p.primary_age_group_id = ag.group_id
WHERE p.idp_meeting_apr = 1
ORDER BY ag.group_name, p.full_name;

-- 6. Find players who are VEO members
SELECT 
    p.full_name,
    ag.group_name AS age_group,
    p.jersey_number
FROM players p
JOIN age_groups ag ON p.primary_age_group_id = ag.group_id
WHERE p.veo_member = 1
ORDER BY ag.group_name, p.full_name;

-- 7. Find players with photos
SELECT 
    p.full_name,
    ag.group_name AS age_group,
    p.jersey_number
FROM players p
JOIN age_groups ag ON p.primary_age_group_id = ag.group_id
WHERE p.photos = 1
ORDER BY ag.group_name, p.full_name;

-- 8. Find players with chat access
SELECT 
    p.full_name,
    ag.group_name AS age_group,
    p.jersey_number
FROM players p
JOIN age_groups ag ON p.primary_age_group_id = ag.group_id
WHERE p.chat = 1
ORDER BY ag.group_name, p.full_name;

-- 9. Find players with files
SELECT 
    p.full_name,
    ag.group_name AS age_group,
    p.jersey_number
FROM players p
JOIN age_groups ag ON p.primary_age_group_id = ag.group_id
WHERE p.files = 1
ORDER BY ag.group_name, p.full_name;

-- 10. Get players in a specific age group (example: B 14 & 15)
SELECT 
    p.full_name,
    pt.type_name AS player_type,
    p.birth_day || '/' || p.birth_month || '/' || p.birth_year AS birth_date,
    p.jersey_number
FROM players p
JOIN player_types pt ON p.type_code = pt.type_code
JOIN age_groups ag ON p.primary_age_group_id = ag.group_id
WHERE ag.group_name = 'B 14 & 15'
ORDER BY p.full_name;

-- 11. Get players with secondary age group assignments
SELECT 
    p.full_name,
    ag1.group_name AS primary_age_group,
    ag2.group_name AS secondary_age_group,
    p.jersey_number
FROM players p
JOIN age_groups ag1 ON p.primary_age_group_id = ag1.group_id
JOIN age_groups ag2 ON p.secondary_age_group_id = ag2.group_id
ORDER BY ag1.group_name, p.full_name;

-- 12. Get players born in a specific year (example: 2012)
SELECT 
    p.full_name,
    ag.group_name AS age_group,
    p.birth_day || '/' || p.birth_month || '/' || p.birth_year AS birth_date,
    p.jersey_number
FROM players p
JOIN age_groups ag ON p.primary_age_group_id = ag.group_id
WHERE p.birth_year = 2012
ORDER BY p.birth_month, p.birth_day;

-- 13. Get players with birthdays in the current month
SELECT 
    p.full_name,
    ag.group_name AS age_group,
    p.birth_day || '/' || p.birth_month || '/' || p.birth_year AS birth_date,
    p.jersey_number
FROM players p
JOIN age_groups ag ON p.primary_age_group_id = ag.group_id
WHERE p.birth_month = strftime('%m', 'now')
ORDER BY p.birth_day;

-- 14. Compare actual vs. budget for each age group
SELECT 
    ag.group_name AS age_group,
    s.total AS actual_players,
    s.budget AS budgeted_players,
    s.net AS difference
FROM academy_statistics s
JOIN age_groups ag ON s.age_group_id = ag.group_id
ORDER BY ag.group_name;

-- 15. Get detailed player type breakdown by age group
SELECT 
    ag.group_name AS age_group,
    s.ft_players AS full_time,
    s.pt_players AS part_time,
    s.sc_players AS scholarship,
    s.trial_players AS trial,
    s.total AS total_players
FROM academy_statistics s
JOIN age_groups ag ON s.age_group_id = ag.group_id
ORDER BY ag.group_name;

-- 16. Add a new player
-- INSERT INTO players (
--     full_name, type_code, primary_age_group_id, secondary_age_group_id,
--     birth_day, birth_month, birth_year, jersey_number, league_team_id,
--     veo_member, photos, idp_meeting_sep, idp_meeting_apr, chat, files
-- ) VALUES (
--     'New Player Name', 'FT', 
--     (SELECT group_id FROM age_groups WHERE group_name = 'B 14 & 15'),
--     NULL, 15, 6, 2014, '42', NULL, 0, 0, 0, 0, 0, 0
-- );

-- 17. Update player information
-- UPDATE players
-- SET 
--     jersey_number = '99',
--     veo_member = 1,
--     photos = 1
-- WHERE full_name = 'Player Name';

-- 18. Delete a player
-- DELETE FROM players WHERE full_name = 'Player Name';

-- 19. Add a new age group
-- INSERT INTO age_groups (group_name) VALUES ('B 18 & 19');

-- 20. Update academy statistics after changes
-- UPDATE academy_statistics
-- SET 
--     total = (SELECT COUNT(*) FROM players p WHERE p.primary_age_group_id = academy_statistics.age_group_id),
--     ft_players = (SELECT COUNT(*) FROM players p WHERE p.primary_age_group_id = academy_statistics.age_group_id AND p.type_code = 'FT'),
--     pt_players = (SELECT COUNT(*) FROM players p WHERE p.primary_age_group_id = academy_statistics.age_group_id AND p.type_code = 'PT'),
--     sc_players = (SELECT COUNT(*) FROM players p WHERE p.primary_age_group_id = academy_statistics.age_group_id AND p.type_code = 'SC'),
--     trial_players = (SELECT COUNT(*) FROM players p WHERE p.primary_age_group_id = academy_statistics.age_group_id AND p.type_code = 'T'),
--     net = budget - (SELECT COUNT(*) FROM players p WHERE p.primary_age_group_id = academy_statistics.age_group_id)
-- WHERE age_group_id = (SELECT group_id FROM age_groups WHERE group_name = 'B 14 & 15');