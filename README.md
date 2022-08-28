# Chord Trainer

This app visualize chords by motion and colors with sounds, which would help you to understand the difference among chords.

## Preparation

1. Enable MIDI output on your computer.
2. Install [poetry](https://python-poetry.org/docs/). If you don't want to use poetry, please install python libraries listed in pyproject.toml.
3. Install python libraries using poetry
```
$ poetry install
```

## 準備: MIDIの音を鳴らす(Mac)

1. パソコンのMIDI出力設定をする
    - [pythonからMIDI用の信号を作成し、音を再生する](https://kagari.github.io/note/2020/macos_pygame_midi/)
    - [MacでのAudio MIDI設定（結構重要です）](https://hideshigelog.com/audio-midi)
2. [poetry](https://python-poetry.org/docs/)をインストールしてから，以下を実行
    ```
    $ poetry install
    ```
    Python環境にpoetryを使わない場合は，python(3.10以上)に`pyproject.toml`にあるライブラリをインストールした環境を作っておく。