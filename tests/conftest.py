import sys
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(CURRENT_DIR, "..", "src", "nl2sql")
sys.path.insert(0, os.path.abspath(SRC_DIR))
