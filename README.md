##### 4.1.2.1 Bet Records

For each bet:
- bet_id
- bet_mode
- bet_amount
- total_win
- is_hit
- has_trigger_freegame
- round_count
- final_state
- round(s)_records

Each bet contains one or more rounds.
The objects contained within the bet_mode read their specific configurations.

##### 4.1.2.2 Round Records

For each round:
- round_id
- round_type
- round_win
- is_hit
- final_state
- roll(s)_records

Each round contains one or more rolls.
The objects contained within the round_type are Basic or Freegame

##### 4.1.2.3 Roll Records

For each roll:
- roll_id
- state_type
- pre_state
- post_state
- roll_win
- events
- reel_set_id
- multiplier_profile_id

