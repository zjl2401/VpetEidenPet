package com.vpet.mobile

import android.app.Dialog
import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Canvas
import android.graphics.PixelFormat
import android.graphics.Typeface
import android.graphics.drawable.BitmapDrawable
import android.util.TypedValue
import android.view.Gravity
import android.view.MotionEvent
import android.view.WindowManager
import android.widget.Button
import android.widget.HorizontalScrollView
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.SeekBar
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.view.ContextThemeWrapper

/** 面板 → 装扮：初始无装饰；拖预览定位、点素材替换、可叠多件。 */
object OutfitEditorUi {
    private var openDialog: Dialog? = null

    fun show(context: Context, onSaved: () -> Unit) {
        openDialog?.dismiss()
        val themed = ContextThemeWrapper(context, R.style.Theme_VpetMobile)
        val pad = dp(themed, 12)
        val draft = OutfitStore.load(context).map { it.copy() }.toMutableList()
        var pendingKind = ""
        var pendingRef = ""
        var pendingNx = OutfitStore.DEFAULT_NX
        var pendingNy = OutfitStore.DEFAULT_NY
        var pendingScale = OutfitStore.DEFAULT_SCALE
        var pendingRot = OutfitStore.DEFAULT_ROT
        var pendingLive = false
        var selectedId: String? = draft.firstOrNull()?.id

        val root = LinearLayout(themed).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(pad, pad, pad, pad)
            background = PanelTheme.creamPanelBg(themed)
        }
        PanelTheme.attachSignStrip(root)
        root.addView(TextView(themed).apply {
            text = "装扮"
            setTextColor(MenuDecor.THEME_PINK)
            textSize = AppDataStore.fontTitleSp(context)
            typeface = UiFonts.cute(context)
            setTypeface(typeface, Typeface.BOLD)
        })
        root.addView(TextView(themed).apply {
            text = "初始无装饰；保存后下次打开仍保留\n列表点选 · 拖预览移动 · 点素材替换 · 可叠多件"
            setTextColor(MenuDecor.MENU_FG); alpha = 0.7f
            textSize = AppDataStore.fontHintSp(context)
            typeface = UiFonts.cute(context)
            setPadding(0, dp(themed, 4), 0, dp(themed, 8))
        })

        val preview = ImageView(themed).apply {
            layoutParams = LinearLayout.LayoutParams(dp(themed, 200), dp(themed, 200))
            scaleType = ImageView.ScaleType.FIT_CENTER
            setBackgroundColor(MenuDecor.THEME_ITEM_BG)
        }
        root.addView(preview)
        val tip = TextView(themed).apply {
            setTextColor(MenuDecor.THEME_BLUE)
            textSize = AppDataStore.fontHintSp(context)
            typeface = UiFonts.cute(context)
            setPadding(0, dp(themed, 4), 0, dp(themed, 4))
        }
        root.addView(tip)

        val nudgeRow = LinearLayout(themed).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
        }
        root.addView(nudgeRow)

        val listHost = LinearLayout(themed).apply { orientation = LinearLayout.VERTICAL }
        root.addView(listHost)

        val scaleBar = SeekBar(themed).apply {
            max = 100
            val initScale = draft.firstOrNull()?.scale ?: pendingScale
            progress = (((initScale - OutfitStore.SCALE_MIN) /
                (OutfitStore.SCALE_MAX - OutfitStore.SCALE_MIN)) * 100).toInt()
        }
        root.addView(TextView(themed).apply {
            text = "大小"
            setTextColor(MenuDecor.MENU_FG)
            textSize = AppDataStore.fontBodySp(context)
            typeface = UiFonts.cute(context)
        })
        root.addView(scaleBar)

        val rotBar = SeekBar(themed).apply {
            max = 100
            val initRot = draft.firstOrNull()?.rot ?: pendingRot
            progress = (((initRot - OutfitStore.ROT_MIN) /
                (OutfitStore.ROT_MAX - OutfitStore.ROT_MIN)) * 100).toInt().coerceIn(0, 100)
        }
        root.addView(TextView(themed).apply {
            text = "旋转"
            setTextColor(MenuDecor.MENU_FG)
            textSize = AppDataStore.fontBodySp(context)
            typeface = UiFonts.cute(context)
        })
        root.addView(rotBar)

        lateinit var addBtn: Button
        val assetButtons = mutableMapOf<String, Button>()

        fun scaleFromBar(): Float {
            val t = scaleBar.progress / 100f
            return OutfitStore.clampScale(
                OutfitStore.SCALE_MIN + t * (OutfitStore.SCALE_MAX - OutfitStore.SCALE_MIN),
            )
        }

        fun rotFromBar(): Float {
            val t = rotBar.progress / 100f
            return OutfitStore.clampRot(
                OutfitStore.ROT_MIN + t * (OutfitStore.ROT_MAX - OutfitStore.ROT_MIN),
            )
        }

        fun syncRotBar(rot: Float) {
            val t = ((rot - OutfitStore.ROT_MIN) / (OutfitStore.ROT_MAX - OutfitStore.ROT_MIN))
                .coerceIn(0f, 1f)
            rotBar.progress = (t * 100f).toInt().coerceIn(0, 100)
        }

        fun current(): OutfitStore.Decor? = draft.firstOrNull { it.id == selectedId }

        fun applyPos(nx: Float, ny: Float) {
            val cx = OutfitStore.clampNorm(nx)
            val cy = OutfitStore.clampNorm(ny)
            val t = current()
            if (t != null) {
                t.nx = cx
                t.ny = cy
            } else {
                pendingNx = cx
                pendingNy = cy
            }
        }

        fun rebuildPreview() {
            val size = 200
            val bmp = Bitmap.createBitmap(size, size, Bitmap.Config.ARGB_8888)
            val c = Canvas(bmp)
            c.drawColor(MenuDecor.MENU_BG)
            fun drawFit(src: Bitmap, maxSide: Int) {
                val sw = src.width.coerceAtLeast(1)
                val sh = src.height.coerceAtLeast(1)
                val scale = minOf(maxSide.toFloat() / sw, maxSide.toFloat() / sh)
                val nw = maxOf(1, (sw * scale).toInt())
                val nh = maxOf(1, (sh * scale).toInt())
                val scaled = if (nw == sw && nh == sh) src else Bitmap.createScaledBitmap(src, nw, nh, false)
                c.drawBitmap(scaled, (size - nw) / 2f, (size - nh).toFloat(), null)
            }
            try {
                context.assets.open("gallery/stand.png").use { stream ->
                    val stand = BitmapFactory.decodeStream(stream)
                    if (stand != null) drawFit(stand, size)
                }
            } catch (_: Exception) {
                try {
                    context.assets.open("home/house.png").use { stream ->
                        val stand = BitmapFactory.decodeStream(stream)
                        if (stand != null) drawFit(stand, size / 2)
                    }
                } catch (_: Exception) {
                }
            }
            val view = draft.toMutableList()
            val tgt = current()
            if (tgt == null && pendingLive && pendingKind.isNotBlank()) {
                view += OutfitStore.newDecor(
                    pendingKind, pendingRef, pendingNx, pendingNy, scaleFromBar(), rotFromBar(),
                )
            }
            OutfitStore.drawOnPet(c, context, 0f, 0f, size.toFloat(), view)
            preview.setImageBitmap(bmp)
            val t = current()
            tip.text = when {
                t != null ->
                    "编辑中 · (${"%.2f".format(t.nx)}, ${"%.2f".format(t.ny)})  " +
                        "缩放 ${"%.2f".format(t.scale)}  旋转 ${"%.0f".format(t.rot)}°\n拖预览 · 点素材可换"
                pendingLive ->
                    "待添加 · (${"%.2f".format(pendingNx)}, ${"%.2f".format(pendingNy)})  " +
                        "缩放 ${"%.2f".format(scaleFromBar())}  旋转 ${"%.0f".format(rotFromBar())}°\n拖预览 · 点「添加」"
                else -> "当前无待添加件 · 点素材开始选，或点列表编辑已有件"
            }
            addBtn.text = if (t != null) "再添一件" else "添加所选"
            val curKey = when {
                t != null -> "${t.kind}|${t.ref}"
                pendingLive -> "$pendingKind|$pendingRef"
                else -> ""
            }
            for ((key, btn) in assetButtons) {
                btn.setBackgroundColor(if (key == curKey) 0xFF4A6A88.toInt() else 0xFF1A2838.toInt())
            }
        }

        fun rebuildList() {
            listHost.removeAllViews()
            if (draft.isEmpty()) {
                listHost.addView(TextView(themed).apply {
                    text = "（还没有装饰）"
                    setTextColor(0xFF667788.toInt())
                    textSize = AppDataStore.fontCaptionSp(context)
                    typeface = UiFonts.cute(context)
                })
                return
            }
            for (d in draft) {
                val label = when (d.kind) {
                    OutfitStore.KIND_USER_PAINT -> "自创画"
                    OutfitStore.KIND_GIFT_ART -> "礼物画"
                    else -> OutfitBuiltinData.catalog.firstOrNull { it.id == d.ref }?.name ?: d.ref
                }
                val row = LinearLayout(themed).apply {
                    orientation = LinearLayout.HORIZONTAL
                    gravity = Gravity.CENTER_VERTICAL
                }
                row.addView(Button(themed).apply {
                    text = (if (d.id == selectedId) "● " else "○ ") + label
                    setOnClickListener {
                        selectedId = d.id
                        pendingLive = false
                        pendingScale = d.scale
                        pendingRot = d.rot
                        pendingKind = d.kind
                        pendingRef = d.ref
                        pendingNx = d.nx
                        pendingNy = d.ny
                        scaleBar.progress = (((d.scale - OutfitStore.SCALE_MIN) /
                            (OutfitStore.SCALE_MAX - OutfitStore.SCALE_MIN)) * 100).toInt()
                        syncRotBar(d.rot)
                        rebuildList()
                        rebuildPreview()
                        Toast.makeText(context, "已选中该配饰", Toast.LENGTH_SHORT).show()
                    }
                    layoutParams = LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f)
                })
                row.addView(Button(themed).apply {
                    text = "删"
                    setOnClickListener {
                        draft.removeAll { it.id == d.id }
                        if (selectedId == d.id) {
                            selectedId = draft.firstOrNull()?.id
                            draft.firstOrNull()?.let {
                                scaleBar.progress = (((it.scale - OutfitStore.SCALE_MIN) /
                                    (OutfitStore.SCALE_MAX - OutfitStore.SCALE_MIN)) * 100).toInt()
                                syncRotBar(it.rot)
                            }
                        }
                        rebuildList()
                        rebuildPreview()
                    }
                })
                listHost.addView(row)
            }
        }

        fun nudge(dx: Float, dy: Float) {
            val t = current()
            if (t != null) applyPos(t.nx + dx, t.ny + dy) else applyPos(pendingNx + dx, pendingNy + dy)
            rebuildPreview()
        }

        nudgeRow.addView(TextView(themed).apply {
            text = "微调"
            setTextColor(MenuDecor.MENU_FG)
            textSize = AppDataStore.fontBodySp(context)
            typeface = UiFonts.cute(context)
            setPadding(0, 0, dp(themed, 6), 0)
        })
        for ((label, dx, dy) in listOf(
            Triple("←", -0.03f, 0f),
            Triple("→", 0.03f, 0f),
            Triple("↑", 0f, -0.03f),
            Triple("↓", 0f, 0.03f),
        )) {
            nudgeRow.addView(Button(themed).apply {
                text = label
                setOnClickListener { nudge(dx, dy) }
                layoutParams = LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.WRAP_CONTENT,
                    LinearLayout.LayoutParams.WRAP_CONTENT,
                ).also { it.marginEnd = dp(themed, 4) }
            })
        }
        nudgeRow.addView(Button(themed).apply {
            text = "居中偏上"
            setOnClickListener {
                applyPos(OutfitStore.DEFAULT_NX, OutfitStore.DEFAULT_NY)
                rebuildPreview()
            }
        })

        preview.setOnTouchListener { v, e ->
            when (e.actionMasked) {
                MotionEvent.ACTION_DOWN, MotionEvent.ACTION_MOVE -> {
                    if (current() == null && !pendingLive) return@setOnTouchListener false
                    val w = v.width.coerceAtLeast(1).toFloat()
                    val h = v.height.coerceAtLeast(1).toFloat()
                    applyPos((e.x / w - 0.5f) * 1.1f, (e.y / h - 0.5f) * 1.1f)
                    rebuildPreview()
                    true
                }
                else -> false
            }
        }

        scaleBar.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) {
                val sc = scaleFromBar()
                current()?.scale = sc
                pendingScale = sc
                if (fromUser) rebuildPreview()
            }
            override fun onStartTrackingTouch(seekBar: SeekBar?) {}
            override fun onStopTrackingTouch(seekBar: SeekBar?) {}
        })
        rotBar.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) {
                val r = rotFromBar()
                current()?.rot = r
                pendingRot = r
                if (fromUser) rebuildPreview()
            }
            override fun onStartTrackingTouch(seekBar: SeekBar?) {}
            override fun onStopTrackingTouch(seekBar: SeekBar?) {}
        })

        root.addView(TextView(themed).apply {
            text = "素材（按分类；有选中=替换；无选中=待添加）"
            setTextColor(MenuDecor.THEME_BLUE)
            textSize = AppDataStore.fontBodySp(context)
            typeface = UiFonts.cute(context)
            setPadding(0, dp(themed, 8), 0, dp(themed, 4))
        })
        val assetHost = LinearLayout(themed).apply { orientation = LinearLayout.VERTICAL }
        var lastGroup = ""
        for (ch in OutfitStore.choices(context)) {
            if (ch.group != lastGroup) {
                lastGroup = ch.group
                assetHost.addView(TextView(themed).apply {
                    text = ch.group
                    setTextColor(MenuDecor.THEME_PINK)
                    textSize = AppDataStore.fontCaptionSp(context)
                    typeface = UiFonts.cute(context)
                    setPadding(0, dp(themed, 6), 0, dp(themed, 2))
                })
            }
            val thumb = OutfitStore.thumbFor(context, ch, 36)
            val key = "${ch.kind}|${ch.ref}"
            val btn = Button(themed).apply {
                text = ch.name.take(6)
                if (thumb != null) {
                    setCompoundDrawablesWithIntrinsicBounds(
                        null,
                        BitmapDrawable(resources, thumb),
                        null,
                        null,
                    )
                }
                setBackgroundColor(MenuDecor.THEME_ITEM_BG)
                setOnClickListener {
                    pendingKind = ch.kind
                    pendingRef = ch.ref
                    val defs = OutfitStore.defaultsFor(ch.kind, ch.ref)
                    pendingNx = defs[0]
                    pendingNy = defs[1]
                    pendingScale = defs[2]
                    pendingRot = defs[3]
                    scaleBar.progress = ((pendingScale - OutfitStore.SCALE_MIN) /
                        (OutfitStore.SCALE_MAX - OutfitStore.SCALE_MIN) * 100f)
                        .toInt().coerceIn(0, 100)
                    syncRotBar(pendingRot)
                    val t = current()
                    if (t != null) {
                        val probe = t.copy(kind = ch.kind, ref = ch.ref)
                        if (OutfitStore.bitmapFor(context, probe, 32) == null) {
                            Toast.makeText(context, "素材读不到", Toast.LENGTH_SHORT).show()
                            return@setOnClickListener
                        }
                        t.kind = ch.kind
                        t.ref = ch.ref
                        pendingLive = false
                        rebuildList()
                        rebuildPreview()
                        Toast.makeText(context, "已换成该素材（记得保存）", Toast.LENGTH_SHORT).show()
                    } else {
                        pendingLive = true
                        rebuildPreview()
                    }
                }
                layoutParams = LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.WRAP_CONTENT,
                    LinearLayout.LayoutParams.WRAP_CONTENT,
                ).also { it.marginEnd = dp(themed, 4) }
            }
            assetButtons[key] = btn
            // 同一分组横排：若刚开新组则新开一行
            val rowTag = "row_$lastGroup"
            var row = assetHost.findViewWithTag<LinearLayout>(rowTag)
            if (row == null) {
                row = LinearLayout(themed).apply {
                    orientation = LinearLayout.HORIZONTAL
                    tag = rowTag
                }
                assetHost.addView(HorizontalScrollView(themed).apply { addView(row) })
            }
            row.addView(btn)
        }
        root.addView(ScrollView(themed).apply {
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                dp(themed, 160),
            )
            addView(assetHost)
        })

        val holder = arrayOfNulls<Dialog>(1)
        val actions = LinearLayout(themed).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.END
            setPadding(0, dp(themed, 10), 0, 0)
        }
        addBtn = Button(themed).apply {
            text = "添加所选"
            setOnClickListener {
                if (draft.size >= OutfitStore.MAX) {
                    Toast.makeText(context, "最多 ${OutfitStore.MAX} 件", Toast.LENGTH_SHORT).show()
                    return@setOnClickListener
                }
                if (pendingKind.isBlank()) {
                    pendingKind = OutfitStore.KIND_BUILTIN
                    pendingRef = "star"
                    pendingLive = true
                }
                if (current() != null) selectedId = null
                val d = OutfitStore.newDecor(pendingKind, pendingRef, pendingNx, pendingNy, scaleFromBar(), rotFromBar())
                if (OutfitStore.bitmapFor(context, d, 32) == null) {
                    Toast.makeText(context, "素材读不到", Toast.LENGTH_SHORT).show()
                    return@setOnClickListener
                }
                draft += d
                selectedId = d.id
                pendingLive = false
                rebuildList()
                rebuildPreview()
            }
        }
        actions.addView(addBtn)
        actions.addView(Button(themed).apply {
            text = "新建"
            setOnClickListener {
                selectedId = null
                pendingLive = true
                if (pendingKind.isBlank()) {
                    pendingKind = OutfitStore.KIND_BUILTIN
                    pendingRef = "star"
                }
                pendingNx = OutfitStore.DEFAULT_NX
                pendingNy = OutfitStore.DEFAULT_NY
                pendingScale = OutfitStore.DEFAULT_SCALE
                pendingRot = OutfitStore.DEFAULT_ROT
                scaleBar.progress = (((pendingScale - OutfitStore.SCALE_MIN) /
                    (OutfitStore.SCALE_MAX - OutfitStore.SCALE_MIN)) * 100).toInt()
                syncRotBar(pendingRot)
                rebuildList()
                rebuildPreview()
                Toast.makeText(context, "已进入新建：点素材再添加", Toast.LENGTH_SHORT).show()
            }
        })
        actions.addView(Button(themed).apply {
            text = "清空"
            setOnClickListener {
                draft.clear()
                selectedId = null
                pendingLive = false
                pendingKind = ""
                pendingRef = ""
                OutfitStore.save(context, emptyList())
                onSaved()
                rebuildList()
                rebuildPreview()
                Toast.makeText(context, "已清空装扮", Toast.LENGTH_SHORT).show()
            }
        })
        actions.addView(Button(themed).apply {
            text = "保存佩戴"
            setOnClickListener {
                OutfitStore.save(context, draft)
                onSaved()
                Toast.makeText(
                    context,
                    if (draft.isEmpty()) "已清空装扮" else "装扮已保存（${draft.size} 件）",
                    Toast.LENGTH_SHORT,
                ).show()
                holder[0]?.dismiss()
            }
        })
        actions.addView(Button(themed).apply {
            text = "关闭"
            setOnClickListener { holder[0]?.dismiss() }
        })
        root.addView(actions)

        val scroll = ScrollView(themed).apply { addView(root) }
        rebuildList()
        rebuildPreview()
        val dialog = Dialog(themed)
        holder[0] = dialog
        dialog.setContentView(scroll)
        dialog.setCancelable(true)
        dialog.setOnDismissListener { openDialog = null }
        dialog.window?.apply {
            setBackgroundDrawableResource(android.R.color.transparent)
            setLayout(
                (themed.resources.displayMetrics.widthPixels * 0.92f).toInt(),
                WindowManager.LayoutParams.WRAP_CONTENT,
            )
            try {
                setType(WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY)
            } catch (_: Exception) {
            }
            addFlags(WindowManager.LayoutParams.FLAG_DIM_BEHIND)
            attributes = attributes?.also {
                it.dimAmount = 0.45f
                it.format = PixelFormat.TRANSLUCENT
            }
        }
        openDialog = dialog
        dialog.show()
        OverlayZOrder.onOverlayDialogShown(dialog)
    }

    private fun dp(context: Context, v: Int): Int =
        TypedValue.applyDimension(
            TypedValue.COMPLEX_UNIT_DIP,
            v.toFloat(),
            context.resources.displayMetrics,
        ).toInt()
}
