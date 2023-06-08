import numpy as np
import neurosift.saneslab.views as sl
from typing import List
import kachery_cloud as kcl
from scipy.io import wavfile
from matplotlib.pyplot import specgram


def main():
    V = create_audio_spectrogram()

    V.save_figure('tests/sparse_audio_spectrogram')

    # url = V.url(label='audio spectrogram')
    # print(url)

def create_audio_spectrogram(view_id: str='audio_spectrogram'):
    # 1002 MB
    mic_wav_uri = 'sha1://c59c69a73c64d49d8da795e2f6cd66d088e50935?label=mic_2021_08_10_15_10_38_554833combined.wav'
    mic_wav_path = kcl.load_file(mic_wav_uri)
    audio_sr_hz, audio = wavfile.read(mic_wav_path)
    n_samples = audio.shape[0]
    # n_channels = audio.shape[1]
    duration_sec = n_samples / audio_sr_hz
    print(f'Sampling frequency (Hz): {audio_sr_hz}')
    print(f'Duration (sec): {duration_sec}')

    freq_range=[130, 230]

    # between 0 and 100... percentile cutoff in the target freq band
    # in spectrogram_for_gui
    # everything below the value is set to zero
    # affects detection and compressed file size
    # threshold_pct = 99.8
    threshold_pct = 99.8
    
    print('Extracting audio signals')
    X = audio[0:int(duration_sec * audio_sr_hz)]

    if X.ndim == 1:
        X = X.reshape((len(X), 1))
    
    num_channels = X.shape[1]
    print(f'Num. channels: {num_channels}')

    print('Computing spectrograms')
    spectrograms = []
    for channel_ind in range(num_channels):
        s, f, t, im = specgram(X[:, channel_ind], NFFT=512, noverlap=256, Fs=audio_sr_hz)
        sr_spectrogram = 1 / (t[1] - t[0])
        spectrograms.append(s)
    print(f'Spectrogram sampling rate (Hz): {sr_spectrogram}')
    spectrogram_for_gui = sum(spectrograms)

    print('Auto detecting maxval')
    maxval = _auto_detect_spectrogram_maxval(spectrogram_for_gui, sr_spectrogram=sr_spectrogram)
    minval = 0
    print(f'Absolute spectrogram max: {np.max(spectrogram_for_gui)}')
    print(f'Auto detected spectrogram max: {maxval}')

    print('Scaling spectogram data')
    # Nf x Nt
    spectrogram_for_gui = np.floor((spectrogram_for_gui - minval) / (maxval - minval) * 255).astype(np.uint8)

    threshold = np.percentile(spectrogram_for_gui[freq_range[0]:freq_range[1]], threshold_pct)
    print(f'Using threshold: {threshold} ({threshold_pct} pct)')
    spectrogram_for_gui[spectrogram_for_gui <= threshold] = 0

    print(spectrogram_for_gui.shape)
    V = sl.SparseAudioSpectrogram(
        view_id=view_id,
        sampling_frequency=sr_spectrogram,
        spectrogram_data=spectrogram_for_gui.T,
        hide_toolbar=True
    )
    return V

def _auto_detect_spectrogram_maxval(spectrogram: np.array, *, sr_spectrogram: float):
    Nf = spectrogram.shape[0]
    Nt = spectrogram.shape[1]
    chunk_num_samples = int(15 * sr_spectrogram)
    chunk_maxvals: List[float] = []
    i = 0
    while i + chunk_num_samples < Nt:
        chunk = spectrogram[:, i:i + chunk_num_samples]
        chunk_maxvals.append(np.max(chunk))
        i += chunk_num_samples
    v = np.median(chunk_maxvals) / 6
    return v

if __name__ == '__main__':
    main()