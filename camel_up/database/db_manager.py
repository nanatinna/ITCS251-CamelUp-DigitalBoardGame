"""
db_manager.py - Manages MySQL database connections and queries.
"""
import mysql.connector
from mysql.connector import pooling, Error
from .models import GameRecord, RoundRecord, BetRecord, PlayerStats
from config.db_config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
from utils.logger import get_logger
from contextlib import contextmanager
from typing import List, Optional

logger = get_logger(__name__)

class DBManager:
    def __init__(self):
        self.pool = None
        self.init_db()

    def init_db(self):
        """Initializes the database schema if it doesn't exist, and creates the connection pool."""
        try:
            # First, connect without a specific database to create it if needed
            conn = mysql.connector.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD
            )
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME};")
            conn.commit()
            cursor.close()
            conn.close()

            # Now create the connection pool
            self.pool = pooling.MySQLConnectionPool(
                pool_name="camel_up_pool",
                pool_size=5,
                pool_reset_session=True,
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )

            # Execute schema.sql to ensure tables exist
            with self.get_connection() as c:
                with c.cursor() as cur:
                    with open("database/schema.sql", "r") as f:
                        sql_script = f.read()
                        statements = [s.strip() for s in sql_script.split(';') if s.strip()]
                        for statement in statements:
                            cur.execute(statement)
                c.commit()
            logger.info("Database initialized successfully.")

        except Error as e:
            logger.error(f"Error initializing database: {e}")

    @contextmanager
    def get_connection(self):
        """Context manager for acquiring and releasing a connection from the pool."""
        if not self.pool:
            raise Exception("Connection pool not initialized.")
        conn = self.pool.get_connection()
        try:
            yield conn
        finally:
            conn.close()

    def save_game_start(self, started_at: str, player_count: int, players: List[str]) -> int:
        """Saves a new game and its initial players. Returns the game ID."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                query = "INSERT INTO games (started_at, player_count) VALUES (%s, %s)"
                cursor.execute(query, (started_at, player_count))
                game_id = cursor.lastrowid
                
                for name in players:
                    p_query = "INSERT INTO players (game_id, name) VALUES (%s, %s)"
                    cursor.execute(p_query, (game_id, name))
                    
                    # Ensure they exist in stats table
                    s_query = "INSERT IGNORE INTO player_statistics (player_name) VALUES (%s)"
                    cursor.execute(s_query, (name,))
                
                conn.commit()
                return game_id
        except Error as e:
            logger.error(f"Error saving game start: {e}")
            return -1

    def update_game_end(self, game_id: int, ended_at: str, winner_name: str, total_rounds: int, player_results: List[dict]):
        """Updates game with end result and updates player stats."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                g_query = "UPDATE games SET ended_at=%s, winner_name=%s, total_rounds=%s WHERE id=%s"
                cursor.execute(g_query, (ended_at, winner_name, total_rounds, game_id))
                
                for res in player_results:
                    name = res['name']
                    coins = res['coins']
                    rank = res['rank']
                    
                    p_query = "UPDATE players SET final_coins=%s, final_rank=%s WHERE game_id=%s AND name=%s"
                    cursor.execute(p_query, (coins, rank, game_id, name))
                    
                    won = 1 if rank == 1 else 0
                    
                    s_query = """
                        UPDATE player_statistics 
                        SET games_played = games_played + 1,
                            games_won = games_won + %s,
                            total_coins_earned = total_coins_earned + %s,
                            best_score = GREATEST(best_score, %s)
                        WHERE player_name = %s
                    """
                    cursor.execute(s_query, (won, coins, coins, name))
                    
                conn.commit()
        except Error as e:
            logger.error(f"Error updating game end: {e}")

    def save_round(self, round_record: RoundRecord) -> int:
        """Saves round data. Returns the round ID."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                query = """INSERT INTO rounds (game_id, round_number, camel_moved, spaces_moved, leg_ended) 
                           VALUES (%s, %s, %s, %s, %s)"""
                cursor.execute(query, (
                    round_record.game_id, 
                    round_record.round_number, 
                    round_record.camel_moved, 
                    round_record.spaces_moved, 
                    round_record.leg_ended
                ))
                conn.commit()
                return cursor.lastrowid
        except Error as e:
            logger.error(f"Error saving round: {e}")
            return -1

    def save_bet(self, game_id: int, player_name: str, bet_record: BetRecord):
        """Saves a bet."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT id FROM players WHERE game_id=%s AND name=%s", (game_id, player_name))
                res = cursor.fetchone()
                if not res:
                    return
                player_id = res[0]
                
                query = """INSERT INTO bets (game_id, player_id, round_id, bet_type, camel_color, coins_won)
                           VALUES (%s, %s, %s, %s, %s, %s)"""
                cursor.execute(query, (
                    game_id,
                    player_id,
                    bet_record.round_id,
                    bet_record.bet_type,
                    bet_record.camel_color,
                    bet_record.coins_won
                ))
                conn.commit()
        except Error as e:
            logger.error(f"Error saving bet: {e}")

    def get_history(self, limit: int = 10) -> List[dict]:
        """Returns a list of recent games."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                query = "SELECT * FROM games ORDER BY id DESC LIMIT %s"
                cursor.execute(query, (limit,))
                return cursor.fetchall()
        except Error as e:
            logger.error(f"Error fetching history: {e}")
            return []

    def get_player_stats(self, name: str) -> Optional[PlayerStats]:
        """Returns player statistics."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                query = "SELECT * FROM player_statistics WHERE player_name = %s"
                cursor.execute(query, (name,))
                res = cursor.fetchone()
                if res:
                    return PlayerStats(
                        name=res['player_name'],
                        games_played=res['games_played'],
                        games_won=res['games_won'],
                        total_coins_earned=res['total_coins_earned'],
                        best_score=res['best_score']
                    )
                return None
        except Error as e:
            logger.error(f"Error fetching player stats: {e}")
            return None
