# PipeWire対応ガイド

**作成日**: 2024年12月15日

---

## 1. 背景

Ubuntu 22.04以降、デフォルトのオーディオシステムがPulseAudioからPipeWireに移行しています。

| Ubuntu バージョン | デフォルトオーディオ |
|------------------|---------------------|
| 20.04 LTS | PulseAudio |
| 22.04 LTS | PipeWire (PulseAudio互換) |
| 24.04 LTS | PipeWire (PulseAudio互換) |

---

## 2. 現在の対応状況

### 2.1 PulseAudio互換レイヤー経由での動作

mkchromecastは`pactl`コマンドを使用してPulseAudioシンクを作成します。
PipeWireの`pipewire-pulse`サービスがPulseAudio APIをエミュレートするため、
`pulseaudio-utils`パッケージをインストールすれば動作します。

```bash
# 必要なパッケージ
sudo apt-get install pulseaudio-utils pavucontrol
```

### 2.2 動作確認済み環境

- Ubuntu 24.04.3 LTS
- PipeWire 1.0.5
- pipewire-pulse (PulseAudio互換デーモン)

---

## 3. 技術詳細

### 3.1 シンク作成

```python
# mkchromecast/pulseaudio.py
create_sink_cmd = [
    "pactl", "load-module", "module-null-sink",
    "sink_name=Mkchromecast",
    'sink_properties=device.description="Mkchromecast"'
]
```

PipeWire環境では、`pactl`コマンドは`pipewire-pulse`経由で処理されます。

### 3.2 オーディオキャプチャ

```python
# parec バックエンド使用時
c_parec = ["parec", "--format=s16le", "-d", "Mkchromecast.monitor"]
```

---

## 4. 将来のPipeWireネイティブ対応

### 4.1 推奨アプローチ

PipeWireネイティブAPIを使用することで、より効率的なオーディオキャプチャが可能です。

```bash
# PipeWireネイティブコマンド
pw-record --target=<node_id> - | ffmpeg -i - ...
```

### 4.2 実装案

```python
# 新しいバックエンド: pipewire
class PipeWireBackend:
    def create_capture_node(self):
        # pw-cli を使用してキャプチャノードを作成
        pass
    
    def get_audio_stream(self):
        # pw-record を使用してオーディオをキャプチャ
        pass
```

### 4.3 メリット

| 項目 | PulseAudio互換 | PipeWireネイティブ |
|------|----------------|-------------------|
| レイテンシ | 高め | 低い |
| CPU使用率 | 高め | 低い |
| 機能 | 制限あり | フル機能 |
| 依存関係 | pulseaudio-utils | pipewire-bin |

---

## 5. トラブルシューティング

### 5.1 `pactl`が見つからない

```bash
# エラー
FileNotFoundError: [Errno 2] No such file or directory: 'pactl'

# 解決
sudo apt-get install pulseaudio-utils
```

### 5.2 シンクが残る

```bash
# 手動削除
pactl unload-module module-null-sink

# または
python -c "from mkchromecast.pulseaudio import remove_sink; remove_sink()"
```

### 5.3 PipeWireサービスの確認

```bash
# サービス状態確認
systemctl --user status pipewire pipewire-pulse

# シンク一覧
pactl list sinks short
```

---

## 6. 参考リンク

- [PipeWire Documentation](https://pipewire.org/)
- [PipeWire Wiki](https://gitlab.freedesktop.org/pipewire/pipewire/-/wikis/home)
- [Ubuntu PipeWire Migration](https://ubuntu.com/blog/pipewire-as-a-replacement-for-pulseaudio)
