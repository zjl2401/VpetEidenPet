package com.vpet.mobile

import android.content.Context
import android.content.SharedPreferences
import android.util.TypedValue
import android.widget.TextView
import org.json.JSONArray
import org.json.JSONObject
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.UUID

/** 日记 / 成就 / 应用设置（字体·声音·难度）。 */
object AppDataStore {
    private const val PREF = "vpet_appdata"
    private const val KEY_DIARY = "diary_json"
    private const val KEY_ACH = "achievements_json"
    private const val KEY_FONT = "font_label"
    private const val KEY_SOUND = "sound_on"
    private const val KEY_VOICE_MODE = "voice_mode"
    private const val KEY_VOICE_VOL = "voice_volume"
    private const val KEY_SFX_VOL = "sfx_volume"
    private const val KEY_AUDIO_BALANCE = "audio_balance_v2"
    private const val KEY_DIFF = "difficulty"
    private const val KEY_FREE_IDLE_SEC = "free_idle_banter_sec"

    /** 与桌面 FONT_SIZE_PRESETS 对齐：小/中/大/特大（档差拉开，便于肉眼分辨）。 */
    val FONT_PRESETS = linkedMapOf("小" to 12f, "中" to 14f, "大" to 17f, "特大" to 21f)

    /**
     * Kotlin 的 `TextView.textSize =` 会按 **px** 赋值；字号设置必须走 SP。
     */
    fun applySp(tv: TextView?, sp: Float) {
        tv ?: return
        tv.setTextSize(TypedValue.COMPLEX_UNIT_SP, sp)
    }
    val DIFF_PRESETS = listOf("低", "中", "高")
    /** 自由站立闲聊间隔（秒）· 自定义范围。 */
    const val FREE_IDLE_SEC_MIN = 5
    const val FREE_IDLE_SEC_MAX = 120
    const val FREE_IDLE_SEC_DEFAULT = 20
    @Deprecated("改用连续秒数")
    val FREE_IDLE_SEC_PRESETS = listOf(10, 20, 30)

    private fun prefs(ctx: Context): SharedPreferences =
        ctx.getSharedPreferences(PREF, Context.MODE_PRIVATE)

    fun fontLabel(ctx: Context): String {
        val v = prefs(ctx).getString(KEY_FONT, "中") ?: "中"
        return if (v in FONT_PRESETS) v else "中"
    }

    fun fontSp(ctx: Context): Float = FONT_PRESETS.getValue(fontLabel(ctx))

    /** 面板/菜单统一字号层级（相对 fontSp）。 */
    fun fontTitleSp(ctx: Context): Float = fontSp(ctx) + 3f
    fun fontBodySp(ctx: Context): Float = fontSp(ctx)
    fun fontCaptionSp(ctx: Context): Float = (fontSp(ctx) - 1f).coerceAtLeast(9f)
    fun fontHintSp(ctx: Context): Float = (fontSp(ctx) - 2f).coerceAtLeast(8f)
    fun fontMenuSp(ctx: Context): Float = fontSp(ctx)
    fun fontClockTitleSp(ctx: Context): Float = fontCaptionSp(ctx)
    fun fontClockTimeSp(ctx: Context): Float = (fontSp(ctx) + 6f).coerceAtLeast(16f)
    fun fontClockBtnSp(ctx: Context): Float = fontCaptionSp(ctx)

    fun setFontLabel(ctx: Context, label: String) {
        val k = if (label in FONT_PRESETS) label else "中"
        prefs(ctx).edit().putString(KEY_FONT, k).apply()
    }

    /** 音效（打字音等）；对照桌面 sfx，与语音分离。 */
    fun soundOn(ctx: Context): Boolean = prefs(ctx).getBoolean(KEY_SOUND, true)

    fun setSoundOn(ctx: Context, on: Boolean) {
        prefs(ctx).edit().putBoolean(KEY_SOUND, on).apply()
    }

    /** 语音模式；对照桌面 voice_mode。默认开（兼容旧「声音含语音」习惯）。 */
    fun voiceMode(ctx: Context): Boolean = prefs(ctx).getBoolean(KEY_VOICE_MODE, true)

    fun setVoiceMode(ctx: Context, on: Boolean) {
        prefs(ctx).edit().putBoolean(KEY_VOICE_MODE, on).apply()
    }

    /** 语音音量 0–100；默认偏大（手机喇叭上原先偏小）。 */
    fun voiceVolume(ctx: Context): Int = prefs(ctx).getInt(KEY_VOICE_VOL, 100).coerceIn(0, 100)

    fun setVoiceVolume(ctx: Context, v: Int) {
        prefs(ctx).edit().putInt(KEY_VOICE_VOL, v.coerceIn(0, 100)).apply()
    }

    /** 播放增益：滑条到顶也能更响一点（MediaPlayer 上限 1）。 */
    fun voiceVolumeF(ctx: Context): Float =
        (voiceVolume(ctx) / 100f * 1.2f).coerceIn(0f, 1f)

    /** 音效相对音量 0–100；默认压低（打字音等原先偏响）。 */
    fun sfxVolume(ctx: Context): Int = prefs(ctx).getInt(KEY_SFX_VOL, 28).coerceIn(0, 100)

    fun setSfxVolume(ctx: Context, v: Int) {
        prefs(ctx).edit().putInt(KEY_SFX_VOL, v.coerceIn(0, 100)).apply()
    }

    fun sfxVolumeF(ctx: Context): Float = (sfxVolume(ctx) / 100f).coerceIn(0f, 1f)

    /** 一次性：抬高默认语音、压低音效（旧装默认语音 80 偏小）。 */
    fun ensureAudioBalance(ctx: Context) {
        val p = prefs(ctx)
        if (p.getBoolean(KEY_AUDIO_BALANCE, false)) return
        val ed = p.edit().putBoolean(KEY_AUDIO_BALANCE, true)
        if (!p.contains(KEY_SFX_VOL)) ed.putInt(KEY_SFX_VOL, 28)
        val curVoice = p.getInt(KEY_VOICE_VOL, 100)
        if (curVoice in 1..85) ed.putInt(KEY_VOICE_VOL, 100)
        ed.apply()
    }

    fun difficulty(ctx: Context): String {
        val v = prefs(ctx).getString(KEY_DIFF, "中") ?: "中"
        return if (v in DIFF_PRESETS) v else "中"
    }

    fun setDifficulty(ctx: Context, d: String) {
        val k = if (d in DIFF_PRESETS) d else "中"
        prefs(ctx).edit().putString(KEY_DIFF, k).apply()
    }

    /** 自由模式站立时语音/动作触发间隔（秒），默认 20，可自定义。 */
    fun freeIdleBanterSec(ctx: Context): Int =
        prefs(ctx).getInt(KEY_FREE_IDLE_SEC, FREE_IDLE_SEC_DEFAULT)
            .coerceIn(FREE_IDLE_SEC_MIN, FREE_IDLE_SEC_MAX)

    fun setFreeIdleBanterSec(ctx: Context, sec: Int) {
        prefs(ctx).edit()
            .putInt(KEY_FREE_IDLE_SEC, sec.coerceIn(FREE_IDLE_SEC_MIN, FREE_IDLE_SEC_MAX))
            .apply()
    }

    // —— 工作显示设置（对齐 show_props / show_stack）——
    private const val KEY_WORK_PROPS = "work_show_props"
    private const val KEY_WORK_STACK = "work_show_stack"
    private const val KEY_PERSONA = "persona" // default | jinmu
    private const val KEY_STAMINA = "stamina"
    private const val KEY_MOOD = "mood"
    private const val KEY_COMPANION = "companion_enabled"
    private const val KEY_COMPANION_ASTER = "companion_aster"
    private const val KEY_COMPANION_MORVAY = "companion_morvay"

    fun workShowProps(ctx: Context): Boolean = prefs(ctx).getBoolean(KEY_WORK_PROPS, true)
    fun setWorkShowProps(ctx: Context, v: Boolean) {
        prefs(ctx).edit().putBoolean(KEY_WORK_PROPS, v).apply()
    }
    fun workShowStack(ctx: Context): Boolean = prefs(ctx).getBoolean(KEY_WORK_STACK, true)
    fun setWorkShowStack(ctx: Context, v: Boolean) {
        prefs(ctx).edit().putBoolean(KEY_WORK_STACK, v).apply()
    }

    fun persona(ctx: Context): String =
        prefs(ctx).getString(KEY_PERSONA, "default") ?: "default"

    fun isJinmu(ctx: Context): Boolean = persona(ctx) == "jinmu"

    fun togglePersona(ctx: Context): String {
        val next = if (isJinmu(ctx)) "default" else "jinmu"
        prefs(ctx).edit().putString(KEY_PERSONA, next).apply()
        return next
    }

    fun stamina(ctx: Context): Int = prefs(ctx).getInt(KEY_STAMINA, 80).coerceIn(0, 100)
    fun mood(ctx: Context): Int = prefs(ctx).getInt(KEY_MOOD, 80).coerceIn(0, 100)
    fun setStamina(ctx: Context, v: Int) {
        prefs(ctx).edit().putInt(KEY_STAMINA, v.coerceIn(0, 100)).apply()
    }
    fun setMood(ctx: Context, v: Int) {
        prefs(ctx).edit().putInt(KEY_MOOD, v.coerceIn(0, 100)).apply()
    }
    fun addStaminaMood(ctx: Context, ds: Int, dm: Int) {
        setStamina(ctx, stamina(ctx) + ds)
        setMood(ctx, mood(ctx) + dm)
    }

    fun companionEnabled(ctx: Context): Boolean =
        companionAsterEnabled(ctx) || companionMorvayEnabled(ctx) ||
            prefs(ctx).getBoolean(KEY_COMPANION, false)

    fun setCompanionEnabled(ctx: Context, on: Boolean) {
        prefs(ctx).edit().putBoolean(KEY_COMPANION, on).apply()
    }

    fun companionAsterEnabled(ctx: Context): Boolean {
        val p = prefs(ctx)
        if (!p.contains(KEY_COMPANION_ASTER) && p.getBoolean(KEY_COMPANION, false)) {
            return true
        }
        return p.getBoolean(KEY_COMPANION_ASTER, false)
    }

    fun companionMorvayEnabled(ctx: Context): Boolean =
        prefs(ctx).getBoolean(KEY_COMPANION_MORVAY, false)

    fun setCompanionAsterEnabled(ctx: Context, on: Boolean) {
        prefs(ctx).edit().putBoolean(KEY_COMPANION_ASTER, on).apply()
    }

    fun setCompanionMorvayEnabled(ctx: Context, on: Boolean) {
        prefs(ctx).edit().putBoolean(KEY_COMPANION_MORVAY, on).apply()
    }

    fun diaries(ctx: Context): JSONArray {
        return try {
            JSONArray(prefs(ctx).getString(KEY_DIARY, "[]"))
        } catch (_: Exception) {
            JSONArray()
        }
    }

    /** 日记天气选项（对照桌面 DIARY_WEATHER_OPTIONS）。 */
    val DIARY_WEATHER: List<Pair<String, String>> = listOf(
        "sunny" to "晴朗",
        "partly" to "多云",
        "cloudy" to "阴天",
        "fog" to "有雾",
        "drizzle" to "毛毛雨",
        "rain" to "降雨",
        "snow" to "降雪",
        "storm" to "雷暴",
    )

    /** 日记心情（对照桌面 DIARY_MOOD_FACES 标签）。 */
    val DIARY_MOODS: List<Pair<String, String>> = listOf(
        "stand" to "平常",
        "happy" to "开心",
        "wink" to "Wink",
        "like" to "点赞",
        "shy" to "害羞",
        "sad" to "伤心",
        "angry" to "生气",
        "question" to "疑惑",
        "speechless" to "无语",
        "awkward" to "尴尬",
        "zzz" to "睡觉Z",
        "sleep" to "困倦",
    )

    fun diaryWeatherLabel(kind: String): String =
        DIARY_WEATHER.firstOrNull { it.first == kind }?.second.orEmpty()

    fun diaryMoodLabel(face: String): String =
        DIARY_MOODS.firstOrNull { it.first == face }?.second.orEmpty()

    fun defaultDiaryMoodFace(ctx: Context): String {
        val v = mood(ctx)
        return when {
            v >= 85 -> "happy"
            v >= 65 -> "wink"
            v >= 45 -> "stand"
            v >= 25 -> "sad"
            else -> "sleep"
        }
    }

    fun addDiary(
        ctx: Context,
        text: String,
        weather: String = "sunny",
        moodFace: String = "stand",
        auto: Boolean = false,
    ): Boolean {
        val t = text.trim()
        if (t.isEmpty()) return false
        val arr = diaries(ctx)
        val now = Date()
        val dateFmt = SimpleDateFormat("yyyy-MM-dd", Locale.CHINA)
        val timeFmt = SimpleDateFormat("HH:mm", Locale.CHINA)
        val tsFmt = SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.CHINA)
        val w = weather.ifBlank { "sunny" }
        val face = moodFace.ifBlank { defaultDiaryMoodFace(ctx) }
        // 新页插到最前（对照桌面翻页 0=最新）
        val obj = JSONObject()
            .put("id", UUID.randomUUID().toString())
            .put("ts", tsFmt.format(now))
            .put("date", dateFmt.format(now))
            .put("time", timeFmt.format(now))
            .put("text", t.take(400))
            .put("weather", w)
            .put("weather_label", diaryWeatherLabel(w))
            .put("mood_face", face)
            .put("mood_label", diaryMoodLabel(face))
            .put("auto", auto)
        val next = JSONArray()
        next.put(obj)
        for (i in 0 until arr.length()) {
            if (next.length() >= 200) break
            next.put(arr.getJSONObject(i))
        }
        prefs(ctx).edit().putString(KEY_DIARY, next.toString()).apply()
        unlock(ctx, "diary_first")
        if (next.length() >= 5) unlock(ctx, "diary_count")
        return true
    }

    fun addAutoDiary(ctx: Context, text: String) {
        addDiary(ctx, text, weather = "sunny", moodFace = defaultDiaryMoodFace(ctx), auto = true)
    }

    fun deleteDiary(ctx: Context, id: String): Boolean {
        if (id.isBlank()) return false
        val arr = diaries(ctx)
        val next = JSONArray()
        var removed = false
        for (i in 0 until arr.length()) {
            val o = arr.getJSONObject(i)
            if (o.optString("id") == id) {
                removed = true
                continue
            }
            next.put(o)
        }
        if (!removed) return false
        prefs(ctx).edit().putString(KEY_DIARY, next.toString()).apply()
        return true
    }

    fun clearDiaries(ctx: Context) {
        prefs(ctx).edit().putString(KEY_DIARY, "[]").apply()
    }

    fun achievements(ctx: Context): Set<String> {
        val raw = prefs(ctx).getString(KEY_ACH, "[]") ?: "[]"
        return try {
            val arr = JSONArray(raw)
            buildSet {
                for (i in 0 until arr.length()) add(arr.getString(i))
            }
        } catch (_: Exception) {
            emptySet()
        }
    }

    fun unlock(ctx: Context, id: String) {
        val set = achievements(ctx).toMutableSet()
        if (set.add(id)) {
            val arr = JSONArray()
            set.forEach { arr.put(it) }
            prefs(ctx).edit().putString(KEY_ACH, arr.toString()).apply()
        }
    }

    fun achievementCatalog(): List<Triple<String, String, String>> = listOf(
        Triple("owner_named", "认主成功", "填写所属人昵称"),
        Triple("companion_on", "使魔来伴", "开启使魔栏"),
        Triple("diary_first", "落笔成忆", "写下第一条日记"),
        Triple("memory_open", "翻开回忆", "打开画廊或留声"),
        Triple("home_visit", "回家看看", "进入家园"),
        Triple("farm_open", "田园生活", "开启家园经营"),
        Triple("music_play", "耳机不离", "进入音乐模式"),
        Triple("listen_hour", "一小时歌单", "累计听歌满 1 小时"),
        Triple("work_done", "伏案赶工", "完成一次伏案工作"),
        Triple("rpg_play", "誓言启程", "打开 Silent Oath"),
        Triple("pomo_done", "番茄达人", "完成一轮番茄"),
        Triple("timer_use", "时间在手", "使用一次秒表或计时器"),
    )

    /**
     * 重置：清日记/成就标记/设置等到默认。
     * 保留所属人、相伴起点、装扮、戴花；模式时长/食物背包/钱包在独立 prefs，本函数不碰。
     */
    fun resetKeepOwner(ctx: Context) {
        val cur = PetProfileStore.profile(ctx)
        val ownerName = cur.optString("owner_name", "").trim()
        val ownerAt = cur.optString("owner_set_at")
        val outfit = cur.optJSONArray("outfit_decors")
        val wearFlower = cur.optBoolean("wear_flower", false)
        val created = cur.optString("created").ifBlank {
            ownerAt.ifBlank {
                SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.CHINA).format(Date())
            }
        }
        prefs(ctx).edit().clear().apply()
        val p = JSONObject()
            .put("owner_name", ownerName)
            .put("owner_set_at", ownerAt)
            .put("owner_welcome_done", ownerName.isNotEmpty())
            .put("created", created)
            .put("bless_month", 0)
            .put("bless_day", 0)
            .put("bless_message", "")
            .put("gift_text", "")
            .put("wear_flower", wearFlower)
            .put("records", JSONObject())
        if (outfit != null && outfit.length() > 0) {
            p.put("outfit_decors", outfit)
        }
        PetProfileStore.saveProfile(ctx, p)
        PetProfileStore.saveSchedules(ctx, JSONArray())
        PetProfileStore.setMusic(ctx, null, null)
        PetPrefs.setSizeLabel(ctx, PetPrefs.DEFAULT_SIZE_LABEL)
        PersistVault.snapshot(ctx)
    }
}
