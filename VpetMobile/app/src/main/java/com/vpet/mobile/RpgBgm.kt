package com.vpet.mobile

import android.content.Context
import android.content.res.AssetFileDescriptor
import android.media.MediaPlayer
import android.os.Handler
import android.os.Looper

/**
 * Silent Oath BGM：先播 startmusic，结束后循环 music（对照 game.py）。
 */
class RpgBgm(private val context: Context) {
    private var player: MediaPlayer? = null
    private var looping = false
    private val handler = Handler(Looper.getMainLooper())
    private var fadeRunnable: Runnable? = null

    /** 开场/标题页只播 startmusic（循环）。 */
    fun playIntroOnly() {
        stop()
        playAsset("rpg/startmusic.mp3", loop = true)
    }

    fun startAdventure() {
        stop()
        playAsset("rpg/startmusic.mp3", loop = false) {
            playAsset("rpg/music.mp3", loop = true)
        }
    }

    fun stop() {
        looping = false
        cancelFade()
        try {
            player?.stop()
        } catch (_: Exception) {
        }
        try {
            player?.release()
        } catch (_: Exception) {
        }
        player = null
    }

    private fun cancelFade() {
        fadeRunnable?.let { handler.removeCallbacks(it) }
        fadeRunnable = null
    }

    private fun beginFadeIn(mp: MediaPlayer, durationMs: Long = 900L) {
        cancelFade()
        val tgt = AppDataStore.musicVolumeF(context).coerceIn(0f, 1f)
        try {
            mp.setVolume(0f, 0f)
        } catch (_: Exception) {
        }
        if (tgt <= 0.001f) return
        val steps = 18
        val stepMs = (durationMs / steps).coerceAtLeast(30L)
        var i = 0
        val tick = object : Runnable {
            override fun run() {
                fadeRunnable = null
                val cur = player ?: return
                i += 1
                val t = (i.toFloat() / steps.toFloat()).coerceIn(0f, 1f)
                val ease = 1f - (1f - t) * (1f - t)
                val vol = tgt * ease
                try {
                    cur.setVolume(vol, vol)
                } catch (_: Exception) {
                }
                if (i < steps) {
                    fadeRunnable = this
                    handler.postDelayed(this, stepMs)
                } else {
                    try {
                        cur.setVolume(tgt, tgt)
                    } catch (_: Exception) {
                    }
                }
            }
        }
        fadeRunnable = tick
        handler.postDelayed(tick, stepMs)
    }

    private fun playAsset(path: String, loop: Boolean, onComplete: (() -> Unit)? = null) {
        stop()
        looping = loop
        try {
            val afd: AssetFileDescriptor = context.assets.openFd(path)
            val mp = MediaPlayer()
            mp.setDataSource(afd.fileDescriptor, afd.startOffset, afd.length)
            afd.close()
            mp.isLooping = loop
            mp.setOnCompletionListener {
                if (!loop) {
                    onComplete?.invoke()
                }
            }
            mp.setOnErrorListener { _, _, _ ->
                if (!loop) onComplete?.invoke()
                true
            }
            mp.prepare()
            mp.setVolume(0f, 0f)
            mp.start()
            player = mp
            beginFadeIn(mp)
        } catch (_: Exception) {
            if (!loop) onComplete?.invoke()
        }
    }
}
