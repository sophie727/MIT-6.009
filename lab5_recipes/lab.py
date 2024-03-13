"""
6.101 Lab 5:
Recipes
"""

import pickle
import sys

sys.setrecursionlimit(20_000)
# NO ADDITIONAL IMPORTS!


def atomic_ingredient_costs(recipes):
    """
    Given a recipes list, make and return a dictionary mapping each atomic food item
    name to its cost.
    """
    return {
        ingredient: cost
        for (ing_type, ingredient, cost) in recipes
        if ing_type == "atomic"
    }

def compound_ingredient_possibilities(recipes):
    """
    Given recipes, a list containing compound and atomic food items, make and
    return a dictionary that maps each compound food item name to a list
    of all the ingredient lists associated with that name.
    """
    return {
        ingredient: [
            ing_list
            for (_, ing, ing_list) in recipes
            if ing == ingredient
        ]
        for (ing_type, ingredient, _) in recipes
        if ing_type == "compound"
    }

def lowest_cost_recursive_helper(atomics, compounds, curr_food_item, forbidden):
    """
    Helper function for lowest_cost
    INPUT: atomics (dict of ints), compounds (dict of lists of lists),
           curr_food_item (str)
    OUTPUT: lowest cost of making curr_food_item
    """
    # base case: the item in question is an atomic
    if curr_food_item in forbidden:
        return None
    if curr_food_item in atomics:
        return atomics[curr_food_item]
    if curr_food_item not in compounds:
        return None
    # recursive case: item in question is not atomic
    costs = []
    for cooking_method in compounds[curr_food_item]:
        cost = 0
        for (food, amount) in cooking_method:
            cost_food = lowest_cost_recursive_helper(atomics, compounds, food, forbidden)
            if cost_food is None:
                cost = None
                break
            else:
                cost += amount * cost_food
        if cost is not None:
            costs.append(cost)
    if not costs:
        return None
    return min(costs)

def lowest_cost(recipes, food_item, forbidden=[]):
    """
    Given a recipes list, the name of a food item, and (optionally) a list of
    forbidden items, return the lowest cost of a full recipe for the given food item.
    """
    atomics = atomic_ingredient_costs(recipes)
    compounds = compound_ingredient_possibilities(recipes)

    return lowest_cost_recursive_helper(atomics, compounds, food_item, forbidden)

def scaled_flat_recipe(flat_recipe, n):
    """
    Given a dictionary of ingredients mapped to quantities needed, returns a
    new dictionary with the quantities scaled by n.
    """
    return {
        ingredient: flat_recipe[ingredient] * n
        for ingredient in flat_recipe
    }

def add_flat_recipes(flat_recipes):
    """
    Given a list of flat_recipe dictionaries that map food items to quantities,
    return a new overall 'grocery list' dictionary that maps each ingredient name
    to the sum of its quantities across the given flat recipes.

    For example,
        add_flat_recipes([{'milk':1, 'chocolate':1}, {'sugar':1, 'milk':2}])
    should return:
        {'milk':3, 'chocolate': 1, 'sugar': 1}
    """
    summed_flat_recipes = {}
    for flat_recipe in flat_recipes:
        for ingredient in flat_recipe:
            amt = flat_recipe[ingredient]
            if ingredient in summed_flat_recipes:
                summed_flat_recipes[ingredient] += amt
            else:
                summed_flat_recipes[ingredient] = amt
    return summed_flat_recipes

def cheapest_flat_recipe(recipes, food_item, forbidden=[]):
    """
    Given a recipes list and the name of a food item, as well as an optional
    input of a list of forbidden food items, return a dictionary (mapping
    atomic food items to quantities) representing the cheapest full
    recipe for the given food item.

    Returns None if there is no possible recipe.
    """
    atomics = atomic_ingredient_costs(recipes)
    all_recipes = all_flat_recipes(recipes, food_item, forbidden)
    (min_cost, index) = (-1, 0)
    if not all_recipes:
        return None
    for i, recipe in enumerate(all_recipes):
        cost = sum(recipe[ingredient] * atomics[ingredient] for ingredient in recipe)
        if min_cost == -1 or cost < min_cost:
            min_cost = cost
            index = i

    return all_recipes[index]


def combined_flat_recipes(flat_recipes):
    """
    Given a list of lists of dictionaries, where each inner list represents all
    the flat recipes for a certain ingredient, compute and return a list of flat
    recipe dictionaries that represent all the possible combinations of
    ingredient recipes.
    """
    # we'll calculate this recursively.

    # base case
    if not flat_recipes:
        return []
    if len(flat_recipes) == 1:
        return flat_recipes[0]
    # recursive case
    combined = []
    ingredient1 = flat_recipes[0]
    other_ingredients = combined_flat_recipes(flat_recipes[1:])
    for ingredient1_method in ingredient1:
        for other_method in other_ingredients:
            combined.append(add_flat_recipes([ingredient1_method, other_method]))
    return combined

def all_flat_recipes_helper_function(atomics, compounds, curr_food_item, forbidden):
    """
    Helper function for all_flat_recipes
    INPUT: atomics (dict of ints), compounds (dict of lists of lists),
           curr_food_item (str)
    OUTPUT: lowest cost of making curr_food_item
    """
    # base case: the item in question is forbidden, an atomic, or nonexistent
    if curr_food_item in forbidden:
        return []
    if curr_food_item in atomics:
        return [{curr_food_item: 1}]
    if curr_food_item not in compounds:
        return []
    # recursive case: item in question is not atomic
    flat_recipes = []
    for cooking_method in compounds[curr_food_item]:
        method_success = True
        cooking_method_recipes = []
        for (food, amount) in cooking_method:
            food_recipes = all_flat_recipes_helper_function(atomics, compounds, food, forbidden)
            if not food_recipes:
                method_success = False
                break
            scaled_food_recipes = [
                scaled_flat_recipe(food_recipe, amount)
                for food_recipe in food_recipes
            ]
            cooking_method_recipes.append(scaled_food_recipes)
        if method_success:
            cooking_method_recipes = combined_flat_recipes(cooking_method_recipes)
            for recipe in cooking_method_recipes:
                flat_recipes.append(recipe)

    return flat_recipes

def all_flat_recipes(recipes, food_item, forbidden=[]):
    """
    Given a list of recipes and the name of a food item, produce a list (in any
    order) of all possible flat recipes for that category.

    Returns an empty list if there are no possible recipes
    """
    atomics = atomic_ingredient_costs(recipes)
    compounds = compound_ingredient_possibilities(recipes)

    return all_flat_recipes_helper_function(atomics, compounds, food_item, forbidden)

if __name__ == "__main__":
    # load example recipes from section 3 of the write-up
    with open("test_recipes/example_recipes.pickle", "rb") as f:
        example_recipes = pickle.load(f)
    # you are free to add additional testing code here!

    # compounds = set()
    # for (type, name, _) in example_recipes:
    #     if type == 'compound':
    #         compounds.add(name)
    # print("compounds", len(list(compounds)))

    # atomics = atomic_ingredient_costs(example_recipes)
    # cost = 0
    # for atom in atomics:
    #     cost += atomics[atom]
    # print(cost)

    # compounds = compound_ingredient_possibilities(example_recipes)
    # multi_ways = 0
    # for compound in compounds:
    #     if len(compounds[compound]) > 1:
    #         multi_ways += 1
    # print(compounds)
    # print(multi_ways)

    # dairy_recipes_2 = [
    #     ('compound', 'milk', [('cow', 2), ('milking stool', 1)]),
    #     ('compound', 'cheese', [('milk', 1), ('time', 1)]),
    #     ('compound', 'cheese', [('cutting-edge laboratory', 11)]),
    #     ('atomic', 'milking stool', 5),
    #     ('atomic', 'cutting-edge laboratory', 1000),
    #     ('atomic', 'time', 10000),
    # ]
    # print(lowest_cost(dairy_recipes_2, 'cheese'))
    # print(lowest_cost(dairy_recipes_2, 'cheese', ["cutting-edge laboratory"]))

    # soup = {"carrots": 5, "celery": 3, "broth": 2, "noodles": 1, "chicken": 3, "salt": 10}
    # print(scaled_flat_recipe(soup, 3))

    # carrot_cake = {"carrots": 5, "flour": 8, "sugar": 10, "oil": 5, "eggs": 4, "salt": 3}
    # bread = {"flour": 10, "sugar": 3, "oil": 3, "yeast": 15, "salt": 5}
    # grocery_list = [soup, carrot_cake, bread]
    # print(add_flat_recipes(grocery_list))

    # cake_recipes = [{"cake": 1}, {"gluten free cake": 1}]
    # print(combined_flat_recipes([cake_recipes]))
    # icing_recipes = [{"vanilla icing": 1}, {"cream cheese icing": 1}]
    # print(combined_flat_recipes([cake_recipes, icing_recipes]))
    # topping_recipes = [{"sprinkles": 20}]
    # print(combined_flat_recipes([cake_recipes, icing_recipes, topping_recipes]))

    cookie_recipes = [
        ('compound', 'cookie sandwich', [('cookie', 2), ('ice cream scoop', 3)]),
        ('compound', 'cookie', [('chocolate chips', 3)]),
        ('compound', 'cookie', [('sugar', 10)]),
        ('atomic', 'chocolate chips', 200),
        ('atomic', 'sugar', 5),
        ('compound', 'ice cream scoop', [('vanilla ice cream', 1)]),
        ('compound', 'ice cream scoop', [('chocolate ice cream', 1)]),
        ('atomic', 'vanilla ice cream', 20),
        ('atomic', 'chocolate ice cream', 30),
    ]
    # print(all_flat_recipes(cookie_recipes, 'cookie sandwich'))
    print(cheapest_flat_recipe(cookie_recipes, 'cookie sandwich'))
