package com.vpet.mobile

import android.content.Context
import android.graphics.Color

/**
 * 内置曲库（assets/music）。对照桌面 VpetEiden/music：BGM / 主题曲 / 其他。
 */
object BundledMusic {
    const val DEFAULT_TRACK_ID = "pluviasilvae_bgm001"
    const val DEFAULT_FILE = "pluviasilvae - BGM001.mp3"
    const val DEFAULT_FOLDER = "BGM"

    data class CharDef(
        val id: String,
        val folder: String,
        val label: String,
        val colorKey: String,
    )

    data class Track(
        val folder: String,
        val fileName: String,
        val id: String = idFromFileName(fileName),
        val title: String = titleFromFileName(fileName),
        val charId: String = charIdForFolder(folder),
    ) {
        val assetPath: String get() = "music/$folder/$fileName"
        val label: String get() = "${shortFolder(folder)} · $title"
    }

    /** 对照桌面 MUSIC_CHAR_DEFS：BGM / 主题曲 / 其他（非 DMMD 角色文件夹）。 */
    val CHAR_DEFS: List<CharDef> = listOf(
        CharDef("bgm", "BGM", "BGM", "blue"),
        CharDef("theme", "主题曲", "主题曲", "pink"),
        CharDef("other", "其他", "其他", "grey"),
    )

    /** 旧苍叶文件夹名 → 伊得分类 */
    private val LEGACY_FOLDER_CHAR: Map<String, String> = mapOf(
        "aoba-blue" to "bgm",
        "ren-deep blue" to "other",
    )

    /** 对照桌面家园 FURN_COLOR_PRESETS：光圈随机取其一（不跟分类文件夹）。 */
    private val DECOR_WAVE_PALETTE: IntArray = intArrayOf(
        Color.parseColor("#E89AB0"), // 樱粉
        Color.parseColor("#8A6AB0"), // 葡萄
        Color.parseColor("#F4EAD8"), // 象牙
        Color.parseColor("#8B5A2B"), // 原木
        Color.parseColor("#6AA8D8"), // 天蓝
        Color.parseColor("#6ABA98"), // 薄荷
        Color.parseColor("#5A6068"), // 炭灰
    )

    /** 对照桌面 THEME_RAINBOW：主题曲光圈整圈彩色 */
    private val THEME_WAVE_COLORS: IntArray = intArrayOf(
        Color.parseColor("#FFC2D4"),
        Color.parseColor("#FFD4A8"),
        Color.parseColor("#FFF0A8"),
        Color.parseColor("#B8ECD4"),
        Color.parseColor("#B3E5FC"),
        Color.parseColor("#E0C4F5"),
    )

    private val TITLE_TO_ID = mapOf(
        "pluviasilvae - BGM001" to "pluviasilvae_bgm001",
        "RADICAL MAT" to "radical_mat",
        "AI CATCH" to "ai_catch",
        "Crystalline" to "crystalline",
        "your reply" to "your_reply",
        "SLIP ON THE PUMPS" to "slip_on_the_pumps",
        "By My Side" to "by_my_side",
        "felt" to "felt",
        "Lullaby Blue" to "lullaby_blue",
        "Soul Grace" to "soul_grace",
    )

    fun folders(ctx: Context): List<String> =
        ctx.assets.list("music")?.filter {
            it.isNotBlank() && !it.endsWith(".txt", true)
        }?.sorted().orEmpty()

    fun tracks(ctx: Context, folder: String? = null): List<Track> {
        val dirs = if (folder.isNullOrBlank()) folders(ctx) else listOf(folder)
        val out = mutableListOf<Track>()
        for (dir in dirs) {
            val files = ctx.assets.list("music/$dir")?.filter {
                val n = it.lowercase()
                n.endsWith(".wav") || n.endsWith(".mp3") || n.endsWith(".ogg")
            }.orEmpty().sorted()
            for (f in files) out += Track(dir, f)
        }
        return out
    }

    /** 默认曲：优先 radical_mat，否则曲库第一首。 */
    fun defaultTrack(ctx: Context): Track? {
        val all = tracks(ctx)
        if (all.isEmpty()) return null
        return all.firstOrNull { it.id == DEFAULT_TRACK_ID }
            ?: all.firstOrNull {
                it.folder == DEFAULT_FOLDER &&
                    it.fileName.equals(DEFAULT_FILE, ignoreCase = true)
            }
            ?: all.first()
    }

    fun waveColorsForFolder(folder: String): IntArray {
        if (isThemeFolder(folder)) return THEME_WAVE_COLORS.copyOf()
        return randomDecorWaveColors(folder.hashCode())
    }

    fun waveColorsForTrack(track: Track?): IntArray {
        val folder = track?.folder ?: DEFAULT_FOLDER
        if (isThemeFolder(folder)) return THEME_WAVE_COLORS.copyOf()
        val seed = (track?.id ?: folder).hashCode()
        return randomDecorWaveColors(seed)
    }

    /**
     * 跟随外部音乐 App 切歌换色：按签名稳定映射到装饰色（不跟分类）。
     */
    fun waveColorsForSignature(signature: String): IntArray {
        if (signature.isBlank()) {
            return randomDecorWaveColors(0)
        }
        return randomDecorWaveColors(signature.hashCode())
    }

    private fun isThemeFolder(folder: String): Boolean {
        val name = folder.trim()
        return name == "主题曲" || name.contains("主题") || name.contains("theme", ignoreCase = true)
    }

    private fun randomDecorWaveColors(seed: Int): IntArray {
        val idx = (seed.toLong() and 0x7fffffffL).toInt() % DECOR_WAVE_PALETTE.size
        val base = DECOR_WAVE_PALETTE[idx]
        val light = Color.argb(
            255,
            (Color.red(base) + 255) / 2,
            (Color.green(base) + 255) / 2,
            (Color.blue(base) + 255) / 2,
        )
        return intArrayOf(base, light)
    }

    fun charIdForFolder(folder: String): String =
        LEGACY_FOLDER_CHAR[folder.lowercase()]
            ?: CHAR_DEFS.firstOrNull { it.folder.equals(folder, ignoreCase = true) }?.id
            ?: when {
                folder.contains("theme", true) || folder.contains("主题") -> "theme"
                folder.contains("bgm", true) -> "bgm"
                else -> "other"
            }

    fun charLabel(charId: String): String =
        CHAR_DEFS.firstOrNull { it.id == charId }?.label ?: charId

    private fun idFromFileName(fileName: String): String {
        val stem = fileName.substringBeforeLast('.')
        return TITLE_TO_ID[stem]
            ?: stem.lowercase()
                .replace(Regex("""[^a-z0-9]+"""), "_")
                .trim('_')
                .ifBlank { "track" }
    }

    private fun titleFromFileName(fileName: String): String = fileName.substringBeforeLast('.')

    private fun shortFolder(folder: String): String = folder.substringBefore('-').ifBlank { folder }
}
