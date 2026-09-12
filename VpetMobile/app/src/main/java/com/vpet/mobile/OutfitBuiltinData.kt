package com.vpet.mobile

/** Auto-synced from pet_outfit.BUILTIN_CATALOG — do not hand-edit pixels. */
internal object OutfitBuiltinData {
    data class Entry(
        val id: String,
        val name: String,
        val group: String,
        val cells: IntArray,
        val nx: Float = OutfitStore.DEFAULT_NX,
        val ny: Float = OutfitStore.DEFAULT_NY,
        val scale: Float = OutfitStore.DEFAULT_SCALE,
    )

    private fun cellsOf(draw: (put: (Int, Int, Int) -> Unit) -> Unit): IntArray {
        val cells = IntArray(144)
        draw { x, y, c -> if (x in 0 until 12 && y in 0 until 12) cells[y * 12 + x] = c }
        return cells
    }

    val catalog: List<Entry> = listOf(
        Entry(
            "star", "星星", "装饰",
            cellsOf { put ->
                listOf(
                    5 to 1 to 2, 5 to 2 to 2, 4 to 3 to 2, 5 to 3 to 2, 6 to 3 to 2, 3 to 4 to 2,
                    4 to 4 to 2, 5 to 4 to 2, 6 to 4 to 2, 7 to 4 to 2, 5 to 5 to 2, 4 to 6 to 2,
                    6 to 6 to 2, 3 to 7 to 2, 7 to 7 to 2
                ).forEach { (xy, c) ->
                    val (x, y) = xy
                    put(x, y, c)
                }
            },
        ),
        Entry(
            "heart", "爱心", "装饰",
            cellsOf { put ->
                listOf(
                    3 to 2 to 1, 4 to 2 to 1, 7 to 2 to 1, 8 to 2 to 1, 2 to 3 to 1, 3 to 3 to 1,
                    4 to 3 to 1, 5 to 3 to 1, 6 to 3 to 1, 7 to 3 to 1, 8 to 3 to 1, 9 to 3 to 1,
                    2 to 4 to 1, 3 to 4 to 1, 4 to 4 to 1, 5 to 4 to 1, 6 to 4 to 1, 7 to 4 to 1,
                    8 to 4 to 1, 9 to 4 to 1, 3 to 5 to 1, 4 to 5 to 1, 5 to 5 to 1, 6 to 5 to 1,
                    7 to 5 to 1, 8 to 5 to 1, 4 to 6 to 1, 5 to 6 to 1, 6 to 6 to 1, 7 to 6 to 1,
                    5 to 7 to 1, 6 to 7 to 1
                ).forEach { (xy, c) ->
                    val (x, y) = xy
                    put(x, y, c)
                }
            },
        ),
        Entry(
            "bow", "蝴蝶结", "装饰",
            cellsOf { put ->
                listOf(
                    2 to 4 to 6, 3 to 4 to 6, 4 to 4 to 6, 5 to 4 to 6, 7 to 4 to 6, 8 to 4 to 6,
                    9 to 4 to 6, 1 to 5 to 6, 2 to 5 to 6, 3 to 5 to 6, 4 to 5 to 6, 5 to 5 to 5,
                    6 to 5 to 6, 7 to 5 to 6, 8 to 5 to 6, 9 to 5 to 6, 10 to 5 to 6, 2 to 6 to 6,
                    3 to 6 to 6, 4 to 6 to 6, 5 to 6 to 6, 7 to 6 to 6, 8 to 6 to 6, 9 to 6 to 6
                ).forEach { (xy, c) ->
                    val (x, y) = xy
                    put(x, y, c)
                }
            }, nx = 0.0f, ny = -0.36f, scale = 0.26f,
        ),
        Entry(
            "leaf", "小叶", "装饰",
            cellsOf { put ->
                listOf(
                    6 to 1 to 4, 5 to 2 to 4, 6 to 2 to 4, 7 to 2 to 4, 4 to 3 to 4, 5 to 3 to 4,
                    6 to 3 to 4, 7 to 3 to 4, 3 to 4 to 4, 4 to 4 to 4, 5 to 4 to 4, 6 to 4 to 4,
                    4 to 5 to 4, 5 to 5 to 4, 6 to 5 to 4, 5 to 6 to 4, 6 to 6 to 4, 6 to 7 to 4,
                    7 to 8 to 4
                ).forEach { (xy, c) ->
                    val (x, y) = xy
                    put(x, y, c)
                }
            },
        ),
        Entry(
            "question", "问号", "表情",
            cellsOf { put ->
                listOf(
                    4 to 1 to 2, 5 to 1 to 2, 6 to 1 to 2, 7 to 1 to 2, 7 to 2 to 2, 6 to 3 to 2,
                    7 to 3 to 2, 5 to 4 to 2, 5 to 5 to 2, 5 to 7 to 2
                ).forEach { (xy, c) ->
                    val (x, y) = xy
                    put(x, y, c)
                }
            }, nx = 0.36f, ny = -0.42f, scale = 0.22f,
        ),
        Entry(
            "droplet", "无语", "表情",
            cellsOf { put ->
                listOf(
                    5 to 1 to 3, 4 to 2 to 3, 5 to 2 to 3, 6 to 2 to 3, 3 to 3 to 3, 4 to 3 to 3,
                    5 to 3 to 3, 6 to 3 to 3, 7 to 3 to 3, 3 to 4 to 3, 4 to 4 to 3, 5 to 4 to 3,
                    6 to 4 to 3, 7 to 4 to 3, 4 to 5 to 3, 5 to 5 to 3, 6 to 5 to 3, 5 to 6 to 3
                ).forEach { (xy, c) ->
                    val (x, y) = xy
                    put(x, y, c)
                }
            }, nx = -0.36f, ny = -0.42f, scale = 0.22f,
        ),
        Entry(
            "sweat", "流汗", "表情",
            cellsOf { put ->
                listOf(
                    6 to 1 to 10, 5 to 2 to 10, 6 to 2 to 10, 7 to 2 to 10, 4 to 3 to 10,
                    5 to 3 to 10, 6 to 3 to 10, 8 to 3 to 10, 5 to 4 to 10, 6 to 4 to 10,
                    8 to 4 to 10, 6 to 5 to 10, 7 to 6 to 10
                ).forEach { (xy, c) ->
                    val (x, y) = xy
                    put(x, y, c)
                }
            }, nx = 0.38f, ny = -0.4f, scale = 0.2f,
        ),
        Entry(
            "angry_mark", "生气", "表情",
            cellsOf { put ->
                listOf(
                    2 to 1 to 8, 5 to 1 to 8, 8 to 1 to 8, 5 to 2 to 8, 3 to 3 to 8, 4 to 3 to 8,
                    5 to 3 to 8, 6 to 3 to 8, 7 to 3 to 8, 5 to 4 to 8, 2 to 5 to 8, 5 to 5 to 8,
                    8 to 5 to 8
                ).forEach { (xy, c) ->
                    val (x, y) = xy
                    put(x, y, c)
                }
            }, nx = 0.36f, ny = -0.38f, scale = 0.22f,
        ),
        Entry(
            "sleep_z", "睡觉", "表情",
            cellsOf { put ->
                listOf(
                    3 to 2 to 9, 4 to 2 to 9, 5 to 2 to 9, 6 to 2 to 9, 6 to 3 to 9, 5 to 4 to 9,
                    4 to 5 to 9, 3 to 6 to 9, 4 to 6 to 9, 5 to 6 to 9, 6 to 6 to 9, 7 to 7 to 9,
                    8 to 7 to 9, 9 to 7 to 9, 9 to 8 to 9, 8 to 9 to 9, 7 to 10 to 9, 8 to 10 to 9,
                    9 to 10 to 9
                ).forEach { (xy, c) ->
                    val (x, y) = xy
                    put(x, y, c)
                }
            }, nx = 0.34f, ny = -0.44f, scale = 0.24f,
        ),
        Entry(
            "hat_winter", "冬帽", "帽子",
            cellsOf { put ->
                listOf(
                    5 to 1 to 1, 6 to 1 to 1, 5 to 2 to 5, 6 to 2 to 5, 3 to 3 to 8, 4 to 3 to 8,
                    5 to 3 to 8, 6 to 3 to 8, 7 to 3 to 8, 8 to 3 to 8, 3 to 4 to 8, 4 to 4 to 8,
                    5 to 4 to 8, 6 to 4 to 8, 7 to 4 to 8, 8 to 4 to 8, 3 to 5 to 8, 4 to 5 to 8,
                    5 to 5 to 8, 6 to 5 to 8, 7 to 5 to 8, 8 to 5 to 8, 2 to 6 to 12, 3 to 6 to 12,
                    4 to 6 to 12, 5 to 6 to 12, 6 to 6 to 12, 7 to 6 to 12, 8 to 6 to 12,
                    9 to 6 to 12, 2 to 7 to 12, 3 to 7 to 12, 4 to 7 to 12, 5 to 7 to 12,
                    6 to 7 to 12, 7 to 7 to 12, 8 to 7 to 12, 9 to 7 to 12
                ).forEach { (xy, c) ->
                    val (x, y) = xy
                    put(x, y, c)
                }
            }, nx = 0.0f, ny = -0.44f, scale = 0.34f,
        ),
        Entry(
            "hat_cap", "鸭舌帽", "帽子",
            cellsOf { put ->
                listOf(
                    3 to 3 to 16, 4 to 3 to 16, 5 to 3 to 16, 6 to 3 to 16, 7 to 3 to 16,
                    8 to 3 to 16, 3 to 4 to 16, 4 to 4 to 16, 5 to 4 to 13, 6 to 4 to 16,
                    7 to 4 to 16, 8 to 4 to 16, 2 to 5 to 16, 3 to 5 to 16, 4 to 5 to 16,
                    5 to 5 to 16, 6 to 5 to 16, 7 to 5 to 16, 8 to 5 to 16, 9 to 5 to 16,
                    2 to 6 to 16, 3 to 6 to 16, 4 to 6 to 16, 5 to 6 to 16, 6 to 6 to 16,
                    7 to 6 to 16, 8 to 6 to 16, 9 to 6 to 16, 10 to 6 to 16, 11 to 6 to 16,
                    7 to 7 to 16, 8 to 7 to 16, 9 to 7 to 16, 10 to 7 to 16, 11 to 7 to 16
                ).forEach { (xy, c) ->
                    val (x, y) = xy
                    put(x, y, c)
                }
            }, nx = 0.0f, ny = -0.42f, scale = 0.34f,
        ),
        Entry(
            "hat_sleep", "睡帽", "帽子",
            cellsOf { put ->
                listOf(
                    5 to 0 to 1, 5 to 1 to 6, 4 to 2 to 6, 5 to 2 to 6, 6 to 2 to 6, 3 to 3 to 6,
                    4 to 3 to 6, 5 to 3 to 6, 6 to 3 to 6, 7 to 3 to 6, 8 to 3 to 6, 3 to 4 to 6,
                    4 to 4 to 6, 5 to 4 to 6, 6 to 4 to 6, 7 to 4 to 6, 8 to 4 to 6, 3 to 5 to 6,
                    4 to 5 to 6, 5 to 5 to 6, 6 to 5 to 6, 7 to 5 to 6, 8 to 5 to 6, 3 to 6 to 6,
                    4 to 6 to 6, 5 to 6 to 6, 6 to 6 to 6, 7 to 6 to 6, 8 to 6 to 6
                ).forEach { (xy, c) ->
                    val (x, y) = xy
                    put(x, y, c)
                }
            }, nx = 0.0f, ny = -0.46f, scale = 0.32f,
        ),
        Entry(
            "beanie", "针织帽", "帽子",
            cellsOf { put ->
                put(5, 0, 1)
                put(6, 0, 1)
                for (x in 3 until 9) {
                    put(x, 1, 6)
                    put(x, 2, 6)
                    put(x, 3, 6)
                }
                for (x in 2 until 10) {
                    put(x, 4, 5)
                }
            }, nx = 0.0f, ny = -0.48f, scale = 0.30f,
        ),
        Entry(
            "beret", "贝雷", "帽子",
            cellsOf { put ->
                for (x in 2 until 10) put(x, 2, 8)
                for (x in 1 until 10) put(x, 3, 8)
                for (x in 3 until 9) put(x, 4, 7)
                put(1, 4, 7)
            }, nx = -0.04f, ny = -0.46f, scale = 0.28f,
        ),
        Entry(
            "glasses_thick", "粗框眼镜", "眼镜",
            cellsOf { put ->
                listOf(
                    1 to 4 to 7, 2 to 4 to 7, 3 to 4 to 7, 4 to 4 to 7, 7 to 4 to 7, 8 to 4 to 7,
                    9 to 4 to 7, 10 to 4 to 7, 1 to 5 to 7, 2 to 5 to 10, 3 to 5 to 10,
                    4 to 5 to 7, 5 to 5 to 7, 6 to 5 to 7, 7 to 5 to 7, 8 to 5 to 10, 9 to 5 to 10,
                    10 to 5 to 7, 1 to 6 to 7, 2 to 6 to 10, 3 to 6 to 10, 4 to 6 to 7,
                    7 to 6 to 7, 8 to 6 to 10, 9 to 6 to 10, 10 to 6 to 7, 1 to 7 to 7,
                    2 to 7 to 7, 3 to 7 to 7, 4 to 7 to 7, 7 to 7 to 7, 8 to 7 to 7, 9 to 7 to 7,
                    10 to 7 to 7
                ).forEach { (xy, c) ->
                    val (x, y) = xy
                    put(x, y, c)
                }
            }, nx = 0.0f, ny = -0.16f, scale = 0.3f,
        ),
        Entry(
            "glasses_thin", "细框眼镜", "眼镜",
            cellsOf { put ->
                listOf(
                    2 to 4 to 7, 3 to 4 to 7, 4 to 4 to 7, 7 to 4 to 7, 8 to 4 to 7, 9 to 4 to 7,
                    2 to 5 to 7, 4 to 5 to 7, 5 to 5 to 7, 6 to 5 to 7, 7 to 5 to 7, 9 to 5 to 7,
                    2 to 6 to 7, 4 to 6 to 7, 7 to 6 to 7, 9 to 6 to 7, 2 to 7 to 7, 3 to 7 to 7,
                    4 to 7 to 7, 7 to 7 to 7, 8 to 7 to 7, 9 to 7 to 7
                ).forEach { (xy, c) ->
                    val (x, y) = xy
                    put(x, y, c)
                }
            }, nx = 0.0f, ny = -0.16f, scale = 0.28f,
        ),
        Entry(
            "glasses_gold", "金丝边", "眼镜",
            cellsOf { put ->
                listOf(
                    2 to 4 to 13, 3 to 4 to 13, 4 to 4 to 13, 7 to 4 to 13, 8 to 4 to 13,
                    9 to 4 to 13, 2 to 5 to 13, 4 to 5 to 13, 5 to 5 to 13, 6 to 5 to 13,
                    7 to 5 to 13, 9 to 5 to 13, 2 to 6 to 13, 4 to 6 to 13, 7 to 6 to 13,
                    9 to 6 to 13, 2 to 7 to 13, 3 to 7 to 13, 4 to 7 to 13, 7 to 7 to 13,
                    8 to 7 to 13, 9 to 7 to 13
                ).forEach { (xy, c) ->
                    val (x, y) = xy
                    put(x, y, c)
                }
            }, nx = 0.0f, ny = -0.16f, scale = 0.28f,
        ),
        Entry(
            "thin_round", "细圆框", "眼镜",
            cellsOf { put ->
                listOf(
                    2 to 4, 3 to 4, 1 to 5, 4 to 5, 1 to 6, 4 to 6, 2 to 7, 3 to 7,
                    7 to 4, 8 to 4, 6 to 5, 9 to 5, 6 to 6, 9 to 6, 7 to 7, 8 to 7,
                ).forEach { (x, y) -> put(x, y, 13) }
                put(5, 5, 13)
                put(5, 6, 13)
            }, nx = 0.0f, ny = -0.22f, scale = 0.26f,
        ),
        Entry(
            "thin_oval", "细椭圆", "眼镜",
            cellsOf { put ->
                listOf(
                    1 to 5, 2 to 4, 3 to 4, 4 to 5, 4 to 6, 3 to 7, 2 to 7, 1 to 6,
                    7 to 5, 8 to 4, 9 to 4, 10 to 5, 10 to 6, 9 to 7, 8 to 7, 7 to 6,
                ).forEach { (x, y) -> put(x, y, 13) }
                put(5, 5, 13)
                put(6, 5, 13)
            }, nx = 0.0f, ny = -0.22f, scale = 0.26f,
        ),
        Entry(
            "half_rim", "半框", "眼镜",
            cellsOf { put ->
                for (x in 1 until 5) put(x, 4, 13)
                for (x in 7 until 11) put(x, 4, 13)
                put(1, 5, 13)
                put(4, 5, 13)
                put(7, 5, 13)
                put(10, 5, 13)
                put(5, 4, 13)
                put(6, 4, 13)
            }, nx = 0.0f, ny = -0.22f, scale = 0.26f,
        ),
        Entry(
            "glasses_square", "方框眼镜", "眼镜",
            cellsOf { put ->
                listOf(
                    1 to 4 to 7, 2 to 4 to 7, 3 to 4 to 7, 4 to 4 to 7, 7 to 4 to 7, 8 to 4 to 7,
                    9 to 4 to 7, 10 to 4 to 7, 1 to 5 to 7, 2 to 5 to 3, 3 to 5 to 3, 4 to 5 to 7,
                    5 to 5 to 7, 6 to 5 to 7, 7 to 5 to 7, 8 to 5 to 3, 9 to 5 to 3, 10 to 5 to 7,
                    1 to 6 to 7, 2 to 6 to 3, 3 to 6 to 3, 4 to 6 to 7, 7 to 6 to 7, 8 to 6 to 3,
                    9 to 6 to 3, 10 to 6 to 7, 1 to 7 to 7, 2 to 7 to 7, 3 to 7 to 7, 4 to 7 to 7,
                    7 to 7 to 7, 8 to 7 to 7, 9 to 7 to 7, 10 to 7 to 7
                ).forEach { (xy, c) ->
                    val (x, y) = xy
                    put(x, y, c)
                }
            }, nx = 0.0f, ny = -0.16f, scale = 0.3f,
        ),
        Entry(
            "glasses_round", "圆框眼镜", "眼镜",
            cellsOf { put ->
                listOf(
                    2 to 4 to 7, 3 to 4 to 7, 4 to 4 to 7, 7 to 4 to 7, 8 to 4 to 7, 9 to 4 to 7,
                    1 to 5 to 7, 3 to 5 to 10, 5 to 5 to 7, 6 to 5 to 7, 8 to 5 to 10,
                    10 to 5 to 7, 1 to 6 to 7, 3 to 6 to 10, 5 to 6 to 7, 6 to 6 to 7,
                    8 to 6 to 10, 10 to 6 to 7, 2 to 7 to 7, 3 to 7 to 7, 4 to 7 to 7, 7 to 7 to 7,
                    8 to 7 to 7, 9 to 7 to 7
                ).forEach { (xy, c) ->
                    val (x, y) = xy
                    put(x, y, c)
                }
            }, nx = 0.0f, ny = -0.16f, scale = 0.3f,
        ),
        Entry(
            "glasses_odd", "异形眼镜", "眼镜",
            cellsOf { put ->
                listOf(
                    1 to 4 to 7, 2 to 4 to 7, 3 to 4 to 7, 4 to 4 to 7, 7 to 4 to 7, 8 to 4 to 7,
                    9 to 4 to 7, 1 to 5 to 7, 2 to 5 to 15, 3 to 5 to 15, 4 to 5 to 7, 5 to 5 to 7,
                    6 to 5 to 7, 8 to 5 to 15, 10 to 5 to 7, 1 to 6 to 7, 2 to 6 to 15,
                    3 to 6 to 15, 4 to 6 to 7, 6 to 6 to 7, 8 to 6 to 15, 10 to 6 to 7,
                    1 to 7 to 7, 2 to 7 to 7, 3 to 7 to 7, 4 to 7 to 7, 7 to 7 to 7, 8 to 7 to 7,
                    9 to 7 to 7
                ).forEach { (xy, c) ->
                    val (x, y) = xy
                    put(x, y, c)
                }
            }, nx = 0.0f, ny = -0.16f, scale = 0.3f,
        ),
        Entry(
            "sunglasses", "墨镜", "眼镜",
            cellsOf { put ->
                listOf(
                    1 to 4 to 14, 2 to 4 to 14, 3 to 4 to 14, 4 to 4 to 14, 7 to 4 to 14,
                    8 to 4 to 14, 9 to 4 to 14, 10 to 4 to 14, 1 to 5 to 14, 2 to 5 to 7,
                    3 to 5 to 14, 4 to 5 to 14, 5 to 5 to 14, 6 to 5 to 14, 7 to 5 to 14,
                    8 to 5 to 7, 9 to 5 to 14, 10 to 5 to 14, 1 to 6 to 14, 2 to 6 to 14,
                    3 to 6 to 14, 4 to 6 to 14, 7 to 6 to 14, 8 to 6 to 14, 9 to 6 to 14,
                    10 to 6 to 14, 1 to 7 to 14, 2 to 7 to 14, 3 to 7 to 14, 4 to 7 to 14,
                    7 to 7 to 14, 8 to 7 to 14, 9 to 7 to 14, 10 to 7 to 14
                ).forEach { (xy, c) ->
                    val (x, y) = xy
                    put(x, y, c)
                }
            }, nx = 0.0f, ny = -0.16f, scale = 0.3f,
        ),
        Entry(
            "glasses_funny", "搞怪眼镜", "眼镜",
            cellsOf { put ->
                listOf(
                    0 to 3 to 8, 1 to 3 to 8, 2 to 3 to 8, 3 to 3 to 8, 4 to 3 to 8, 0 to 4 to 8,
                    1 to 4 to 2, 2 to 4 to 2, 3 to 4 to 2, 4 to 4 to 8, 0 to 5 to 8, 1 to 5 to 2,
                    2 to 5 to 2, 3 to 5 to 2, 4 to 5 to 8, 7 to 5 to 6, 8 to 5 to 6, 9 to 5 to 6,
                    10 to 5 to 6, 0 to 6 to 8, 1 to 6 to 2, 2 to 6 to 2, 3 to 6 to 2, 4 to 6 to 8,
                    5 to 6 to 7, 6 to 6 to 7, 7 to 6 to 6, 8 to 6 to 5, 9 to 6 to 5, 10 to 6 to 6,
                    0 to 7 to 8, 1 to 7 to 2, 2 to 7 to 2, 3 to 7 to 2, 4 to 7 to 8, 7 to 7 to 6,
                    8 to 7 to 5, 9 to 7 to 5, 10 to 7 to 6, 0 to 8 to 8, 1 to 8 to 8, 2 to 8 to 8,
                    3 to 8 to 8, 4 to 8 to 8, 7 to 8 to 6, 8 to 8 to 6, 9 to 8 to 6, 10 to 8 to 6
                ).forEach { (xy, c) ->
                    val (x, y) = xy
                    put(x, y, c)
                }
            }, nx = 0.0f, ny = -0.14f, scale = 0.32f,
        ),
        Entry(
            "scarf", "围巾", "颈饰",
            cellsOf { put ->
                listOf(
                    2 to 7 to 17, 3 to 7 to 17, 4 to 7 to 17, 5 to 7 to 17, 6 to 7 to 17,
                    7 to 7 to 17, 8 to 7 to 17, 9 to 7 to 17, 2 to 8 to 17, 3 to 8 to 17,
                    4 to 8 to 17, 5 to 8 to 17, 6 to 8 to 17, 7 to 8 to 17, 8 to 8 to 17,
                    9 to 8 to 17, 7 to 9 to 17, 8 to 9 to 1, 9 to 9 to 17, 7 to 10 to 17,
                    8 to 10 to 17, 9 to 10 to 17, 7 to 11 to 17, 8 to 11 to 1, 9 to 11 to 17
                ).forEach { (xy, c) ->
                    val (x, y) = xy
                    put(x, y, c)
                }
            }, nx = 0.0f, ny = 0.08f, scale = 0.32f,
        ),
        Entry(
            "silk_scarf", "丝巾", "颈饰",
            cellsOf { put ->
                listOf(
                    2 to 5 to 6, 9 to 5 to 6, 1 to 6 to 6, 2 to 6 to 6, 3 to 6 to 6, 4 to 6 to 6,
                    5 to 6 to 6, 6 to 6 to 6, 7 to 6 to 6, 8 to 6 to 6, 9 to 6 to 6, 10 to 6 to 6,
                    1 to 7 to 6, 2 to 7 to 6, 3 to 7 to 6, 4 to 7 to 5, 5 to 7 to 1, 6 to 7 to 5,
                    7 to 7 to 6, 8 to 7 to 6, 9 to 7 to 6, 10 to 7 to 6, 3 to 8 to 6, 8 to 8 to 6
                ).forEach { (xy, c) ->
                    val (x, y) = xy
                    put(x, y, c)
                }
            }, nx = 0.0f, ny = 0.02f, scale = 0.3f,
        ),
        Entry(
            "necklace", "项链", "颈饰",
            cellsOf { put ->
                listOf(
                    2 to 6 to 13, 9 to 6 to 13, 3 to 7 to 13, 4 to 7 to 13, 5 to 7 to 13,
                    6 to 7 to 13, 7 to 7 to 13, 8 to 7 to 13, 5 to 8 to 1, 6 to 8 to 1, 5 to 9 to 8
                ).forEach { (xy, c) ->
                    val (x, y) = xy
                    put(x, y, c)
                }
            }, nx = 0.0f, ny = 0.06f, scale = 0.26f,
        ),
        Entry(
            "bag", "包包", "包袋",
            cellsOf { put ->
                listOf(
                    4 to 3 to 7, 5 to 3 to 7, 6 to 3 to 7, 7 to 3 to 7, 3 to 4 to 11, 4 to 4 to 11,
                    5 to 4 to 11, 6 to 4 to 11, 7 to 4 to 11, 8 to 4 to 11, 3 to 5 to 11,
                    4 to 5 to 11, 5 to 5 to 11, 6 to 5 to 11, 7 to 5 to 11, 8 to 5 to 11,
                    3 to 6 to 11, 4 to 6 to 11, 5 to 6 to 13, 6 to 6 to 13, 7 to 6 to 11,
                    8 to 6 to 11, 3 to 7 to 11, 4 to 7 to 11, 5 to 7 to 11, 6 to 7 to 11,
                    7 to 7 to 11, 8 to 7 to 11, 3 to 8 to 11, 4 to 8 to 11, 5 to 8 to 11,
                    6 to 8 to 11, 7 to 8 to 11, 8 to 8 to 11, 3 to 9 to 11, 4 to 9 to 11,
                    5 to 9 to 11, 6 to 9 to 11, 7 to 9 to 11, 8 to 9 to 11
                ).forEach { (xy, c) ->
                    val (x, y) = xy
                    put(x, y, c)
                }
            }, nx = 0.36f, ny = 0.12f, scale = 0.28f,
        ),
        Entry(
            "handbag", "手袋", "包袋",
            cellsOf { put ->
                listOf(
                    4 to 3 to 7, 5 to 3 to 7, 6 to 3 to 7, 7 to 3 to 7, 3 to 4 to 7, 8 to 4 to 7,
                    2 to 5 to 17, 3 to 5 to 17, 4 to 5 to 17, 5 to 5 to 17, 6 to 5 to 17,
                    7 to 5 to 17, 8 to 5 to 17, 9 to 5 to 17, 2 to 6 to 17, 3 to 6 to 17,
                    4 to 6 to 17, 5 to 6 to 17, 6 to 6 to 17, 7 to 6 to 17, 8 to 6 to 17,
                    9 to 6 to 17, 2 to 7 to 17, 3 to 7 to 17, 4 to 7 to 17, 5 to 7 to 13,
                    6 to 7 to 17, 7 to 7 to 17, 8 to 7 to 17, 9 to 7 to 17, 2 to 8 to 17,
                    3 to 8 to 17, 4 to 8 to 17, 5 to 8 to 17, 6 to 8 to 17, 7 to 8 to 17,
                    8 to 8 to 17, 9 to 8 to 17, 2 to 9 to 17, 3 to 9 to 17, 4 to 9 to 17,
                    5 to 9 to 17, 6 to 9 to 17, 7 to 9 to 17, 8 to 9 to 17, 9 to 9 to 17
                ).forEach { (xy, c) ->
                    val (x, y) = xy
                    put(x, y, c)
                }
            }, nx = 0.34f, ny = 0.1f, scale = 0.28f,
        ),
        Entry(
            "ita_bag", "痛包", "包袋",
            cellsOf { put ->
                listOf(
                    3 to 2 to 7, 8 to 2 to 7, 2 to 3 to 16, 3 to 3 to 16, 4 to 3 to 16,
                    5 to 3 to 16, 6 to 3 to 16, 7 to 3 to 16, 8 to 3 to 16, 9 to 3 to 16,
                    2 to 4 to 16, 3 to 4 to 16, 4 to 4 to 16, 5 to 4 to 16, 6 to 4 to 16,
                    7 to 4 to 16, 8 to 4 to 16, 9 to 4 to 16, 2 to 5 to 16, 3 to 5 to 16,
                    4 to 5 to 1, 5 to 5 to 2, 6 to 5 to 6, 7 to 5 to 16, 8 to 5 to 16,
                    9 to 5 to 16, 2 to 6 to 16, 3 to 6 to 16, 4 to 6 to 16, 5 to 6 to 16,
                    6 to 6 to 16, 7 to 6 to 16, 8 to 6 to 16, 9 to 6 to 16, 2 to 7 to 16,
                    3 to 7 to 16, 4 to 7 to 3, 5 to 7 to 16, 6 to 7 to 8, 7 to 7 to 16,
                    8 to 7 to 16, 9 to 7 to 16, 2 to 8 to 16, 3 to 8 to 16, 4 to 8 to 16,
                    5 to 8 to 5, 6 to 8 to 16, 7 to 8 to 16, 8 to 8 to 16, 9 to 8 to 16,
                    2 to 9 to 16, 3 to 9 to 16, 4 to 9 to 16, 5 to 9 to 16, 6 to 9 to 16,
                    7 to 9 to 16, 8 to 9 to 16, 9 to 9 to 16, 2 to 10 to 16, 3 to 10 to 16,
                    4 to 10 to 16, 5 to 10 to 16, 6 to 10 to 16, 7 to 10 to 16, 8 to 10 to 16,
                    9 to 10 to 16
                ).forEach { (xy, c) ->
                    val (x, y) = xy
                    put(x, y, c)
                }
            }, nx = 0.36f, ny = 0.08f, scale = 0.32f,
        ),
        Entry(
            "bouquet", "花束", "手持",
            cellsOf { put ->
                listOf(
                    5 to 2 to 1, 4 to 3 to 8, 5 to 3 to 1, 6 to 3 to 6, 3 to 4 to 4, 4 to 4 to 1,
                    5 to 4 to 8, 6 to 4 to 4, 7 to 4 to 6, 5 to 5 to 4, 5 to 6 to 11, 5 to 7 to 11,
                    4 to 8 to 12, 5 to 8 to 12, 6 to 8 to 12
                ).forEach { (xy, c) ->
                    val (x, y) = xy
                    put(x, y, c)
                }
            }, nx = 0.34f, ny = 0.18f, scale = 0.3f,
        ),
        Entry(
            "doll", "玩偶", "手持",
            cellsOf { put ->
                listOf(
                    4 to 1 to 12, 5 to 1 to 12, 6 to 1 to 12, 7 to 1 to 12, 4 to 2 to 12,
                    5 to 2 to 7, 6 to 2 to 7, 7 to 2 to 12, 4 to 3 to 12, 5 to 3 to 12,
                    6 to 3 to 12, 7 to 3 to 12, 4 to 4 to 1, 5 to 4 to 1, 6 to 4 to 1, 7 to 4 to 1,
                    3 to 5 to 12, 4 to 5 to 1, 5 to 5 to 1, 6 to 5 to 1, 7 to 5 to 1, 8 to 5 to 12,
                    4 to 6 to 1, 5 to 6 to 1, 6 to 6 to 1, 7 to 6 to 1, 4 to 7 to 1, 5 to 7 to 1,
                    6 to 7 to 1, 7 to 7 to 1, 5 to 8 to 11, 6 to 8 to 11
                ).forEach { (xy, c) ->
                    val (x, y) = xy
                    put(x, y, c)
                }
            }, nx = -0.34f, ny = 0.16f, scale = 0.28f,
        ),
        Entry(
            "cheer_fan", "应援扇", "手持",
            cellsOf { put ->
                listOf(
                    2 to 2 to 1, 3 to 2 to 1, 4 to 2 to 1, 5 to 2 to 1, 6 to 2 to 1, 7 to 2 to 1,
                    8 to 2 to 1, 9 to 2 to 1, 2 to 3 to 1, 3 to 3 to 5, 4 to 3 to 5, 5 to 3 to 8,
                    6 to 3 to 5, 7 to 3 to 5, 8 to 3 to 1, 9 to 3 to 1, 2 to 4 to 1, 3 to 4 to 1,
                    4 to 4 to 1, 5 to 4 to 5, 6 to 4 to 1, 7 to 4 to 1, 8 to 4 to 1, 9 to 4 to 1,
                    2 to 5 to 1, 3 to 5 to 1, 4 to 5 to 1, 5 to 5 to 1, 6 to 5 to 1, 7 to 5 to 1,
                    8 to 5 to 1, 9 to 5 to 1, 2 to 6 to 1, 3 to 6 to 1, 4 to 6 to 1, 5 to 6 to 1,
                    6 to 6 to 1, 7 to 6 to 1, 8 to 6 to 1, 9 to 6 to 1, 5 to 7 to 11, 5 to 8 to 11,
                    5 to 9 to 11
                ).forEach { (xy, c) ->
                    val (x, y) = xy
                    put(x, y, c)
                }
            }, nx = 0.38f, ny = 0.05f, scale = 0.3f,
        ),
        Entry(
            "cheer_stick", "应援棒", "手持",
            cellsOf { put ->
                listOf(
                    5 to 1 to 2, 4 to 2 to 2, 5 to 2 to 5, 6 to 2 to 2, 5 to 3 to 1, 5 to 4 to 1,
                    5 to 5 to 18, 5 to 6 to 18, 5 to 7 to 18, 5 to 8 to 18, 4 to 9 to 7,
                    5 to 9 to 7, 6 to 9 to 7
                ).forEach { (xy, c) ->
                    val (x, y) = xy
                    put(x, y, c)
                }
            }, nx = 0.4f, ny = 0.02f, scale = 0.3f,
        ),
    )
}
