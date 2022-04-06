import random

#
scpu = 0
splayer = 0


#   Single player                                    #
def singleplayer():
    print("####################################")
    print("Rock, Paper, Scissors: Singleplayer")
    print("####################################")
    rpscpu()


#   CPU FUNCTIONS
def rpscpu():
    comp_possible = 1, 2, 3
    comp_choice = random.choice(comp_possible)
    if comp_choice == 1:
        computer_choice_rock()
    elif comp_choice == 2:
        computer_choice_paper()
    else:
        computer_choice_scissors()
    return comp_choice


#   CPU selects rock
def computer_choice_rock():
    global scpu
    global splayer
    user_choice = int(input("1 for rock, 2 for paper, 3 for scissors: "))
    if user_choice == 1:
        print("####################################")
        print("Tie - You and the CPU chose Rock")
        scpu += 1
        splayer += 1
        try_again()
    if user_choice == 2:
        print("####################################")
        print("Win - You selected Paper. CPU selected Rock")
        splayer += 1
        try_again()
    if user_choice == 3:
        print("####################################")
        print("Lose - You selected scissors. CPU selected Rock")
        scpu += 1
        try_again()
    else:
        print("Try again")
        computer_choice_rock()


#   CPU selects paper #rock crushes scissors, paper covers rock, scissors cut paper.
def computer_choice_paper():
    global scpu
    global splayer
    user_choice = int(input("1 for rock, 2 for paper, 3 for scissors: "))
    if user_choice == 1:
        print("####################################")
        print("Lose - You selected rock. CPU selected paper")
        scpu += 1
        try_again()
    if user_choice == 2:
        print("####################################")
        print("Tie - You and the CPU chose paper")
        scpu += 1
        splayer += 1
        try_again()
    if user_choice == 3:
        print("####################################")
        print("Win - You selected scissors. CPU selected paper")
        splayer += 1
        try_again()
    else:
        print("Try again")
        computer_choice_paper()


#   CPU selects scissors
def computer_choice_scissors():
    global scpu
    global splayer
    user_choice = int(input("1 for rock, 2 for paper, 3 for scissors: "))
    if user_choice == 1:
        print("####################################")
        print("Win - You selected rock. CPU selected scissors")
        splayer += 1
        try_again()
    if user_choice == 2:
        print("####################################")
        print("Lose - You selected Paper. CPU selected scissors")
        scpu += 1
        try_again()
    if user_choice == 3:
        print("####################################")
        print("Tie - You selected scissors. CPU selected scissors")
        scpu += 1
        splayer += 1
        try_again()
    else:
        print("Try again")
        computer_choice_rock()


#   Single player try again function
def try_again():
    global scpu
    global splayer
    print("####################################")
    print("Current Scores: \nPlayer 1: ", splayer, " | CPU: ", scpu)
    print("####################################")
    choice = input("Would you like to play again or return to menu? Y/N/M?: ")
    if choice == "y" or choice == "Y" or choice == "yes":
        rpscpu()
    elif choice == "n" or choice == "N" or choice == "no":
        print("Thanks for playing!")
        quit()
    # if choice == "M" or choice == "m" or choice == "menu":
    #     welcome()
    else:
        print("Try again")
        try_again()
