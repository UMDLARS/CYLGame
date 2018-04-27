# CYLGame pipeline

Steps in order:

- game.init_board
- for each bot in room players += game.create_new_player
- game.start_game
- Main Game Loop:
  - if playback: game.get_frame
  - for each player: player.run_turn
  - game.do_turn
- game.get_score

More detail for each step under their respective headings below



## Game.create_new_player

This method should create a new `Player` with the provided `prog`.

## Game.init_board

This method should get the game ready to be played. Note: at this point the players have been created.

Note: after this call the game should be able to correctly respond to `game.get_frame`.

## Game.start_game

This method should make sure that the game is ready to go. Make sure to update the bots vars here.

## Game.get_frame



## Game.do_turn

In this function the game should update the game state according to the players change in state.

## Player

The player should retain the state for the program being run.

## Player.run_turn

Runs the 

### Notes

The player will track the state.

The game needs to react to how the players' states have changed since last turn in `do_turn`