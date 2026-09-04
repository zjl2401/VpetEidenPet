package com.vpet.mobile

/** 对照桌面 pet.py：HI_TEXT / CALL_TEXT / INTERACT_BANTER / WORK_MODE_BANTER（伊得）。 */
object InteractLines {
    const val HI_TEXT = "你好呀！今天也要加油哦~"
    const val CALL_TEXT = "喂？我是伊得。现在方便说话吗？"
    const val YESNO_ANSWER_TEXT = "答案之书说——"
    const val FOLLOW_DIZZY_TEXT = "我晕了……"
    const val ADULT_CONTENT_TEXT =
        "我只是像素哦，更多精彩内容请在正版游戏《新世界狂欢》中解锁"

    val DRAG_DIZZY = listOf(
        "别晃啦我晕了……",
        "慢—慢—点—拖—我—",
        "鼠标在飞吗？",
        "天旋地转……",
        "呕……别摇了",
        "再晃要吐了啦！",
        "拖我别当甩干机啊！",
    )

    val META = mapOf(
        "drag_long" to listOf(
            "你在挪窗口，不是在遛我……",
            "鼠标拖我，算不算出门？",
            "又被拎起来了。",
        ),
        "work_flag" to listOf(
            "键盘敲快点……开玩笑的。",
            "这单要是能早点收工就好了…",
            "伏案久了，伸个懒腰吧。",
        ),
        "idle_long" to listOf(
            "屏幕暗了？还是你去忙了？",
            "……还在吗？",
            "安静好久了呢。",
        ),
        "screen_edge" to listOf(
            "再往外就要掉下去了……",
            "贴边待机中。",
        ),
    )

    fun meta(event: String): String = META[event]?.random() ?: ""

    val FOLLOW_WAIT = listOf("等等我！", "别走那么快嘛~", "等等我啦！", "等等我嘛…")

    val WORK_MODE = listOf(
        "一起加油，努力工作！",
        "敲敲键盘，再赶一波进度~",
        "这单要是能早点收工就好了…",
        "你今天也很努力呢，一起加油吧！",
        "伊得也要把活干漂亮！",
        "咖啡续上，继续干活！",
        "做完这轮还有下一轮…但我们会坚持的！",
        "伏案赶工，交给我吧~",
    )

    private val banter = mapOf(
        "squat" to listOf("嗯…歇一下~", "蹲蹲更健康！"),
        "kick" to listOf("哈！", "吃我一脚！"),
        "eat" to listOf("谢谢投喂！", "肚子已经鼓鼓啦~", "还要吃吗？"),
        "sleep" to listOf("Zzz…", "好困呀…"),
        "work" to listOf("伏案赶工！", "键盘敲起来~"),
        "angry" to listOf("哼！", "气鼓鼓！"),
        "question" to listOf("嗯？", "这是怎么回事？"),
        "sad" to listOf("呜…", "心里下雨了呢…"),
        "idea" to listOf("有了！", "灵光一闪~"),
        "happy" to listOf("耶——！", "超开心！"),
        "shy" to listOf("///", "脸红了啦…"),
        "like" to listOf("棒棒！", "给你点赞~"),
        "bixin" to listOf("比心~", "爱你哦！", "传给你啦~"),
        "yes" to listOf("是！", "嗯嗯！"),
        "no" to listOf("否~", "不要啦…"),
        "yesno" to listOf("答案之书说……", "命运揭晓…"),
        "music" to listOf("♪ 一起听歌吧~", "这首好听！"),
        "expose" to listOf("屏住呼吸…", "对准了吗？", "别眨眼！", "暴露 QTE——"),
        "wink" to listOf("Wink~", "看这边~", "悄悄告诉你…"),
        "walk" to listOf("走走走~", "去哪儿呢？", "散步时间！", "腿脚活动一下~"),
        "stand" to listOf("站好啦。", "待命中~", "我在这儿哦。"),
        "hi" to listOf("你好呀！", "又见面啦~", "今天也要加油哦！"),
        "call" to listOf("喂喂？", "我是伊得~", "伊得在听！"),
        "game" to listOf("来玩一局！", "准备好了吗？", "游戏开始——"),
        "collect" to listOf("接住！", "别漏了~", "下落物来啦！"),
        "home" to listOf("欢迎回家！", "家里真舒服~", "要不要种种田？"),
        "rpg" to listOf("冒险出发！", "小心宝箱陷阱…", "公主在等你吗？"),
    )

    fun line(key: String): String =
        banter[key]?.random() ?: ""

    fun lines(key: String): List<String> = banter[key].orEmpty()
}
