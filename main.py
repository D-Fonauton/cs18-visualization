from tkinter import Tk
import hydra
from omegaconf import DictConfig
import pickle

# local
from utils import Visualizer, Levenshtein_distance, Needleman_Wunsch, Scanmatch, Histogram
from src import COCOSearch18
from calc_similarity import calculate_similarity_images, calculate_similarity_subjects


@hydra.main(version_base=None, config_path="config", config_name="config")
def test(cfg: DictConfig):
    dataset = COCOSearch18(cfg.dataset)
    print(Levenshtein_distance((4,4),cfg.dataset,[[100,100,1],[100,200,1],[800,800,1]],[[100,100,1],[100,200,1],[1600,800,1]]).similarity())


@hydra.main(version_base=None, config_path="config", config_name="config")
def main(cfg: DictConfig):
    dataset = COCOSearch18(cfg.dataset)
    func = [Levenshtein_distance, Needleman_Wunsch, Scanmatch]
    func = [Scanmatch]
    for index in range(1):
        result = calculate_similarity_images(dataset.json,(4,4), cfg.dataset, func[index])
        with open(f'{func[index].__name__}.pkl', 'wb') as f:
            pickle.dump(result, f)

    # print(result)
    

@hydra.main(version_base=None, config_path="config", config_name="config")
def visualizer_app(cfg: DictConfig):
    root = Tk()
    app = Visualizer(root, cfg.dataset)
    root.mainloop()


def read():
    with open(f"Scanmatch.pkl", "rb") as f:
        matrix = pickle.load(f)
        pass


def show_hist():
    root = Tk()
    app = Histogram(root, "Scanmatch.pkl")
    root.mainloop()


if __name__ == "__main__":
    # visualizer_app() 
    # main()
    show_hist()
    # test()
