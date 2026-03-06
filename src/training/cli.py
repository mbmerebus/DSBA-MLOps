from train import train_model
from datetime import datetime

#CLI
def main():
    PATH_TO_DATA = "../../inputs/full.csv"
    PATH_TO_MODEL = f"../scoring/model_storage/model_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
    train_model(PATH_TO_DATA, PATH_TO_MODEL)

if __name__ == "__main__":
    main()