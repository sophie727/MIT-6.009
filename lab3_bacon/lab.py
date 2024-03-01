"""
6.101 Lab 3:
Bacon Number
"""

#!/usr/bin/env python3

import pickle

# NO ADDITIONAL IMPORTS ALLOWED!

def get_key_from_val(dictionary, val):
    """
    INPUT: dictionary (dict), val
    OUTPUT: the key for the val in the dict
    """
    for key, value in dictionary.items():
        if value == val:
            return key
    return None

def get_names_from_ids(names_dict, id_list):
    """
    INPUT: names_dict (dict), id_list (list of ints)
    OUTPUT: a list of names corresponding to the ids
    """
    return [get_key_from_val(names_dict, id) for id in id_list]

def add_to_dict(dict_data, actor1, actor2, film):
    """
    This is a helper function because apparently
    my code is too complex so rood
    """
    if actor1 in dict_data:
        mini_dict = dict_data[actor1]
        if actor2 in mini_dict:
            mini_dict[actor2].add(film)
        else:
            mini_dict[actor2] = {film}
    else:
        dict_data[actor1] = {actor2: {film}}

def transform_data(raw_data):
    """
    Transforms data into a form that's easier to work with.
    In this case, we will put it into a nested dictionary.
    The keys in the outer dictionary are all the actors, 
    and the values at the keys are dictionaries. The keys
    of the inner dictionaries are the actors that acted
    with the key actor from before, and the innermost
    value is the set of all movies they acted in. That is, 
    we might have
    {(bob's id): {(alice's id): {"Alice in Wonderland"}}}
    """
    dict_data = {}

    for (a1, a2, film) in raw_data:
        add_to_dict(dict_data, a1, a2, film)
        add_to_dict(dict_data, a2, a1, film)

    return dict_data

def acted_together(transformed_data, actor_id_1, actor_id_2):
    """
    INPUT: transformed_data (dict of dicts), actor_id_1 (int), and actor_id_2 (int)
    OUTPUT: whether they've acted together (bool)
    By definition, everyone has acted with themselves.
    """
    return (actor_id_1 == actor_id_2) or (actor_id_2 in transformed_data[actor_id_1])

def actors_with_bacon_number(transformed_data, n):
    """
    INPUT: transformed_data (dict of dicts), n (int)
    OUTPUT: all actor ids with a bacon number of n in the dataset
    """
    visited = {4724} # this just says you've visited bacon already
    just_visited = {4724} # just_visited = all actors visited in the prev iteration
    for _ in range(n):
        if just_visited == set():
            break
        temp_just_visited = set()
        for actor in just_visited:
            for actor2 in transformed_data[actor]:
                if actor2 not in visited:
                    visited.add(actor2)
                    temp_just_visited.add(actor2)
        just_visited = temp_just_visited
    return just_visited

def bacon_path(transformed_data, actor_id):
    """
    INPUT: transformed_data (dict of dicts), actor_id (int)
    OUTPUT: bacon_path (list) consisting of the actors
            (inclusive) that would make up the path
            from actor 1 to actor 2.
    """
    return actor_to_actor_path(transformed_data, 4724, actor_id)

def actor_to_actor_path(transformed_data, actor_id_1, actor_id_2):
    """
    INPUT: transformed_data (dict of dicts), actor_id_1 (int),
           actor_id_2 (int)
    OUTPUT: actor_to_actor_path (list) consisting of the actors
            (inclusive) that would make up the path from
            actor 1 to actor 2.
    """
    def check_actor_is_actor_2(actor_id):
        return actor_id == actor_id_2
    path = actor_path(transformed_data, actor_id_1, check_actor_is_actor_2)
    return path

def movies_of_actor_to_actor_path(transformed_data,movies_data,actor_id_1,actor_id_2):
    """
    INPUT: transformed_data (dict of dicts), movies_data (dict),
           actor_id_1 (int), actor_id_2 (int)
    OUTPUT: List of movies (names) that correspond to the actors
            that would make up the path from actor 1 to actor 2.
    """
    path = actor_to_actor_path(transformed_data, actor_id_1, actor_id_2)
    movies_path = []
    for i in range(len(path) - 1):
        movie = list(transformed_data[path[i]][path[i + 1]])[0]
        movies_path.append(movie)
    return get_names_from_ids(movies_data, movies_path)

def actor_path(transformed_data, actor_id_1, goal_test_function):
    """
    INPUT: transformed_data (dict of dicts), actor_id_1 (int),
           goal_test_function
    OUTPUT: actor_path (list) consisting of the actors (inclusive)
            that would make up the shortest path from actor 1 to
            any actor that satisfies goal_test_function.
    """
    return actors_path(transformed_data, {actor_id_1}, goal_test_function)

def actors_path(transformed_data, actor_ids_1, goal_test_function):
    """
    INPUT: transformed_data (dict of dicts), actor_ids_1 (set),
           goal_test_function
    OUTPUT: path (list) consisting of the actors (inclusive)
            that would make up the shortest path from any actor
            in the set actor_ids_1 to any actor that satisfies
            goal_test_function.
    """
    visited_tree = {actor: None for actor in actor_ids_1} # dict = {child: parent,}
    just_visited = actor_ids_1
    goal_actor = None
    for actor in actor_ids_1:
        if goal_test_function(actor):
            return [actor]
    while (goal_actor is None) and just_visited:
        temp_just_visited = set()
        for actor in just_visited:
            for actor2 in transformed_data[actor]:
                if actor2 not in visited_tree:
                    visited_tree[actor2] = actor
                    temp_just_visited.add(actor2)
                    if goal_test_function(actor2):
                        goal_actor = actor2
        just_visited = temp_just_visited

    if goal_actor is not None:
        path = [goal_actor]
        curr_actor = goal_actor
        while curr_actor not in actor_ids_1:
            curr_actor = visited_tree[curr_actor]
            path.append(curr_actor)
        path.reverse()
        return path

def actors_in_film(transformed_data, film):
    """
    This is a helper function because apparently
    my code is too complex so rood
    """
    film_actors = set()
    for actor1 in transformed_data:
        for actor2 in transformed_data[actor1]:
            if film in transformed_data[actor1][actor2]:
                film_actors.add(actor1)
                film_actors.add(actor2)
    return film_actors

def actors_connecting_films(transformed_data, film1, film2):
    """
    INPUT: transformed_data (dict of dicts), film1 (int),
           film2 (int)
    OUTPUT: shortest_path (list) consisting of the actors (inclusive)
            that would make up the shortest path from any actor in
            the first film to any actor in the second film.
    """
    film1_actors = actors_in_film(transformed_data, film1)
    film2_actors = actors_in_film(transformed_data, film2)

    def actor_in_film2(actor):
        return actor in film2_actors

    return actors_path(transformed_data, film1_actors, actor_in_film2)

if __name__ == "__main__":
    with open("resources/small.pickle", "rb") as f:
        smalldb = pickle.load(f)

    with open("resources/large.pickle", "rb") as f:
        largedb = pickle.load(f)

    with open("resources/names.pickle", "rb") as f:
        names = pickle.load(f)

    with open("resources/movies.pickle", "rb") as f:
        movies = pickle.load(f)
    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.

    # online questions

    # print (names['Sven-Bertil Taube']) # prints 87723
    # print (get_key_from_val(names, 27929)) # prints Percy Marmont

    # transformed_smalldb = transform_data(smalldb)
    transformed_largedb = transform_data(largedb)

    # acted_together?

    # actor1 = names["Ewa Froling"]
    # actor2 = names["Stellan Skarsgard"]
    # print(acted_together(transformed_smalldb, actor1, actor2)) # prints True

    # actor1 = names["Anya Benton"]
    # actor2 = names["Dominique Reymond"]
    # print(acted_together(transformed_smalldb, actor1, actor2)) # prints False

    # bacon number?

    # print(actors_with_bacon_number(transformed_smalldb, 0)) # prints {4724}
    # bnums = actors_with_bacon_number(transformed_tinydb, 6)
    # bnum_names = set()
    # for actorid in bnums:
    #     bnum_names.add(get_key_from_val(names, actorid))
    # print(bnum_names)

    # bacon path

    # print(bacon_path(transformed_tinydb, 1640))
    # edna_bp = bacon_path(transformed_tinydb, names["Edna Holland"])
    # print("hi")
    # ans = []
    # for actorid in edna_bp:
    #     ans.append(get_key_from_val(names, actorid))
    # print(ans)

    # actor1 = names["Paul Dalleluche"]
    # actor2 = names["Emily Ann Lloyd"]
    # path = actor_to_actor_path(transformed_largedb, actor1, actor2)
    # print(get_names_from_ids(names, path))

    # actor1 = names["Linda Cardellini"]
    # actor2 = names["Sven Batinic"]
    # path = movies_of_actor_to_actor_path(transformed_largedb, movies, actor1, actor2)
    # print(path)
    # print("movie ids:", movies["Good Burger"], movies["7 Hours Later"])

    # movie1 = 14817
    # movie2 = 295215
    # mov_path = actors_connecting_films(transformed_largedb, movie1, movie2)
    # print(mov_path)

    # random things

    # test_data = [(1, 2, "Wonderland"), (1, 2, "batman"), (1, 3, "fairyland")]
    # print(transform_data(test_data))

    # print(smalldb)
    # print(acted_together(transformed_smalldb, 1168416, 37612))

    pass
