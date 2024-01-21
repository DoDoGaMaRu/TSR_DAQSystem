from dataclasses import dataclass


@dataclass
class ModelConfig:
    NAME            : str
    BATCH_SIZE      : int
    LATENT_DIM      : int
    SEQ_LEN         : int
    THRESHOLD       : int
