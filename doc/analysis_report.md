# mkchromecast プロジェクト分析レポート

**作成日**: 2024年12月15日  
**対象バージョン**: v0.3.9  
**分析環境**: Ubuntu 24.04 LTS, Python 3.12.3

---

## 1. プロジェクト概要

mkchromecastは、macOS/LinuxのシステムオーディオをGoogle CastデバイスやSonosスピーカーにストリーミングするツールです。

### 主要機能
- オーディオキャスト（mp3, ogg, aac, opus, wav, flac）
- ビデオキャスト（ローカルファイル、スクリーンキャスト）
- YouTube/yt-dlp対応サイトの再生
- システムトレイUI（PyQt5）
- マルチルームグループ対応

### 技術スタック
- Python 3.10-3.12
- pychromecast 14.0.9
- Flask（ストリーミングサーバー）
- PyQt5（GUI）
- ffmpeg/parec/node（バックエンド）

---

## 2. 実施した修正（Python 3.12対応）

### 2.1 完了した修正

| ファイル | 修正内容 | コミット |
|----------|----------|----------|
| colors.py | Python 2互換コード削除、型ヒント追加 | 2821ebbc |
| pulseaudio.py | bytes/str処理修正 | 2821ebbc |
| constants.py | `List` → `list` 型ヒント更新 | 2821ebbc |
| cast.py | pychromecast API対応、Zeroconfエラー修正 | b8c34b7c, 26b7ea9a |
| stream_infra.py | stdout Noneチェック追加 | 2821ebbc |
| pipeline_builder.py | backend.path Noneチェック | 2821ebbc |
| video.py | 型修正、変数初期化 | 2821ebbc |
| audio.py | Python 2互換コード削除 | 2821ebbc |
| node.py | Noneチェック追加 | 2821ebbc |
| preferences.py | PyQt5 Qt名前空間更新 | 2821ebbc |
| systray.py | PyQt5 Qt名前空間更新 | 2821ebbc |
| setup.py | Python 3.10/3.11/3.12分類追加 | 2821ebbc |
| getch/getch.py | Windows専用msvcrtに`type: ignore`追加 | 07c23884 |
| tray_threading.py | requestsインポートに`type: ignore`追加 | 07c23884 |

### 2.2 pychromecast 14.0.9対応

| 問題 | 修正内容 |
|------|----------|
| `browser.stop_discovery()`の早期呼び出し | `cast.wait()`後に移動 |
| 不要な`media_controller.play()`呼び出し | 削除（autoplay=Trueがデフォルト） |

### 2.3 その他の修正

| 修正 | コミット |
|------|----------|
| yt-dlp対応（youtube-dlから移行） | 92d796d4 |
| README: PipeWire/pulseaudio-utils要件追加 | 4ef0dd3a |

---

## 3. 現在の品質状況

### 3.1 静的解析結果

```
mypy: 0 errors (23 source files)
pytest: 33 passed, 25 subtests passed
```

### 3.2 残存する技術的負債

- TODOコメント: 56個
- 無効化されたSonos機能: `_DisabledSonosCasting`クラス
- 壊れた統合テスト: test.py

---

## 4. レガシー設計の問題点

### 4.1 優先度高（修正推奨）

#### プロセス間通信
- **問題**: pickleファイル（`/tmp/mkchromecast.tmp`, `/tmp/mkchromecast.pid`）による状態共有
- **リスク**: セキュリティ、競合状態、クリーンアップ失敗
- **推奨**: JSON/SQLiteまたはシグナルベースに移行

#### モジュール設計
- **問題**: インポート時にグローバル処理実行
```python
# audio.py, preferences.py, systray.py, tray_threading.py
_mkcc = mkchromecast.Mkchromecast()  # インポート時に実行される
```
- **リスク**: テスト困難、副作用、メモリ使用
- **推奨**: 遅延初期化パターンに変更

#### Sonos機能
- **問題**: `_DisabledSonosCasting`クラスが壊れた状態で771行のコードが放置
- **推奨**: 削除または完全リファクタリング

#### サブプロセス管理
- **問題**: `shell=True`使用、`pkill`による危険なプロセス制御
```python
# bin/mkchromecast
subprocess.call(['pkill', '-STOP', '-f', 'ffmpeg'])
```
- **リスク**: セキュリティ、意図しないプロセス停止
- **推奨**: Popenオブジェクト管理に変更

### 4.2 優先度中（改善推奨）

| 問題 | 場所 | 推奨対応 |
|------|------|----------|
| 型ヒント不足 | 全体 | 段階的に追加 |
| 設定管理の分散 | __init__.py | 統一設定クラスに集約 |
| 文字列ベースのパス操作 | 全体 | `pathlib.Path`に移行 |
| Flask開発サーバー使用 | stream_infra.py | Gunicorn/Waitress検討 |

---

## 5. 取り込むべき新機能

### 5.1 優先度高

| 機能 | 説明 | 工数見積 |
|------|------|----------|
| PipeWireネイティブ対応 | `pw-record`/`pw-play`の直接サポート | 中 |
| 自動再接続 | 接続断時の自動復旧 | 中 |
| Chromecast with Google TV最適化 | 新デバイスタイプ対応 | 小 |

### 5.2 優先度中

| 機能 | 説明 | 工数見積 |
|------|------|----------|
| 非同期処理 | asyncio/aiohttpによるノンブロッキングI/O | 大 |
| WebSocket対応 | リアルタイム状態更新 | 中 |
| マルチルームグループ管理UI | 複数デバイスの同時制御 | 中 |

### 5.3 優先度低

| 機能 | 説明 | 工数見積 |
|------|------|----------|
| 音声レベルメーター | ストリーミング中の音量可視化 | 小 |
| 設定のGUI化 | コマンドライン引数のGUI設定 | 中 |

---

## 6. 推奨アーキテクチャ

### 現状
```
bin/mkchromecast
    → Mkchromecast(singleton)
        → cast.Casting → pychromecast
        → audio/video → stream_infra.FlaskServer
        → systray (PyQt5)
```

### 推奨構成
```
bin/mkchromecast
    → App (DI container)
        ├── Config (統一設定)
        ├── DeviceManager (Chromecast/Sonos抽象化)
        ├── StreamServer (Flask/ASGI)
        ├── AudioCapture (PulseAudio/PipeWire/ALSA抽象化)
        └── UI (CLI/Tray/Web)
```

---

## 7. 即座に対応可能な項目

1. **`_DisabledSonosCasting`クラスの削除** - 約300行のデッドコード削除
2. **古いpychromecast例外の更新** - `NoChromecastFoundError` → `PyChromecastError`
3. **test.pyの統合テスト修正** - pychromecast 14.0対応
4. **README.mdのPython 3.12対応明記**

---

## 8. 依存関係

### requirements.txt
```
PyGObject
requests
psutil
Flask
netifaces
pychromecast>=4.2
PyQt5
soco
yt-dlp
```

### システム依存関係（Ubuntu 24.04）
```bash
sudo apt-get install pulseaudio-utils pavucontrol ffmpeg lame vorbis-tools sox flac
```

---

## 9. 結論

mkchromecastはPython 3.12環境で動作するようになりましたが、以下の技術的負債が残っています：

1. **Sonos機能の完全停止** - 修正または削除が必要
2. **レガシーなプロセス間通信** - pickleファイルベースの設計
3. **モジュール設計の問題** - インポート時の副作用

プロジェクトのメンテナンス体制が不足しているため（README冒頭で「Looking for help!」と明記）、大規模なリファクタリングよりも、まずは動作する状態を維持しながら段階的に改善することを推奨します。
