import librosa
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from utils.text import phoneme_to_sequence, sequence_to_phoneme


def plot_alignment(alignment, info=None,
                   text_padding_start=None, spec_padding_start=None):
    fig, ax = plt.subplots(figsize=(16, 10))
    im = ax.imshow(
        alignment.T, aspect='auto', origin='lower', interpolation='none',
        vmin=0, vmax=1.0)
    fig.colorbar(im, ax=ax)
    xlabel = 'Decoder timestep'
    if info is not None:
        xlabel += '\n\n' + info
    plt.xlabel(xlabel)
    plt.ylabel('Encoder timestep')
    # plt.yticks(range(len(text)), list(text))
    plt.tight_layout()

    if text_padding_start is not None:
        rect = patches.Rectangle((-1, text_padding_start),
                                 alignment.shape[0] + 2,
                                 alignment.shape[1] - text_padding_start,
                                 alpha=0.2,
                                 facecolor="orange",
                                 color=None,
                                 edgecolor=None)
        ax.add_patch(rect)

    if spec_padding_start is not None:
        rect = patches.Rectangle((spec_padding_start, -1),
                                 alignment.shape[0] - spec_padding_start,
                                 1 + (alignment.shape[1] if text_padding_start is None else text_padding_start),
                                 alpha=0.2,
                                 facecolor="grey",
                                 color=None,
                                 edgecolor=None)
        ax.add_patch(rect)

    return fig


def plot_spectrogram(linear_output, audio):
    spectrogram = audio._denormalize(linear_output)
    fig = plt.figure(figsize=(16, 10))
    plt.imshow(spectrogram.T, aspect="auto", origin="lower", vmin=-100, vmax=0)
    plt.colorbar()
    plt.tight_layout()
    return fig


def visualize(alignment, spectrogram_postnet, text, hop_length, CONFIG, spectrogram=None, output_path=None):
    if spectrogram is not None:
        num_plot = 3
    else:
        num_plot = 2

    label_fontsize = 16
    fig = plt.figure(figsize=(8, 24))

    plt.subplot(num_plot, 1, 1)
    plt.imshow(alignment.T, aspect="auto", origin="lower", interpolation=None)
    plt.xlabel("Decoder timestamp", fontsize=label_fontsize)
    plt.ylabel("Encoder timestamp", fontsize=label_fontsize)
    if CONFIG.use_phonemes:
        seq = phoneme_to_sequence(text, [CONFIG.text_cleaner], CONFIG.phoneme_language, CONFIG.enable_eos_bos_chars)
        text = sequence_to_phoneme(seq)
        print(text)
    plt.yticks(range(len(text)), list(text))
    plt.colorbar()

    # stop_tokens = stop_tokens.squeeze().detach().to('cpu').numpy()
    # plt.subplot(num_plot, 1, 2)
    # plt.plot(range(len(stop_tokens)), list(stop_tokens))

    plt.subplot(num_plot, 1, 2)
    librosa.display.specshow(spectrogram_postnet.T, sr=CONFIG.audio['sample_rate'],
                             hop_length=hop_length, x_axis="time", y_axis="linear")
    plt.xlabel("Time", fontsize=label_fontsize)
    plt.ylabel("Hz", fontsize=label_fontsize)
    plt.tight_layout()
    plt.colorbar()

    if spectrogram is not None:
        plt.subplot(num_plot, 1, 3)
        librosa.display.specshow(spectrogram.T, sr=CONFIG.audio['sample_rate'],
                                 hop_length=hop_length, x_axis="time", y_axis="linear")
        plt.xlabel("Time", fontsize=label_fontsize)
        plt.ylabel("Hz", fontsize=label_fontsize)
        plt.tight_layout()
        plt.colorbar()

    if output_path:
        print(output_path)
        fig.savefig(output_path)
        plt.close()
