#   Start Multi player function
#

# set up scores
mplayer1 = 0
mplayer2 = 0


# multiplayer function
def multiplayer():
    print("####################################")
    print("Rock, Paper, Scissors: Multiplayer")
    print("####################################")
    p1_count = 0
    print("PLAYER 1 GOES FIRST ...")
    p1_in = (input("R FOR ROCK, P FOR PAPER, S FOR SCISSORS: "))
    while p1_count != 50:
        if p1_in == "R" or p1_in == "P" or p1_in == "S" or p1_in == "r" or p1_in == "p" or p1_in == "s":
            print(" ")
            p1_count = p1_count+1
    else:
        if p1_in == "R" or p1_in == "r" or p1_in == "Rock" or p1_in == "rock":
            p1_rock()
        elif p1_in == "P" or p1_in == "p" or p1_in == "Paper" or p1_in == "paper":
            p1_paper()
        if p1_in == "S" or p1_in == "s" or p1_in == "Scissors" or p1_in == "scissors":
            p1_scissors()
        else:
            print("Player 1 input not recognised. Try again")
            p1_in = (input("R FOR ROCK, P FOR PAPER, S FOR SCISSORS: "))


#   Player 1 selects rock
def p1_rock():
    global mplayer1
    global mplayer2
    print("YOUR TURN PLAYER 2>>>")
    p2_in = (input("R FOR ROCK, P FOR PAPER, S FOR SCISSORS: "))
    if p2_in == "R" or p2_in == "r" or p2_in == "Rock" or p2_in == "rock":
        print("####################################")
        print("Tie - You both selected Rock")
        mplayer1 = mplayer1+1
        mplayer2 = mplayer2+1
        sptry_again()
    elif p2_in == "P" or p2_in == "p" or p2_in == "Paper" or p2_in == "paper":
        print("####################################")
        print("Win - You selected Paper. Player 1 selected Rock")
        mplayer2 = mplayer2+1
        sptry_again()
    if p2_in == "S" or p2_in == "s" or p2_in == "Scissors" or p2_in == "scissors":
        print("####################################")
        print("Lose - You selected scissors. Player 1 selected Rock")
        mplayer1 = mplayer1+1
        sptry_again()
    else:
        print("Try again")
        p1_rock()


#   p1 selects paper
def p1_paper():
    global mplayer1
    global mplayer2
    print("YOUR TURN PLAYER 2>>>")
    p2_in = (input("R FOR ROCK, P FOR PAPER, S FOR SCISSORS: "))
    if p2_in == "R" or p2_in == "r" or p2_in == "Rock" or p2_in == "rock":
        print("####################################")
        print("Lose - Player 2 selected rock. Player 1 selected paper")
        mplayer1 = mplayer1+1
        sptry_again()
    elif p2_in == "P" or p2_in == "p" or p2_in == "Paper" or p2_in == "paper":
        print("####################################")
        print("Tie - You both selected paper")
        mplayer1 = mplayer1+1
        mplayer2 = mplayer2+1
        sptry_again()
    if p2_in == "S" or p2_in == "s" or p2_in == "Scissors" or p2_in == "scissors":
        print("####################################")
        print("Win - Player 2 selected scissors. Player 1 selected Paper")
        mplayer2 += 1
        sptry_again()
    else:
        print("Try again")
        p1_rock()


#   p1 selects scissors
def p1_scissors():
    global mplayer1
    global mplayer2
    print("YOUR TURN PLAYER 2>>>")
    p2_in = (input("R FOR ROCK, P FOR PAPER, S FOR SCISSORS: "))
    if p2_in == "R" or p2_in == "r" or p2_in == "Rock" or p2_in == "rock":
        print("####################################")
        print("Win - Player 2 selected rock. Player 1 selected scissors")
        mplayer2 += 1
        sptry_again()
    elif p2_in == "P" or p2_in == "p" or p2_in == "Paper" or p2_in == "paper":
        print("####################################")
        print("Lose - Player 2 selected Paper. Player 1 selected scissors")
        mplayer1 += 1
        sptry_again()
    if p2_in == "S" or p2_in == "s" or p2_in == "Scissors" or p2_in == "scissors":
        print("####################################")
        print("Tie - You both selected scissors")
        mplayer1 += 1
        mplayer2 += 1
        sptry_again()
    else:
        print("Try again")
        p1_rock()


#   multiplayer try again function
def sptry_again():
    global mplayer1
    global mplayer2
    print("####################################")
    print("Current Scores: \nPlayer 1: ", mplayer1, " | Player 2: ", mplayer2)
    print("####################################")
    choice = input("Would you like to play again or return to menu? Y/N/M?: ")
    if choice == "y" or choice == "Y" or choice == "yes":
        multiplayer()
    elif choice == "n" or choice == "N" or choice == "no":
        print("Thanks for playing!")
        quit()
    # if choice == "M" or choice == "m" or choice == "menu":
    #     welcome()
    else:
        print("Try again")
        sptry_again()