from behavior_tree_bot.behaviors import (
    find_threatened_planet,
    find_best_neutral_move,
    find_best_enemy_move,
)

def threatened_planet_exists(state): #not used in the final version of the bot, but keeping just in case
    return find_threatened_planet(state) is not None

def profitable_neutral_exists(state):
    return find_best_neutral_move(state) is not None


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
