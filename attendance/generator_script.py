from ..config import config

a = config['A']
c = config['C']
m = config['M']



def generatorScript(seed):
    seed = (seed % m) * (a % m)
    seed = seed % m
    seed = seed + c
    seed = seed % m
    return seed
