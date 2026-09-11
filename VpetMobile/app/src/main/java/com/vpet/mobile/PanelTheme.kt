package com.vpet.mobile

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.drawable.GradientDrawable
import android.util.AttributeSet
import android.view.Gravity
import android.view.View
import android.widget.LinearLayout
import android.widget.TextView
import kotlin.math.min

/** 奶油纸质面板壳：对照桌面 pack_panel_shell（彩虹边 + signs 条）。 */
object PanelTheme {
    fun creamPanelBg(ctx: Context): GradientDrawable = GradientDrawable().apply {
        setColor(MenuDecor.MENU_BG)
        setStroke(MenuDecor.dp(ctx, 2f), MenuDecor.THEME_BLUE)
        cornerRadius = 10f
    }

    fun applyCreamRoot(box: LinearLayout) {
        box.background = creamPanelBg(box.context)
    }

    fun title(ctx: Context, text: String): TextView =
        TextView(ctx).apply {
            this.text = text
            setTextColor(MenuDecor.THEME_PINK)
            textSize = AppDataStore.fontTitleSp(ctx)
            typeface = UiFonts.cuteBold(ctx)
        }

    fun hint(ctx: Context, text: String): TextView =
        TextView(ctx).apply {
            this.text = text
            setTextColor(MenuDecor.MENU_FG)
            alpha = 0.72f
            textSize = AppDataStore.fontHintSp(ctx)
            typeface = UiFonts.cute(ctx)
            setPadding(0, MenuDecor.dp(ctx, 4f), 0, MenuDecor.dp(ctx, 6f))
        }

    fun label(ctx: Context, text: String): TextView =
        TextView(ctx).apply {
            this.text = text
            setTextColor(MenuDecor.MENU_FG)
            textSize = AppDataStore.fontBodySp(ctx)
            typeface = UiFonts.cute(ctx)
        }

    fun primaryBtn(ctx: Context, text: String, onClick: () -> Unit): TextView =
        TextView(ctx).apply {
            this.text = text
            setTextColor(MenuDecor.MENU_FG)
            textSize = AppDataStore.fontMenuSp(ctx)
            typeface = UiFonts.cute(ctx)
            gravity = Gravity.CENTER
            setPadding(
                MenuDecor.dp(ctx, 14f),
                MenuDecor.dp(ctx, 8f),
                MenuDecor.dp(ctx, 14f),
                MenuDecor.dp(ctx, 8f),
            )
            background = MenuDecor.menuItemBg()
            setOnClickListener { onClick() }
        }

    fun attachSignStrip(parent: LinearLayout) {
        parent.addView(
            SignStripView(parent.context).apply {
                layoutParams = LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.MATCH_PARENT,
                    MenuDecor.dp(parent.context, 18f),
                ).also { it.bottomMargin = MenuDecor.dp(parent.context, 6f) }
            },
            0,
        )
    }

    fun clockBanner(ctx: Context): View =
        ClockBannerView(ctx).apply {
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                MenuDecor.dp(ctx, 72f),
            ).also { it.bottomMargin = MenuDecor.dp(ctx, 6f) }
        }

    fun cakeBanner(ctx: Context): View =
        CakeBannerView(ctx).apply {
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                MenuDecor.dp(ctx, 72f),
            ).also { it.bottomMargin = MenuDecor.dp(ctx, 6f) }
        }
}

class SignStripView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
) : View(context, attrs) {
    private val paints = ArrayList<Bitmap>()
    private val paint = Paint(Paint.FILTER_BITMAP_FLAG)

    init {
        try {
            val names = context.assets.list("signs")?.sorted().orEmpty()
            for (n in names.take(8)) {
                context.assets.open("signs/$n").use { stream ->
                    BitmapFactory.decodeStream(stream)?.let { paints += it }
                }
            }
        } catch (_: Exception) {
        }
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        if (paints.isEmpty()) {
            val step = height.coerceAtLeast(8)
            var x = 4
            var i = 0
            while (x < width - 4) {
                paint.color = MenuDecor.THEME_RAINBOW[i % MenuDecor.THEME_RAINBOW.size]
                canvas.drawCircle(x + step / 2f, height / 2f, step / 3f, paint)
                x += step + 6
                i++
            }
            return
        }
        val side = (height * 0.9f).toInt().coerceAtLeast(8)
        var x = 4
        var i = 0
        while (x + side < width - 4) {
            val bmp = paints[i % paints.size]
            val scaled = Bitmap.createScaledBitmap(bmp, side, side, false)
            canvas.drawBitmap(scaled, x.toFloat(), (height - side) / 2f, paint)
            if (scaled !== bmp) scaled.recycle()
            x += side + 6
            i++
        }
    }
}

class ClockBannerView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
) : View(context, attrs) {
    private val fill = Paint(Paint.ANTI_ALIAS_FLAG).apply { color = Color.parseColor("#FFF8EE") }
    private val ink = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = MenuDecor.THEME_PINK
        style = Paint.Style.STROKE
        strokeWidth = 3f
    }
    private val soft = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor("#33FF6B9D")
        style = Paint.Style.STROKE
        strokeWidth = 2f
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        canvas.drawRect(0f, 0f, width.toFloat(), height.toFloat(), fill)
        var x = 16
        var i = 0
        while (x < width - 20) {
            val cy = 14f + (i % 2) * 8f
            canvas.drawCircle(x.toFloat(), cy, 7f, soft)
            x += 56
            i++
        }
        val cx = width / 2f
        val cy = height / 2f + 2f
        val r = min(width, height) * 0.28f
        canvas.drawCircle(cx, cy, r, ink)
        canvas.drawLine(cx, cy, cx, cy - r * 0.55f, ink)
        canvas.drawLine(cx, cy, cx + r * 0.45f, cy + r * 0.1f, ink)
    }
}

class CakeBannerView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
) : View(context, attrs) {
    private val fill = Paint(Paint.ANTI_ALIAS_FLAG).apply { color = Color.parseColor("#FFF8EE") }
    private val cake = Paint(Paint.ANTI_ALIAS_FLAG).apply { color = MenuDecor.THEME_PINK }
    private val frosting = Paint(Paint.ANTI_ALIAS_FLAG).apply { color = MenuDecor.THEME_YELLOW }
    private val candle = Paint(Paint.ANTI_ALIAS_FLAG).apply { color = MenuDecor.THEME_BLUE }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        canvas.drawRect(0f, 0f, width.toFloat(), height.toFloat(), fill)
        val cx = width / 2f
        val baseTop = height * 0.45f
        canvas.drawRoundRect(cx - 48f, baseTop, cx + 48f, height - 10f, 8f, 8f, cake)
        canvas.drawRoundRect(cx - 40f, baseTop - 18f, cx + 40f, baseTop + 6f, 8f, 8f, frosting)
        canvas.drawRect(cx - 3f, baseTop - 36f, cx + 3f, baseTop - 16f, candle)
        canvas.drawCircle(cx, baseTop - 40f, 5f, frosting)
    }
}
