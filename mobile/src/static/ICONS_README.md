# TabBar 图标说明

## 需要的图标文件

请在 `static` 目录下放置以下图标文件（尺寸：81x81px）：

### 对话页图标
- `tab-chat.png` - 未选中状态（灰色）
- `tab-chat-active.png` - 选中状态（紫色 #5147FF）

### 打卡页图标
- `tab-checkin.png` - 未选中状态（灰色）
- `tab-checkin-active.png` - 选中状态（紫色 #5147FF）

### 个人中心图标
- `tab-profile.png` - 未选中状态（灰色）
- `tab-profile-active.png` - 选中状态（紫色 #5147FF）

## 图标设计建议

### 对话图标
- 可以使用对话气泡、聊天框等图标
- 建议使用 Font Awesome 的 `fa-comments` 或 `fa-message`

### 打卡图标
- 可以使用日历、打勾等图标
- 建议使用 Font Awesome 的 `fa-calendar-check` 或 `fa-check-circle`

### 个人中心图标
- 可以使用用户头像、个人等图标
- 建议使用 Font Awesome 的 `fa-user` 或 `fa-user-circle`

## 临时方案

如果暂时没有图标，可以：
1. 使用纯色方块作为占位
2. 或者使用 iconfont 图标
3. 或者暂时注释掉 tabBar 配置，使用普通导航
