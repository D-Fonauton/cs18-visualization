from tkinter import Tk
import hydra
from omegaconf import DictConfig

# local
from utils import Visualizer


@hydra.main(version_base=None, config_path="config", config_name="config")
def main(cfg: DictConfig):
    root = Tk()
    app = Visualizer(root, cfg.dataset)
    root.mainloop()


if __name__ == "__main__":
    main()    
