import torch
import torch.nn as nn


class ClassifierCNN(nn.Module):
    def __init__(self, in_dim: int = 84, embedding_dim: int = 128, n_classes: int = 8) -> None:
        super().__init__()
        self.backbone = nn.Sequential(
            nn.Linear(in_dim, 256),
            nn.ReLU(),
            nn.Linear(256, embedding_dim),
            nn.ReLU(),
        )
        self.head = nn.Linear(embedding_dim, n_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        emb = self.backbone(x)
        return self.head(emb)

    def get_embedding(self, x: torch.Tensor) -> torch.Tensor:
        return self.backbone(x)
