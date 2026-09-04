package com.vpet.mobile

import android.content.Context
import android.graphics.Point
import android.view.WindowManager
import android.widget.FrameLayout

/**
 * 双使魔栏：艾斯特（左上）与墨菲（右上），对照桌面 `mini_pets` / `companion_aster|morvay`。
 */
class CompanionRoster(
    private val context: Context,
    private val windowManager: WindowManager?,
    private val roomHost: FrameLayout?,
    private val petTopLeft: () -> Point,
    private val petSize: () -> Int,
    private val screenSize: () -> Point,
    private val mainDir: () -> SpriteAssets.Dir,
    private val mainMoving: () -> Boolean,
    private val workAnchor: () -> Point?,
    private val onHoldAllmate: (CompanionFollower.Kind) -> Unit,
    private val restackLayers: () -> Unit,
) {
    private val followers = mutableMapOf<CompanionFollower.Kind, CompanionFollower>()
    private val fxMap = mutableMapOf<CompanionFollower.Kind, PetFxUi>()

    fun init() {
        for (kind in CompanionFollower.Kind.entries) {
            val c = CompanionFollower(
                context = context,
                kind = kind,
                windowManager = windowManager,
                roomHost = roomHost,
                petTopLeft = petTopLeft,
                petSize = petSize,
                screenSize = screenSize,
                mainDir = mainDir,
                mainMoving = mainMoving,
                peerActive = { peer -> followers[peer]?.active == true },
            )
            c.workAnchor = workAnchor
            c.onMultiClick = { clicks ->
                if (clicks >= 3) onHoldAllmate(kind)
            }
            followers[kind] = c
        }
        syncFromPrefs(startIfEnabled = true)
    }

    fun follower(kind: CompanionFollower.Kind): CompanionFollower? = followers[kind]

    fun anyActive(): Boolean = followers.values.any { it.active }

    fun isEnabled(kind: CompanionFollower.Kind): Boolean = when (kind) {
        CompanionFollower.Kind.ASTER -> AppDataStore.companionAsterEnabled(context)
        CompanionFollower.Kind.MORVAY -> AppDataStore.companionMorvayEnabled(context)
    }

    fun syncFromPrefs(startIfEnabled: Boolean = true) {
        for (kind in CompanionFollower.Kind.entries) {
            val want = isEnabled(kind)
            val c = followers[kind] ?: continue
            if (want && startIfEnabled && !c.active) {
                c.start()
                rebuildFx(kind)
            } else if (!want && c.active) {
                c.stop()
                destroyFx(kind)
            }
        }
        syncLegacyCompanionFlag()
    }

    fun toggleKind(kind: CompanionFollower.Kind): Boolean {
        val c = followers[kind] ?: return false
        val want = !isEnabled(kind)
        setEnabled(kind, want)
        if (want) {
            if (!c.active) {
                c.start()
                rebuildFx(kind)
                AppDataStore.unlock(context, "companion_on")
            }
            showToast("噗~ ${kind.label}飞过来啦！")
        } else {
            if (c.active) {
                c.stop()
                destroyFx(kind)
            }
            if (!anyActive()) showToast("使魔栏已关闭")
            else showToast("${kind.label}已收起")
        }
        restackLayers()
        return want
    }

    private fun setEnabled(kind: CompanionFollower.Kind, on: Boolean) {
        when (kind) {
            CompanionFollower.Kind.ASTER -> AppDataStore.setCompanionAsterEnabled(context, on)
            CompanionFollower.Kind.MORVAY -> AppDataStore.setCompanionMorvayEnabled(context, on)
        }
        syncLegacyCompanionFlag()
    }

    private fun syncLegacyCompanionFlag() {
        AppDataStore.setCompanionEnabled(context, anyEnabledInPrefs())
    }

    private fun anyEnabledInPrefs(): Boolean =
        AppDataStore.companionAsterEnabled(context) || AppDataStore.companionMorvayEnabled(context)

    fun setVisible(visible: Boolean) {
        for ((kind, c) in followers) {
            c.setVisible(visible)
            fxMap[kind]?.setVisible(visible && c.active)
        }
    }

    fun refreshSprites(forceReload: Boolean = false) {
        followers.values.forEach { it.refreshSprite(forceReload) }
        fxMap.values.forEach { it.syncPlace() }
    }

    fun syncFxPlace() {
        fxMap.values.forEach { it.syncPlace() }
    }

    fun applyMusicWave(on: Boolean, colors: IntArray?) {
        for ((kind, c) in followers) {
            val fx = fxMap[kind]
            if (on && c.active && colors != null) fx?.setMusicWave(true, colors)
            else fx?.setMusicWave(false)
        }
    }

    fun clearMusicWave() = applyMusicWave(false, null)

    fun clearBurst() {
        fxMap.values.forEach { it.clearBurst() }
    }

    fun raiseLayers() {
        fxMap.values.forEach { it.raiseLayer() }
        followers.values.forEach {
            it.raise()
            it.bringSpriteToFront()
        }
    }

    fun destroy() {
        followers.values.forEach { it.stop() }
        followers.clear()
        fxMap.values.forEach { it.destroy() }
        fxMap.clear()
    }

    fun playEnterDissolves(onEachDone: () -> Unit, onAllDone: () -> Unit) {
        val active = followers.values.filter { it.active }
        if (active.isEmpty()) {
            onAllDone()
            return
        }
        var pending = active.size
        active.forEach { c ->
            c.playDissolve(reverse = false) {
                onEachDone()
                pending -= 1
                if (pending <= 0) onAllDone()
            }
        }
    }

    fun playExitDissolves(totalMs: Long, onAllDone: () -> Unit) {
        val active = followers.values.filter { it.active }
        if (active.isEmpty()) {
            onAllDone()
            return
        }
        var pending = active.size
        active.forEach { c ->
            c.playDissolve(reverse = true, totalMs = totalMs) {
                pending -= 1
                if (pending <= 0) onAllDone()
            }
        }
    }

    fun hideForHoldAllmate() {
        followers.values.forEach { it.setVisible(false) }
        fxMap.values.forEach { it.setVisible(false) }
    }

    fun showAfterHoldAllmate() {
        for ((kind, c) in followers) {
            if (c.active) {
                c.setVisible(true)
                fxMap[kind]?.setVisible(true)
            }
        }
    }

    fun rebuildFxForActive(waveOn: Boolean = false, waveColors: IntArray? = null) {
        for (kind in CompanionFollower.Kind.entries) {
            val c = followers[kind] ?: continue
            if (c.active) {
                rebuildFx(kind)
                if (waveOn && waveColors != null) {
                    fxMap[kind]?.setMusicWave(true, waveColors)
                }
            } else {
                destroyFx(kind)
            }
        }
    }

    private fun rebuildFx(kind: CompanionFollower.Kind) {
        destroyFx(kind)
        val c = followers[kind] ?: return
        val nested = c.fxHost()
        fxMap[kind] = if (nested != null) {
            PetFxUi(
                context = context,
                windowManager = null,
                roomHost = nested,
                petTopLeft = { Point(PetFxUi.PAD, PetFxUi.PAD) },
                petSize = { c.displaySize() },
                raisePet = { c.bringSpriteToFront() },
            )
        } else {
            PetFxUi(
                context = context,
                windowManager = windowManager,
                roomHost = roomHost,
                petTopLeft = { c.displayTopLeft() },
                petSize = { c.displaySize() },
                raisePet = { restackLayers() },
            )
        }
    }

    private fun destroyFx(kind: CompanionFollower.Kind) {
        fxMap.remove(kind)?.destroy()
    }

    private fun showToast(msg: String) {
        android.widget.Toast.makeText(context, msg, android.widget.Toast.LENGTH_SHORT).show()
    }
}
