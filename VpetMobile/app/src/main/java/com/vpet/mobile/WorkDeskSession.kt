package com.vpet.mobile

import android.os.Handler
import android.os.Looper
import kotlin.random.Random

/**
 * 伏案赶工：对照桌面 pet.py WORK_DESK_*（1/2/3work 循环，原地不切运送）。
 */
class WorkDeskSession(
    private val onPose: (String) -> Unit,
    private val onBanter: () -> Unit,
    private val onEnd: () -> Unit,
) {
    companion object {
        private val POSES = listOf(
            SpriteAssets.WORK_DESK_1,
            SpriteAssets.WORK_DESK_2,
            SpriteAssets.WORK_DESK_3,
        )
        private const val POSE_MS = 800L
        private const val BANTER_MIN_MS = 30_000L
        private const val BANTER_MAX_MS = 90_000L
    }

    private val handler = Handler(Looper.getMainLooper())
    private var poseIdx = 0
    private var poseJob: Runnable? = null
    private var banterJob: Runnable? = null
    var active = false
        private set

    fun start() {
        stop(internal = true)
        active = true
        poseIdx = 0
        onPose(POSES[0])
        schedulePose()
        scheduleBanter()
    }

    fun stop(internal: Boolean = false) {
        active = false
        poseJob?.let { handler.removeCallbacks(it) }
        banterJob?.let { handler.removeCallbacks(it) }
        poseJob = null
        banterJob = null
        if (!internal) onEnd()
    }

    private fun schedulePose() {
        poseJob?.let { handler.removeCallbacks(it) }
        poseJob = Runnable {
            if (!active) return@Runnable
            poseIdx = (poseIdx + 1) % POSES.size
            onPose(POSES[poseIdx])
            schedulePose()
        }
        handler.postDelayed(poseJob!!, POSE_MS)
    }

    private fun scheduleBanter() {
        banterJob?.let { handler.removeCallbacks(it) }
        val delay = Random.nextLong(BANTER_MIN_MS, BANTER_MAX_MS)
        banterJob = Runnable {
            if (!active) return@Runnable
            onBanter()
            scheduleBanter()
        }
        handler.postDelayed(banterJob!!, delay)
    }
}
