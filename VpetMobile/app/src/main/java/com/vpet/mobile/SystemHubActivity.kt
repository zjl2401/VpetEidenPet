package com.vpet.mobile

import android.content.Intent
import android.graphics.BitmapFactory
import android.net.Uri
import android.os.Bundle
import android.util.TypedValue
import android.view.Gravity
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.SeekBar
import android.widget.Switch
import android.widget.TextView
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import com.vpet.mobile.databinding.ActivitySystemBinding

/**
 * 系统菜单落地页。
 * extra [EXTRA_PAGE]: diary|achievements|gallery|phonograph|settings|about|feedback|guide|submit|reset
 */
class SystemHubActivity : AppCompatActivity() {

    companion object {
        const val EXTRA_PAGE = "page"
        const val EXTRA_AUTO_GUIDE = "auto_guide"
    }

    private lateinit var binding: ActivitySystemBinding
    private var phonographPlayer: VoicePlayer? = null
    private var phonographMusic: MusicPlayer? = null

    private val pickGalleryImage = registerForActivityResult(ActivityResultContracts.GetContent()) { uri: Uri? ->
        if (uri == null) return@registerForActivityResult
        val e = UserGalleryStore.importUri(this, uri)
        if (e == null) Toast.makeText(this, "导入失败", Toast.LENGTH_SHORT).show()
        else {
            Toast.makeText(this, "已加入画廊：${galleryDisplayTitle(e.title)}", Toast.LENGTH_SHORT).show()
            pageGallery()
        }
    }

    private val pickPhonographAudio = registerForActivityResult(ActivityResultContracts.GetContent()) { uri: Uri? ->
        if (uri == null) return@registerForActivityResult
        val e = UserPhonographStore.importUri(this, uri)
        if (e == null) Toast.makeText(this, "导入失败", Toast.LENGTH_SHORT).show()
        else {
            Toast.makeText(this, "已加入留声：${e.title}", Toast.LENGTH_SHORT).show()
            pagePhonograph()
        }
    }
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        OverlayGate.pause(this)
        binding = ActivitySystemBinding.inflate(layoutInflater)
        setContentView(binding.root)
        when (intent.getStringExtra(EXTRA_PAGE) ?: "about") {
            "diary" -> pageDiary()
            "achievements" -> pageAchievements()
            "gallery" -> pageGallery()
            "phonograph" -> pagePhonograph()
            "settings" -> pageSettings()
            "about" -> pageAbout()
            "feedback" -> pageFeedback()
            "guide" -> pageGuide(auto = intent.getBooleanExtra(EXTRA_AUTO_GUIDE, false))
            "submit" -> pageSubmit()
            "reset" -> pageReset()
            else -> pageAbout()
        }
    }

    override fun onDestroy() {
        diaryClockTv?.removeCallbacks(diaryClockTick)
        diaryClockTv = null
        phonographPlayer?.stop()
        phonographPlayer = null
        phonographMusic?.stop()
        phonographMusic = null
        OverlayGate.resume(this)
        super.onDestroy()
    }

    private fun clearButtons() = binding.sysButtons.removeAllViews()

    private fun dp(v: Int): Int =
        TypedValue.applyDimension(
            TypedValue.COMPLEX_UNIT_DIP,
            v.toFloat(),
            resources.displayMetrics,
        ).toInt()

    private fun addBtn(label: String, onClick: () -> Unit) {
        binding.sysButtons.addView(
            Button(this).apply {
                text = label
                typeface = UiFonts.cute(this@SystemHubActivity)
                setTextColor(MenuDecor.MENU_FG)
                background = MenuDecor.moduleBtnBg(false)
                AppDataStore.applySp(this, AppDataStore.fontBodySp(this@SystemHubActivity))
                minHeight = 0
                minimumHeight = dp(42)
                setPadding(dp(12), dp(8), dp(12), dp(8))
                layoutParams = LinearLayout.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT,
                    ViewGroup.LayoutParams.WRAP_CONTENT,
                ).also { it.bottomMargin = dp(6) }
                setOnClickListener { onClick() }
            },
        )
    }

    /** 设置页开关行。 */
    private fun addSwitchRow(title: String, checked: Boolean, onChanged: (Boolean) -> Unit) {
        val row = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
            setPadding(0, dp(6), 0, dp(6))
        }
        val label = TextView(this).apply {
            text = title
            typeface = UiFonts.cute(this@SystemHubActivity)
            setTextColor(getColor(R.color.text_main))
            AppDataStore.applySp(this, AppDataStore.fontBodySp(this@SystemHubActivity))
            layoutParams = LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f)
        }
        val sw = Switch(this).apply {
            isChecked = checked
            setOnCheckedChangeListener { _, on -> onChanged(on) }
        }
        row.addView(label)
        row.addView(sw)
        binding.sysButtons.addView(row)
    }

    /** 设置页双选/多选行（普通·黑框等）。 */
    private fun addChoiceRow(
        title: String,
        options: List<Pair<String, String>>,
        selected: String,
        onPick: (String) -> Unit,
    ) {
        val wrap = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(0, dp(4), 0, dp(4))
        }
        wrap.addView(
            TextView(this).apply {
                text = title
                typeface = UiFonts.cute(this@SystemHubActivity)
                setTextColor(getColor(R.color.text_main))
                AppDataStore.applySp(this, AppDataStore.fontBodySp(this@SystemHubActivity))
            },
        )
        val row = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
        }
        for ((label, value) in options) {
            val on = value == selected
            row.addView(
                Button(this).apply {
                    text = if (on) "$label ✓" else label
                    typeface = UiFonts.cute(this@SystemHubActivity)
                    setTextColor(MenuDecor.MENU_FG)
                    background = MenuDecor.moduleBtnBg(on)
                    AppDataStore.applySp(this, AppDataStore.fontCaptionSp(this@SystemHubActivity))
                    minHeight = 0
                    minimumHeight = dp(36)
                    setPadding(dp(10), dp(6), dp(10), dp(6))
                    layoutParams = LinearLayout.LayoutParams(
                        ViewGroup.LayoutParams.WRAP_CONTENT,
                        ViewGroup.LayoutParams.WRAP_CONTENT,
                    ).also { it.marginEnd = dp(6) }
                    setOnClickListener { onPick(value) }
                },
            )
        }
        wrap.addView(row)
        binding.sysButtons.addView(wrap)
    }

    /**
     * 设置页滑条。
     * @param applyOnStop 为 true 时仅在松手时回调 [onChange]（拖动中只刷新文案），减轻改大小开销。
     */
    private fun addSliderRow(
        title: String,
        progress: Int,
        max: Int,
        format: (Int) -> String,
        onChange: (Int) -> Unit,
        applyOnStop: Boolean = false,
    ) {
        val box = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(0, dp(8), 0, dp(8))
        }
        val head = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
        }
        val titleTv = TextView(this).apply {
            text = title
            typeface = UiFonts.cute(this@SystemHubActivity)
            setTextColor(getColor(R.color.text_main))
            AppDataStore.applySp(this, AppDataStore.fontBodySp(this@SystemHubActivity))
            layoutParams = LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f)
        }
        val valueTv = TextView(this).apply {
            text = format(progress.coerceIn(0, max))
            typeface = UiFonts.cute(this@SystemHubActivity)
            setTextColor(getColor(R.color.accent_pink))
            AppDataStore.applySp(this, AppDataStore.fontCaptionSp(this@SystemHubActivity))
        }
        head.addView(titleTv)
        head.addView(valueTv)
        val seek = SeekBar(this).apply {
            this.max = max.coerceAtLeast(1)
            this.progress = progress.coerceIn(0, this.max)
            setPadding(dp(4), dp(8), dp(4), dp(4))
            setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
                override fun onProgressChanged(seekBar: SeekBar?, p: Int, fromUser: Boolean) {
                    valueTv.text = format(p)
                    if (fromUser && !applyOnStop) onChange(p)
                }
                override fun onStartTrackingTouch(seekBar: SeekBar?) {}
                override fun onStopTrackingTouch(seekBar: SeekBar?) {
                    if (applyOnStop) onChange(seekBar?.progress ?: return)
                }
            })
        }
        box.addView(head)
        box.addView(seek)
        binding.sysButtons.addView(box)
    }

    private var diaryPageIdx = 0
    private var diaryPickWeather = "sunny"
    private var diaryPickMood = "stand"
    private var diaryClockTv: TextView? = null
    private val diaryClockTick = object : Runnable {
        override fun run() {
            val tv = diaryClockTv ?: return
            val now = java.util.Calendar.getInstance()
            val week = "一二三四五六日"[((now.get(java.util.Calendar.DAY_OF_WEEK) + 5) % 7)]
            val d = java.text.SimpleDateFormat("yyyy-MM-dd", java.util.Locale.CHINA).format(now.time)
            val t = java.text.SimpleDateFormat("HH:mm", java.util.Locale.CHINA).format(now.time)
            tv.text = "$d  周$week  $t"
            tv.postDelayed(this, 15_000L)
        }
    }

    private fun pageDiary() {
        binding.sysTitle.text = "我的日记"
        binding.sysBody.text = "写好后点「写下这一页」· 过往可翻页"
        binding.sysInput.visibility = View.VISIBLE
        binding.sysInput.hint = "写下这一页…"
        binding.sysInput.setTextColor(getColor(R.color.diary_ink))
        binding.root.setBackgroundColor(getColor(R.color.diary_paper))
        diaryPickWeather = "sunny"
        diaryPickMood = AppDataStore.defaultDiaryMoodFace(this)
        diaryPageIdx = 0
        clearButtons()
        applyChromeFonts()

        diaryClockTv = TextView(this).apply {
            setTextColor(getColor(R.color.diary_ink))
            typeface = UiFonts.cute(this@SystemHubActivity)
            AppDataStore.applySp(this, AppDataStore.fontBodySp(this@SystemHubActivity))
            setPadding(0, 0, 0, dp(6))
        }
        binding.sysButtons.addView(diaryClockTv)
        diaryClockTv?.removeCallbacks(diaryClockTick)
        diaryClockTick.run()

        binding.sysButtons.addView(chipSection("天气", AppDataStore.DIARY_WEATHER, diaryPickWeather) {
            diaryPickWeather = it
        })
        binding.sysButtons.addView(chipSection("心情", AppDataStore.DIARY_MOODS, diaryPickMood) {
            diaryPickMood = it
        })

        addBtn("写下这一页") {
            if (AppDataStore.addDiary(
                    this,
                    binding.sysInput.text.toString(),
                    weather = diaryPickWeather,
                    moodFace = diaryPickMood,
                )
            ) {
                Toast.makeText(this, "已写下这一页", Toast.LENGTH_SHORT).show()
                binding.sysInput.setText("")
                diaryPageIdx = 0
                rebuildDiaryPager()
            } else {
                Toast.makeText(this, "内容不能为空", Toast.LENGTH_SHORT).show()
            }
        }

        binding.sysButtons.addView(
            TextView(this).apply {
                text = "— 过往页 —"
                setTextColor(getColor(R.color.diary_muted))
                typeface = UiFonts.cute(this@SystemHubActivity)
                setPadding(0, dp(10), 0, dp(4))
            },
        )
        rebuildDiaryPager()
        addBtn("返回") {
            diaryClockTv?.removeCallbacks(diaryClockTick)
            finish()
        }
    }

    private fun chipSection(
        title: String,
        options: List<Pair<String, String>>,
        selected: String,
        onPick: (String) -> Unit,
    ): LinearLayout {
        val box = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(0, dp(4), 0, dp(4))
        }
        box.addView(TextView(this).apply {
            text = title
            setTextColor(getColor(R.color.diary_muted))
            typeface = UiFonts.cute(this@SystemHubActivity)
        })
        val grid = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL }
        var cur: LinearLayout? = null
        val chips = mutableMapOf<String, TextView>()
        val selectedRef = arrayOf(selected)
        fun paint() {
            for ((k, tv) in chips) {
                val on = k == selectedRef[0]
                tv.setBackgroundColor(if (on) 0xFFFFE8B8.toInt() else getColor(R.color.diary_card))
                tv.setTextColor(getColor(R.color.diary_ink))
            }
        }
        options.forEachIndexed { i, (id, label) ->
            if (i % 4 == 0) {
                cur = LinearLayout(this).apply {
                    orientation = LinearLayout.HORIZONTAL
                    setPadding(0, dp(2), 0, dp(2))
                }
                grid.addView(cur)
            }
            val tv = TextView(this).apply {
                text = label
                gravity = Gravity.CENTER
                typeface = UiFonts.cute(this@SystemHubActivity)
                AppDataStore.applySp(this, AppDataStore.fontCaptionSp(this@SystemHubActivity))
                setPadding(dp(8), dp(6), dp(8), dp(6))
                layoutParams = LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f).also {
                    it.marginEnd = dp(4)
                }
                setOnClickListener {
                    selectedRef[0] = id
                    onPick(id)
                    paint()
                }
            }
            chips[id] = tv
            cur!!.addView(tv)
        }
        val rem = options.size % 4
        if (rem != 0 && cur != null) {
            repeat(4 - rem) {
                cur!!.addView(View(this).apply {
                    layoutParams = LinearLayout.LayoutParams(0, 1, 1f)
                })
            }
        }
        paint()
        box.addView(grid)
        return box
    }

    private fun rebuildDiaryPager() {
        // remove previous pager block if tagged
        val doomed = mutableListOf<View>()
        for (i in 0 until binding.sysButtons.childCount) {
            val v = binding.sysButtons.getChildAt(i)
            if (v.tag == "diary_pager") doomed += v
        }
        doomed.forEach { binding.sysButtons.removeView(it) }
        // insert before last「返回」button if present
        val insertAt = (0 until binding.sysButtons.childCount)
            .lastOrNull { binding.sysButtons.getChildAt(it) is Button &&
                (binding.sysButtons.getChildAt(it) as Button).text == "返回" }
            ?: binding.sysButtons.childCount

        val arr = AppDataStore.diaries(this)
        val pages = (0 until minOf(arr.length(), 30)).map { arr.getJSONObject(it) }
        val host = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            tag = "diary_pager"
            setBackgroundColor(getColor(R.color.diary_card))
            setPadding(dp(10), dp(8), dp(10), dp(8))
        }
        val nav = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
            tag = "diary_pager"
        }
        val idxTv = TextView(this).apply {
            setTextColor(getColor(R.color.diary_muted))
            typeface = UiFonts.cute(this@SystemHubActivity)
            gravity = Gravity.CENTER
            layoutParams = LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f)
        }
        fun paintPage() {
            host.removeAllViews()
            if (pages.isEmpty()) {
                idxTv.text = "0 / 0"
                host.addView(TextView(this).apply {
                    text = "还没有写下的页。\n在上方写好后点「写下这一页」。"
                    setTextColor(getColor(R.color.diary_muted))
                    typeface = UiFonts.cute(this@SystemHubActivity)
                })
                return
            }
            diaryPageIdx = diaryPageIdx.coerceIn(0, pages.lastIndex)
            idxTv.text = "${diaryPageIdx + 1} / ${pages.size}"
            val item = pages[diaryPageIdx]
            val top = LinearLayout(this).apply {
                orientation = LinearLayout.HORIZONTAL
                gravity = Gravity.CENTER_VERTICAL
            }
            top.addView(TextView(this).apply {
                val auto = if (item.optBoolean("auto")) "  ·自动" else ""
                text = "${item.optString("date").ifBlank { item.optString("ts") }}  ${item.optString("time")}$auto"
                setTextColor(getColor(R.color.diary_muted))
                typeface = UiFonts.cute(this@SystemHubActivity)
                layoutParams = LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f)
            })
            top.addView(TextView(this).apply {
                text = "删"
                setTextColor(0xFFCC5555.toInt())
                typeface = UiFonts.cute(this@SystemHubActivity)
                setPadding(dp(8), dp(4), dp(4), dp(4))
                setOnClickListener {
                    val id = item.optString("id")
                    if (AppDataStore.deleteDiary(this@SystemHubActivity, id)) {
                        diaryPageIdx = diaryPageIdx.coerceAtMost((pages.size - 2).coerceAtLeast(0))
                        rebuildDiaryPager()
                    }
                }
            })
            host.addView(top)
            val meta = buildString {
                val wl = item.optString("weather_label").ifBlank {
                    AppDataStore.diaryWeatherLabel(item.optString("weather"))
                }
                val ml = item.optString("mood_label").ifBlank {
                    AppDataStore.diaryMoodLabel(item.optString("mood_face"))
                }
                if (wl.isNotBlank()) append("天气 $wl")
                if (ml.isNotBlank()) {
                    if (isNotEmpty()) append(" · ")
                    append("心情 $ml")
                }
            }
            if (meta.isNotBlank()) {
                host.addView(TextView(this).apply {
                    text = meta
                    setTextColor(getColor(R.color.diary_ink))
                    typeface = UiFonts.cute(this@SystemHubActivity)
                    setPadding(0, dp(4), 0, dp(4))
                })
            }
            host.addView(TextView(this).apply {
                text = item.optString("text")
                setTextColor(getColor(R.color.diary_ink))
                typeface = UiFonts.cute(this@SystemHubActivity)
            })
        }
        nav.addView(TextView(this).apply {
            text = "‹ 上页"
            setTextColor(getColor(R.color.accent_pink))
            typeface = UiFonts.cute(this@SystemHubActivity)
            setPadding(dp(4), dp(6), dp(8), dp(6))
            setOnClickListener {
                if (diaryPageIdx > 0) {
                    diaryPageIdx--
                    paintPage()
                }
            }
        })
        nav.addView(idxTv)
        nav.addView(TextView(this).apply {
            text = "下页 ›"
            setTextColor(getColor(R.color.accent_pink))
            typeface = UiFonts.cute(this@SystemHubActivity)
            setPadding(dp(8), dp(6), dp(4), dp(6))
            setOnClickListener {
                if (diaryPageIdx < pages.lastIndex) {
                    diaryPageIdx++
                    paintPage()
                }
            }
        })
        paintPage()
        binding.sysButtons.addView(nav, insertAt)
        binding.sysButtons.addView(host, insertAt + 1)
    }

    private fun refreshDiaryBody() {
        /* replaced by rebuildDiaryPager */
    }

    private fun pageAchievements() {
        binding.sysTitle.text = "成就"
        if (PetPrefs.hasOwner(this)) AppDataStore.unlock(this, "owner_named")
        val unlocked = AppDataStore.achievements(this)
        binding.sysBody.text = AppDataStore.achievementCatalog().joinToString("\n\n") { (id, title, desc) ->
            val mark = if (id in unlocked) "✓" else "·"
            "$mark $title\n  $desc"
        }
        clearButtons()
        addBtn("返回") { finish() }
    }

    private fun pageMemory(title: String, body: String) {
        binding.sysTitle.text = title
        binding.sysBody.text = body
        AppDataStore.unlock(this, "memory_open")
        clearButtons()
        addBtn("返回") { finish() }
    }

    private fun pageGallery() {
        binding.sysTitle.text = "画廊"
        AppDataStore.unlock(this, "memory_open")
        val groups = GalleryCatalog.loadGroups(this)
        val user = UserGalleryStore.list(this)
        binding.sysBody.text = buildString {
            appendLine("内置画廊 ${groups.size} 组 · 用户图 ${user.size} 张")
            appendLine("点下方按钮看图（对照桌面 gallery.json）")
            appendLine()
            for (g in groups.take(16)) {
                appendLine("· ${g.title}  ${g.paths.size} 张${if (g.sticker != null) " ·${g.sticker}" else ""}")
            }
            if (groups.size > 16) appendLine("…")
            if (user.isNotEmpty()) {
                appendLine()
                appendLine("用户图：")
                for (e in user.take(8)) appendLine("· ${e.title}")
            }
        }
        clearButtons()
        addBtn("导入图片") { pickGalleryImage.launch("image/*") }
        for (e in user) {
            addBtn("看·${galleryDisplayTitle(e.title).take(10)}") {
                val bmp = BitmapFactory.decodeFile(UserGalleryStore.fileOf(this, e).absolutePath)
                if (bmp == null) {
                    Toast.makeText(this, "无法打开", Toast.LENGTH_SHORT).show()
                    return@addBtn
                }
                // 对照桌面：只显示中文标题/预览，不展示文件名
                showBitmapDialog(galleryDisplayTitle(e.title), bmp) {
                    UserGalleryStore.remove(this, e.id)
                    pageGallery()
                }
            }
        }
        for (g in groups) {
            addBtn("看·${g.title.take(12)}") {
                val bmp = g.paths.firstNotNullOfOrNull { GalleryCatalog.decode(this, it) }
                if (bmp == null) {
                    Toast.makeText(this, "无素材：${g.title}", Toast.LENGTH_SHORT).show()
                    return@addBtn
                }
                showBitmapDialog(g.title, bmp)
            }
        }
        addBtn("返回") { finish() }
    }

    /** 文件名（含扩展名）不当作展示标题。 */
    private fun galleryDisplayTitle(raw: String): String {
        val t = raw.trim()
        if (t.isBlank()) return "用户图"
        val low = t.lowercase()
        if (low.endsWith(".png") || low.endsWith(".jpg") || low.endsWith(".jpeg") ||
            low.endsWith(".webp") || low.endsWith(".gif")
        ) {
            return "用户图"
        }
        return t
    }

    private fun showBitmapDialog(
        title: String,
        bmp: android.graphics.Bitmap,
        message: String? = null,
        onDelete: (() -> Unit)? = null,
    ) {
        val iv = ImageView(this).apply {
            setImageBitmap(bmp)
            adjustViewBounds = true
            maxHeight = (resources.displayMetrics.heightPixels * 0.55f).toInt()
            setPadding(24, 16, 24, 8)
        }
        val box = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            addView(iv)
            if (!message.isNullOrBlank()) {
                addView(
                    TextView(this@SystemHubActivity).apply {
                        text = message
                        setPadding(24, 0, 24, 16)
                        textSize = 12f
                    },
                )
            }
        }
        val b = AlertDialog.Builder(this)
            .setTitle(title)
            .setView(box)
            .setPositiveButton("好", null)
        if (onDelete != null) {
            b.setNeutralButton("删除") { _, _ -> onDelete() }
        }
        b.show()
    }

    private fun pagePhonograph() {
        binding.sysTitle.text = "留声"
        AppDataStore.unlock(this, "memory_open")
        phonographPlayer = VoicePlayer(this)
        phonographMusic?.stop()
        phonographMusic = MusicPlayer(this)
        val musicPlayer = phonographMusic!!
        val voiceDirs = listVoiceDirs()
        val musicTracks = BundledMusic.tracks(this)
        val musicFolders = BundledMusic.folders(this)
        val user = UserPhonographStore.list(this)
        binding.sysBody.text = buildString {
            appendLine("语音分类 ${voiceDirs.size} · 内置曲目 ${musicTracks.size} · 用户 ${user.size}")
            appendLine("点分类播随机一条；音乐可点具体曲目")
            appendLine()
            appendLine("语音：${voiceDirs.joinToString(" · ") { it.substringAfterLast('/') }}")
            appendLine()
            appendLine("音乐分类：${musicFolders.joinToString(" · ") { it.substringBefore('-') }}")
        }
        clearButtons()
        addBtn("导入音频") { pickPhonographAudio.launch("audio/*") }
        for (e in user) {
            addBtn("播·${e.title.take(12)}") {
                musicPlayer.stop()
                val ok = phonographPlayer?.playFile(UserPhonographStore.fileOf(this, e)) == true
                Toast.makeText(this, if (ok) "播放：${e.title}" else "播放失败", Toast.LENGTH_SHORT).show()
            }
            addBtn("删·${e.title.take(8)}") {
                UserPhonographStore.remove(this, e.id)
                pagePhonograph()
            }
        }
        for (dir in voiceDirs) {
            val label = dir.substringAfterLast('/')
            addBtn("语·$label") {
                musicPlayer.stop()
                val path = phonographPlayer?.pickAsset(dir)
                if (path == null) {
                    Toast.makeText(this, "无音频：$label", Toast.LENGTH_SHORT).show()
                } else {
                    val ok = phonographPlayer?.playAssetPath(path) == true
                    val title = VoiceTitle.displayTitle(path)
                    Toast.makeText(
                        this,
                        when {
                            !ok -> "播放失败"
                            title == "……" -> "已播放"
                            else -> "播放：$title"
                        },
                        Toast.LENGTH_SHORT,
                    ).show()
                }
            }
        }
        for (t in musicTracks) {
            addBtn("曲·${t.label.take(18)}") {
                phonographPlayer?.stop()
                musicPlayer.playAsset(
                    t.assetPath,
                    loop = false,
                    onError = { Toast.makeText(this, it, Toast.LENGTH_SHORT).show() },
                    onComplete = {},
                )
                Toast.makeText(this, "播放：${t.label.take(18)}", Toast.LENGTH_SHORT).show()
            }
        }
        addBtn("停止") {
            phonographPlayer?.stop()
            musicPlayer.stop()
        }
        addBtn("返回") {
            phonographPlayer?.stop()
            musicPlayer.stop()
            finish()
        }
    }

    private fun listVoiceDirs(): List<String> {
        val preferred = listOf(
            "hi", "normal", "work", "sleep", "game", "eat", "call", "dizzy", "hurt",
            "kick", "walk", "yuqi", "hungry", "forget", "error", "email",
            "end", "interjection", "你好",
        )
        val vpet = assets.list("voice/Vpet")?.toSet().orEmpty()
        val ordered = preferred.filter { it in vpet }.map { "voice/Vpet/$it" }.toMutableList()
        for (extra in vpet.sorted()) {
            if (extra !in preferred && !extra.contains('.')) ordered += "voice/Vpet/$extra"
        }
        if (assets.list("voice/Allmate")?.isNotEmpty() == true) ordered += "voice/Allmate"
        if (assets.list("voice/chain")?.isNotEmpty() == true) ordered += "voice/chain"
        return ordered
    }

    private fun existsAsset(path: String): Boolean = try {
        assets.open(path).close()
        true
    } catch (_: Exception) {
        false
    }

    private fun applyChromeFonts() {
        val face = UiFonts.cute(this)
        binding.sysTitle.typeface = UiFonts.cuteBold(this)
        binding.sysBody.typeface = face
        binding.sysInput.typeface = face
        AppDataStore.applySp(binding.sysTitle, AppDataStore.fontTitleSp(this))
        AppDataStore.applySp(binding.sysBody, AppDataStore.fontBodySp(this))
        AppDataStore.applySp(binding.sysInput, AppDataStore.fontBodySp(this))
        fun walk(v: View) {
            if (v is TextView) {
                v.typeface = face
                AppDataStore.applySp(v, AppDataStore.fontBodySp(this))
            }
            if (v is ViewGroup) {
                for (i in 0 until v.childCount) walk(v.getChildAt(i))
            }
        }
        walk(binding.sysButtons)
    }

    private fun notifyOverlayFont() {
        startService(
            Intent(this, PetOverlayService::class.java).apply {
                action = PetOverlayService.ACTION_APPLY_FONT
            },
        )
    }

    private fun pageSettings() {
        binding.sysTitle.text = "设置"
        binding.sysBody.text = ""
        clearButtons()
        applyChromeFonts()

        val fontLabels = AppDataStore.FONT_PRESETS.keys.toList()
        val diffLabels = AppDataStore.DIFF_PRESETS
        val sizeSteps = (PetPrefs.SIZE_MAX_PX - PetPrefs.SIZE_MIN_PX) / PetPrefs.SIZE_STEP_PX
        val curPx = PetPrefs.sizePx(this)
        val sizeProgress = ((curPx - PetPrefs.SIZE_MIN_PX) / PetPrefs.SIZE_STEP_PX)
            .coerceIn(0, sizeSteps)

        addSliderRow(
            title = "大小",
            progress = sizeProgress,
            max = sizeSteps,
            format = { i ->
                val px = PetPrefs.SIZE_MIN_PX + i * PetPrefs.SIZE_STEP_PX
                val label = PetPrefs.nearestSizeLabel(px)
                "$label · ${PetPrefs.snapSizePx(px)}px"
            },
            onChange = { i ->
                val px = PetPrefs.SIZE_MIN_PX + i * PetPrefs.SIZE_STEP_PX
                PetPrefs.setSizePx(this, px)
                startService(
                    Intent(this, PetOverlayService::class.java).apply {
                        action = PetOverlayService.ACTION_RESIZE
                    },
                )
            },
            applyOnStop = true,
        )

        addSliderRow(
            title = "字体",
            progress = fontLabels.indexOf(AppDataStore.fontLabel(this)).coerceAtLeast(0),
            max = fontLabels.lastIndex,
            format = { i -> fontLabels.getOrElse(i) { "中" } },
            onChange = { i ->
                AppDataStore.setFontLabel(this, fontLabels.getOrElse(i) { "中" })
                applyChromeFonts()
                notifyOverlayFont()
            },
        )

        addSwitchRow("时间显示", AppDataStore.showTimers(this)) { on ->
            AppDataStore.setShowTimers(this, on)
            startService(
                Intent(this, PetOverlayService::class.java).apply {
                    action = PetOverlayService.ACTION_SYNC_TIMERS
                },
            )
            Toast.makeText(
                this,
                if (on) "时间显示：开（模式旁自动秒表）" else "时间显示：关",
                Toast.LENGTH_SHORT,
            ).show()
        }

        addSwitchRow("文本框", AppDataStore.showSpeech(this)) { on ->
            AppDataStore.setShowSpeech(this, on)
            if (!on) {
                startService(
                    Intent(this, PetOverlayService::class.java).apply {
                        action = PetOverlayService.ACTION_HIDE_SPEECH
                    },
                )
            }
            Toast.makeText(
                this,
                if (on) "文本框：开" else "文本框：关（语音仍可播）",
                Toast.LENGTH_SHORT,
            ).show()
        }

        addChoiceRow(
            title = "立绘图组",
            options = listOf("普通" to AppDataStore.SPRITE_PACK_NORMAL, "黑框" to AppDataStore.SPRITE_PACK_BLACK),
            selected = AppDataStore.spritePack(this),
        ) { pack ->
            AppDataStore.setSpritePack(this, pack)
            startService(
                Intent(this, PetOverlayService::class.java).apply {
                    action = PetOverlayService.ACTION_RELOAD_SPRITES
                },
            )
            Toast.makeText(
                this,
                if (pack == AppDataStore.SPRITE_PACK_BLACK) "立绘：黑框（缺图回退普通）" else "立绘：普通",
                Toast.LENGTH_SHORT,
            ).show()
            // 重建本页以刷新选中态
            pageSettings()
        }

        addSwitchRow("音效", AppDataStore.soundOn(this)) { on ->
            AppDataStore.setSoundOn(this, on)
        }
        addSwitchRow("语音", AppDataStore.voiceMode(this)) { on ->
            AppDataStore.setVoiceMode(this, on)
        }

        addSliderRow(
            title = "音乐音量",
            progress = AppDataStore.musicVolume(this),
            max = 100,
            format = { "$it%" },
            onChange = {
                AppDataStore.setMusicVolume(this, it)
                startService(
                    Intent(this, PetOverlayService::class.java).apply {
                        action = PetOverlayService.ACTION_APPLY_MUSIC_VOL
                    },
                )
            },
        )

        addSwitchRow(
            "熄屏显示",
            LockScreenPetStore.enabled(this),
        ) { on ->
            LockScreenPetStore.setEnabled(this, on)
            Toast.makeText(
                this,
                if (on) "熄屏姿势已开" else "熄屏姿势已关",
                Toast.LENGTH_SHORT,
            ).show()
        }

        val usageOn = AppSceneClassifier.hasUsageAccess(this)
        addBtn(
            if (usageOn) "使用情况 · 已授权" else "授权使用情况访问",
        ) {
            AppSceneClassifier.openUsageAccessSettings(this)
            Toast.makeText(
                this,
                if (usageOn) "可在系统设置中关闭授权"
                else "请找到 VpetMobile 并打开「允许查看使用情况」",
                Toast.LENGTH_LONG,
            ).show()
        }

        addSliderRow(
            title = "语音音量",
            progress = AppDataStore.voiceVolume(this),
            max = 100,
            format = { "$it%" },
            onChange = { AppDataStore.setVoiceVolume(this, it) },
        )

        addSliderRow(
            title = "音效音量",
            progress = AppDataStore.sfxVolume(this),
            max = 100,
            format = { "$it%" },
            onChange = { AppDataStore.setSfxVolume(this, it) },
        )

        addBtn("音乐 / 导入本地曲") {
            startActivity(Intent(this, ToolsActivity::class.java))
        }

        addSliderRow(
            title = "难度",
            progress = diffLabels.indexOf(AppDataStore.difficulty(this)).coerceAtLeast(0),
            max = diffLabels.lastIndex,
            format = { diffLabels.getOrElse(it) { "中" } },
            onChange = { i ->
                AppDataStore.setDifficulty(this, diffLabels.getOrElse(i) { "中" })
            },
        )

        addSliderRow(
            title = "闲聊间隔",
            progress = AppDataStore.freeIdleBanterSec(this),
            max = AppDataStore.FREE_IDLE_SEC_MAX,
            format = {
                val s = it.coerceAtLeast(AppDataStore.FREE_IDLE_SEC_MIN)
                "${s}s"
            },
            onChange = { i ->
                AppDataStore.setFreeIdleBanterSec(
                    this,
                    i.coerceAtLeast(AppDataStore.FREE_IDLE_SEC_MIN),
                )
            },
        )

        addBtn("档案导入") {
            startActivity(Intent(this, ToolsActivity::class.java))
        }
        addBtn("返回") { finish() }
    }

    private fun pageAbout() {
        binding.sysTitle.text = "关于"
        binding.sysBody.text = DesktopGuideCopy.aboutBody()
        clearButtons()
        addBtn("打开 GitHub") { openUrl(DesktopGuideCopy.ABOUT_REPO_URL) }
        addBtn("新世界狂欢（正版）") { openUrl(DesktopGuideCopy.ABOUT_STEAM_URL) }
        addBtn("B站") { openUrl(DesktopGuideCopy.FEEDBACK_BILI_URL) }
        addBtn("返回") { finish() }
    }

    private fun pageFeedback() {
        binding.sysTitle.text = "问题反馈"
        binding.sysBody.text = DesktopGuideCopy.feedbackBody()
        clearButtons()
        addBtn("GitHub Issues") { openUrl(DesktopGuideCopy.FEEDBACK_ISSUE_URL) }
        addBtn("小红书") { openUrl(DesktopGuideCopy.FEEDBACK_XHS_URL) }
        addBtn("B站") { openUrl(DesktopGuideCopy.FEEDBACK_BILI_URL) }
        addBtn("返回") { finish() }
    }

    private fun pageGuide(auto: Boolean = false) {
        showGuideHome()
        if (auto) AppConfigStore.markOperationGuideSeen(this)
    }

    private fun showGuideHome() {
        binding.sysTitle.text = "操作说明"
        binding.sysBody.text = DesktopGuideCopy.guideHomeBody()
        clearButtons()
        for (topic in DesktopGuideCopy.GUIDE_TOPICS) {
            addBtn(topic.title) { showGuideTopic(topic) }
        }
        addBtn("知道了") { finish() }
    }

    private fun showGuideTopic(topic: DesktopGuideCopy.Topic) {
        binding.sysTitle.text = topic.title
        binding.sysBody.text = topic.body
        clearButtons()
        for ((label, url) in topic.links) {
            addBtn(label) { openUrl(url) }
        }
        addBtn("返回专题列表") { showGuideHome() }
        addBtn("关闭") { finish() }
    }

    private fun pageSubmit() {
        binding.sysTitle.text = "投稿创意"
        binding.sysBody.text = DesktopGuideCopy.submitBody()
        clearButtons()
        addBtn("去问题反馈") { pageFeedback() }
        addBtn("返回") { finish() }
    }

    private fun pageReset() {
        binding.sysTitle.text = "重置"
        binding.sysBody.text = DesktopGuideCopy.RESET_CONFIRM
        clearButtons()
        addBtn("确定重置") {
            AlertDialog.Builder(this)
                .setTitle("重置确认")
                .setMessage(DesktopGuideCopy.RESET_CONFIRM)
                .setPositiveButton("确定重置") { _, _ ->
                    AppDataStore.resetKeepOwner(this)
                    Toast.makeText(
                        this,
                        "已重置设置；相伴时间、装扮与背包已保留",
                        Toast.LENGTH_LONG,
                    ).show()
                    finish()
                }
                .setNegativeButton("取消", null)
                .show()
        }
        addBtn("取消") { finish() }
    }

    private fun openUrl(url: String) {
        try {
            startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url)))
        } catch (_: Exception) {
            Toast.makeText(this, "无法打开链接", Toast.LENGTH_SHORT).show()
        }
    }
}
