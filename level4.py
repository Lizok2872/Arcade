import arcade
import random
import math

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Кристаллические Приключения - Уровень 4"
CHARACTER_SCALING = 0.5
TILE_SCALING = 0.5
CRYSTAL_SCALING = 0.3
PLAYER_MOVEMENT_SPEED = 5
GRAVITY = 1
PLAYER_JUMP_SPEED = 20
SPIKE_SCALING = 0.5
SMALL_SPIKE_SCALING = 0.3


class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.uniform(2, 6)
        self.speed = random.uniform(2, 8)
        self.angle = random.uniform(0, 2 * math.pi)
        self.vx = math.cos(self.angle) * self.speed
        self.vy = math.sin(self.angle) * self.speed
        self.gravity = 0.3
        self.life = 1.0
        self.decay = random.uniform(0.02, 0.05)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy -= self.gravity
        self.life -= self.decay
        self.size = max(0, self.size * 0.95)

    def draw(self):
        if self.life > 0:
            alpha = int(255 * self.life)
            arcade.draw_circle_filled(
                self.x, self.y, self.size,
                (self.color[0], self.color[1], self.color[2], alpha)
            )


class CrystalExplosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.particles = []
        self.colors = [
            (100, 200, 255),
            (150, 220, 255),
            (200, 240, 255),
            (80, 180, 255),
        ]
        self.create_particles()

    def create_particles(self):
        num_particles = random.randint(15, 25)
        for _ in range(num_particles):
            color = random.choice(self.colors)
            particle = Particle(self.x, self.y, color)
            self.particles.append(particle)

    def update(self):
        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)

    def draw(self):
        for particle in self.particles:
            particle.draw()

    def is_finished(self):
        return len(self.particles) == 0


class Level4(arcade.View):
    def __init__(self):
        super().__init__()
        self.level_name = "Уровень 4"
        self.level = 4
        self.scene = None
        self.score = 0
        self.crystals_collected = 0
        self.total_crystals = 0
        self.player_lives = 5
        self.collect_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        self.hurt_sound = arcade.load_sound(":resources:sounds/hurt3.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump3.wav")
        self.explosions = []

        self.moving_platforms = []
        self.moving_enemies = []
        self.all_walls = arcade.SpriteList()

        try:
            self.background_music = arcade.load_sound(":resources:music/1918.mp3")
            self.music_player = None
        except:
            self.background_music = None

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def on_show(self):
        if self.background_music:
            self.music_player = self.background_music.play(volume=0.2, loop=True)

    def on_hide(self):
        if self.music_player and self.background_music:
            self.background_music.stop(self.music_player)

    def setup(self):
        self.world_camera = arcade.Camera2D()
        self.gui_camera = arcade.Camera2D()
        self.scene = arcade.Scene()
        self.scene.add_sprite_list("Player")
        self.scene.add_sprite_list("Walls", use_spatial_hash=True)
        self.scene.add_sprite_list("Crystals", use_spatial_hash=True)
        self.scene.add_sprite_list("Spikes", use_spatial_hash=True)
        self.scene.add_sprite_list("SmallSpikes", use_spatial_hash=True)
        self.scene.add_sprite_list("MovingPlatforms")
        self.scene.add_sprite_list("Enemies")

        self.player_sprite = arcade.Sprite(
            ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png",
            CHARACTER_SCALING
        )

        self.player_sprite.center_x = 64
        self.player_sprite.center_y = 128

        self.scene.add_sprite("Player", self.player_sprite)
        self.create_level()
        self.create_crystals()
        self.create_hazards()
        self.create_small_spikes_on_platforms()
        self.create_moving_platforms()
        self.create_enemies()

        self.all_walls = arcade.SpriteList()
        self.all_walls.extend(self.scene.get_sprite_list("Walls"))
        self.all_walls.extend(self.scene.get_sprite_list("MovingPlatforms"))

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            self.all_walls,
            GRAVITY
        )

    def create_level(self):
        wall_texture = ":resources:images/tiles/grassMid.png"

        platforms = [
            (0, 0, 25),
            (500, 120, 6),
            (1000, 180, 4),
            (1300, 300, 10),
            (2100, 200, 8),
            (2800, 400, 15),
        ]

        for x, y, width in platforms:
            for i in range(width):
                wall = arcade.Sprite(wall_texture, TILE_SCALING)
                wall.center_x = x + i * 64
                wall.center_y = y
                self.scene.add_sprite("Walls", wall)

    def create_crystals(self):
        crystal_texture = ":resources:images/items/gemBlue.png"

        crystal_positions = [
            (300, 150),
            (1100, 230),
            (1350, 370),
            (2150, 250),
            (2850, 450),
        ]

        self.total_crystals = len(crystal_positions)

        for x, y in crystal_positions:
            crystal = arcade.Sprite(crystal_texture, CRYSTAL_SCALING)
            crystal.center_x = x
            crystal.center_y = y
            self.scene.add_sprite("Crystals", crystal)

    def create_hazards(self):
        spike_texture = ":resources:images/tiles/spikes.png"

        spike_positions = [
            (200, 65), (232, 65),
            (700, 115), (732, 115), (764, 115), (796, 115),
            (850, 65), (882, 65),
            (1500, 65), (1532, 65), (1564, 65),
            (2600, 65), (2632, 65), (2664, 65),
        ]

        for x, y in spike_positions:
            spike = arcade.Sprite(spike_texture, SPIKE_SCALING)
            spike.center_x = x
            spike.center_y = y
            self.scene.add_sprite("Spikes", spike)

    def create_small_spikes_on_platforms(self):
        spike_texture = ":resources:images/tiles/spikes.png"

        spike_positions = [
            (530, 130),
            (1350, 310), (1382, 310),
            (2870, 430),
        ]

        for x, y in spike_positions:
            spike = arcade.Sprite(spike_texture, SMALL_SPIKE_SCALING)
            spike.center_x = x
            spike.center_y = y
            self.scene.add_sprite("SmallSpikes", spike)

    def create_moving_platforms(self):
        platform_texture = ":resources:images/tiles/stoneMid.png"

        platform1 = arcade.Sprite(platform_texture, TILE_SCALING)
        platform1.center_x = 1100
        platform1.center_y = 120
        platform1.change_y = 2.0
        platform1.boundary_top = 280
        platform1.boundary_bottom = 100
        self.scene.add_sprite("MovingPlatforms", platform1)
        self.moving_platforms.append(platform1)

        platform2 = arcade.Sprite(platform_texture, TILE_SCALING)
        platform2.center_x = 1700
        platform2.center_y = 340
        platform2.change_x = 1.8
        platform2.boundary_left = 1650
        platform2.boundary_right = 2000
        self.scene.add_sprite("MovingPlatforms", platform2)
        self.moving_platforms.append(platform2)

        platform3 = arcade.Sprite(platform_texture, TILE_SCALING)
        platform3.center_x = 2400
        platform3.center_y = 150
        platform3.change_x = 2.2
        platform3.change_y = 1.5
        platform3.boundary_left = 2350
        platform3.boundary_right = 2650
        platform3.boundary_top = 220
        platform3.boundary_bottom = 140
        self.scene.add_sprite("MovingPlatforms", platform3)
        self.moving_platforms.append(platform3)

        platform4 = arcade.Sprite(platform_texture, TILE_SCALING)
        platform4.center_x = 2700
        platform4.center_y = 200
        platform4.change_y = 2.5
        platform4.boundary_top = 380
        platform4.boundary_bottom = 180
        self.scene.add_sprite("MovingPlatforms", platform4)
        self.moving_platforms.append(platform4)

        platform5 = arcade.Sprite(platform_texture, TILE_SCALING)
        platform5.center_x = 3000
        platform5.center_y = 180
        platform5.change_y = 2.0
        platform5.boundary_top = 410
        platform5.boundary_bottom = 160
        self.scene.add_sprite("MovingPlatforms", platform5)
        self.moving_platforms.append(platform5)

    def create_enemies(self):
        enemy_texture = ":resources:images/enemies/slimeBlock.png"

        enemy1 = arcade.Sprite(enemy_texture, 0.6)
        enemy1.center_x = 350
        enemy1.center_y = 70
        enemy1.change_x = 1.2
        enemy1.boundary_left = 300
        enemy1.boundary_right = 450
        self.scene.add_sprite("Enemies", enemy1)
        self.moving_enemies.append(enemy1)

        enemy2 = arcade.Sprite(enemy_texture, 0.55)
        enemy2.center_x = 750
        enemy2.center_y = 70
        enemy2.change_x = 1.0
        enemy2.boundary_left = 700
        enemy2.boundary_right = 850
        self.scene.add_sprite("Enemies", enemy2)
        self.moving_enemies.append(enemy2)

        enemy3 = arcade.Sprite(enemy_texture, 0.5)
        enemy3.center_x = 1400
        enemy3.center_y = 120
        enemy3.change_x = 1.3
        enemy3.boundary_left = 1350
        enemy3.boundary_right = 1550
        self.scene.add_sprite("Enemies", enemy3)
        self.moving_enemies.append(enemy3)

        enemy4 = arcade.Sprite(enemy_texture, 0.5)
        enemy4.center_x = 2550
        enemy4.center_y = 100
        enemy4.change_x = 1.5
        enemy4.boundary_left = 2500
        enemy4.boundary_right = 2650
        self.scene.add_sprite("Enemies", enemy4)
        self.moving_enemies.append(enemy4)

        for i in range(3):
            enemy = arcade.Sprite(enemy_texture, 0.5)
            enemy.center_x = 2300 + i * 70
            enemy.center_y = 100
            enemy.change_x = 1.2
            enemy.boundary_left = 2250
            enemy.boundary_right = 2600
            self.scene.add_sprite("Enemies", enemy)
            self.moving_enemies.append(enemy)

    def on_draw(self):
        self.clear()
        self.world_camera.use()
        self.scene.draw()
        for explosion in self.explosions:
            explosion.draw()

        self.gui_camera.use()
        arcade.draw_text(
            self.level_name,
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 100,
            arcade.color.PURPLE,
            20,
            anchor_x="center"
        )

        arcade.draw_text(
            "M - вкл/выкл музыку",
            SCREEN_WIDTH - 150,
            SCREEN_HEIGHT - 20,
            arcade.color.LIGHT_GRAY,
            14
        )

        arcade.draw_text(
            f"Кристаллы: {self.crystals_collected}/{self.total_crystals}",
            10,
            SCREEN_HEIGHT - 30,
            arcade.csscolor.WHITE,
            18
        )

        arcade.draw_text(
            f"Уровень: {self.level_name}",
            10,
            SCREEN_HEIGHT - 60,
            arcade.csscolor.WHITE,
            18
        )

        arcade.draw_text(
            f"Жизни: {'♥' * self.player_lives}",
            SCREEN_WIDTH - 120,
            SCREEN_HEIGHT - 60,
            arcade.color.RED,
            24
        )

    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP or key == arcade.key.W or key == arcade.key.SPACE:
            if self.physics_engine.can_jump():
                self.physics_engine.jump(PLAYER_JUMP_SPEED)
                arcade.play_sound(self.jump_sound, volume=0.3)
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.ESCAPE:
            self.return_to_menu()
        elif key == arcade.key.M:
            self.toggle_music()

    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = 0
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = 0

    def toggle_music(self):
        if self.background_music:
            if self.music_player:
                self.background_music.stop(self.music_player)
                self.music_player = None
            else:
                self.music_player = self.background_music.play(volume=0.2, loop=True)

    def center_camera_to_player(self):
        target = list(self.player_sprite.position)
        target[0] = max(self.width / 2, target[0])
        target[1] = max(self.height / 2, target[1])
        self.world_camera.position = arcade.math.lerp_2d(self.world_camera.position, target, 0.12)

    def check_collision_with_hazards(self):
        spikes_hit = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene.get_sprite_list("Spikes")
        )

        small_spikes_hit = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene.get_sprite_list("SmallSpikes")
        )

        enemies_hit = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene.get_sprite_list("Enemies")
        )

        if spikes_hit or enemies_hit or small_spikes_hit:
            if self.player_lives > 1:
                self.player_lives -= 1
                arcade.play_sound(self.hurt_sound, volume=0.5)
                self.player_sprite.center_x = 64
                self.player_sprite.center_y = 128
            else:
                self.game_over()

    def game_over(self):
        if self.background_music and self.music_player:
            self.background_music.stop(self.music_player)

        class GameOverView(arcade.View):
            def __init__(self, level_name, crystals_collected, total_crystals):
                super().__init__()
                self.level_name = level_name
                self.crystals_collected = crystals_collected
                self.total_crystals = total_crystals

            def on_draw(self):
                self.clear()
                arcade.draw_text(
                    "ИГРА ОКОНЧЕНА",
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT // 2 + 50,
                    arcade.color.RED,
                    60,
                    anchor_x="center"
                )
                arcade.draw_text(
                    f"Собрано кристаллов: {self.crystals_collected}/{self.total_crystals}",
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT // 2,
                    arcade.color.WHITE,
                    30,
                    anchor_x="center"
                )
                arcade.draw_text(
                    "Нажмите ENTER для повтора уровня",
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT // 2 - 50,
                    arcade.color.WHITE,
                    20,
                    anchor_x="center"
                )
                arcade.draw_text(
                    "Нажмите ESC для выхода в меню",
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT // 2 - 100,
                    arcade.color.WHITE,
                    20,
                    anchor_x="center"
                )

            def on_key_press(self, key, modifiers):
                if key == arcade.key.ENTER:
                    game_view = Level4()
                    game_view.setup()
                    self.window.show_view(game_view)
                elif key == arcade.key.ESCAPE:
                    import main_menu
                    menu_view = main_menu.MainMenu()
                    self.window.show_view(menu_view)

        game_over_view = GameOverView(self.level_name,
                                      self.crystals_collected, self.total_crystals)
        self.window.show_view(game_over_view)

    def update_moving_objects(self):
        for platform in self.moving_platforms:
            platform.center_x += platform.change_x
            platform.center_y += platform.change_y

            if hasattr(platform, 'boundary_left') and platform.boundary_left is not None:
                if platform.center_x <= platform.boundary_left:
                    platform.change_x *= -1
                    platform.center_x = platform.boundary_left

            if hasattr(platform, 'boundary_right') and platform.boundary_right is not None:
                if platform.center_x >= platform.boundary_right:
                    platform.change_x *= -1
                    platform.center_x = platform.boundary_right

            if hasattr(platform, 'boundary_top') and platform.boundary_top is not None:
                if platform.center_y >= platform.boundary_top:
                    platform.change_y *= -1
                    platform.center_y = platform.boundary_top

            if hasattr(platform, 'boundary_bottom') and platform.boundary_bottom is not None:
                if platform.center_y <= platform.boundary_bottom:
                    platform.change_y *= -1
                    platform.center_y = platform.boundary_bottom

        for enemy in self.moving_enemies:
            enemy.center_x += enemy.change_x
            enemy.center_y += enemy.change_y

            if hasattr(enemy, 'boundary_left') and enemy.boundary_left is not None:
                if enemy.center_x <= enemy.boundary_left:
                    enemy.change_x *= -1
                    enemy.center_x = enemy.boundary_left

            if hasattr(enemy, 'boundary_right') and enemy.boundary_right is not None:
                if enemy.center_x >= enemy.boundary_right:
                    enemy.change_x *= -1
                    enemy.center_x = enemy.boundary_right

    def on_update(self, delta_time):
        self.physics_engine.update()
        self.update_moving_objects()
        for explosion in self.explosions[:]:
            explosion.update()
            if explosion.is_finished():
                self.explosions.remove(explosion)

        crystals_hit = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene.get_sprite_list("Crystals")
        )

        for crystal in crystals_hit:
            explosion = CrystalExplosion(crystal.center_x, crystal.center_y)
            self.explosions.append(explosion)

            crystal.remove_from_sprite_lists()
            self.crystals_collected += 1
            arcade.play_sound(self.collect_sound, volume=0.3)

        self.check_collision_with_hazards()

        if self.player_sprite.center_y < -100:
            if self.player_lives > 1:
                self.player_lives -= 1
                arcade.play_sound(self.hurt_sound, volume=0.5)
                self.player_sprite.center_x = 64
                self.player_sprite.center_y = 128
            else:
                self.game_over()

        if self.crystals_collected >= self.total_crystals:
            self.show_victory()

        self.center_camera_to_player()

    def show_victory(self):
        if self.background_music and self.music_player:
            self.background_music.stop(self.music_player)

        class VictoryView(arcade.View):
            def __init__(self, level_name):
                super().__init__()
                self.level_name = level_name
                try:
                    self.victory_music = arcade.load_sound(":resources:music/1918.mp3")
                    self.music_player = None
                except:
                    self.victory_music = None

            def on_show(self):
                if self.victory_music:
                    self.music_player = self.victory_music.play(volume=0.3, loop=True)

            def on_hide(self):
                if self.music_player:
                    self.victory_music.stop(self.music_player)

            def on_draw(self):
                self.clear()
                arcade.draw_text(
                    "ПОБЕДА!",
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT // 2 + 50,
                    arcade.color.GOLD,
                    60,
                    anchor_x="center"
                )
                arcade.draw_text(
                    f"Уровень 4 пройден!",
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT // 2 - 50,
                    arcade.color.WHITE,
                    30,
                    anchor_x="center"
                )
                arcade.draw_text(
                    "Нажмите ESC для выхода в меню",
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT // 2 - 100,
                    arcade.color.WHITE,
                    20,
                    anchor_x="center"
                )

            def on_key_press(self, key, modifiers):
                if key == arcade.key.ESCAPE:
                    if self.music_player:
                        self.victory_music.stop(self.music_player)
                    import main_menu
                    menu_view = main_menu.MainMenu()
                    self.window.show_view(menu_view)

        victory_view = VictoryView(self.level_name)
        self.window.show_view(victory_view)

    def return_to_menu(self):
        menu_view = main_menu.MainMenu()
        self.window.show_view(menu_view)


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game_view = Level4()
    game_view.setup()
    window.show_view(game_view)
    arcade.run()


if __name__ == "__main__":
    main()
