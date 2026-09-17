# 动作 / 表情素材包清单

投稿或自绘时，把 PNG/JPG 放到精灵目录（或 `react/` 子目录）。缺文件时程序会回退到已有表情，不崩。

## 命名约定

| 标签 | 建议文件名（任选其一存在即可） | 触发 | 回退表情 |
|------|--------------------------------|------|----------|
| react_code | `react_code_think` / `react_code_1` | 场景·写代码 | idea |
| react_study | `react_study_read` / `react_study_1` | 场景·学习 | like |
| react_office | `react_office_nod` / `react_office_1` | 场景·办公 | happy |
| react_chat | `react_chat_wave` / `react_chat_1` | 场景·聊天 | hi |
| react_game | `react_game_cheer` | 场景·游戏 | happy |
| react_video | `react_video_watch` | 场景·视频 | wink |
| react_music | `react_music_sway` | 场景·音乐 | happy |
| contract_focus | `contract_focus_1` / `contract_focus_2` | 专注契约中 | squat |
| contract_done | `contract_done_1` | 契约完成 | happy |
| bond_milestone | `bond_milestone_1` / `bond_stage_up` | 羁绊升级 | like |
| blush | `blush_1` / `date_blush` | 恋爱预留 | shy |
| date_park | `date_park_1` / `date_walk` | 约会脚本 | happy |

## 绘制优先级（建议）

1. 场景反应：code / study / office / chat 各 2～3 张  
2. 契约专注 / 完成夸赞各 1 套短帧  
3. 羁绊里程碑表情  
4. 恋爱差分（脸红、约会便装）

## 技术说明

- 注册表：`emote_registry.py`  
- 扩展新标签：在 `REACT_REGISTRY` 增加条目即可  
- 约会脚本：`data/date_scripts/*.json`（见 `park_evening.json`）  
- 多角色档案：`character_profile.py`  
