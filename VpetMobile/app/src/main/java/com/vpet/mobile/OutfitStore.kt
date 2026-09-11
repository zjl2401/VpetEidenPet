package com.vpet.mobile

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Matrix
import android.graphics.Paint
import org.json.JSONArray
import org.json.JSONObject
import java.util.UUID
import kotlin.math.max
import kotlin.math.roundToInt

/**
 * 装扮数据与像素素材（对齐桌面 pet_outfit.py）。
 * kind: builtin | user_paint | gift_art
 */
object OutfitStore {
    const val MAX = 8
    const val SCALE_MIN = 0.12f
    const val SCALE_MAX = 0.55f
    const val DEFAULT_NX = 0f
    const val DEFAULT_NY = -0.38f
    const val DEFAULT_SCALE = 0.28f
    const val DEFAULT_ROT = 0f
    const val ROT_MIN = -180f
    const val ROT_MAX = 180f

    const val KIND_BUILTIN = "builtin"
    const val KIND_USER_PAINT = "user_paint"
    const val KIND_GIFT_ART = "gift_art"

    val GROUP_ORDER = listOf("我的", "帽子", "眼镜", "颈饰", "包袋", "手持", "装饰", "表情", "公开")

    data class Decor(
        val id: String,
        var kind: String,
        var ref: String,
        var nx: Float,
        var ny: Float,
        var scale: Float,
        var rot: Float = DEFAULT_ROT,
    )

    data class Choice(val kind: String, val ref: String, val name: String, val group: String)

    private val builtinPalette = intArrayOf(
        Color.TRANSPARENT,
        Color.parseColor("#FF6688"),
        Color.parseColor("#FFCC66"),
        Color.parseColor("#66CCFF"),
        Color.parseColor("#88EEAA"),
        Color.parseColor("#FFFFFF"),
        Color.parseColor("#CC88FF"),
        Color.parseColor("#442233"),
        Color.parseColor("#FF4444"),
        Color.parseColor("#8899EE"),
        Color.parseColor("#88DDFF"),
        Color.parseColor("#8A6848"),
        Color.parseColor("#F0E0C8"),
        Color.parseColor("#D4A84A"),
        Color.parseColor("#1A1A22"),
        Color.parseColor("#FF9944"),
        Color.parseColor("#3A5080"),
        Color.parseColor("#F0A0C0"),
        Color.parseColor("#8899AA"),
    )

    fun defaultsFor(kind: String, ref: String): FloatArray {
        if (kind == KIND_BUILTIN) {
            val e = OutfitBuiltinData.catalog.firstOrNull { it.id == ref }
            if (e != null) {
                return floatArrayOf(clampNorm(e.nx), clampNorm(e.ny), clampScale(e.scale), DEFAULT_ROT)
            }
        }
        return floatArrayOf(DEFAULT_NX, DEFAULT_NY, DEFAULT_SCALE, DEFAULT_ROT)
    }

    fun clampNorm(v: Float): Float = v.coerceIn(-0.55f, 0.55f)
    fun clampScale(v: Float): Float = v.coerceIn(SCALE_MIN, SCALE_MAX)
    fun clampRot(v: Float): Float = v.coerceIn(ROT_MIN, ROT_MAX)

    fun load(ctx: Context): List<Decor> {
        val arr = PetProfileStore.profile(ctx).optJSONArray("outfit_decors") ?: return emptyList()
        val out = ArrayList<Decor>()
        for (i in 0 until arr.length()) {
            val o = arr.optJSONObject(i) ?: continue
            val kind = o.optString("kind")
            if (kind !in setOf(KIND_BUILTIN, KIND_USER_PAINT, KIND_GIFT_ART)) continue
            val ref = o.optString("ref")
            if (kind == KIND_BUILTIN && ref.isBlank()) continue
            out += Decor(
                id = o.optString("id").ifBlank { UUID.randomUUID().toString().take(10) },
                kind = kind,
                ref = ref,
                nx = clampNorm(o.optDouble("nx", DEFAULT_NX.toDouble()).toFloat()),
                ny = clampNorm(o.optDouble("ny", DEFAULT_NY.toDouble()).toFloat()),
                scale = clampScale(o.optDouble("scale", DEFAULT_SCALE.toDouble()).toFloat()),
                rot = clampRot(o.optDouble("rot", DEFAULT_ROT.toDouble()).toFloat()),
            )
            if (out.size >= MAX) break
        }
        return out
    }

    fun save(ctx: Context, list: List<Decor>) {
        val p = PetProfileStore.profile(ctx)
        val arr = JSONArray()
        for (d in list.take(MAX)) {
            arr.put(
                JSONObject()
                    .put("id", d.id)
                    .put("kind", d.kind)
                    .put("ref", d.ref)
                    .put("nx", d.nx.toDouble())
                    .put("ny", d.ny.toDouble())
                    .put("scale", d.scale.toDouble())
                    .put("rot", d.rot.toDouble()),
            )
        }
        p.put("outfit_decors", arr)
        PetProfileStore.saveProfile(ctx, p)
    }

    fun newDecor(
        kind: String,
        ref: String,
        nx: Float = DEFAULT_NX,
        ny: Float = DEFAULT_NY,
        scale: Float = DEFAULT_SCALE,
        rot: Float = DEFAULT_ROT,
    ) = Decor(
        UUID.randomUUID().toString().take(10),
        kind,
        ref,
        clampNorm(nx),
        clampNorm(ny),
        clampScale(scale),
        clampRot(rot),
    )

    fun choices(ctx: Context): List<Choice> {
        val list = mutableListOf<Choice>()
        if (assetExists(ctx, "home/user_paint.png")) {
            list += Choice(KIND_USER_PAINT, "", "自创画", "我的")
        }
        if (assetExists(ctx, "home/gift_art.png")) {
            list += Choice(KIND_GIFT_ART, "", "礼物画", "我的")
        }
        for (e in OutfitBuiltinData.catalog) {
            list += Choice(KIND_BUILTIN, e.id, e.name, e.group)
        }
        val rank = GROUP_ORDER.withIndex().associate { it.value to it.index }
        return list.withIndex().sortedWith(
            compareBy({ rank[it.value.group] ?: 99 }, { it.index }),
        ).map { it.value }
    }

    private fun assetExists(ctx: Context, path: String): Boolean =
        try {
            ctx.assets.open(path).close()
            true
        } catch (_: Exception) {
            false
        }

    fun bitmapFor(ctx: Context, decor: Decor, sizePx: Int): Bitmap? {
        val side = sizePx.coerceAtLeast(8)
        return when (decor.kind) {
            KIND_BUILTIN -> builtinBitmap(decor.ref, side)
            KIND_USER_PAINT -> decodeAsset(ctx, "home/user_paint.png", side)
            KIND_GIFT_ART -> decodeAsset(ctx, "home/gift_art.png", side)
            else -> null
        }
    }

    fun thumbFor(ctx: Context, choice: Choice, sizePx: Int = 36): Bitmap? =
        bitmapFor(ctx, Decor("t", choice.kind, choice.ref, 0f, 0f, DEFAULT_SCALE), sizePx)

    private fun decodeAsset(ctx: Context, path: String, sizePx: Int): Bitmap? =
        try {
            ctx.assets.open(path).use { stream ->
                val raw = BitmapFactory.decodeStream(stream) ?: return null
                fitIntoSquare(raw, sizePx)
            }
        } catch (_: Exception) {
            null
        }

    private fun fitIntoSquare(src: Bitmap, side: Int): Bitmap {
        val sw = src.width.coerceAtLeast(1)
        val sh = src.height.coerceAtLeast(1)
        if (sw == side && sh == side) return src
        val scale = minOf(side.toFloat() / sw, side.toFloat() / sh)
        val nw = max(1, (sw * scale).roundToInt())
        val nh = max(1, (sh * scale).roundToInt())
        val scaled = if (nw == sw && nh == sh) src else Bitmap.createScaledBitmap(src, nw, nh, false)
        val out = Bitmap.createBitmap(side, side, Bitmap.Config.ARGB_8888)
        Canvas(out).drawBitmap(scaled, (side - nw) / 2f, (side - nh).toFloat(), null)
        if (scaled !== src && scaled !== out) {
            try {
                scaled.recycle()
            } catch (_: Exception) {
            }
        }
        if (src !== out && src !== scaled) {
            try {
                src.recycle()
            } catch (_: Exception) {
            }
        }
        return out
    }

    private fun builtinBitmap(ref: String, sizePx: Int): Bitmap? {
        val cells = OutfitBuiltinData.catalog.firstOrNull { it.id == ref }?.cells ?: return null
        val scale = 4
        val base = 12 * scale
        val bmp = Bitmap.createBitmap(base, base, Bitmap.Config.ARGB_8888)
        val c = Canvas(bmp)
        val p = Paint().apply {
            style = Paint.Style.FILL
            isAntiAlias = false
        }
        for (y in 0 until 12) {
            for (x in 0 until 12) {
                val idx = cells[y * 12 + x]
                if (idx <= 0 || idx >= builtinPalette.size) continue
                p.color = builtinPalette[idx]
                c.drawRect(
                    (x * scale).toFloat(),
                    (y * scale).toFloat(),
                    ((x + 1) * scale).toFloat(),
                    ((y + 1) * scale).toFloat(),
                    p,
                )
            }
        }
        return if (sizePx == base) bmp else fitIntoSquare(bmp, sizePx)
    }

    /** 在宠框坐标系绘制（PAD 已由调用方处理时，传 pet 边长与左上）。 */
    fun drawOnPet(
        canvas: Canvas,
        ctx: Context,
        petLeft: Float,
        petTop: Float,
        petSize: Float,
        list: List<Decor>,
    ) {
        if (list.isEmpty()) return
        val cx = petLeft + petSize / 2f
        val cy = petTop + petSize / 2f
        val paint = Paint(Paint.FILTER_BITMAP_FLAG)
        for (d in list) {
            val side = max(8, (petSize * d.scale).roundToInt())
            val bmp = bitmapFor(ctx, d, side) ?: continue
            val x = cx + d.nx * petSize - bmp.width / 2f
            val y = cy + d.ny * petSize - bmp.height / 2f
            if (kotlin.math.abs(d.rot) < 0.5f) {
                canvas.drawBitmap(bmp, x, y, null)
            } else {
                val m = Matrix()
                m.postTranslate(-bmp.width / 2f, -bmp.height / 2f)
                m.postRotate(d.rot)
                m.postTranslate(cx + d.nx * petSize, cy + d.ny * petSize)
                canvas.drawBitmap(bmp, m, paint)
            }
        }
    }
}
