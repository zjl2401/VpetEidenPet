# VpetMobile（伊得 · 手机试做）

与电脑版 **`VpetEidenPet` 完全独立**：本目录是 Android 工程，不会改桌面桌宠代码。

从苍叶 `VpetAOBA/VpetMobile` 分叉，**正在对齐伊得电脑版**（非苍叶换皮）：

- ✅ 主宠立绘 / 应用名 / 完整预设对话（伊得设定）
- ✅ **伏案赶工**（1/2/3work 循环，对照电脑版工作模式）
- ✅ **使魔**贴图改用艾斯特 `Aster*.png`（非莲 minipet）
- ✅ 音乐分类改为 BGM / 主题曲 / 其他
- ✅ 移除金目人格菜单；成就/台词去苍叶化
- ✅ **双使魔**：艾斯特 / 墨菲 分开关，左上 / 右上飞行停靠
- ✅ **语音**：已换成伊得台词（从桌面 `VpetEiden/voice` 抽音）；去掉苍叶/莲/金目语音
- ⏳ 跨桌宠友情（苍叶↔伊得）— 电脑版已有，手机待接

`applicationId`：`com.vpet.eiden.mobile`，可与苍叶手机版并存。

## 安装 debug APK

1. 产物：`dist/VpetEiden-debug.apk`
2. 拷到手机安装（允许未知来源）→ 授予「显示在其他应用上层」→ 启动悬浮桌宠。

## 命令行构建

需 JDK 17；可复用苍叶工程内 `.android-sdk`。

```powershell
cd VpetMobile
.\build_debug.ps1
```

## 资源

- 语音：桌面 `VpetEiden/voice` 的 mp4 抽音 → `bundled/Vpetvoice` 与 `app/src/main/assets/voice`
  - 同步：`python VpetMobile/tools/sync_eiden_voices.py`
  - 使魔对答链需文件名带数字/字母前缀（如 `1 台词.wav`）才会生成 `chain/`
- 启动图标：`python tools/gen_launcher_icons.py`（对齐电脑版 `app_icon.png`）
- 复现进度：[`MOBILE_CHECKLIST.md`](MOBILE_CHECKLIST.md)
