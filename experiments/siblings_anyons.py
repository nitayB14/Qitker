





def main():

    #my_tuple = ((1,(2,3)),(4,5))
    #anyon1 = 3
    #anyon2 = 2

    
    my_tuple = (
    (((1, 2), (3, 4)),
     ((5, 6), (7, 8)))
)
    anyon1 = 2
    anyon2 = 8

    x = is_siblings(my_tuple, anyon1, anyon2)

    if x:
        print("hell yeaa")
    else:
        print('XXXXXXXX')



def is_siblings(my_tuple, anyon1, anyon2):

    are_they = False
    count = 0

    if(anyon1 == anyon2):
        return False

    for item in my_tuple:
        if isinstance(item, tuple):
            are_they = is_siblings(item, anyon1, anyon2)
        else:
            if item == anyon1 or item == anyon2:
                count += 1
            
        if count == 2 or are_they:
            return True

    return are_they

main()


