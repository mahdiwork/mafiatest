from abc import ABC, abstractmethod
import time
import random

class Role(ABC):
    def __init__(self, name):
        self.name = name
        self.alive = True

    def die(self):
        self.alive = False

    def revive(self):
        self.alive = True

    @abstractmethod
    def perform_night_action(self, game_state):
        pass

class Citizen(Role):
    def perform_night_action(self, game_state):
        pass

class Sniper(Role):
    def __init__(self, name):
        super().__init__(name)
        self.bullet = 1

    def perform_night_action(self, game_state):
        if self.bullet > 0:
            target = self.choose_target(game_state)
            if target:
                if isinstance(target, Werewolf):
                    target.die()
                else:
                    self.die()
                self.bullet -= 1

    def choose_target(self, game_state):
        # انتخاب هدف بر اساس منطق بازی
        alive_players = [p for p in game_state['players'] if p.alive and p != self]
        if alive_players:
            return random.choice(alive_players)
        return None

class Doctor(Role):
    def perform_night_action(self, game_state):
        target = self.choose_target(game_state)
        if target:
            target.revive()

    def choose_target(self, game_state):
        # انتخاب هدف بر اساس منطق بازی
        alive_players = [p for p in game_state['players'] if p.alive]
        if alive_players:
            return random.choice(alive_players)
        return None

class Werewolf(Role):
    def perform_night_action(self, game_state):
        target = self.choose_target(game_state)
        if target:
            target.die()

    def choose_target(self, game_state):
        # انتخاب هدف بر اساس منطق بازی
        alive_players = [p for p in game_state['players'] if p.alive and p != self]
        if alive_players:
            return random.choice(alive_players)
        return None
def day_phase(game_state):
    print("Day phase started. Players can discuss.")
    alive_players = [p for p in game_state['players'] if p.alive]
    random.shuffle(alive_players)
    
    for player in alive_players:
        print(f"{player.name}, share your thoughts.")
        # شبیه‌سازی بحث بازیکنان
        time.sleep(1)
    
    print("Voting time. Players vote to eliminate one player.")
    votes = {player.name: 0 for player in game_state['players'] if player.alive}
    
    for player in alive_players:
        vote = random.choice([p.name for p in alive_players if p != player])
        print(f"{player.name} votes to eliminate {vote}.")
        votes[vote] += 1
    
    eliminated_player = max(votes, key=votes.get)
    for player in game_state['players']:
        if player.name == eliminated_player:
            player.die()
            print(f"{player.name} has been eliminated.")
            break

def night_phase(game_state):
    print("Night phase started. Players perform their actions.")
    roles_order = sorted(game_state['players'], key=lambda x: isinstance(x, Werewolf), reverse=True)
    
    for player in roles_order:
        if player.alive:
            print(f"{player.name} ({player.__class__.__name__}), it's your turn.")
            player.perform_night_action(game_state)
            time.sleep(1)  # شبیه‌سازی تصمیم‌گیری بازیکن

def check_game_over(game_state):
    alive_werewolves = [p for p in game_state['players'] if isinstance(p, Werewolf) and p.alive]
    alive_citizens = [p for p in game_state['players'] if not isinstance(p, Werewolf) and p.alive]
    
    if not alive_werewolves:
        print("Citizens win!")
        return True
    if len(alive_werewolves) >= len(alive_citizens):
        print("Werewolves win!")
        return True
    return False

def main():
    player1 = Citizen("Player1")
    player2 = Sniper("Player2")
    player3 = Doctor("Player3")
    player4 = Werewolf("Player4")

    game_state = {
        'players': [player1, player2, player3, player4]
    }

    game_over = False
    while not game_over:
        day_phase(game_state)
        game_over = check_game_over(game_state)
        if game_over:
            break
        night_phase(game_state)
        game_over = check_game_over(game_state)


