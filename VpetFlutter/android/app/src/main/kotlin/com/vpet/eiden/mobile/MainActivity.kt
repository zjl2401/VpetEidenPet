package com.vpet.eiden.mobile

import android.content.Intent
import android.net.Uri
import android.os.Build
import android.provider.Settings
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel

class MainActivity : FlutterActivity() {
    private val channelName = "com.vpet.eiden.mobile/overlay"

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, channelName)
            .setMethodCallHandler { call, result ->
                when (call.method) {
                    "canDrawOverlays" -> {
                        result.success(
                            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                                Settings.canDrawOverlays(this)
                            } else {
                                true
                            },
                        )
                    }
                    "requestOverlayPermission" -> {
                        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M &&
                            !Settings.canDrawOverlays(this)
                        ) {
                            val intent = Intent(
                                Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                                Uri.parse("package:$packageName"),
                            )
                            startActivity(intent)
                            result.success(false)
                        } else {
                            result.success(true)
                        }
                    }
                    "startOverlay" -> {
                        val i = Intent(this, FlutterPetOverlayService::class.java)
                        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                            startForegroundService(i)
                        } else {
                            startService(i)
                        }
                        result.success(null)
                    }
                    "stopOverlay" -> {
                        stopService(Intent(this, FlutterPetOverlayService::class.java))
                        result.success(null)
                    }
                    "updatePose" -> {
                        val asset = call.argument<String>("asset") ?: "stand.png"
                        val x = call.argument<Double>("x") ?: 80.0
                        val y = call.argument<Double>("y") ?: 200.0
                        val size = call.argument<Double>("size") ?: 160.0
                        FlutterPetOverlayService.updatePose(this, asset, x, y, size)
                        result.success(null)
                    }
                    "startPip", "stopPip" -> result.success(null) // iOS-only
                    else -> result.notImplemented()
                }
            }
    }
}
