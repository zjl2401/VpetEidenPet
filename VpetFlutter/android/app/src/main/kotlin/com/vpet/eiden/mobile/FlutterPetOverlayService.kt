package com.vpet.eiden.mobile

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.graphics.PixelFormat
import android.os.Build
import android.os.IBinder
import android.view.Gravity
import android.view.MotionEvent
import android.view.View
import android.view.WindowManager
import android.widget.ImageView
import androidx.core.app.NotificationCompat

/**
 * Lightweight SYSTEM_ALERT_WINDOW pet — pose updates come from Flutter via [updatePose].
 */
class FlutterPetOverlayService : Service() {
    private var wm: WindowManager? = null
    private var params: WindowManager.LayoutParams? = null
    private var petView: ImageView? = null

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onCreate() {
        super.onCreate()
        startAsForeground()
        attachOverlay()
        instance = this
    }

    override fun onDestroy() {
        instance = null
        petView?.let { runCatching { wm?.removeView(it) } }
        petView = null
        super.onDestroy()
    }

    private fun startAsForeground() {
        val channelId = "eiden_overlay"
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val nm = getSystemService(NOTIFICATION_SERVICE) as NotificationManager
            nm.createNotificationChannel(
                NotificationChannel(channelId, "伊得悬浮", NotificationManager.IMPORTANCE_LOW),
            )
        }
        val pi = PendingIntent.getActivity(
            this,
            0,
            Intent(this, MainActivity::class.java),
            PendingIntent.FLAG_IMMUTABLE,
        )
        val n: Notification = NotificationCompat.Builder(this, channelId)
            .setContentTitle("伊得在桌面")
            .setContentText("点按返回完整菜单")
            .setSmallIcon(android.R.drawable.ic_menu_myplaces)
            .setContentIntent(pi)
            .setOngoing(true)
            .build()
        startForeground(42, n)
    }

    private fun attachOverlay() {
        wm = getSystemService(WINDOW_SERVICE) as WindowManager
        val type = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY
        } else {
            @Suppress("DEPRECATION")
            WindowManager.LayoutParams.TYPE_PHONE
        }
        params = WindowManager.LayoutParams(
            dp(120),
            dp(120),
            type,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or
                WindowManager.LayoutParams.FLAG_LAYOUT_NO_LIMITS,
            PixelFormat.TRANSLUCENT,
        ).apply {
            gravity = Gravity.TOP or Gravity.START
            x = 80
            y = 200
        }
        petView = ImageView(this).apply {
            setImageResource(android.R.drawable.sym_def_app_icon)
            scaleType = ImageView.ScaleType.FIT_CENTER
            setOnTouchListener(dragListener)
            setOnClickListener {
                startActivity(
                    Intent(this@FlutterPetOverlayService, MainActivity::class.java)
                        .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK),
                )
            }
        }
        wm?.addView(petView, params)
    }

    private val dragListener = object : View.OnTouchListener {
        private var lastX = 0f
        private var lastY = 0f
        private var paramX = 0
        private var paramY = 0
        override fun onTouch(v: View, e: MotionEvent): Boolean {
            val p = params ?: return false
            when (e.action) {
                MotionEvent.ACTION_DOWN -> {
                    lastX = e.rawX
                    lastY = e.rawY
                    paramX = p.x
                    paramY = p.y
                    return true
                }
                MotionEvent.ACTION_MOVE -> {
                    p.x = paramX + (e.rawX - lastX).toInt()
                    p.y = paramY + (e.rawY - lastY).toInt()
                    wm?.updateViewLayout(petView, p)
                    return true
                }
            }
            return false
        }
    }

    private fun applyPose(asset: String, x: Double, y: Double, size: Double) {
        val p = params ?: return
        p.width = size.toInt().coerceAtLeast(64)
        p.height = size.toInt().coerceAtLeast(64)
        p.x = x.toInt()
        p.y = y.toInt()
        // Flutter assets are not directly bindable here; keep placeholder / last bitmap.
        // Full sprite sync can stream bytes via another channel in a later pass.
        petView?.contentDescription = asset
        wm?.updateViewLayout(petView, p)
    }

    private fun dp(v: Int): Int = (v * resources.displayMetrics.density).toInt()

    companion object {
        @Volatile
        private var instance: FlutterPetOverlayService? = null

        fun updatePose(ctx: Context, asset: String, x: Double, y: Double, size: Double) {
            instance?.applyPose(asset, x, y, size)
                ?: ctx.startService(Intent(ctx, FlutterPetOverlayService::class.java))
        }
    }
}
