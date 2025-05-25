"""
Platformer Game
"""

# type: ignore
import arcade

# Constants
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Platformer"

PLAYER_MOVEMENT_SPEED = 5
TILE_SCALING = 0.5
COIN_SCALING = 0.5

# Constant for gravity based 2D games
GRAVITY = 1
PLAYER_JUMP_SPEED = 20

class Player(arcade.Sprite):

    def update(self, delta_time: float = 1/60):
        """ Move the player """
        # Move player.
        # Remove these lines if physics engine is moving player.
        self.center_x += self.change_x
        self.center_y += self.change_y

        # Check for out-of-bounds
        if self.left < 0:
            self.left = 0
        elif self.right > WINDOW_WIDTH - 1:
            self.right = WINDOW_WIDTH - 1

        if self.bottom < 0:
            self.bottom = 0
        elif self.top > WINDOW_HEIGHT - 1:
            self.top = WINDOW_HEIGHT - 1

class GameView(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):

        # Call the parent class to set up the window
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)

        # Creates empty variables for sprites and sprites lists to be setup each time game starts
        self.player_texture = None

        self.player_sprite = None

        self.scene = None

        self.tile_map = None

        self.camera = None

        self.gui_camera = None

        self.score = 0

        self.score_text = None

        # Loading sounds inside __init__ because sound will not change on restart
        self.collect_coin_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")

        # Creates variables the current state of what key is pressed with the default being false
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

    def setup(self):
        """Set up the game here. Call this function to restart the game."""

        layer_options = {
            "Platforms": {
                "use_spatial_hash": True
            }
        }

        # Loads in map for game play
        self.tile_map = arcade.load_tilemap(":resources:tiled_maps/map2_level_1.json", scaling=TILE_SCALING, layer_options=layer_options)

        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # Loads in a texture to assign to player_texture using Arcades load_texture() method
        self.player_texture = arcade.load_texture(":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png")

        # Uses player_texture and assigns a player sprite using Arcades Sprite() method
        self.player_sprite = arcade.Sprite(self.player_texture)
        # Assigns player_sprite a coordinate on game window
        self.player_sprite.center_x = 64
        self.player_sprite.center_y = 128
        # Add player sprite to scene
        self.scene.add_sprite("Player", self.player_sprite)

        # Assigns player_list a sprite list using Arcades SpriteList() Method
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player_sprite)
       
        # The bottom code would be used for a top down experience
        # Uses Arcades built in simple engine and assigns to all sprite lists inside a physics_engine variable
        # self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite, self.wall_list)

        # Uses Arcades built in platformer physics engine and assigns to all sprite lists inside a physics_engine variable
        # Sets parameter gravity_constant to GRAVITY constant 
        # Passes wall_list as a walls parameter since arcade supports a walls and platforms parameter
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite, walls=self.scene["Platforms"], gravity_constant=GRAVITY)

        # Initializes the camera that moves with the move around the player
        self.camera = arcade.Camera2D()

        # Initializes the camera that stays stationary around the player
        self.gui_camera = arcade.Camera2D()
        # Resets score to zero
        self.score = 0

        # Displays "Score: ..." at the x and y coordinates using the Text() method from the arcade library
        self.score_text = arcade.Text(f"Score: {self.score}", x=(WINDOW_WIDTH // 2), y=WINDOW_HEIGHT - 70, anchor_x="center", font_size=12, color=arcade.color.WHITE)
        self.title_text = arcade.Text("Platformer Game", x=WINDOW_WIDTH // 2, y=WINDOW_HEIGHT - 40, anchor_x="center", font_size=24, color=arcade.color.WHITE)


        # Sets background color for game window using arcade.csscolor.color
        self.background_color = arcade.csscolor.CORNFLOWER_BLUE

    def on_draw(self):
        """Render the screen."""

        # Clears the whole screen to whatever the background color is set to
        self.clear()

        # Activates the cameras before drawing
        self.camera.use()

        # Draws scene and all its layers
        self.scene.draw()

        self.gui_camera.use()
        # Draws text on screen
        self.score_text.draw()
        self.title_text.draw()

        #self.player_list.draw_hit_boxes()
        #self.wall_list.draw_hit_boxes()

    def on_update(self, delta_time):
        """Movement and Game Logic"""

        # Updates at a default of 60 FPS with changes in regards to our simple physics engine
        self.physics_engine.update()

        # Checks for collision betweeen player sprite and coin sprites during each update
        coin_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.scene["Coins"])

        # If collision does happen then the coin sprite will be removed from the sprite list
        for coin in coin_hit_list:  
            coin.remove_from_sprite_lists()
            # Play coin collect sound
            arcade.play_sound(self.collect_coin_sound)
            # Updates the score to plus one
            self.score += 1
            # Updates the text
            self.score_text.text = f"Score: {self.score}"

        # Updates the cameras postion to center around the player sprite
        self.camera.position = self.player_sprite.position

    def update_player_speed(self):

        # Calculate speed based on the keys pressed
        self.player_sprite.change_x = 0
        self.player_sprite.change_y = 0

        # Goes based off the updating of defined variables in th __init__ method
        # If up_pressed is TRUE AND down_pressed is FALSE, the y coordinate increases by PLAYER_MOVEMENT_SPEED(5)
        if self.up_pressed and not self.down_pressed:
            self.player_sprite.change_y = PLAYER_JUMP_SPEED
        # If down_pressed is TRUE AND up_pressed is FALSE, the y coordinate decreased by PLAYER_MOVEMENT_SPEED(5)
        elif self.down_pressed and not self.up_pressed:
            self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED
        # If left_pressed is TRUE AND right_pressed is FALSE, the x coordinate decreases by PLAYER_MOVEMENT_SPEED(5)
        if self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        # If right_pressed is TRUE AND left_pressed is FALSE, the x coordinate increases by PLAYER_MOVEMENT_SPEED(5)
        elif self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""

        if key == arcade.key.ESCAPE:
            self.setup()

        # If key pressed is equal to UP arrow key, update up_pressed variable in __init__ to TRUE
        if key == arcade.key.UP:
            # Checks if player_sprite is touching ground or not
            if self.physics_engine.can_jump():
                self.up_pressed = True
                # Calls update_player_speed() in parent superclass
                self.update_player_speed()
                # Plays jump sound
                arcade.play_sound(self.jump_sound)
        # If key pressed is equal to DOWN arrow key, update down_pressed variable in __init__ to TRUE
        elif key == arcade.key.DOWN:
            self.down_pressed = True
            # Calls update_player_speed() in parent superclass
            self.update_player_speed()
        # If key pressed is equal to LEFT arrow key, update left_pressed variable in __init__ to TRUE
        elif key == arcade.key.LEFT:
            # Calls update_player_speed() in parent superclass
            self.left_pressed = True
            self.update_player_speed()
        # If key pressed is equal to RIGHT arrow key, update right_pressed variable in __init__ to TRUE
        elif key == arcade.key.RIGHT:
            # Calls update_player_speed() in parent superclass
            self.right_pressed = True
            self.update_player_speed()

    def on_key_release(self, key, modifiers):
        """Called whenever a key is released."""
        """Changes are set to zero since change will happen on press and not on release"""

        # After releasing UP key set the up_pressed variable in the __init__ method to FALSE
        if key == arcade.key.UP:
            self.up_pressed = False
            self.update_player_speed()
        # After releasing DOWN key set the up_pressed variable in the __init__ method to FALSE
        elif key == arcade.key.DOWN:
            self.down_pressed = False
            self.update_player_speed()
        # After releasing LEFT key set the up_pressed variable in the __init__ method to FALSE
        elif key == arcade.key.LEFT:
            self.left_pressed = False
            self.update_player_speed()
        # After releasing RIGHT key set the up_pressed variable in the __init__ method to FALSE
        elif key == arcade.key.RIGHT:
            self.right_pressed = False
            self.update_player_speed()


def main():
    """Main function"""
    window = GameView()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()