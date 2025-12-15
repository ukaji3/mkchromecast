# mkchromecast TODOリスト

**作成日**: 2024年12月15日

---

## 即時対応（1-2日）

- [ ] `_DisabledSonosCasting`クラスの削除または分離
- [ ] test.pyの統合テストをpychromecast 14.0対応に修正
- [ ] README.mdにPython 3.12対応を明記

---

## 短期対応（1-2週間）

### コード品質
- [ ] pickleファイルによる状態共有をJSONに移行
- [ ] インポート時のグローバル処理を遅延初期化に変更
- [ ] `shell=True`のsubprocess呼び出しを修正
- [ ] 文字列パスを`pathlib.Path`に移行

### 機能改善
- [ ] PipeWireネイティブ対応（`pw-record`）
- [ ] 自動再接続機能の実装
- [ ] エラーメッセージの改善

---

## 中期対応（1-2ヶ月）

### アーキテクチャ
- [ ] 設定管理の統一（Config クラスの整理）
- [ ] DeviceManager抽象化（Chromecast/Sonos）
- [ ] AudioCapture抽象化（PulseAudio/PipeWire/ALSA）

### テスト
- [ ] ユニットテストのカバレッジ向上
- [ ] モック化による統合テストの安定化

---

## 長期対応（3ヶ月以上）

- [ ] asyncio/aiohttpによる非同期化
- [ ] WebSocket対応
- [ ] Web UI（Flask/FastAPI）
- [ ] Sonos機能の完全リファクタリング

---

## 既存TODOコメント（56個）

### __init__.py (10個)
- [ ] Require arg parsing to be done outside of this class
- [ ] Probably don't need to initialize most of this class for Tray mode
- [ ] Switch input_file to pathlib.Path
- [ ] Validate port range 0..65535
- [ ] Why is fps typed as a str?
- [ ] Validate config codec
- [ ] Unbreak command to accept full command string
- [ ] Warn that we're overriding the backend
- [ ] These were just printed warnings, should they be errors?
- [ ] Maybe use stderr for debug messages?

### cast.py (4個)
- [ ] Get rid of conditional imports
- [ ] Centralize media type storage
- [ ] The original code had what was likely a typo here
- [ ] No. (Sonos関連)

### audio.py (5個)
- [ ] Encapsulate this so that we don't do this work on import
- [ ] Clean this up more when we refactor this file
- [ ] Why is this only run in tray mode?
- [ ] We should not be setting up a custom path like this
- [ ] Update init_audio to take an EncodeSettings

### pipeline_builder.py (7個)
- [ ] Use SubprocessCommand here
- [ ] It's really weird that the legacy code excludes...
- [ ] Figure out and document why -segment_time and -cutoff are...
- [ ] This always applies the 18kHz cutoff
- [ ] Should display be Optional?
- [ ] Check user_command type
- [ ] Figure out if there's any way to actually get here

### その他 (30個)
- 詳細は各ファイルのTODOコメントを参照
