CREATE TABLE IF NOT EXISTS games (
    id INT AUTO_INCREMENT PRIMARY KEY,
    started_at DATETIME NOT NULL,
    ended_at DATETIME,
    winner_name VARCHAR(255),
    total_rounds INT DEFAULT 0,
    player_count INT NOT NULL
);

CREATE TABLE IF NOT EXISTS players (
    id INT AUTO_INCREMENT PRIMARY KEY,
    game_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    final_coins INT DEFAULT 0,
    final_rank INT DEFAULT 0,
    FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS rounds (
    id INT AUTO_INCREMENT PRIMARY KEY,
    game_id INT NOT NULL,
    round_number INT NOT NULL,
    camel_moved VARCHAR(50),
    spaces_moved INT,
    leg_ended BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS bets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    game_id INT NOT NULL,
    player_id INT NOT NULL,
    round_id INT,
    bet_type ENUM('leg', 'race_winner', 'race_loser') NOT NULL,
    camel_color VARCHAR(50) NOT NULL,
    coins_won INT DEFAULT 0,
    FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE,
    FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE,
    FOREIGN KEY (round_id) REFERENCES rounds(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS player_statistics (
    player_name VARCHAR(255) UNIQUE PRIMARY KEY,
    games_played INT DEFAULT 0,
    games_won INT DEFAULT 0,
    total_coins_earned INT DEFAULT 0,
    best_score INT DEFAULT 0
);
