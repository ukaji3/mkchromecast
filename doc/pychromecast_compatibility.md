# pychromecast 14.0.9 互換性レポート

**作成日**: 2024年12月15日

---

## 1. 現在のバージョン

```
pychromecast: 14.0.9
zeroconf: 0.148.0
```

---

## 2. 修正済みの非互換性

### 2.1 Zeroconf AssertionError

**問題**: `browser.stop_discovery()`を`cast.wait()`より前に呼び出すとエラー

```
AssertionError: Zeroconf instance loop must be running, was it already stopped?
```

**原因**: `_get_chromecast_names()`でdiscoveryを早期停止

**修正**: `_browser`インスタンスを保持し、`cast.wait()`後に`stop_discovery()`を呼び出す

```python
# Before (NG)
def _get_chromecast_names(self):
    chromecasts, browser = pychromecast.get_chromecasts()
    browser.stop_discovery()  # ← 早すぎる
    ...

# After (OK)
def _get_chromecast_names(self):
    chromecasts, browser = pychromecast.get_chromecasts()
    self._browser = browser  # 保持
    ...

def get_devices(self):
    ...
    self.cast.wait()
    self._stop_discovery()  # ← wait()後に呼び出し
```

### 2.2 RequestTimeout エラー

**問題**: `media_controller.play()`がタイムアウト

```
pychromecast.error.RequestTimeout: Execution of play timed out after 10.0 s.
```

**原因**: `play_media()`は`autoplay=True`がデフォルトなので、追加の`play()`呼び出しは不要

**修正**: 不要な`play()`呼び出しを削除

```python
# Before (NG)
media_controller.play_media(url, media_type, stream_type="LIVE")
if media_controller.is_active:
    media_controller.play()  # ← 不要
time.sleep(5.0)
media_controller.play()  # ← 不要、タイムアウトの原因

# After (OK)
media_controller.play_media(url, media_type, stream_type="LIVE")
# autoplay=True (default) で自動再生される
```

---

## 3. 未修正の非互換性（無効化コード内）

以下は`_DisabledSonosCasting`クラス内にあり、現在は使用されていません。

### 3.1 削除されたAPI

| API | 場所 | 状況 |
|-----|------|------|
| `pychromecast.get_chromecast()` | test.py:138 | テストはスキップ済み |
| `pychromecast.error.NoChromecastFoundError` | cast.py:655 | 無効化クラス内 |

### 3.2 削除された属性

| 属性 | 場所 | 代替 |
|------|------|------|
| `cast.device` | cast.py:645 | `cast.cast_info` |

---

## 4. 現行API（互換性あり）

| API | 用途 | 状況 |
|-----|------|------|
| `pychromecast.get_chromecasts()` | デバイス検出 | ✓ 使用中 |
| `Chromecast.wait()` | 接続待機 | ✓ 使用中 |
| `Chromecast.status` | 状態取得 | ✓ 使用中 |
| `Chromecast.socket_client.host` | IPアドレス取得 | ✓ 使用中 |
| `Chromecast.media_controller` | メディア制御 | ✓ 使用中 |
| `Chromecast.quit_app()` | アプリ終了 | ✓ 使用中 |
| `MediaController.play_media()` | メディア再生 | ✓ 使用中 |
| `MediaController.pause()` | 一時停止 | ✓ 使用中 |
| `CastBrowser.stop_discovery()` | 検出停止 | ✓ 使用中 |
| `pychromecast.error.NotConnected` | 例外 | ✓ 使用中 |

---

## 5. 推奨事項

### 即時対応
1. `_DisabledSonosCasting`クラスの削除
2. test.pyの`get_chromecast()`を`get_chromecasts()`に更新

### 将来の互換性維持
1. pychromecastのリリースノートを定期確認
2. 非推奨APIの使用を避ける
3. 型ヒントを活用してAPI変更を早期検出
