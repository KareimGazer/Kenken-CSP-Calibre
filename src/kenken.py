import csp
from sys import stderr, stdin
from itertools import product, permutations
from functools import reduce
from random import seed, random, shuffle, randint, choice
from time import time
import csv


def operation(operator):
    """
    A utility function used in order to determine the operation corresponding
    to the operator that is given in string format
    """
    if operator == '+':
        return lambda a, b: a + b
    elif operator == '-':
        return lambda a, b: a - b
    elif operator == '*':
        return lambda a, b: a * b
    elif operator == '/':
        return lambda a, b: a / b
    else:
        return None


def adjacent(xy1, xy2):
    """
    Checks wheither two positions represented in 2D coordinates are adjacent
    """
    x1, y1 = xy1
    x2, y2 = xy2
    dx, dy = x1 - x2, y1 - y2
    return (dx == 0 and abs(dy) == 1) or (dy == 0 and abs(dx) == 1)


def generate(size):
    """
    Generate a random kenken puzzle of the given size
      * Initially create a latin square of size 'size' and elements the values [1...size]
      * Shuffle the board by rows and columns in order to get a somewhat random
        board that still satisfies the different row-col constraint of kenken
      * Initialize the 'uncaged' set with all cell coordinates
      * Proceed in creating cliques:
        * Randomly choose a clique size in the range [1..4]
        * Set the first cell in the 'uncaged' set in row major order as
          the root cell of the clique and remove it from the 'uncaged' set
        * Randomly visit at most 'clique-size' 'uncaged' adjacent cells
          in random directions while adding them to the current clique
          and removing them from the 'uncaged' cells
        * The size of the resulting clique is:
          * == 1:
            there is no operation to be performed and the target of the clique
            is equal to the only element of the clique
          * == 2:
            * if the two elements of the clique can be divided without a remainder
              then the operation is set to division and the target is the quotient
            * otherwise, the operation is set to subtraction and the target is the
              difference of the elements
          * >  2:
           randomly choose an operation between addition and multiplication.
            The target of the operation is the result of applying the decided
            operation on all the elements of the clique
        * Continue until the 'uncaged' set is empty i.e. there is no cell belonging
          to no clique
    """
    # returns indicies
    board = [[((i + j) % size) + 1 for i in range(size)] for j in range(size)]
    for _ in range(size):
        shuffle(board)

    for c1 in range(size):
        for c2 in range(size):
            if random() > 0.5:
                for r in range(size):
                    board[r][c1], board[r][c2] = board[r][c2], board[r][c1]

    board = {(j + 1, i + 1): board[i][j]
             for i in range(size) for j in range(size)}
    uncaged = sorted(board.keys(), key=lambda var: var[1])
    cliques = []
    while uncaged:
        cliques.append([])
        csize = randint(1, 4)
        cell = uncaged[0]
        uncaged.remove(cell)
        cliques[-1].append(cell)
        for _ in range(csize - 1):
            adjs = [other for other in uncaged if adjacent(cell, other)]
            cell = choice(adjs) if adjs else None
            if not cell:
                break
            uncaged.remove(cell)
            cliques[-1].append(cell)
        csize = len(cliques[-1])

        if csize == 1:
            cell = cliques[-1][0]
            cliques[-1] = ((cell, ), '.', board[cell])
            continue
        elif csize == 2:
            fst, snd = cliques[-1][0], cliques[-1][1]
            if board[fst] / board[snd] > 0 and not board[fst] % board[snd]:
                operator = "/"  # choice("+-*/")
            else:
                operator = "-"  # choice("+-*")
        else:
            operator = choice("+*")

        target = reduce(operation(operator), [
                        board[cell] for cell in cliques[-1]])
        cliques[-1] = (tuple(cliques[-1]), operator, int(target))
    return size, cliques


# may not need parse and validate
# to be moved to a special file
def parse(lines):
    """
    Used in order to parse a non-generated / handmade kenken puzzle
    given in string / list of strings format
    """
    # check if the input is string
    if isinstance(lines, str):
        lines = lines.splitlines(True)

    try:
        content = lines[0][:-1]
        size = int(content)
    except:
        print("Unable to determine board size [", content, "]", file=stderr)
        exit(11)

    cliques = []
    for line in lines[1:]:
        content = line[:-1]  # line string
        if content:
            try:
                # evaluate makes it possible to index tuples,operators, and attributes as objects
                clique = eval(content)
                cliques.append(clique)
            except:
                print("Malformed clique [", content, "]")
                exit(12)

    return size, cliques


# it could be a method in kenken class but it's global for global usage
def validate(size, cliques):
    """
    Validate the integrity of the input as a kenken board
      * For each of the cliques:
        * Remove duplicate members of the clique at hand
        * Check whether the specified operator is acceptable or not
        * Check if any of the members of the clique are out of bounds
        * Check if any member of the clique is mentioned in any other clique
      * Check if the given cliques cover the whole board or not
    """
    def outOfBounds(
        xy): return xy[0] < 1 or xy[0] > size or xy[1] < 1 or xy[1] > size
    mentioned = set()
    for i in range(len(cliques)):
        members, operator, target = cliques[i]
        cliques[i] = (tuple(set(members)), operator, target)
        members, operator, target = cliques[i]
        if operator not in "+-*/.":
            print("Operation", operator, "of clique",
                  cliques[i], "is unacceptable", file=stderr)
            exit(1)
        problematic = list(filter(outOfBounds, members))
        if problematic:
            print("Members", problematic, "of clique",
                  cliques[i], "are out of bounds", file=stderr)
            exit(2)
        problematic = mentioned.intersection(set(members))
        if problematic:
            print("Members", problematic, "of clique",
                  cliques[i], "are cross referenced", file=stderr)
            exit(3)
        mentioned.update(set(members))

    indexes = range(1, size + 1)
    problematic = set([(x, y)
                      for y in indexes for x in indexes]).difference(mentioned)
    if problematic:
        print("Positions", problematic,
              "were not mentioned in any clique", file=stderr)
        exit(4)


def RowXorCol(xy1, xy2):
    """
    Evaluates to true if the given positions are in the same row / column
    but are in different columns / rows "row or col adj"
    """
    return (xy1[0] == xy2[0]) != (xy1[1] == xy2[1])


def conflicting(A, a, B, b):
    """
    Evaluates to true if:
      * there exists mA so that ma is a member of A and
      * there exists mb so that mb is a member of B and
      * RowXorCol(mA, mB) evaluates to true and
      * the value of mA in 'assignment' a is equal to
        the value of mb in 'assignment' b
    """
    for i in range(len(A)):
        for j in range(len(B)):
            mA = A[i]
            mB = B[j]

            ma = a[i]
            mb = b[j]
            if RowXorCol(mA, mB) and ma == mb:
                return True

    return False


def satisfies(values, operation, target):
    """
    Evaluates to true if the result of applying the operation
    on a permutation of the given values is equal to the specified target
    """
    for p in permutations(values):
        if reduce(operation, p) == target:
            return True

    return False


def gdomains(size, cliques):
    """
    @ https://docs.python.org/2/library/itertools.html
    @ product('ABCD', repeat=2) = [AA AB AC AD BA BB BC BD CA CB CC CD DA DB DC DD]

    For every clique in cliques:
        * Initialize the domain of each variable to contain every product
        of the set [1...board-size] that are of length 'clique-size'.
        For example:

            board-size = 3 and clique-size = 2

            products = [(1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (2, 3), (3, 1), (3, 2), (3, 3)]

        * Discard any value (assignment of the members of the clique) that:
        * is resulting in the members of the clique 'conflicting' with each other
        * does not 'satisfy' the given operation
    """
    domains = {}
    for clique in cliques:
        members, operator, target = clique
        domains[members] = list(
            product(range(1, size + 1), repeat=len(members)))

        def qualifies(values): return not conflicting(
            members, values, members, values) and satisfies(values, operation(operator), target)
        domains[members] = list(filter(qualifies, domains[members]))
    return domains


def gneighbors(cliques):
    """
    Determine the neighbors of each variable for the given puzzle
        For every clique in cliques
        * Initialize its neighborhood as empty
        * For every clique in cliques other than the clique at hand,
            if they are probable to 'conflict' they are considered neighbors
    """
    neighbors = {}
    for members, _, _ in cliques:
        neighbors[members] = []

    for A, _, _ in cliques:
        for B, _, _ in cliques:
            if A != B and B not in neighbors[A]:
                if conflicting(A, [-1] * len(A), B, [-1] * len(B)):
                    neighbors[A].append(B)
                    neighbors[B].append(A)

    return neighbors


class Kenken(csp.CSP):

    def __init__(self, size, cliques):
        """
        In my implementation, I consider the cliques themselves as variables.
        A clique is of the format (((X1, Y1), ..., (XN, YN)), <operation>, <target>)
        where
            * (X1, Y1), ..., (XN, YN) are the members of the clique
            * <operation> is either addition, subtraction, division or multiplication
            * <target> is the value that the <operation> should produce
              when applied on the members of the clique
        """
        validate(size, cliques)
        variables = [members for members, _, _ in cliques]
        domains = gdomains(size, cliques)
        neighbors = gneighbors(cliques)
        csp.CSP.__init__(self, variables, domains, neighbors, self.constraint)
        self.size = size

        # Used in assessing performance
        self.checks = 0
        # Used in displaying
        self.padding = 0
        self.meta = {}
        for members, operator, target in cliques:
            self.meta[members] = (operator, target)
            self.padding = max(self.padding, len(str(target)))

    def constraint(self, A, a, B, b):
        """
        Any two variables satisfy the constraint if they are the same
        or they are not 'conflicting' i.e. every member of variable A
        which shares the same row or column with a member of variable B
        must not have the same value assigned to it
        """
        self.checks += 1
        return A == B or not conflicting(A, a, B, b)

    def display(self, assignment):
        """
        Print the kenken puzzle in a format easily readable by a human
        """
        if assignment:
            atomic = {}
            for members in self.variables:
                values = assignment.get(members)

                if values:
                    for i in range(len(members)):
                        atomic[members[i]] = values[i]
                else:
                    for member in members:
                        atomic[member] = None
        else:
            atomic = {
                member: None for members in self.variables for member in members}

        atomic = sorted(
            atomic.items(), key=lambda item: item[0][1] * self.size + item[0][0])

        def padding(c, offset): return (c * (self.padding + 2 - offset))
        def embrace(inner, beg, end): return beg + inner + end
        mentioned = set()

        # why not used lambda?
        def meta(member):
            for var, val in self.meta.items():
                if member in var and var not in mentioned:
                    mentioned.add(var)
                    return str(val[1]) + " " + (val[0] if val[0] != "." else " ")

            return ""

        def fit(word): return padding(" ", len(word)) + word + padding(" ", 0)
        cpadding = embrace(2 * padding(" ", 0), "|", "") * self.size + "|"

        # why not used lambda?
        def show(row):
            rpadding = "".join(["|" + fit(meta(item[0]))
                               for item in row]) + "|"
            data = "".join(["|" + fit(str(item[1] if item[1] else ""))
                           for item in row]) + "|"
            print(rpadding, data, cpadding, sep="\n")

        rpadding = embrace(2 * padding("-", 0), "+", "") * self.size + "+"
        print(rpadding)
        for i in range(1, self.size + 1):
            show(list(filter(lambda item: item[0][1] == i, atomic)))
            print(rpadding)

    def info(self):
        """
        Print debugging info
        """

        print("\nVariables:")
        for var in self.variables:
            print(var)

        print("\nDomains:")
        for var in self.variables:
            print("domains[", var, "] =", self.domains[var])

        print("\nNeighbors:")
        for var in self.variables:
            print("neighbors[", var, "] =", self.neighbors[var])


def assess_performance(kenken, algorithm):
    """Used in order to assess the performance of the given algorithm in terms of
        * The number of nodes it visits
        * The number of constraint checks it performs
        * The number of assignments it performs
        * The completion time
        Parameters:
          * kenken: kenken puzzel object
          * algorithm: the algorithm to solve the puzzel"""
    kenken.checks, kenken.nassigns = 0, 0
    initial_time = time()
    algorithm(kenken)
    final_time = time()
    elapsed_time = final_time - initial_time
    return kenken.checks, kenken.nassigns, elapsed_time


def get_algorithm(is_mrv, is_lcv, algo):
    unassigned_variable_selection = None
    domain_values_order = None
    algorithm = None

    if is_mrv:
        unassigned_variable_selection = csp.mrv
    else:
        unassigned_variable_selection = csp.first_unassigned_variable
    if is_lcv:
        domain_values_order = csp.lcv
    else:
        domain_values_order = csp.unordered_domain_values

    # vannila backtracking
    if algo == "BT":
        def bt(ken): return csp.backtracking_search(ken,
                                                    select_unassigned_variable=unassigned_variable_selection,
                                                    order_domain_values=domain_values_order,
                                                    inference=csp.no_inference)
        algorithm = bt
    elif algo == "FC":
        # forward checking (backtracking + forward checking)
        def fc(ken): return csp.backtracking_search(ken, select_unassigned_variable=unassigned_variable_selection,
                                                    order_domain_values=domain_values_order, inference=csp.forward_checking)
        algorithm = fc

    elif "MAC":
        # maintain arc consistency (backtracking + arc consistency)
        def mac(ken): return csp.backtracking_search(ken, select_unassigned_variable=unassigned_variable_selection,
                                                     order_domain_values=domain_values_order, inference=csp.mac)
        algorithm = mac

    return algorithm


def configure_algorithms(is_mrv, is_lcv, is_BT, is_FC, is_MAC):
    unassigned_variable_selection = None
    domain_values_order = None
    algorithms = dict()

    if is_mrv:
        unassigned_variable_selection = csp.mrv
    else:
        unassigned_variable_selection = csp.first_unassigned_variable
    if is_lcv:
        domain_values_order = csp.lcv
    else:
        domain_values_order = csp.unordered_domain_values

    # vannila backtracking
    if is_BT:
        def bt(ken): return csp.backtracking_search(ken,
                                                    select_unassigned_variable=unassigned_variable_selection,
                                                    order_domain_values=domain_values_order,
                                                    inference=csp.no_inference)
        algorithms['BT'] = bt

    if is_FC:
        # forward checking (backtracking + forward checking)
        def fc(ken): return csp.backtracking_search(ken, select_unassigned_variable=unassigned_variable_selection,
                                                    order_domain_values=domain_values_order, inference=csp.forward_checking)
        algorithms['FC'] = fc

    if is_MAC:
        # maintain arc consistency (backtracking + arc consistency)
        def mac(ken): return csp.backtracking_search(ken, select_unassigned_variable=unassigned_variable_selection,
                                                     order_domain_values=domain_values_order, inference=csp.mac)
        algorithms['MAC'] = mac

    return algorithms


def gather_info(max_board_size, iterations, out_file, algorithms):
    """Benchmark each one of the following algorithms for various kenken puzzles
      * For every one of the following algorithms
       * For every possible size of a kenken board
         * Create 'iterations' random kenken puzzles of the current size
           and evaluate the algorithm on each one of them in order to get
           statistically sound data. Then calculate the average evaluation
           of the algorithm for the current size.
      * Save the results into a csv file
      Parameters:
          * iterations: number of iterations to average over
          * out_file: the location of the outputfile
          * max_board_size: max board size to run test on"""

    with open(out_file, "w", newline='') as csvfile:
        out_writer = csv.writer(csvfile)
        out_writer.writerow(["Algorithm Name", "Size", "Constraint checks",
                             "no. of Assignments", "Running time"])
        for name, algorithm in algorithms.items():
            for size in range(3, max_board_size+1):
                average_constraint_checks, average_assignments_num, average_elapsed_time = 0, 0, 0
                for iteration in range(1, iterations + 1):
                    size, cliques = generate(size)
                    kenken_puzzle = Kenken(size, cliques)
                    constraint_checks, assigments_num, elapsed_time = assess_performance(
                        kenken_puzzle, algorithm)
                    average_constraint_checks += constraint_checks / iterations
                    average_assignments_num += assigments_num / iterations
                    average_elapsed_time += elapsed_time / iterations
                out_writer.writerow(
                    [name, size, round(average_constraint_checks), round(average_assignments_num), round(average_elapsed_time, 4)])
