package com.vpet.mobile

import android.os.Handler
import android.os.Looper
import kotlin.random.Random

/**
 * 伏案赶工：对照桌面 pet.py
 * - 主立绘：1/2/3work 随机切换
 * - 每 8s 旁侧：work_0(1s) → work_1(1s) → work_2~5 随机(2s)
 *   （手机端暂无独立细节窗，主立绘节奏与桌面对齐的主段）
 */
class WorkDeskSession(
    private val onPose: (String) -> Unit,
    private val onBanter: () -> Unit,
    private val onEnd: () -> Unit,
    private val onDetail: ((String?) -> Unit)? = null,
) {
    companion object {
        private val MAIN = listOf(
            SpriteAssets.WORK_DETAIL_1,
            SpriteAssets.WORK_DETAIL_2,
            SpriteAssets.WORK_DETAIL_3,
        )
        private val DETAILS = listOf(
            SpriteAssets.WORK_DESK_0,
            SpriteAssets.WORK_DESK_1,
            SpriteAssets.WORK_DESK_2,
            SpriteAssets.WORK_DESK_3,
            SpriteAssets.WORK_DESK_4,
            SpriteAssets.WORK_DESK_5,
        )
        private const val MAIN_HOLD_MS = 1_200L
        private const val IDLE_MS = 8_000L
        private const val EXTRA0_MS = 1_000L
        private const val EXTRA1_MS = 1_000L
        private const val BURST_MS = 2_000L
        private const val BANTER_MIN_MS = 30_000L
        private const val BANTER_MAX_MS = 90_000L
    }

    private val handler = Handler(Looper.getMainLooper())
    private var mainIdx = 0
    private var phase = 0
    private var detailPick = 2
    private var mainJob: Runnable? = null
    private var phaseJob: Runnable? = null
    private var banterJob: Runnable? = null
    var active = false
        private set

    fun start() {
        stop(internal = true)
        active = true
        mainIdx = Random.nextInt(MAIN.size)
        phase = 0
        onPose(MAIN[mainIdx])
        onDetail?.invoke(null)
        scheduleMain()
        scheduleIdleThenDetail()
        scheduleBanter()
    }

    fun stop(internal: Boolean = false) {
        active = false
        mainJob?.let { handler.removeCallbacks(it) }
        phaseJob?.let { handler.removeCallbacks(it) }
        banterJob?.let { handler.removeCallbacks(it) }
        mainJob = null
        phaseJob = null
        banterJob = null
        onDetail?.invoke(null)
        if (!internal) onEnd()
    }

    private fun pickMain() {
        val choices = MAIN.indices.filter { it != mainIdx }.ifEmpty { MAIN.indices.toList() }
        mainIdx = choices.random()
        onPose(MAIN[mainIdx])
    }

    private fun scheduleMain() {
        mainJob?.let { handler.removeCallbacks(it) }
        mainJob = Runnable {
            if (!active) return@Runnable
            pickMain()
            scheduleMain()
        }
        handler.postDelayed(mainJob!!, MAIN_HOLD_MS)
    }

    private fun scheduleIdleThenDetail() {
        phaseJob?.let { handler.removeCallbacks(it) }
        phase = 0
        onDetail?.invoke(null)
        phaseJob = Runnable {
            if (!active) return@Runnable
            // work_0 · 1s
            phase = 1
            onDetail?.invoke(DETAILS[0])
            phaseJob = Runnable {
                if (!active) return@Runnable
                // work_1 · 1s
                phase = 2
                onDetail?.invoke(DETAILS[1])
                phaseJob = Runnable {
                    if (!active) return@Runnable
                    // work_2~5 随机 · 2s
                    phase = 3
                    detailPick = Random.nextInt(2, 6)
                    onDetail?.invoke(DETAILS[detailPick])
                    phaseJob = Runnable {
                        if (!active) return@Runnable
                        scheduleIdleThenDetail()
                    }
                    handler.postDelayed(phaseJob!!, BURST_MS)
                }
                handler.postDelayed(phaseJob!!, EXTRA1_MS)
            }
            handler.postDelayed(phaseJob!!, EXTRA0_MS)
        }
        handler.postDelayed(phaseJob!!, IDLE_MS)
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
