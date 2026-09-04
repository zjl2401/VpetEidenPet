package com.vpet.mobile

import android.content.Context
import android.content.SharedPreferences
import kotlin.math.roundToInt

/**
 * 大小档仍用独立 pref；所属人等走 [PetProfileStore]（与桌面 pet_profile.json 对齐）。
 * 首次读取时迁移旧版 SharedPreferences 所属人。
 * 初始档位对齐苍叶手机版：小 96 / 中 128 / 大 176。
 */
object PetPrefs {
    private const val PREF = "vpet_mobile"
    private const val KEY_SIZE = "display_preset"
    private const val KEY_SIZE_PX = "display_size_px"
    private const val KEY_OWNER_LEGACY = "owner_name"
    private const val KEY_OWNER_AT_LEGACY = "owner_set_at_ms"
    private const val KEY_MIGRATED = "profile_migrated_v1"
    private const val KEY_SIZE_ALIGNED_AOBA = "size_aligned_aoba_v1"

    const val OWNER_NAME_MAX_LEN = PetProfileStore.OWNER_NAME_MAX_LEN

    /** 对齐 Aoba 手机版预设。 */
    val SIZE_PRESETS: Map<String, Int> = linkedMapOf(
        "小" to 96,
        "中" to 128,
        "大" to 176,
    )

    const val SIZE_MIN_PX = 80
    const val SIZE_MAX_PX = 200
    const val SIZE_STEP_PX = 8
    const val DEFAULT_SIZE_LABEL = "中"
    val DEFAULT_SIZE_PX: Int = SIZE_PRESETS.getValue(DEFAULT_SIZE_LABEL)

    private fun prefs(ctx: Context): SharedPreferences =
        ctx.getSharedPreferences(PREF, Context.MODE_PRIVATE)

    private fun migrateIfNeeded(ctx: Context) {
        val p = prefs(ctx)
        if (p.getBoolean(KEY_MIGRATED, false)) return
        val legacy = (p.getString(KEY_OWNER_LEGACY, "") ?: "").trim()
        if (legacy.isNotEmpty() && !PetProfileStore.hasOwner(ctx)) {
            val at = p.getLong(KEY_OWNER_AT_LEGACY, 0L)
            val profile = PetProfileStore.profile(ctx)
            profile.put("owner_name", legacy.take(OWNER_NAME_MAX_LEN))
            if (at > 0L) {
                val sdf = java.text.SimpleDateFormat("yyyy-MM-dd HH:mm", java.util.Locale.CHINA)
                profile.put("owner_set_at", sdf.format(java.util.Date(at)))
            } else {
                profile.put(
                    "owner_set_at",
                    java.text.SimpleDateFormat("yyyy-MM-dd HH:mm", java.util.Locale.CHINA)
                        .format(java.util.Date()),
                )
            }
            profile.put("owner_welcome_done", true)
            PetProfileStore.saveProfile(ctx, profile)
        }
        p.edit().putBoolean(KEY_MIGRATED, true).apply()
    }

    /** 一次性把旧版偏大默认（中=264）拉回苍叶同款中=128。 */
    private fun alignSizeOnce(ctx: Context) {
        val p = prefs(ctx)
        if (p.getBoolean(KEY_SIZE_ALIGNED_AOBA, false)) return
        val cur = if (p.contains(KEY_SIZE_PX)) p.getInt(KEY_SIZE_PX, DEFAULT_SIZE_PX) else DEFAULT_SIZE_PX
        // 仅纠正明显是旧「中/大」锚点的值，用户自调过的仍 snap 进新范围
        val reset = cur in setOf(192, 264, 360) || cur > SIZE_MAX_PX
        if (reset) {
            p.edit()
                .putInt(KEY_SIZE_PX, DEFAULT_SIZE_PX)
                .putString(KEY_SIZE, DEFAULT_SIZE_LABEL)
                .putBoolean(KEY_SIZE_ALIGNED_AOBA, true)
                .apply()
        } else {
            p.edit()
                .putInt(KEY_SIZE_PX, snapSizePx(cur))
                .putBoolean(KEY_SIZE_ALIGNED_AOBA, true)
                .apply()
        }
    }

    fun snapSizePx(px: Int): Int {
        val clamped = px.coerceIn(SIZE_MIN_PX, SIZE_MAX_PX)
        val stepped = SIZE_MIN_PX +
            ((clamped - SIZE_MIN_PX).toFloat() / SIZE_STEP_PX).roundToInt() * SIZE_STEP_PX
        return stepped.coerceIn(SIZE_MIN_PX, SIZE_MAX_PX)
    }

    /** 最近命名档（仅展示用）。 */
    fun nearestSizeLabel(px: Int): String {
        val target = snapSizePx(px)
        return SIZE_PRESETS.minByOrNull { kotlin.math.abs(it.value - target) }?.key
            ?: DEFAULT_SIZE_LABEL
    }

    fun sizeLabel(ctx: Context): String = nearestSizeLabel(sizePx(ctx))

    fun sizePx(ctx: Context): Int {
        migrateIfNeeded(ctx)
        alignSizeOnce(ctx)
        val p = prefs(ctx)
        if (p.contains(KEY_SIZE_PX)) {
            return snapSizePx(p.getInt(KEY_SIZE_PX, DEFAULT_SIZE_PX))
        }
        val label = p.getString(KEY_SIZE, DEFAULT_SIZE_LABEL) ?: DEFAULT_SIZE_LABEL
        val fromLabel = SIZE_PRESETS[label] ?: DEFAULT_SIZE_PX
        p.edit().putInt(KEY_SIZE_PX, fromLabel).apply()
        return fromLabel
    }

    fun setSizePx(ctx: Context, px: Int) {
        val snapped = snapSizePx(px)
        val label = nearestSizeLabel(snapped)
        prefs(ctx).edit()
            .putInt(KEY_SIZE_PX, snapped)
            .putString(KEY_SIZE, label)
            .putBoolean(KEY_SIZE_ALIGNED_AOBA, true)
            .apply()
    }

    fun setSizeLabel(ctx: Context, label: String) {
        val px = SIZE_PRESETS[label] ?: DEFAULT_SIZE_PX
        setSizePx(ctx, px)
    }

    fun ownerName(ctx: Context): String {
        migrateIfNeeded(ctx)
        return PetProfileStore.ownerName(ctx)
    }

    fun hasOwner(ctx: Context): Boolean {
        migrateIfNeeded(ctx)
        return PetProfileStore.hasOwner(ctx)
    }

    fun setOwnerName(ctx: Context, raw: String): Boolean {
        migrateIfNeeded(ctx)
        return PetProfileStore.setOwnerName(ctx, raw)
    }

    fun companionDays(ctx: Context): Int {
        migrateIfNeeded(ctx)
        return PetProfileStore.companionDays(ctx)
    }
}
