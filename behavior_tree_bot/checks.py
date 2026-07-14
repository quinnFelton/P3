from behavior_tree_bot.behaviors import (
    find_threatened_planet,
    find_best_neutral_move,
    find_best_enemy_move,
)

def threatened_planet_exists(state):
    return find_threatened_planet(state) is not None

def better_to_expand(state):
    neutral_move = find_best_neutral_move(state)
    enemy_move = find_best_enemy_move(state)
    
    if neutral_move is None:
        return False
    if enemy_move is None:
        return True
        
    expand_score = neutral_move[3]
    attack_score = enemy_move[3]
    return expand_score > attack_score

def profitable_neutral_exists(state):
    return find_best_neutral_move(state) is not None

def better_to_attack(state):
    neutral_move = find_best_neutral_move(state)
    enemy_move = find_best_enemy_move(state)
    
    if neutral_move is None:
        return True
    if enemy_move is None:
        return False
        
    expand_score = neutral_move[3]
    attack_score = enemy_move[3]
    return expand_score <= attack_score

def safe_enemy_attack_exists(state):
    return find_best_enemy_move(state) is not None


# Keeping just in case:

def if_neutral_planet_available(state):
    return any(state.neutral_planets())


def have_largest_fleet(state):
    return sum(planet.num_ships for planet in state.my_planets()) \
             + sum(fleet.num_ships for fleet in state.my_fleets()) \
           > sum(planet.num_ships for planet in state.enemy_planets()) \
             + sum(fleet.num_ships for fleet in state.enemy_fleets())
