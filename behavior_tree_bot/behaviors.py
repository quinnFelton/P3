import sys
sys.path.insert(0, '../')

from planet_wars import issue_order


 
# Utility functions

def reserve_for(planet):
    """
    Ships that should remain behind at each planet
    """
    return max(5, int(planet.growth_rate) * 2)


def available_ships(planet):
    """Ships that can safely be used for an order"""
    return max(0, int(planet.num_ships) - reserve_for(planet))


def friendly_fleet_heading_to(state, planet_id):
    """Return True when we already have a fleet going to this target"""
    return any(
        fleet.destination_planet == planet_id
        for fleet in state.my_fleets()
    )

def sum_friendly_fleet_heading_to(state, planet_id):
    """Return total of friendly fleet heading to target"""
    return sum(fleet.num_ships for fleet in state.my_fleets() if fleet.destination_planet == planet_id)

def enemy_fleet_heading_to(state, planet_id):
    """Return size of fleet the enemy already has going to this target, 0 if none"""
    total_enemy_fleet_size = 0
    for fleet in state.enemy_fleets():
        if(fleet.destination_planet == planet_id):
            total_enemy_fleet_size += fleet.num_ships
    return total_enemy_fleet_size

def time_for_enemy_to_capture(state, planet_id):
    """Return arrival time of last fleet sent to target"""
    incoming_enemy_times = [
        fleet.turns_remaining 
        for fleet in state.enemy_fleets() 
        if fleet.destination_planet == planet_id
    ]
    if not incoming_enemy_times:
        return float('inf')
    return min(incoming_enemy_times)


#Defensive checks

def find_threatened_planet(state):
    """
    Find biggest planet that is threatened by an incoming enemy fleet

    Returns:
        (planet, ships_needed_to_defend), or None
    """
    max_ships_needed = 0
    target_planet = None
    for planet in state.my_planets():
        if enemy_fleet_heading_to(state, planet.ID) > planet.num_ships:
            ships_needed = enemy_fleet_heading_to(state, planet.ID)-(planet.num_ships+sum_friendly_fleet_heading_to(state, planet.ID))
            if ships_needed > max_ships_needed:
                max_ships_needed = ships_needed
                target_planet = planet
    if target_planet is not None:
        return (target_planet, max_ships_needed)
    return None

def defend_threatened_planet(state):
    """
    Defend planet that is threatened by an incoming enemy fleet if possible, if no source planet has enough ships to defend return False
    """
    threatened_planet = find_threatened_planet(state)

    if threatened_planet is None:
        return False
    
    planet, ships_needed = threatened_planet
    close_planets = sorted(state.my_planets(), key=lambda p: state.distance(p.ID, planet.ID))
    available_planets = []
    available_ships_to_send = 0
    # get closest planets and see if they are able to donate, summing the total number of donate-able ships
    for source in close_planets:
        if source.ID == planet.ID:
            continue
        # big planets should defend small planets, not other way around
        # don't add planet if too far away to make it in time to save threatened planet
        if source.num_ships > planet.num_ships and state.distance(source.ID, planet.ID) < time_for_enemy_to_capture(state, planet.ID):
            available_planets.append(source)
            available_ships_to_send += available_ships(source)
    # if there are enough ships, send ships in order from planets with most ships to least ships
    if available_ships_to_send >= ships_needed:
        ships_remaining = int(ships_needed)
        available_planets.sort(key=lambda p: p.num_ships, reverse=True)
        for source in available_planets:
            ships_sent = min(ships_remaining, int(available_ships(source)))
            ships_remaining -= ships_sent
            issue_order(state, source.ID, planet.ID, ships_sent)
            if ships_remaining <= 0:
                return True
    return False
 
# Neutral expansion
 

def find_best_neutral_move(state):
    """
    Find the best valid source/neutral-target combination

    Returns:
        (source_planet, target_planet, ships_to_send) or None
    """
    best_move = None
    best_score = None

    for source in state.my_planets():
        source_available = available_ships(source)

        for target in state.neutral_planets():
            # Prevent repeatedly attacking the same neutral planet.
            if friendly_fleet_heading_to(state, target.ID):
                continue

            required = int(target.num_ships) + 1

            if source_available < required:
                continue

            distance = state.distance(source.ID, target.ID)

            # Higher growth is good, large defending populations and long travel are bad
            score = (
                int(target.growth_rate) * 8
                - required
                - distance
            )

            if best_score is None or score > best_score:
                best_score = score
                best_move = source, target, required

    return best_move


def expand_to_best_neutral(state):
    move = find_best_neutral_move(state)

    if move is None:
        return False

    source, target, ships = move

    return issue_order(
        state,
        source.ID,
        target.ID,
        int(ships)
    )


 
# Enemy attacks
 

def find_best_enemy_move(state):
    """
    Find an enemy planet that one source planet can capture
    calculates enemy growth during travel time, checks for incoming enemy fleets, and returns the best source/target combination

    Returns:
        (source_planet, target_planet, ships_to_send) or None
    """
    best_move = None
    best_score = None

    for source in state.my_planets():
        source_available = available_ships(source)

        for target in state.enemy_planets():
            if friendly_fleet_heading_to(state, target.ID):
                continue

            distance = state.distance(source.ID, target.ID)

            projected_defenders = (
                int(target.num_ships)
                + distance * int(target.growth_rate)+int(enemy_fleet_heading_to(state, target.ID))
            )

            required = projected_defenders + 1

            if source_available < required:
                continue

            # Capturing an enemy planet with high growthrate is more valuable compared to neutral planets, so weight more heavily
            score = (
                int(target.growth_rate) * 10
                - required
                - distance
            )

            if best_score is None or score > best_score:
                best_score = score
                best_move = source, target, required

    return best_move


def attack_best_enemy(state):
    move = find_best_enemy_move(state)

    if move is None:
        return False

    source, target, ships = move

    return issue_order(
        state,
        source.ID,
        target.ID,
        int(ships)
    )


 
# Fallback
 

def pass_turn(state):
    """
    do nothing

    finish_turn() is called by bt_bot.py after the behavior tree finishes
    """
    return True