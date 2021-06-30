import sys, pickle

with open("boards.pkl", "rb") as input:
    boards = pickle.load(input)

print(boards)