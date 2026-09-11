package com.vpet.mobile

import android.app.Dialog
import android.content.Context
import android.graphics.PixelFormat
import android.text.InputType
import android.util.TypedValue
import android.view.Gravity
import android.view.ViewGroup
import android.view.WindowManager
import android.widget.CheckBox
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.view.ContextThemeWrapper

/** 日程 / 生日：奶油纸质浮窗，对齐桌面 schedule/birthday 面板。 */
object ScheduleBirthdayDialogs {

    private val WEEK_LABELS = arrayOf("一", "二", "三", "四", "五", "六", "日")

    fun showSchedule(context: Context) {
        val themed = ContextThemeWrapper(context, R.style.Theme_VpetMobile)
        val pad = MenuDecor.dp(context, 12f)
        val box = LinearLayout(themed).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(pad, pad, pad, pad)
        }
        PanelTheme.applyCreamRoot(box)
        PanelTheme.attachSignStrip(box)
        box.addView(PanelTheme.title(themed, "日程提醒"))
        box.addView(PanelTheme.clockBanner(themed))
        box.addView(PanelTheme.hint(themed, "到点 Toast；点条目删除。可选每天/工作日/周末。"))

        val listHost = LinearLayout(themed).apply { orientation = LinearLayout.VERTICAL }
        fun refreshList() {
            listHost.removeAllViews()
            val arr = PetProfileStore.schedules(context)
            if (arr.length() == 0) {
                listHost.addView(PanelTheme.hint(themed, "暂无日程"))
                return
            }
            for (i in 0 until arr.length()) {
                val o = arr.getJSONObject(i)
                val id = o.optString("id")
                val line = "${o.optString("time")} [${PetProfileStore.formatWeekdays(o)}]  ${o.optString("text")}"
                listHost.addView(
                    TextView(themed).apply {
                        text = line
                        setTextColor(MenuDecor.MENU_FG)
                        textSize = AppDataStore.fontBodySp(context)
                        typeface = UiFonts.cute(context)
                        setPadding(0, MenuDecor.dp(context, 6f), 0, MenuDecor.dp(context, 6f))
                        background = MenuDecor.menuItemBg()
                        setOnClickListener {
                            PetProfileStore.removeSchedule(context, id)
                            Toast.makeText(context, "已删除", Toast.LENGTH_SHORT).show()
                            refreshList()
                        }
                    },
                )
            }
        }
        refreshList()
        box.addView(
            ScrollView(themed).apply {
                layoutParams = LinearLayout.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT,
                    (context.resources.displayMetrics.heightPixels * 0.18f).toInt(),
                )
                addView(listHost)
            },
        )

        val dayChecks = Array(7) { i ->
            CheckBox(themed).apply {
                text = WEEK_LABELS[i]
                isChecked = true
                setTextColor(MenuDecor.MENU_FG)
                typeface = UiFonts.cute(context)
            }
        }
        box.addView(
            LinearLayout(themed).apply {
                orientation = LinearLayout.HORIZONTAL
                dayChecks.forEach { addView(it) }
            },
        )
        box.addView(
            LinearLayout(themed).apply {
                orientation = LinearLayout.HORIZONTAL
                gravity = Gravity.START
                fun setDays(indices: Set<Int>) {
                    dayChecks.forEachIndexed { i, cb -> cb.isChecked = i in indices }
                }
                addView(PanelTheme.primaryBtn(themed, "每天") { setDays((0..6).toSet()) })
                addView(PanelTheme.primaryBtn(themed, "工作日") { setDays((0..4).toSet()) }.also {
                    (it.layoutParams as LinearLayout.LayoutParams).marginStart = MenuDecor.dp(context, 6f)
                })
                addView(PanelTheme.primaryBtn(themed, "周末") { setDays(setOf(5, 6)) }.also {
                    (it.layoutParams as LinearLayout.LayoutParams).marginStart = MenuDecor.dp(context, 6f)
                })
            },
        )

        val time = textField(themed, "08:30", InputType.TYPE_CLASS_DATETIME or InputType.TYPE_DATETIME_VARIATION_TIME)
        val content = textField(themed, "", InputType.TYPE_CLASS_TEXT).also { it.hint = "提醒内容" }
        box.addView(labeled(themed, "时间 HH:MM", time))
        box.addView(labeled(themed, "内容", content))

        val holder = arrayOfNulls<Dialog>(1)
        box.addView(
            LinearLayout(themed).apply {
                orientation = LinearLayout.HORIZONTAL
                gravity = Gravity.END
                setPadding(0, MenuDecor.dp(context, 12f), 0, 0)
                addView(PanelTheme.primaryBtn(themed, "关闭") { holder[0]?.dismiss() })
                addView(
                    PanelTheme.primaryBtn(themed, "添加") {
                        val selected = dayChecks.mapIndexedNotNull { i, cb -> if (cb.isChecked) i else null }
                        if (selected.isEmpty()) {
                            Toast.makeText(context, "至少选一天", Toast.LENGTH_SHORT).show()
                            return@primaryBtn
                        }
                        val days = if (selected.size >= 7) null else selected
                        val ok = PetProfileStore.addSchedule(
                            context,
                            time.text.toString(),
                            content.text.toString(),
                            days,
                        )
                        if (!ok) {
                            Toast.makeText(context, "时间用 HH:MM，内容不能空", Toast.LENGTH_SHORT).show()
                            return@primaryBtn
                        }
                        content.setText("")
                        Toast.makeText(context, "已添加", Toast.LENGTH_SHORT).show()
                        refreshList()
                    }.also {
                        (it.layoutParams as LinearLayout.LayoutParams).marginStart = MenuDecor.dp(context, 8f)
                    },
                )
            },
        )
        holder[0] = showOverlayDialog(themed, box)
    }

    fun showBirthday(context: Context) {
        val themed = ContextThemeWrapper(context, R.style.Theme_VpetMobile)
        val pad = MenuDecor.dp(context, 12f)
        val box = LinearLayout(themed).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(pad, pad, pad, pad)
        }
        PanelTheme.applyCreamRoot(box)
        PanelTheme.attachSignStrip(box)
        box.addView(PanelTheme.title(themed, "生日祝福"))
        box.addView(PanelTheme.cakeBanner(themed))
        box.addView(PanelTheme.hint(themed, "所属人生日 + 伊得 6/17 礼物文案"))

        val p = PetProfileStore.profile(context)
        val month = numField(themed, p.optInt("bless_month").takeIf { it > 0 }?.toString() ?: "1")
        val day = numField(themed, p.optInt("bless_day").takeIf { it > 0 }?.toString() ?: "1")
        val msg = textField(themed, p.optString("bless_message"), InputType.TYPE_CLASS_TEXT)
        val gift = textField(themed, p.optString("gift_text"), InputType.TYPE_CLASS_TEXT)

        box.addView(
            LinearLayout(themed).apply {
                orientation = LinearLayout.HORIZONTAL
                gravity = Gravity.CENTER_VERTICAL
                addView(PanelTheme.label(themed, "月"))
                addView(month)
                addView(PanelTheme.label(themed, "日").also { v ->
                    (v.layoutParams as LinearLayout.LayoutParams).marginStart = MenuDecor.dp(context, 12f)
                })
                addView(day)
            },
        )
        box.addView(labeled(themed, "祝福语", msg))
        box.addView(labeled(themed, "礼物（伊得）", gift))

        val holder = arrayOfNulls<Dialog>(1)
        box.addView(
            LinearLayout(themed).apply {
                orientation = LinearLayout.HORIZONTAL
                gravity = Gravity.END
                setPadding(0, MenuDecor.dp(context, 12f), 0, 0)
                addView(PanelTheme.primaryBtn(themed, "取消") { holder[0]?.dismiss() })
                addView(
                    PanelTheme.primaryBtn(themed, "保存") {
                        val m = month.text.toString().trim().toIntOrNull() ?: 0
                        val d = day.text.toString().trim().toIntOrNull() ?: 0
                        if (m !in 1..12 || d !in 1..31) {
                            Toast.makeText(context, "请填写有效月/日", Toast.LENGTH_SHORT).show()
                            return@primaryBtn
                        }
                        PetProfileStore.setBless(context, m, d, msg.text.toString())
                        PetProfileStore.setGiftText(context, gift.text.toString())
                        Toast.makeText(context, "已保存生日与礼物", Toast.LENGTH_SHORT).show()
                        holder[0]?.dismiss()
                    }.also {
                        (it.layoutParams as LinearLayout.LayoutParams).marginStart = MenuDecor.dp(context, 8f)
                    },
                )
            },
        )
        holder[0] = showOverlayDialog(themed, box)
    }

    private fun showOverlayDialog(context: Context, content: LinearLayout): Dialog {
        val dialog = Dialog(context)
        dialog.setContentView(content)
        dialog.setCancelable(true)
        dialog.window?.apply {
            setBackgroundDrawableResource(android.R.color.transparent)
            setLayout(
                (context.resources.displayMetrics.widthPixels * 0.90f).toInt(),
                WindowManager.LayoutParams.WRAP_CONTENT,
            )
            try {
                setType(WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY)
            } catch (_: Exception) {
            }
            try {
                setFormat(PixelFormat.TRANSLUCENT)
            } catch (_: Exception) {
            }
        }
        OverlayZOrder.prepareOverlayWindow(dialog.window)
        dialog.setOnDismissListener { }
        dialog.show()
        OverlayZOrder.onOverlayDialogShown(dialog)
        return dialog
    }

    private fun labeled(ctx: Context, title: String, field: EditText): LinearLayout =
        LinearLayout(ctx).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(0, MenuDecor.dp(ctx, 6f), 0, 0)
            addView(PanelTheme.label(ctx, title))
            addView(field)
        }

    private fun textField(ctx: Context, value: String, inputType: Int): EditText =
        EditText(ctx).apply {
            setText(value)
            this.inputType = inputType
            setTextColor(MenuDecor.MENU_FG)
            setHintTextColor(0x88442233.toInt())
            textSize = AppDataStore.fontBodySp(ctx)
            typeface = UiFonts.cute(ctx)
            setBackgroundColor(MenuDecor.THEME_ITEM_BG)
            setPadding(MenuDecor.dp(ctx, 8f), MenuDecor.dp(ctx, 6f), MenuDecor.dp(ctx, 8f), MenuDecor.dp(ctx, 6f))
        }

    private fun numField(ctx: Context, value: String): EditText =
        textField(ctx, value, InputType.TYPE_CLASS_NUMBER).also {
            it.layoutParams = LinearLayout.LayoutParams(
                MenuDecor.dp(ctx, 56f),
                LinearLayout.LayoutParams.WRAP_CONTENT,
            )
        }
}
