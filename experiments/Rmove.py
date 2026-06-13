



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

    #my_tuple = ((1,(2,3)),(4,5))
    #anyon1 = 3
    #anyon2 = 2

    
 



    anyon1 = anyon(1)
    anyon2 = anyon(2)
    anyon3 = anyon(3)
    anyon4 = anyon(4)
    anyon5 = anyon(5)
    anyon6 = anyon(6)

    
    check_id1 = 2
    check_id2 = 1

    #my_tuple = ((anyon1, anyon2),(anyon3, anyon4))
    my_tuple = (((anyon1, anyon2), anyon3), (anyon4, anyon5))
    my_tuple = ((((((anyon1, anyon2))))))


    print(f"before swap: {my_tuple}")

    my_tuple = swap_siblings(my_tuple, check_id1, check_id2)
    
    print(f"after swap: {my_tuple}")



    """
    x = is_siblings(my_tuple, anyon1, anyon2)

    if x:
        print("hell yeaa")
    else:
        print('XXXXXXXX')
        """


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


def swap_siblings(tree, id1, id2):
    if not is_siblings(tree, id1, id2):
        print("Not siblings — need F move before R")
        return tree

    def swap_recursive(node):
        if not isinstance(node, tuple):
            return node

        left, right = node

        if not isinstance(left, tuple) and not isinstance(right, tuple):
            if {left.getid(), right.getid()} == {id1, id2}:
                return (right, left)

        return tuple(swap_recursive(x) for x in node)

    return swap_recursive(tree)



main()


