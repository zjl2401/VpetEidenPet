# VpetFlutter — 伊得双端（Flutter）

对齐电脑版 [`FEATURES.md`](../FEATURES.md) 的全量手机实现。对照表见 [`FEATURE_PARITY.md`](FEATURE_PARITY.md)。

包名：`com.vpet.eiden.mobile`（与苍叶手机版并存）。

## 环境

- Flutter 3.24+ / Dart 3.3+
- Android：本机 Windows 可 `flutter build apk`
- iOS：需 macOS 或 CI（本仓库 `.github/workflows/vpet_flutter.yml`）

## 首次搭建

```powershell
cd VpetFlutter
python tools/sync_assets.py
# 若缺少 ios/Runner.xcodeproj 等，用 Flutter 补齐平台壳：
flutter create --org com.vpet.eiden --project-name vpet_eiden .
flutter pub get
flutter run
```

或运行：`.\tools\bootstrap.ps1`

Android 本机首次出包前需安装 NDK `25.1.8937393`（`sdkmanager "ndk;25.1.8937393"`）。语音资源由同步脚本改成 ASCII 文件名，避免 Windows 资源拷贝失败。

## 功能分期（代码已落地）

| Phase | 内容 |
|-------|------|
| 0 | 工程 / 资产同步 / FEATURE_PARITY |
| 1 | 认主、立绘拖拽、模式、气泡、Android 悬浮、iOS PiP 通道 |
| 2 | 语音包 + BGM 打断断点续播（`MediaHub`） |
| 3 | 四大菜单、喂食、使魔、装扮、工作运送 |
| 4 | 秒表/计时/番茄/日程/天气/生日/时钟 |
| 5 | 采集/音游/暴露/莱姆/打字/背单词/RPG stub |
| 6 | 家园锄种浇收砍钓采店 |
| 7 | 日记/成就/画廊/留声/社区/重置 |
| 8 | 本机相遇友情 + CI 双端构建 |

## 平台差异

- Android：`SYSTEM_ALERT_WINDOW` → `FlutterPetOverlayService`
- iOS：无任意悬浮 → 前台桌宠 + `startPip` MethodChannel（PiP 保活）

旧 Kotlin 工程 `VpetMobile/` 保留为对照，Phase 1 可玩后视为 legacy。
