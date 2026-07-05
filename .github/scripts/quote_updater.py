#!/usr/bin/env python3
import os
import json
import random

QUOTES = [
    {"quote": "Simplicity is the soul of efficiency.", "author": "Austin Freeman"},
    {"quote": "Before software can be reusable it first has to be usable.", "author": "Ralph Johnson"},
    {"quote": "Make it simple, but significant.", "author": "Don Draper"},
    {"quote": "Talk is cheap. Show me the code.", "author": "Linus Torvalds"},
    {"quote": "Programs must be written for people to read, and only secondarily for machines to execute.", "author": "Harold Abelson"},
    {"quote": "Truth can only be found in one place: the code.", "author": "Robert C. Martin"},
    {"quote": "Clean code always looks like it was written by someone who cares.", "author": "Michael Feathers"},
    {"quote": "Of course, bad code can be cleaned up. But it's very expensive.", "author": "Robert C. Martin"},
    {"quote": "You've got to start with the customer experience and work back toward the technology.", "author": "Steve Jobs"},
    {"quote": "The best way to predict the future is to invent it.", "author": "Alan Kay"},
    {"quote": "Optimism is a occupational hazard of programming: feedback is the treatment.", "author": "Kent Beck"},
    {"quote": "Simplicity is prerequisite for reliability.", "author": "Edsger W. Dijkstra"}
]

def main():
    os.makedirs("stats", exist_ok=True)
    selected = random.choice(QUOTES)
    
    with open("stats/quote.json", "w", encoding="utf-8") as f:
        json.dump(selected, f, indent=4)
        
    print(f"Updated quote: \"{selected['quote']}\" — {selected['author']}")

if __name__ == "__main__":
    main()
