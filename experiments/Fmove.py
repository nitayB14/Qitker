



class anyon:

    def __init__(self, anyon_id):
        self.anyon_id = anyon_id

    def __str__(self):
        return str(self.anyon_id)

    def __repr__(self):
        return str(self.anyon_id)

    def getid(self):
        return self.anyon_id

def main():

    anyon1 = anyon(1)
    anyon2 = anyon(2)
    anyon3 = anyon(3)
    anyon4 = anyon(4)
    anyon5 = anyon(5)
    anyon6 = anyon(6)

    
    check_id1 = 2
    check_id2 = 1

    my_tuple = ((anyon1, anyon2),(anyon3, anyon4))
    #my_tuple = (((anyon1, anyon2), anyon3), (anyon4, anyon5))
    

    print(f"before swap: {my_tuple}")

    my_tuple = bring_to_same_subgroup(my_tuple, 2, 3)
    
    print(f"after swap: {my_tuple}")

    my_tuple = restore_pair_basis(my_tuple)
    
    print(f"return to normal: {my_tuple}")


    

###########################################################################################################
def is_siblings(my_tuple, anyon1, anyon2):

    are_they = False
    count = 0

    if(anyon1 == anyon2):
        return False

    for item in my_tuple:
        if isinstance(item, tuple):
            are_they = is_siblings(item, anyon1, anyon2)
        else:
            if item.getid() == anyon1 or item.getid() == anyon2:
                count += 1
            
        if count == 2 or are_they:
            return True

    return are_they

##########################################################################
def flatten_tree(tree):
    if not isinstance(tree, tuple):
        return [tree]

    result = []
    for child in tree:
        result.extend(flatten_tree(child))
    return result


def build_tree_with_pair(items, id1, id2):
    result = []

    i = 0
    while i < len(items):
        current = items[i]

        if i + 1 < len(items):
            next_item = items[i + 1]

            if {current.getid(), next_item.getid()} == {id1, id2}:
                result.append((current, next_item))
                i += 2
                continue

        result.append(current)
        i += 1

    tree = result[0]
    for item in result[1:]:
        tree = (tree, item)

    return tree


def bring_to_same_subgroup(tree, id1, id2):
    items = flatten_tree(tree)

    ids = [x.getid() for x in items]

    if id1 not in ids or id2 not in ids:
        raise ValueError("One of the anyons does not exist in the tree")

    return build_tree_with_pair(items, id1, id2)

############################################################################################
def restore_pair_basis(tree):
    items = flatten_tree(tree)

    if len(items) % 2 != 0:
        raise ValueError("Cannot restore pair basis with odd number of anyons")

    pairs = []

    for i in range(0, len(items), 2):
        pairs.append((items[i], items[i + 1]))

    # אם יש רק זוג אחד
    if len(pairs) == 1:
        return pairs[0]

    # בונה עץ מזוגות
    new_tree = pairs[0]
    for pair in pairs[1:]:
        new_tree = (new_tree, pair)

    return new_tree



main()


