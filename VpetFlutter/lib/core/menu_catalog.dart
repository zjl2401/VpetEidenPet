/// Desktop-aligned four root menus + leaf actions (from DesktopMenuCatalog / FEATURES).
class MenuNode {
  final String id;
  final String title;
  final List<MenuNode> children;
  final String? action; // leaf action key
  const MenuNode(this.id, this.title, {this.children = const [], this.action});
  bool get isLeaf => children.isEmpty;
}

const rootMenus = <MenuNode>[
  MenuNode('interact', '互动', children: [
    MenuNode('actions', '动作', children: [
      MenuNode('a_eat', '吃东西', action: 'action:eat'),
      MenuNode('a_hi', '打招呼', action: 'action:hi'),
      MenuNode('a_call', '打电话', action: 'action:call'),
      MenuNode('a_adult', '（成人向）', action: 'action:adult'),
      MenuNode('a_squat', '蹲下', action: 'action:squat'),
      MenuNode('a_kick', '侧踢', action: 'action:kick'),
      MenuNode('a_yes', '是', action: 'action:yes'),
      MenuNode('a_no', '否', action: 'action:no'),
      MenuNode('a_judge', '判断', action: 'action:judge'),
      MenuNode('a_walk', '走动', action: 'action:walk'),
      MenuNode('a_stand', '站立', action: 'action:stand'),
      MenuNode('a_sleep', '睡眠', action: 'action:sleep'),
      MenuNode('a_work', '工作', action: 'action:work'),
    ]),
    MenuNode('expr', '表情', children: [
      MenuNode('e_happy', '开心', action: 'expr:happy'),
      MenuNode('e_angry', '生气', action: 'expr:angry'),
      MenuNode('e_q', '疑问', action: 'expr:question'),
      MenuNode('e_sad', '难过', action: 'expr:sad'),
      MenuNode('e_shy', '害羞', action: 'expr:shy'),
      MenuNode('e_wink', '眨眼', action: 'expr:wink'),
      MenuNode('e_like', '点赞', action: 'expr:like'),
      MenuNode('e_bixin', '比心', action: 'expr:bixin'),
      MenuNode('e_idea', '想法', action: 'expr:idea'),
      MenuNode('e_speechless', '无语', action: 'expr:speechless'),
      MenuNode('e_awkward', '尴尬', action: 'expr:awkward'),
    ]),
    MenuNode('dialog', '预设对话', children: [
      MenuNode('d1', '今天怎么样？', action: 'dialog:today'),
      MenuNode('d2', '想听故事吗？', action: 'dialog:story'),
      MenuNode('d3', '累不累？', action: 'dialog:tired'),
    ]),
    MenuNode('feed', '喂食', action: 'nav:feed'),
    MenuNode('companion', '使魔', children: [
      MenuNode('c_aster', '艾斯特', action: 'companion:aster'),
      MenuNode('c_morvay', '墨菲', action: 'companion:morvay'),
    ]),
    MenuNode('outfit', '装扮', action: 'nav:outfit'),
    MenuNode('work', '工作运送', action: 'mode:work'),
  ]),
  MenuNode('tools', '工具', children: [
    MenuNode('t_sw', '秒表', action: 'nav:stopwatch'),
    MenuNode('t_timer', '计时器', action: 'nav:timer'),
    MenuNode('t_pomo', '番茄钟', action: 'nav:pomo'),
    MenuNode('t_sched', '日程', action: 'nav:schedule'),
    MenuNode('t_weather', '天气', action: 'tool:weather'),
    MenuNode('t_bday', '生日', action: 'nav:birthday'),
    MenuNode('t_clock', '时间显示', action: 'nav:clock'),
  ]),
  MenuNode('games', '娱乐', children: [
    MenuNode('g_collect', '采集', action: 'nav:collect'),
    MenuNode('g_rhythm', '音游', action: 'nav:rhythm'),
    MenuNode('g_expose', '暴露', action: 'nav:expose'),
    MenuNode('g_lime', '莱姆', action: 'nav:lime'),
    MenuNode('g_type', '打字', action: 'nav:typing'),
    MenuNode('g_vocab', '背单词', action: 'nav:vocab'),
    MenuNode('g_rpg', 'RPG', action: 'nav:rpg'),
    MenuNode('g_music', '音乐漫步', action: 'mode:music'),
    MenuNode('g_home', '家园', action: 'nav:home'),
  ]),
  MenuNode('system', '系统', children: [
    MenuNode('s_owner', '所属人', action: 'nav:owner'),
    MenuNode('s_size', '大小', action: 'nav:size'),
    MenuNode('s_mode', '模式', children: [
      MenuNode('m_free', '自由', action: 'mode:free'),
      MenuNode('m_stroll', '漫步', action: 'mode:stroll'),
      MenuNode('m_follow', '跟随', action: 'mode:follow'),
      MenuNode('m_sleep', '睡眠', action: 'mode:sleep'),
    ]),
    MenuNode('s_speech', '气泡开关', action: 'toggle:speech'),
    MenuNode('s_vol', '音量', action: 'nav:volume'),
    MenuNode('s_diff', '难度', action: 'nav:difficulty'),
    MenuNode('s_diary', '日记', action: 'nav:diary'),
    MenuNode('s_ach', '成就', action: 'nav:achievements'),
    MenuNode('s_gal', '画廊', action: 'nav:gallery'),
    MenuNode('s_phono', '留声机', action: 'nav:phonograph'),
    MenuNode('s_community', '社区说明', action: 'nav:community'),
    MenuNode('s_meet', '相遇', action: 'meet:now'),
    MenuNode('s_reset', '重置存档', action: 'nav:reset'),
    MenuNode('s_exit', '退出悬浮', action: 'sys:exit_overlay'),
  ]),
];
