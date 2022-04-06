from contextlib import suppress

from RPS_singleplayer import *
from RPS_multiplayer import *


def runner():
    options = ["Single player", "Multiplayer", "Exit"]
    print("Welcome to Rock Paper Scissors")
    print("Main menu")
    for i, title in enumerate(options, 1):
        print(f"{i}. {title}")

    while True:
        user_option = int_input("Enter an option: ")
        if user_option == 1:
            print("Taking you to singleplayer mode... please wait")
            singleplayer()
        elif user_option == 2:
            print("Taking you to multiplayer mode... please wait")
            multiplayer()
        elif user_option == 3:
            print("Thanks for playing")
            return
        else:
            print("Invalid input. try again")


def int_input(question):
    with suppress(ValueError):
        return int(input(question))
    return 0

if __name__ == "__main__":
    runner()
