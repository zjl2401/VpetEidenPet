package com.vpet.mobile

/**
 * 菜单树对照桌面 pet.py（伊得版）；条目精简、少嵌套。
 */
object DesktopMenuCatalog {

    enum class Status { READY, STUB, LATER }

    data class Item(
        val id: String,
        val title: String,
        val status: Status = Status.STUB,
        val children: List<Item> = emptyList(),
    )

    private val dialogChildren: List<Item> =
        PresetDialogs.all.mapIndexed { i, e ->
            Item("dialog_q_$i", e.question, Status.READY)
        }

    val root: List<Item> = listOf(
        Item(
            "mode", "模式", Status.READY,
            listOf(
                Item("mode_free", "自由", Status.READY),
                Item("mode_follow", "跟随", Status.READY),
                Item("mode_stroll", "漫步", Status.READY),
                Item("mode_quiet", "睡眠", Status.READY),
                Item("mode_music", "音乐", Status.READY),
                // 与睡眠同：点开 / 再点结束
                Item("mode_work", "工作", Status.READY),
                Item(
                    "mode_game", "游戏 ▶", Status.READY,
                    listOf(
                        Item("game_collect", "采集", Status.READY),
                        Item("game_rhythm", "音游", Status.READY),
                    ),
                ),
            ),
        ),
        Item(
            "panel", "面板", Status.READY,
            listOf(
                Item("panel_open", "打开面板", Status.READY),
                Item(
                    "panel_companion", "使魔 ▶", Status.READY,
                    listOf(
                        Item("companion_aster", "艾斯特", Status.READY),
                        Item("companion_morvay", "墨菲", Status.READY),
                    ),
                ),
                Item("panel_outfit", "装扮", Status.READY),
                Item("panel_invite", "邀请", Status.STUB),
            ),
        ),
        Item(
            "interact", "互动", Status.READY,
            listOf(
                Item(
                    "act", "动作 ▶", Status.READY,
                    listOf(
                        Item("act_eat", "吃东西", Status.READY),
                        Item("act_hi", "打招呼", Status.READY),
                        Item("act_call", "打电话", Status.READY),
                        Item("act_adult", "×生活", Status.READY),
                        Item("act_work", "工作", Status.READY),
                        Item("act_sleep", "睡眠", Status.READY),
                        Item("act_squat", "下蹲", Status.READY),
                        Item("act_kick", "侧踢", Status.READY),
                        Item("act_judge", "判断", Status.READY),
                        Item("act_yes", "是", Status.READY),
                        Item("act_no", "否", Status.READY),
                        Item("act_walk", "走路", Status.READY),
                        Item("act_stand", "站立", Status.READY),
                    ),
                ),
                Item(
                    "expr", "表情 ▶", Status.READY,
                    listOf(
                        Item("expr_idea", "有主意", Status.READY),
                        Item("expr_happy", "开心", Status.READY),
                        Item("expr_angry", "生气", Status.READY),
                        Item("expr_question", "疑惑", Status.READY),
                        Item("expr_speechless", "无语", Status.READY),
                        Item("expr_awkward", "尴尬", Status.READY),
                        Item("expr_sad", "伤心", Status.READY),
                        Item("expr_shy", "脸红", Status.READY),
                        Item("expr_wink", "wink", Status.READY),
                        Item("expr_like", "点赞", Status.READY),
                        Item("expr_bixin", "比心", Status.READY),
                    ),
                ),
                Item(
                    "dialog", "对话 ▶", Status.READY,
                    listOf(
                        Item("dialog_preset", "普通对话 ▶", Status.READY, dialogChildren),
                        Item("dialog_ai", "AI 对话", Status.STUB),
                    ),
                ),
                Item(
                    "tools", "工具 ▶", Status.READY,
                    listOf(
                        Item("tool_sw", "秒表", Status.READY),
                        Item("tool_timer", "计时器", Status.READY),
                        Item(
                            "tool_pomo", "番茄钟 ▶", Status.READY,
                            listOf(
                                Item("tool_pomo_custom", "自定义", Status.READY),
                                Item("tool_pomo_end", "结束", Status.READY),
                            ),
                        ),
                        Item("tool_schedule", "日程", Status.READY),
                        Item(
                            "tool_birthday", "生日 ▶", Status.READY,
                            listOf(Item("tool_bday_set", "设定", Status.READY)),
                        ),
                    ),
                ),
            ),
        ),
        Item(
            "system", "系统", Status.READY,
            listOf(
                Item(
                    "sys_mine", "我的 ▶", Status.READY,
                    listOf(
                        Item("sys_owner", "所属人", Status.READY),
                        Item("sys_diary", "日记", Status.READY),
                    ),
                ),
                // 直接进设置页（去掉「打开设置」一层）；音量/开关在设置页内
                Item("sys_settings", "设置", Status.READY),
                Item(
                    "sys_community", "社区 ▶", Status.READY,
                    listOf(
                        Item("sys_about", "关于", Status.READY),
                        Item("sys_feedback", "反馈", Status.READY),
                        Item("sys_submit", "投稿", Status.LATER),
                        Item("sys_guide", "说明", Status.READY),
                    ),
                ),
                Item("sys_reset", "重置", Status.READY),
                Item("sys_exit", "退出", Status.READY),
            ),
        ),
    )
}
