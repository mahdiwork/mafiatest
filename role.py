from abc import ABC, abstractmethod
import random

class Role(ABC):
    def __init__(self, name):
        self.name = name
        self.alive = True

    def die(self):
        self.alive = False

    # def revive(self):
    #     self.alive = True

    @abstractmethod
    def perform_night_action(self, game_state):
        pass

class Seer(Role):
    def perform_night_action(self, choose):
        target = self.choose_target(choose)
        if target:
            print(f"{target.name} is a {target.__class__.__name__}.")
        # if target:
        #     if isinstance(target, Werewolf):
        #         print(f"{target.name} is a Werewolf.")
        #     else:
        #         print(f"{target.name} is not a Werewolf.")

    def choose_target(self, choose):
        for i in game_state['players']:
            if i.name == choose:
                return i



class Sheriff(Role):
    def __init__(self, name):
        super().__init__(name)
        self.revenge_target = None

    def perform_night_action(self, game_state):
        pass

    def die(self):
        super().die()
        print(f"{self.name} was the Sheriff and has died")
        if self.revenge_target:
            print(f"{self.name} shoots {self.revenge_target.name} as a revenge")
            self.revenge_target.die()
        elif random.random() < 0.5:
            werewolves = [p for p in game_state['players'] if isinstance(p, Werewolf) and p.alive]
            if werewolves:
                wolf_to_kill = random.choice(werewolves)
                print(f"{self.name} shoots {wolf_to_kill.name} in a panic")
                wolf_to_kill.die()

    def revenge(self):
        pass

class Gunslinger(Role):
    def __init__(self, name):
        super().__init__(name)
        self.bullets = 2

    def perform_night_action(self, game_state):
        if self.bullets > 0:
            target = self.choose_target(game_state)
            if target:
                print(f"{self.name} shoots {target.name}.")
                target.die()
                self.bullets -= 1

    def choose_target(self, choose):
        for i in game_state['players']:
            if i.name == choose:
                return i

class AlphaWerewolf(Role):
    def perform_night_action(self, game_state):
        target = self.choose_target(game_state)
        if target:
            print(f"{self.name} attacks {target.name}.")
            if random.random() < 0.9:
                print(f"{target.name} is turned into a Werewolf.")
                game_state['players'].append(Werewolf(target.name))
            else:
                target.die()

    def choose_target(self, choose):
        for i in game_state['players']:
            if i.name == choose:
                return i
    

class Werewolf(Role):
    def perform_night_action(self, game_state):
        target = self.choose_target(game_state)
        if target:
            print(f"{self.name} attacks {target.name}.")
            if isinstance(target, Killer):
                print(f"{self.name} attacks {target.name} and dies in the process")
                self.die()
            else:
                if isinstance(target, DarkKnight) and random.random() < 0.5:
                    self.die()
                else:
                    target.die()

    def choose_target(self, choose):
        for i in game_state['players']:
            if i.name == choose:
                return i


class Killer(Role):
    def perform_night_action(self, game_state):
        target = self.choose_target(game_state)
        if target:
            print(f"{self.name} kills {target.name}.")
            if isinstance(target, DarkKnight) and random.random() < 0.5:
                print(f"{self.name} tries to kill {target.name} but dies in the process")
                self.die()
            else:
                target.die()

    def choose_target(self, choose):
        for i in game_state['players']:
            if i.name == choose:
                return i





class FireKing(Role):
    def __init__(self, name):
        super().__init__(name)
        self.oil_targets = []

    def perform_night_action(self, game_state):
        target = self.choose_target(game_state)
        if target:
            self.oil_targets.append(target)
            print(f"{target.name} is oiled by the Fire King.")

    def ignite(self, game_state):
        for target in self.oil_targets:
            print(f"{target.name} is burned by the Fire King.")
            target.die()

        for player in game_state['players']:
            if player != self and player.alive:
                for t in self.oil_targets:
                    if player.role and player.role.choose_target(game_state) == t:
                        print(f"{player.name} has died because they targeted {t.name}.")
                        player.die()
        self.oil_targets = []

    def choose_target(self, choose):
        for i in game_state['players']:
            if i.name == choose:
                return i



class IceQueen(Role):
    def perform_night_action(self, game_state):
        target = self.choose_target(game_state)
        if target:
            if hasattr(target, 'frozen'):
                print(f"{target.name} is frozen to death by the Ice Queen.")
                target.die()
            else:
                print(f"{target.name} is frozen by the Ice Queen.")
                target.frozen = True

    def choose_target(self, choose):
        for i in game_state['players']:
            if i.name == choose:
                return i

class CommonVampire(Role):
    def perform_night_action(self, game_state):
        target = self.choose_target(game_state)
        if target:
            if isinstance(target, Sheriff):
                print(f"{self.name} is searching for the Sheriff.")
            else:
                print(f"{self.name} bites {target.name}.")
                if random.random() < 0.3:
                    print(f"{target.name} is killed by {self.name}.")
                    target.die()

    def choose_target(self, choose):
        for i in game_state['players']:
            if i.name == choose:
                return i

class PureVampire(Role):
    def perform_night_action(self, game_state):
        print(f"{self.name} is imprisoned and cannot act until freed.")

    def be_freed(self):
        print(f"{self.name} is freed and becomes the leader of the vampires.")

class DarkKnight(Role):
    def perform_night_action(self, game_state):
        pass

    def encounter(self, visitor):
        if random.random() < 0.5:
            print(f"{self.name} kills the visitor {visitor.name}.")
            visitor.die()
        else:
            print(f"{self.name} is killed by the visitor {visitor.name}.")
            self.die()

class Doppelganger(Role):
    def __init__(self, name):
        super().__init__(name)
        self.target = None

    def perform_night_action(self, game_state):
        if self.target is None:
            self.target = self.choose_target(game_state)
            print(f"{self.name} has chosen {self.target.name} as their target.")

    def inherit_role(self):
        if self.target and not self.target.alive:
            self.__class__ = self.target.__class__
            print(f"{self.name} has inherited the role of {self.target.name}.")

    def choose_target(self, choose):
        for i in game_state['players']:
            if i.name == choose:
                return i

class Cultist(Role):
    def perform_night_action(self, choose,game_state):
        target = self.choose_target(choose)
        if target:
            # print(f"{self.name} invites {target.name} to the cult.")
            # if isinstance(target,Seer) and random.random() < 0.4:
            #     game_state['players'].remove(target)
            #     game_state['players'].append(Cultist(target.name))
            #     print('kill seer')

            # elif isinstance(target,Sheriff) and random.random() < 0.5:
            #     game_state['players'].remove(target)
            #     game_state['players'].append(Cultist(target.name))
            #     print('kill Sheriff')

            # elif isinstance(target,Gunslinger):
            #     game_state['players'].remove(target)
            #     game_state['players'].append(Cultist(target.name))
            #     print('kill Gunslinger')     

            # elif isinstance(target,CommonVampire) and random.random() < 0.5:
            #     game_state['players'].remove(target)
            #     game_state['players'].append(Cultist(target.name))
            #     print('kill CommonVampire')             
            
            game_state['cult'].append(target)
            print(game_state['players'])

    def choose_target(self, choose):
        for i in game_state['players']:
            if i.name == choose:
                return i

class CultLeader(Role):
    def die(self):
        super().die()
        print(f"{self.name} was the Cult Leader and has died.")
        self.revenge()

    def revenge(self):
        print(f"{self.name}'s death causes the cult to invite two new members next night.")

    def perform_night_action(self, choose,game_state):
        target = self.choose_target(choose)
        if target:
            game_state['cult'].append(target)
            print(game_state['players'])

    def choose_target(self, choose):
        for i in game_state['players']:
            if i.name == choose:
                return i
            
game_state = {
    'players': [
        Seer('Alice'),
        Sheriff('Bob'),
        Gunslinger('Charlie'),
        AlphaWerewolf('Dave'),
        Werewolf('Eve'),
        Killer('Frank'),
        FireKing('George'),
        IceQueen('Hannah'),
        CommonVampire('Ivy'),
        PureVampire('Jack'),
        DarkKnight('Kevin'),
        Doppelganger('Liam'),
        Cultist('Mike'),
        CultLeader('Nina')
    ],
    'cult': []
}

ply=Cultist('Mike')
ply.perform_night_action('Alice',game_state)