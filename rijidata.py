import sys, pickle

sys.setrecursionlimit(50000)

with open("mostrecent.pkl", "rb") as input:
    boards = pickle.load(input)

top = boards[1].topics[0]
print(top.content)
print()
for r in top.replies:
    print(r.content+"\n")