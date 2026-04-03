from train import train_model
from datetime import datetime
import os

# Absolute path resolution relative to this file location,
# so the CLI works regardless of where it is called from.
# Otherwise we get "no such file in directory" errors when the 
# "python src/training/cli.py --data inputs/full.csv" command is used from root of project.

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


#CLI
def main():
    PATH_TO_DATA = os.path.join(BASE_DIR, "../../inputs/full.csv")
    PATH_TO_MODEL = os.path.join(BASE_DIR, f"../scoring/model_storage/model_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl")
    train_model(PATH_TO_DATA, PATH_TO_MODEL)

if __name__ == "__main__":
    main()