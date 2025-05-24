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
        self.player_list = None

        self.wall_list = None

        # Creates variables the current state of what key is pressed with the default being false
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        self.camera = None

    def setup(self):
        """Set up the game here. Call this function to restart the game."""

        # Loads in a texture to assign to player_texture using Arcades load_texture() method
        self.player_texture = arcade.load_texture(":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png")

        # Uses player_texture and assigns a player sprite using Arcades Sprite() method
        self.player_sprite = arcade.Sprite(self.player_texture)
        # Assigns player_sprite a coordinate on game window
        self.player_sprite.center_x = 64
        self.player_sprite.center_y = 128

        # Assigns player_list a sprite list using Arcades SpriteList() Method
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player_sprite)
        # Assigns wall_list wall sprites using Arcades SpriteList() Method
        # Use spatial hash is used to detect collision on an object that is not likely to move
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)

        # Creates a wall sprite every 64 pixels between x = 0 and x = 1250 for width of screen
        # Results in a row of grass tiles across the bottom of the screen
        for x in range(0, 1250, 64):
            # Assigns a new sprite to wall variable using Arcades Sprite() method to be added to the wall_list
            wall = arcade.Sprite(":resources:images/tiles/grassMid.png", scale=TILE_SCALING)
            # Center of sprite on x-axis will be equal to 64x loop in for loop
            wall.center_x = x
            # Center of sprite on y axis will be equal to 32
            wall.center_y = 32
            # Adds each sprite created to the wall_list sprite list
            self.wall_list.append(wall)

        # Declares specific coordinates for sprites to be drawn onto
        # Results in a row of boxes across the screen at these coordinates
        coordinate_list = [[512, 96], [256, 96], [768, 96]]
        # Loops through each coordinate and draws sprites on those coordinates
        for coordinate in coordinate_list:
            # Assigns a new sprite to a wall variable to be added to the wall_list using the Arcade Sprite() method
            wall = arcade.Sprite(":resources:images/tiles/boxCrate_double.png", scale=TILE_SCALING)
            # Assigns the sprites position to the coordinate in the for loop
            wall.position = coordinate
            # Adds the new sprite to the wall_list
            self.wall_list.append(wall)

        # The bottom code would be used for a top down experience
        # Uses Arcades built in simple engine and assigns to all sprite lists inside a physics_engine variable
        # self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite, self.wall_list)

        # Uses Arcades built in platformer physics engine and assigns to all sprite lists inside a physics_engine variable
        # Sets parameter gravity_constant to GRAVITY constant 
        # Passes wall_list as a walls parameter since arcade supports a walls and platforms parameter
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite, walls=self.wall_list, gravity_constant=GRAVITY)

        # Initializes the camera and sets a viewport the size of the window
        self.camera = arcade.Camera2D()

        # Sets background color for game window using arcade.csscolor.color
        self.background_color = arcade.csscolor.CORNFLOWER_BLUE

    def on_draw(self):
        """Render the screen."""

        # Clears the whole screen to whatever the background color is set to
        self.clear()

        # Activates the camera before drawing
        self.camera.use()

        # Draws the player list sprites using Arcades draw() method
        self.player_list.draw()
        # Draws the wall list sprites using Arcades draw() method
        self.wall_list.draw()

        #self.player_list.draw_hit_boxes()
        #self.wall_list.draw_hit_boxes()

    def on_update(self, delta_time):
        """Movement and Game Logic"""

        # Updates at a default of 60 FPS with changes in regards to our simple physics engine
        self.physics_engine.update()

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