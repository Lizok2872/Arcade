import arcade
import random
import math

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Кристаллические Приключения - Обучение"
CHARACTER_SCALING = 0.5
TILE_SCALING = 0.5
CRYSTAL_SCALING = 0.3
PLAYER_MOVEMENT_SPEED = 5
GRAVITY = 1
PLAYER_JUMP_SPEED = 20


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


class TutorialLevel(arcade.View):
    def __init__(self):
        super().__init__()
        self.level_name = "Обучение"
        self.level = 0
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
            self.background_music = arcade.load_sound(":resources:music/funkyrobot.mp3")
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

        self.player_sprite = arcade.Sprite(
            ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png",
            CHARACTER_SCALING
        )

        self.player_sprite.center_x = 100
        self.player_sprite.center_y = 128

        self.scene.add_sprite("Player", self.player_sprite)
        self.create_level()
        self.create_crystals()

        self.all_walls = arcade.SpriteList()
        self.all_walls.extend(self.scene.get_sprite_list("Walls"))

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            self.all_walls,
            GRAVITY
        )

    def create_level(self):
        wall_texture = ":resources:images/tiles/grassMid.png"

        platforms = [
            (0, 0, 20),
            (500, 150, 6),
            (900, 250, 6),
            (1300, 350, 8),
            (1700, 200, 4),
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
            (200, 100),
            (600, 200),
            (1000, 300),
            (1400, 400),
            (1750, 250),
        ]

        self.total_crystals = len(crystal_positions)

        for x, y in crystal_positions:
            crystal = arcade.Sprite(crystal_texture, CRYSTAL_SCALING)
            crystal.center_x = x
            crystal.center_y = y
            self.scene.add_sprite("Crystals", crystal)

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
            arcade.color.YELLOW,
            20,
            anchor_x="center"
        )

        arcade.draw_text(
            "Добро пожаловать в обучение!",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 150,
            arcade.color.YELLOW,
            16,
            anchor_x="center"
        )
        arcade.draw_text(
            "Соберите все кристаллы, чтобы продолжить",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 180,
            arcade.color.WHITE,
            14,
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
        pass  

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
                    game_view = TutorialLevel()
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
        pass

    def on_update(self, delta_time):
        self.physics_engine.update()
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

        if self.player_sprite.center_y < -100:
            if self.player_lives > 1:
                self.player_lives -= 1
                arcade.play_sound(self.hurt_sound, volume=0.5)
                self.player_sprite.center_x = 100
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
                    f"Обучение завершено!",
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
    game_view = TutorialLevel()
    game_view.setup()
    window.show_view(game_view)
    arcade.run()


if __name__ == "__main__":
    main()
