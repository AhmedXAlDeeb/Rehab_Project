import torch
import torch.nn as nn


class ConditionalVAE(nn.Module):
    def __init__(self, config) -> None:
        super().__init__()
        self.latent_dim = 64
        self.output_t = int(config.WINDOW_MS * config.FS / 1000)
        self.output_c = config.N_CHANNELS
        cond_dim = 16
        self.decoder = nn.Sequential(
            nn.Linear(self.latent_dim + cond_dim, 512),
            nn.ReLU(),
            nn.Linear(512, self.output_t * self.output_c),
        )

    def decode(self, z: torch.Tensor, cond: torch.Tensor) -> torch.Tensor:
        x = self.decoder(torch.cat([z, cond], dim=-1))
        return x.view(z.shape[0], self.output_t, self.output_c)
