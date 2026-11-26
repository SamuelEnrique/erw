"""Session 10222: are two drawings the same HTML once a given attribute text is taken out? Prints the count removed."""
import sys

a = open(sys.argv[1], encoding="utf-8").read()
b = open(sys.argv[2], encoding="utf-8").read()
cut = sys.argv[3]
n = b.count(cut)
print("occurrences in the second:", n, "| the same once removed:", a == b.replace(cut, ""))
