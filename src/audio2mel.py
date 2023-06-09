import torch
import torch.nn as nn
import torch.nn.functional as F
from librosa.filters import mel as librosa_mel_fn


class Audio2Mel(nn.Module):

    def __init__(self, n_fft, hop_length, win_length, sampling_rate, n_mel_channels, mel_fmin,
                 mel_fmax):
        super().__init__()

        window = torch.hann_window(win_length).float()
        mel_basis = librosa_mel_fn(sampling_rate, n_fft, n_mel_channels, mel_fmin, mel_fmax)
        mel_basis = torch.from_numpy(mel_basis).float()

        self.register_buffer("mel_basis", mel_basis)
        self.register_buffer("window", window)

        self.n_fft = n_fft
        self.hop_length = hop_length
        self.win_length = win_length
        self.sampling_rate = sampling_rate
        self.n_mel_channels = n_mel_channels

    def forward(self, audio, eps=0.0):
        p = (self.n_fft - self.hop_length) // 2
        audio = F.pad(audio, (p, p), "reflect").squeeze(1)

        fft = torch.stft(audio,
                         n_fft=self.n_fft,
                         hop_length=self.hop_length,
                         win_length=self.win_length,
                         window=self.window,
                         center=False,
                         return_complex=False)

        real_part, imag_part = fft.unbind(-1)
        magnitude = torch.sqrt(real_part**2 + imag_part**2 + eps)
        mel_output = torch.matmul(self.mel_basis, magnitude)
        log_mel_spec = torch.log10(torch.clamp(mel_output, min=1e-5))

        return log_mel_spec
