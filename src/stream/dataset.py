from datasets import load_dataset, Dataset


def get_dataset(name: str = "newfacade/LeetCodeDataset") -> Dataset:
    ds = load_dataset(name)
    return ds
