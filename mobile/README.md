# 智糖小助手 - 移动端

基于 uni-app + Vue 3 的糖尿病管理移动应用

## 项目结构

```
src/
├── api/              # API接口管理
│   └── index.js      # 统一的API接口定义
├── store/            # Pinia状态管理
│   ├── user.js       # 用户状态
│   └── chat.js       # 聊天状态
├── utils/            # 工具函数
│   └── request.js    # HTTP请求封装
├── pages/            # 页面
│   ├── login/        # 登录页
│   ├── chat/         # 对话页
│   ├── profile/      # 个人中心
│   └── checkin/      # 打卡页
├── static/           # 静态资源
├── App.vue           # 应用入口
├── main.js           # 主入口文件
├── pages.json        # 页面配置
└── manifest.json     # 应用配置
```

## 功能模块

### 1. 用户认证
- ✅ 登录功能
- ✅ 自动保持登录状态
- ✅ 退出登录

### 2. 智能对话
- ✅ 实时对话功能
- ✅ 消息历史记录
- ✅ TTS语音播报开关
- ✅ 会话管理
- 🚧 语音输入（开发中）

### 3. 健康打卡
- ✅ 每日打卡
- ✅ 控糖状态记录
- ✅ 打卡历史查看
- ✅ 心情感受记录

### 4. 个人中心
- ✅ 个人信息管理
- ✅ 昵称修改
- ✅ 生日设置
- ✅ 打卡记录入口

## 技术栈

- **框架**: uni-app (Vue 3 + Composition API)
- **状态管理**: Pinia
- **UI**: 原生组件 + 自定义样式
- **HTTP**: uni.request 封装
- **构建工具**: Vite

## 开发指南

### 安装依赖

```bash
cd AI-For-Diabetes/mobile
npm install
```

### 运行项目

```bash
# H5
npm run dev:h5

# 微信小程序
npm run dev:mp-weixin

# App
npm run dev:app
```

### 构建项目

```bash
# H5
npm run build:h5

# 微信小程序
npm run build:mp-weixin

# App
npm run build:app
```

## API配置

API基础地址配置在 `src/utils/request.js`:

```javascript
const BASE_URL = 'https://chat.cmkjai.com/api'
```

## 接口说明

### 用户接口
- `POST /api/login` - 用户登录
- `GET /api/user/profile` - 获取用户信息

### 对话接口
- `GET /api/chat/sessions/latest` - 获取最新会话
- `POST /api/chat/stream_with_tts` - 发送消息
- `POST /api/chat/speech_to_text` - 语音转文字

### 打卡接口
- `POST /api/checkin` - 提交打卡
- `GET /api/checkin/records` - 获取打卡记录

### TTS接口
- `POST /api/tts/stream` - 文字转语音

## 注意事项

1. **跨域问题**: 开发环境需要配置代理或后端开启CORS
2. **Token管理**: Token存储在本地storage，自动添加到请求头
3. **登录状态**: 未登录自动跳转到登录页
4. **平台适配**: 支持H5、小程序、App多端运行

## 待开发功能

- [ ] 语音输入功能
- [ ] 消息流式输出
- [ ] 图片上传
- [ ] 数据可视化
- [ ] 离线消息缓存
- [ ] 推送通知

## 开发规范

### 代码风格
- 使用 Composition API
- 组件使用 `<script setup>` 语法
- 样式使用 scoped
- 使用 rpx 作为尺寸单位

### 命名规范
- 文件名: 小写 + 连字符 (kebab-case)
- 组件名: 大驼峰 (PascalCase)
- 变量/函数: 小驼峰 (camelCase)
- 常量: 大写 + 下划线 (UPPER_CASE)

### Git提交规范
- feat: 新功能
- fix: 修复bug
- docs: 文档更新
- style: 代码格式调整
- refactor: 重构
- test: 测试相关
- chore: 构建/工具相关

## 许可证

MIT License
