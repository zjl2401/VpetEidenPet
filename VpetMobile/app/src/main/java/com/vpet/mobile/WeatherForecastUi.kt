package com.vpet.mobile

import android.app.Dialog
import android.content.Context
import android.graphics.Canvas
import android.graphics.Paint
import android.os.Handler
import android.os.Looper
import android.view.Gravity
import android.view.View
import android.view.WindowManager
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.view.ContextThemeWrapper
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.net.URLEncoder
import java.util.concurrent.Executors

/**
 * 天气预报：对照桌面 Open-Meteo（无需 Key）。
 */
object WeatherForecastUi {
    private val io = Executors.newSingleThreadExecutor()
    private val main = Handler(Looper.getMainLooper())

    private val CITY_COORDS = mapOf(
        "北京" to (39.9042 to 116.4074),
        "上海" to (31.2304 to 121.4737),
        "广州" to (23.1291 to 113.2644),
        "杭州" to (30.2741 to 120.1551),
        "成都" to (30.5728 to 104.0668),
        "深圳" to (22.5431 to 114.0579),
    )

    fun show(context: Context) {
        val themed = ContextThemeWrapper(context, R.style.Theme_VpetMobile)
        val pad = MenuDecor.dp(context, 12f)
        val box = LinearLayout(themed).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(pad, pad, pad, pad)
        }
        PanelTheme.applyCreamRoot(box)
        PanelTheme.attachSignStrip(box)
        box.addView(PanelTheme.title(themed, "天气预报"))

        val city = EditText(themed).apply {
            setText(AppDataStore.weatherCity(context))
            setTextColor(MenuDecor.MENU_FG)
            setBackgroundColor(MenuDecor.THEME_ITEM_BG)
            typeface = UiFonts.cute(context)
            setPadding(MenuDecor.dp(context, 8f), MenuDecor.dp(context, 6f), MenuDecor.dp(context, 8f), MenuDecor.dp(context, 6f))
        }
        box.addView(PanelTheme.label(themed, "城市"))
        box.addView(city)

        val canvas = WeatherCanvas(themed)
        canvas.layoutParams = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            MenuDecor.dp(context, 160f),
        )
        val status = TextView(themed).apply {
            text = "获取天气中…"
            setTextColor(MenuDecor.MENU_FG)
            typeface = UiFonts.cute(context)
            textSize = AppDataStore.fontHintSp(context)
        }

        val presets = LinearLayout(themed).apply {
            orientation = LinearLayout.HORIZONTAL
            CITY_COORDS.keys.take(6).forEach { name ->
                addView(
                    PanelTheme.primaryBtn(themed, name) {
                        city.setText(name)
                        load(themed, name, status, canvas)
                    }.also {
                        (it.layoutParams as LinearLayout.LayoutParams).apply {
                            marginEnd = MenuDecor.dp(context, 4f)
                            width = LinearLayout.LayoutParams.WRAP_CONTENT
                        }
                    },
                )
            }
        }
        box.addView(presets)
        box.addView(canvas)
        box.addView(status)

        val holder = arrayOfNulls<Dialog>(1)
        box.addView(
            LinearLayout(themed).apply {
                orientation = LinearLayout.HORIZONTAL
                gravity = Gravity.END
                setPadding(0, MenuDecor.dp(context, 8f), 0, 0)
                addView(PanelTheme.primaryBtn(themed, "刷新") {
                    load(themed, city.text.toString(), status, canvas)
                })
                addView(
                    PanelTheme.primaryBtn(themed, "关闭") { holder[0]?.dismiss() }.also {
                        (it.layoutParams as LinearLayout.LayoutParams).marginStart = MenuDecor.dp(context, 8f)
                    },
                )
            },
        )

        val dialog = Dialog(themed)
        dialog.setContentView(box)
        dialog.setCancelable(true)
        dialog.window?.apply {
            setBackgroundDrawableResource(android.R.color.transparent)
            setLayout(
                (context.resources.displayMetrics.widthPixels * 0.90f).toInt(),
                WindowManager.LayoutParams.WRAP_CONTENT,
            )
        }
        OverlayZOrder.prepareOverlayWindow(dialog.window)
        dialog.show()
        OverlayZOrder.onOverlayDialogShown(dialog)
        holder[0] = dialog
        load(themed, city.text.toString(), status, canvas)
    }

    private fun load(ctx: Context, cityName: String, status: TextView, canvas: WeatherCanvas) {
        val name = cityName.trim().ifBlank { "北京" }
        AppDataStore.setWeatherCity(ctx, name)
        status.text = "获取天气中…"
        io.execute {
            try {
                val (lat, lon) = CITY_COORDS[name] ?: geocode(name) ?: (39.9042 to 116.4074)
                val url =
                    "https://api.open-meteo.com/v1/forecast?latitude=$lat&longitude=$lon" +
                        "&current=temperature_2m,apparent_temperature,relative_humidity_2m,weather_code,wind_speed_10m" +
                        "&daily=weather_code,temperature_2m_max,temperature_2m_min&timezone=auto&forecast_days=3"
                val raw = httpGet(url)
                val json = JSONObject(raw)
                val cur = json.optJSONObject("current") ?: JSONObject()
                val code = cur.optInt("weather_code", 3)
                val (desc, kind) = weatherCodeInfo(code)
                val temp = cur.optDouble("temperature_2m", Double.NaN)
                val feels = cur.optDouble("apparent_temperature", Double.NaN)
                val hum = cur.optDouble("relative_humidity_2m", Double.NaN)
                val wind = cur.optDouble("wind_speed_10m", Double.NaN)
                val line = buildString {
                    append(name)
                    if (!temp.isNaN()) append("  ${temp.toInt()}°C")
                    append("  $desc")
                    if (!feels.isNaN()) append("\n体感 ${feels.toInt()}°C")
                    if (!hum.isNaN()) append("  湿度 ${hum.toInt()}%")
                    if (!wind.isNaN()) append("  风 ${wind.toInt()}km/h")
                }
                main.post {
                    status.text = line
                    canvas.kind = kind
                    canvas.invalidate()
                }
            } catch (e: Exception) {
                main.post {
                    status.text = "获取失败：${e.message?.take(40) ?: "网络异常"}"
                    Toast.makeText(ctx, "天气获取失败", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }

    private fun geocode(name: String): Pair<Double, Double>? {
        return try {
            val q = URLEncoder.encode(name, "UTF-8")
            val raw = httpGet("https://geocoding-api.open-meteo.com/v1/search?name=$q&count=1&language=zh")
            val arr = JSONObject(raw).optJSONArray("results") ?: return null
            if (arr.length() == 0) return null
            val o = arr.getJSONObject(0)
            o.getDouble("latitude") to o.getDouble("longitude")
        } catch (_: Exception) {
            null
        }
    }

    private fun httpGet(url: String): String {
        val conn = (URL(url).openConnection() as HttpURLConnection).apply {
            connectTimeout = 8000
            readTimeout = 8000
            requestMethod = "GET"
        }
        return conn.inputStream.bufferedReader().use { it.readText() }
    }

    private fun weatherCodeInfo(code: Int): Pair<String, String> = when (code) {
        0 -> "晴" to "sunny"
        1, 2 -> "多云" to "cloudy"
        3 -> "阴" to "overcast"
        45, 48 -> "雾" to "fog"
        in 51..67 -> "雨" to "rain"
        in 71..77 -> "雪" to "snow"
        in 80..82 -> "阵雨" to "rain"
        in 95..99 -> "雷雨" to "storm"
        else -> "多云" to "cloudy"
    }

    private class WeatherCanvas(ctx: Context) : View(ctx) {
        var kind: String = "sunny"
        private val paint = Paint(Paint.ANTI_ALIAS_FLAG)

        override fun onDraw(canvas: Canvas) {
            super.onDraw(canvas)
            paint.color = MenuDecor.MENU_BG
            canvas.drawRect(0f, 0f, width.toFloat(), height.toFloat(), paint)
            val cx = width / 2f
            val cy = height / 2f
            when (kind) {
                "sunny" -> {
                    paint.color = MenuDecor.THEME_YELLOW
                    canvas.drawCircle(cx, cy, 36f, paint)
                }
                "rain", "storm" -> {
                    paint.color = MenuDecor.THEME_BLUE
                    canvas.drawCircle(cx, cy - 10f, 40f, paint)
                    paint.color = MenuDecor.THEME_BLUE_DEEP
                    for (i in -2..2) {
                        canvas.drawLine(cx + i * 14f, cy + 20f, cx + i * 14f - 6f, cy + 48f, paint)
                    }
                }
                "snow" -> {
                    paint.color = MenuDecor.THEME_WHITE
                    paint.setShadowLayer(4f, 0f, 0f, MenuDecor.THEME_BLUE)
                    canvas.drawCircle(cx, cy, 34f, paint)
                }
                else -> {
                    paint.color = 0xFFCCDDEE.toInt()
                    canvas.drawCircle(cx - 16f, cy, 28f, paint)
                    canvas.drawCircle(cx + 18f, cy + 4f, 34f, paint)
                }
            }
        }
    }
}
