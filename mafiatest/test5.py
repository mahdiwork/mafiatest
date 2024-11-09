import random

class Role:
    def __init__(self, name):
        self.name = name
        self.alive = True
        self.house = None  # Each role has a house attribute

    def die(self):
        self.alive = False
        print(f"{self.name} has died.")

    def enter_house(self, house):
        self.house = house
        print(f"{self.name} enters {house.name}.")

    def perform_night_action(self, game_state):
        pass  # To be overridden in subclasses

class Sheriff(Role):
    def perform_night_action(self, game_state):
        pass

    def die(self):
        super().die()
        print(f"{self.name} was the Sheriff and has died.")
        self.revenge()

    def revenge(self):
        print(f"{self.name} has shot a random player as a revenge!")

class Werewolf(Role):
    def perform_night_action(self, game_state):
        target = self.choose_target(game_state)
        if target:
            print(f"{self.name} attacks {target.name}.")
            target.die()

    def choose_target(self, game_state):
        alive_players = [p for p in game_state['players'] if p.alive and p != self]
        if alive_players:
            return random.choice(alive_players)
        return None

class Killer(Role):
    def perform_night_action(self, game_state):
        target = self.choose_target(game_state)
        if target:
            print(f"{self.name} kills {target.name}.")
            target.die()

    def choose_target(self, game_state):
        alive_players = [p for p in game_state['players'] if p.alive and p != self]
        if alive_players:
            return random.choice(alive_players)
        return None

class FireKing(Role):
    def __init__(self, name):
        super().__init__(name)
        self.oil_targets = []

    def perform_night_action(self, game_state):
        target = self.choose_target(game_state)
        if target:
            self.oil_targets.append(target)
            print(f"{target.name} is oiled by the Fire King.")

    def ignite(self):
        victims = [target for target in self.oil_targets if target.alive]
        if victims:
            print(f"The Fire King ignites the oiled targets:")
            for target in victims:
                print(f"{target.name} is burned by the Fire King.")
                target.die()
                # Check if there is another target in the same house
                other_target = self.get_other_target_in_same_house(target)
                if other_target:
                    print(f"{other_target.name} is also burned by the Fire King.")
                    other_target.die()
        else:
            print("No valid targets to ignite.")
        self.oil_targets = []

    def get_other_target_in_same_house(self, target):
        # Check if there is another target in the same house as 'target'
        if target.house and target.house.players:
            for player in target.house.players:
                if player != target and player.alive:
                    return player
        return None

    def choose_target(self, game_state):
        alive_players = [p for p in game_state['players'] if p.alive and p != self]
        if alive_players:
            return random.choice(alive_players)
        return None

class House:
    def __init__(self, name):
        self.name = name
        self.players = []

    def add_player(self, player):
        self.players.append(player)

# Sample game setup
def setup_game():
    # Create roles
    sheriff = Sheriff("Sheriff")
    werewolf = Werewolf("Werewolf")
    killer = Killer("Killer")
    fire_king = FireKing("Fire King")

    # Create houses
    house1 = House("House 1")
    house2 = House("House 2")

    # Assign roles to houses
    house1.add_player(sheriff)
    house1.add_player(werewolf)
    house2.add_player(killer)
    house2.add_player(fire_king)

    # Assign houses to players
    sheriff.enter_house(house1)
    werewolf.enter_house(house1)
    killer.enter_house(house2)
    fire_king.enter_house(house2)

    # Simulate game actions
    print("Night 1:")
    sheriff.perform_night_action({'players': [sheriff, werewolf, killer, fire_king]})
    werewolf.perform_night_action({'players': [sheriff, werewolf, killer, fire_king]})
    killer.perform_night_action({'players': [sheriff, werewolf, killer, fire_king]})
    fire_king.perform_night_action({'players': [sheriff, werewolf, killer, fire_king]})

    print("\nFire King ignites:")
    fire_king.ignite()

setup_game()
