export const translations = {
  en: {
    splashTitle: "Luna 2025\nMerry Christmas",
    enterSystem: "ENTER SYSTEM",
    windowTitle: "Todo List - Christmas Edition",
    newTaskPlaceholder: "New Task...",
    descriptionPlaceholder: "Description (optional)...",
    addTask: "Add Task",
    items: "items",
    refresh: "Refresh",
    loading: "Loading...",
    noTasks: "No tasks found.",
    footer: "Luna 2025 © Christmas Special",
    confirmDelete: "Are you sure you want to delete this task?",
    createError: "Failed to create task",
    toggleLang: "中文",
  },
  zh: {
    splashTitle: "Luna 2025\n圣诞节快乐",
    enterSystem: "进入系统",
    windowTitle: "任务列表 - 圣诞特辑",
    newTaskPlaceholder: "新任务...",
    descriptionPlaceholder: "描述 (可选)...",
    addTask: "添加任务",
    items: "个任务",
    refresh: "刷新",
    loading: "加载中...",
    noTasks: "暂无任务。",
    footer: "Luna 2025 © 圣诞特辑",
    confirmDelete: "确定要删除这个任务吗？",
    createError: "创建任务失败",
    toggleLang: "English",
  }
};

export type Language = 'en' | 'zh';
export type TranslationKey = keyof typeof translations.en;
