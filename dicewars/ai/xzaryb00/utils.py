from dicewars.ai.utils import (
    attack_succcess_probability,
    probability_of_holding_area as probability_of_holding_area_client
)

def get_features(board, atk_name, def_name):
    attacker = board.get_area_by_name(atk_name)
    defender = board.get_area_by_name(def_name)
    atk_owner = attacker.owner_name
    def_owner = defender.owner_name
    aa1n = k_neighbors(board, 1, atk_name, atk_owner)
    ad1n = k_neighbors(board, 1, atk_name, def_owner)
    aa2n = k_neighbors(board, 2, atk_name, atk_owner)
    ad2n = k_neighbors(board, 2, atk_name, def_owner)
    dd1n = k_neighbors(board, 1, def_name, def_owner)
    da1n = k_neighbors(board, 1, def_name, atk_owner)
    dd2n = k_neighbors(board, 2, def_name, def_owner)
    da2n = k_neighbors(board, 2, def_name, atk_owner)
    return (
        (   # Inputs
            attacker.dice / 8,
            defender.dice / 8,
            attack_succcess_probability(attacker.dice, defender.dice),
            probability_of_holding_area(board, attacker.name, attacker.dice, atk_owner),
            probability_of_holding_area(board, attacker.name, 1, atk_owner),
            (sum(aa1n) / len(aa1n)) if aa1n else 0,
            (sum(ad1n) / len(ad1n)) if ad1n else 0,
            ((sum(aa2n) - sum(aa1n)) / (len(aa2n) - len(aa1n))) if len(aa2n) - len(aa1n) else 0,
            ((sum(ad2n) - sum(ad1n)) / (len(ad2n) - len(ad1n))) if len(ad2n) - len(ad1n) else 0,
            (sum(dd1n) / len(dd1n)) if dd1n else 0,
            (sum(da1n) / len(da1n)) if da1n else 0,
            ((sum(dd2n) - sum(dd1n)) / (len(dd2n) - len(dd1n))) if len(dd2n) - len(dd1n) else 0,
            ((sum(da2n) - sum(da1n)) / (len(da2n) - len(da1n))) if len(da2n) - len(da1n) else 0,
            len(aa1n) / 10,
            len(ad1n) / 10,
            len(aa2n) / 10 - len(aa1n) / 10,
            len(ad2n) / 10 - len(ad1n) / 10,
            len(dd1n) / 10,
            len(da1n) / 10,
            len(dd2n) / 10 - len(dd1n) / 10,
            len(da2n) / 10 - len(da1n) / 10,
        ),
        [   # Outputs
            1, # Holding atk after N turns
            1, # Holding def after N turns
        ],
        (   # Helper data
            atk_owner,
            attacker,
            defender,
        ),
    )


def k_neighbors(board, neighborhood_size, start, owner):
    neighbors = set()
    current_areas = set([start])
    for i in range(neighborhood_size):
        new_areas = set()
        for a in current_areas:
            for an in board.get_area_by_name(a).adjacent_areas_names:
                if an not in neighbors and board.get_area_by_name(an).owner_name == owner:
                    neighbors.add(an)
                    new_areas.add(an)
        current_areas = new_areas
    if start in neighbors:
        neighbors.remove(start)
    return [board.get_area_by_name(i).dice / 8 for i in neighbors]


def probability_of_holding_area(board, area_name, area_dice, player_name):
    """Copied over from AI utils, adapted for the server"""
    area = board.get_area_by_name(area_name)
    probability = 1.0
    for adj in area.adjacent_areas_names:
        adjacent_area = board.get_area_by_name(adj)
        if adjacent_area.get_owner_name() != player_name:
            enemy_dice = adjacent_area.get_dice()
            if enemy_dice == 1:
                continue
            lose_prob = attack_succcess_probability(enemy_dice, area_dice)
            hold_prob = 1.0 - lose_prob
            probability *= hold_prob
    return probability


def get_features_client(board, atk_name, def_name):
    attacker = board.get_area(atk_name)
    defender = board.get_area(def_name)
    atk_owner = attacker.owner_name
    def_owner = defender.owner_name
    aa1n = k_neighbors_client(board, 1, atk_name, atk_owner)
    ad1n = k_neighbors_client(board, 1, atk_name, def_owner)
    aa2n = k_neighbors_client(board, 2, atk_name, atk_owner)
    ad2n = k_neighbors_client(board, 2, atk_name, def_owner)
    dd1n = k_neighbors_client(board, 1, def_name, def_owner)
    da1n = k_neighbors_client(board, 1, def_name, atk_owner)
    dd2n = k_neighbors_client(board, 2, def_name, def_owner)
    da2n = k_neighbors_client(board, 2, def_name, atk_owner)
    return (
        (   # Inputs
            attacker.dice / 8,
            defender.dice / 8,
            attack_succcess_probability(attacker.dice, defender.dice),
            probability_of_holding_area_client(board, attacker.name, attacker.dice, atk_owner),
            probability_of_holding_area_client(board, attacker.name, 1, atk_owner),
            (sum(aa1n) / len(aa1n)) if aa1n else 0,
            (sum(ad1n) / len(ad1n)) if ad1n else 0,
            ((sum(aa2n) - sum(aa1n)) / (len(aa2n) - len(aa1n))) if len(aa2n) - len(aa1n) else 0,
            ((sum(ad2n) - sum(ad1n)) / (len(ad2n) - len(ad1n))) if len(ad2n) - len(ad1n) else 0,
            (sum(dd1n) / len(dd1n)) if dd1n else 0,
            (sum(da1n) / len(da1n)) if da1n else 0,
            ((sum(dd2n) - sum(dd1n)) / (len(dd2n) - len(dd1n))) if len(dd2n) - len(dd1n) else 0,
            ((sum(da2n) - sum(da1n)) / (len(da2n) - len(da1n))) if len(da2n) - len(da1n) else 0,
            len(aa1n) / 10,
            len(ad1n) / 10,
            len(aa2n) / 10 - len(aa1n) / 10,
            len(ad2n) / 10 - len(ad1n) / 10,
            len(dd1n) / 10,
            len(da1n) / 10,
            len(dd2n) / 10 - len(dd1n) / 10,
            len(da2n) / 10 - len(da1n) / 10,
        ),
        [   # Outputs
            1, # Holding atk after N turns
            1, # Holding def after N turns
        ],
        (   # Helper data
            atk_owner,
            attacker,
            defender,
        ),
    )


def k_neighbors_client(board, neighborhood_size, start, owner):
    neighbors = set()
    current_areas = set([start])
    for i in range(neighborhood_size):
        new_areas = set()
        for a in current_areas:
            for an in board.get_area(a).neighbours:
                if an not in neighbors and board.get_area(an).owner_name == owner:
                    neighbors.add(an)
                    new_areas.add(an)
        current_areas = new_areas
    if start in neighbors:
        neighbors.remove(start)
    return [board.get_area(i).dice / 8 for i in neighbors]
