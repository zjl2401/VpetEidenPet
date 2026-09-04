package com.vpet.mobile

import android.app.Dialog
import android.content.Context
import android.content.Intent
import android.graphics.PixelFormat
import android.os.Build
import android.view.View
import android.view.Window
import android.view.WindowManager
import java.lang.ref.WeakReference
import java.util.concurrent.CopyOnWriteArrayList
import java.util.concurrent.atomic.AtomicInteger

/**
 * 全屏/系统页打开时收起悬浮桌宠；支持嵌套引用计数
 * （设置里再开档案页时，关档案不立刻把宠弹回来）。
 */
object OverlayGate {
    private val pauseCount = AtomicInteger(0)

    fun pause(context: Context) {
        if (pauseCount.getAndIncrement() == 0) {
            context.startService(
                Intent(context, PetOverlayService::class.java).setAction(PetOverlayService.ACTION_PAUSE),
            )
        }
    }

    fun resume(context: Context) {
        val left = pauseCount.decrementAndGet()
        if (left <= 0) {
            pauseCount.set(0)
            context.startService(
                Intent(context, PetOverlayService::class.java).setAction(PetOverlayService.ACTION_RESUME),
            )
        }
    }
}

/**
 * 悬浮窗 Z 序：后打开的盖在先打开的上面（对照桌面 lift）。
 * 同 TYPE_APPLICATION_OVERLAY 靠 remove+add 顶到最前；模态弹窗登记后 restack 时最后抬。
 */
object OverlayZOrder {
    private val modals = CopyOnWriteArrayList<WeakReference<Dialog>>()

    fun raise(windowManager: WindowManager?, view: View?, lp: WindowManager.LayoutParams?) {
        if (windowManager == null || view == null || lp == null) return
        try {
            if (view.parent != null) {
                windowManager.removeView(view)
            }
            windowManager.addView(view, lp)
        } catch (_: Exception) {
            try {
                windowManager.updateViewLayout(view, lp)
            } catch (_: Exception) {
            }
        }
    }

    fun prepareOverlayWindow(window: Window?) {
        window ?: return
        try {
            window.setType(WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY)
            window.addFlags(WindowManager.LayoutParams.FLAG_DIM_BEHIND)
            window.attributes = window.attributes?.also {
                it.dimAmount = (it.dimAmount.takeIf { d -> d > 0f } ?: 0.45f)
                it.format = PixelFormat.TRANSLUCENT
                if (Build.VERSION.SDK_INT >= 28) {
                    it.layoutInDisplayCutoutMode =
                        WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES
                }
            }
        } catch (_: Exception) {
        }
    }

    /** show 之后调用：登记为最上层模态，并顶到同类型最前。 */
    fun onOverlayDialogShown(dialog: Dialog) {
        prune()
        modals.removeAll { it.get() == null || it.get() === dialog }
        modals.add(WeakReference(dialog))
        bringDialogToFront(dialog)
        dialog.window?.decorView?.post { bringDialogToFront(dialog) }
    }

    fun raiseModals() {
        prune()
        for (ref in modals) {
            val d = ref.get() ?: continue
            if (d.isShowing) bringDialogToFront(d)
        }
    }

    fun hasModal(): Boolean {
        prune()
        return modals.any { it.get()?.isShowing == true }
    }

    fun bringDialogToFront(dialog: Dialog) {
        val w = dialog.window ?: return
        try {
            prepareOverlayWindow(w)
            w.decorView.bringToFront()
            // 部分机型需再 clear/set 一次 type 才会真正置顶
            w.setType(WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY)
        } catch (_: Exception) {
        }
    }

    private fun prune() {
        modals.removeAll { it.get() == null || it.get()?.isShowing != true }
    }
}
