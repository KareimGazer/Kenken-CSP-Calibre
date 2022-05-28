from kenken import *


if __name__ == "__main__":

    # gather_info(3, "kenken.csv", 5)

    # you may add the utility to write this as a string into
    # a file to save or load the game
    # this can be used as the template of the object bassed to the GUI
    example = \
        "6\n"\
        "(((1, 1), (1, 2)), '+', 11)\n"\
        "(((2, 1), (3, 1)), '/', 2)\n"\
        "(((2, 2), (3, 2)), '-', 3)\n"\
        "(((4, 1), (4, 2)), '*', 20)\n"\
        "(((5, 1), (6, 1), (6, 2), (6, 3)), '*', 6)\n"\
        "(((5, 2), (5, 3)), '/', 3)\n"\
        "(((1, 3), (1, 4), (2, 3), (2, 4)), '*', 240)\n"\
        "(((3, 3), (4, 3)), '*', 6)\n"\
        "(((5, 4), (6, 4)), '*', 30)\n"\
        "(((1, 5), (2, 5)), '*', 6)\n"\
        "(((3, 4), (3, 5)), '*', 6)\n"\
        "(((4, 4), (4, 5), (5, 5)), '+', 7)\n"\
        "(((1, 6), (2, 6), (3, 6)), '+', 8)\n"\
        "(((4, 6), (5, 6)), '/', 2)\n"\
        "(((6, 5), (6, 6)), '+', 9)\n"

    # size, cliques = generate(3)
    # ken = Kenken(size, cliques)
    # assignment = csp.backtracking_search(ken)
    # print(assignment)  # (col, row)
    # ken.display(assignment)
