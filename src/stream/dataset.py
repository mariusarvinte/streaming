from datasets import load_dataset


def get_dataset(name: str = "newfacade/LeetCodeDataset"):
    ds = load_dataset(name)
    return ds
