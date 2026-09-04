package com.vpet.mobile

import android.content.Context
import android.graphics.Typeface
import android.view.View
import android.view.ViewGroup
import android.widget.TextView

/** 伊得向可爱正文字体（楷体资源优先）。 */
object UiFonts {
    @Volatile
    private var cute: Typeface? = null

    fun cute(context: Context): Typeface {
        cute?.let { return it }
        val loaded = try {
            Typeface.createFromAsset(context.assets, "fonts/ui_cute.ttf")
        } catch (_: Exception) {
            null
        } ?: Typeface.create("serif", Typeface.NORMAL) ?: Typeface.SANS_SERIF
        cute = loaded
        return loaded
    }

    fun cuteBold(context: Context): Typeface =
        Typeface.create(cute(context), Typeface.BOLD) ?: cute(context)

    /** 递归套用到 Activity/Dialog 根视图下所有 TextView。 */
    fun applyTree(root: View?) {
        root ?: return
        val face = cute(root.context)
        fun walk(v: View) {
            if (v is TextView) {
                val bold = v.typeface?.isBold == true ||
                    (v.paintFlags and android.graphics.Paint.FAKE_BOLD_TEXT_FLAG) != 0
                v.typeface = if (bold) cuteBold(v.context) else face
            }
            if (v is ViewGroup) {
                for (i in 0 until v.childCount) walk(v.getChildAt(i))
            }
        }
        walk(root)
    }
}
