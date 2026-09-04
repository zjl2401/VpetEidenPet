package com.vpet.mobile

import android.app.Activity
import android.app.Application
import android.os.Bundle
import android.view.View
import android.view.ViewTreeObserver

class VpetApp : Application() {
    override fun onCreate() {
        super.onCreate()
        // 覆盖安装后先尝试从保险档恢复相伴/装扮/背包，再刷新快照
        PersistVault.bootstrap(this)
        registerActivityLifecycleCallbacks(object : ActivityLifecycleCallbacks {
            override fun onActivityCreated(activity: Activity, savedInstanceState: Bundle?) {
                val content = activity.findViewById<View>(android.R.id.content) ?: return
                content.viewTreeObserver.addOnGlobalLayoutListener(
                    object : ViewTreeObserver.OnGlobalLayoutListener {
                        override fun onGlobalLayout() {
                            content.viewTreeObserver.removeOnGlobalLayoutListener(this)
                            UiFonts.applyTree(content)
                        }
                    },
                )
            }

            override fun onActivityStarted(activity: Activity) {}
            override fun onActivityResumed(activity: Activity) {
                UiFonts.applyTree(activity.findViewById(android.R.id.content))
            }

            override fun onActivityPaused(activity: Activity) {}
            override fun onActivityStopped(activity: Activity) {}
            override fun onActivitySaveInstanceState(activity: Activity, outState: Bundle) {}
            override fun onActivityDestroyed(activity: Activity) {}
        })
    }
}
