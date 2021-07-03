import os, sys, pickle

sys.setrecursionlimit(50000)

with open("wtf.pkl", "rb") as f:
    boards = pickle.load(f)

top = boards[1].topics[0]
print(top.content)
print()
for r in top.replies:
    print(r.content+"\n")