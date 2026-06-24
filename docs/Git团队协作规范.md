# HR制度智能问答系统 — Git 团队协作规范

> **适用团队**：课程设计小组（2-5人）  
> **分支模型**：简化版 GitHub Flow + develop  
> **远程仓库**：https://gitee.com/pure-dhmo/hr.git

---

## 一、仓库结构

```
https://gitee.com/pure-dhmo/hr.git
├── main          ← 生产就绪分支（只合并，不直接提交）
└── develop       ← 日常开发主线
    ├── feature/xxx    ← 功能开发（从 develop 切出，合并回 develop）
    ├── hotfix/xxx     ← 紧急修复（从 main 切出，合并回 main + develop）
    └── release/xxx    ← 版本发布准备（从 develop 切出，合并到 main + develop）
```

## 二、分支命名规范

| 分支类型 | 命名格式 | 示例 |
|---------|---------|------|
| 主分支 | `main` | 生产环境代码 |
| 开发分支 | `develop` | 日常开发主线 |
| 功能分支 | `feature/<模块>-<简述>` | `feature/qa-engine`, `feature/user-login` |
| 修复分支 | `hotfix/<简述>` | `hotfix/login-error` |
| 发布分支 | `release/v<版本号>` | `release/v1.0.0` |

## 三、Commit Message 规范

采用 **Conventional Commits** 格式：

```
<type>(<scope>): <subject>

<body>
```

### type 类型

| type | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat(qa): 添加智能问答引擎` |
| `fix` | Bug修复 | `fix(api): 修复回答匹配空指针` |
| `docs` | 文档更新 | `docs: 更新API接口文档` |
| `style` | 代码格式 | `style: 统一缩进为4空格` |
| `refactor` | 重构 | `refactor(db): 优化查询语句` |
| `test` | 测试 | `test(qa): 添加问答引擎单元测试` |
| `chore` | 构建/工具 | `chore: 更新.gitignore规则` |

### scope 可选范围

- `qa` — 问答引擎
- `api` — 接口服务
- `ui` — 前端界面
- `db` — 数据库
- `auth` — 认证授权
- `deploy` — 部署相关

## 四、日常开发 SOP

### 4.1 首次克隆项目（新成员）

```bash
# 1. 克隆仓库
git clone https://gitee.com/pure-dhmo/hr.git
cd hr

# 2. 切换到 develop 分支
git checkout develop

# 3. 配置用户名（仅首次）
git config user.name "你的姓名"
git config user.email "你的邮箱"
```

### 4.2 开始一个新功能

```bash
# 1. 确保 develop 是最新的
git checkout develop
git pull origin develop

# 2. 创建功能分支
git checkout -b feature/qa-engine

# 3. 开发...写代码...

# 4. 提交代码
git add .
git commit -m "feat(qa): 实现关键词匹配问答引擎"

# 5. 推送到远程
git push -u origin feature/qa-engine
```

### 4.3 提交 Pull Request（Code Review）

1. 访问 https://gitee.com/pure-dhmo/hr/pulls
2. 点击「新建 Pull Request」
3. 源分支：`feature/qa-engine` → 目标分支：`develop`
4. 填写 PR 描述，指定 Reviewer
5. 等待 Code Review 通过后合并

### 4.4 同步最新代码

```bash
# 在 develop 分支上拉取最新代码
git checkout develop
git pull origin develop

# 如果你的 feature 分支需要同步 develop 的更新
git checkout feature/qa-engine
git merge develop
# 或使用 rebase（保持历史干净）
git rebase develop
```

### 4.5 紧急修复流程

```bash
# 1. 从 main 切出 hotfix 分支
git checkout main
git pull origin main
git checkout -b hotfix/login-error

# 2. 修复并提交
git add .
git commit -m "fix(auth): 修复登录验证异常"

# 3. 推送并创建 PR → main
git push -u origin hotfix/login-error

# 4. 合并后，同步到 develop
git checkout develop
git merge main
git push origin develop
```

## 五、冲突解决

### 常见冲突场景

```bash
# 场景：多人修改了同一文件
git checkout develop
git pull origin develop
git merge feature/my-work

# 如果出现冲突：
# CONFLICT (content): Merge conflict in xxx.md

# 1. 查看冲突文件
git status

# 2. 手动编辑文件，解决冲突标记
# <<<<<<< HEAD
# 你的代码
# =======
# 别人的代码
# >>>>>>> feature/my-work

# 3. 标记为已解决
git add .

# 4. 完成合并
git commit -m "merge: 解决xxx冲突"
```

### ⚠️ 冲突预防原则

- 提交前先 `git pull` 拉取最新代码
- 小步提交，避免一个 PR 改动过大
- 与队友沟通正在修改的文件，避免同时编辑同一模块
- 定期将 `develop` 合并到自己的 `feature` 分支

## 六、分支保护规则（Gitee 配置）

建议在 Gitee 仓库设置中配置以下规则：

| 分支 | 保护规则 |
|------|---------|
| `main` | ✅ 禁止直接推送<br>✅ 必须通过 PR 合并<br>✅ 至少 1 人 Review<br>✅ 禁止强制推送 |
| `develop` | ✅ 禁止直接推送<br>✅ 必须通过 PR 合并<br>⚠️ 至少 1 人 Review（可选） |

> 配置路径：Gitee 仓库 → 管理 → 分支保护

## 七、Tag 版本规范

```bash
# 创建标签
git tag -a v1.0.0 -m "首个可用版本：基础问答功能"

# 推送标签
git push origin v1.0.0

# 查看所有标签
git tag -l
```

**版本号规则**：`v<主版本>.<次版本>.<修订号>`

- `v0.1.0` — 原型阶段
- `v1.0.0` — 首个正式版本
- `v1.1.0` — 功能增强
- `v1.1.1` — 问题修复

## 八、快速参考卡片

```
┌──────────────────────────────────────────────────┐
│              日常开发速查表                        │
├──────────────────────────────────────────────────┤
│  🆕 新功能：                                      │
│    git checkout -b feature/xxx develop            │
│    git push -u origin feature/xxx                 │
│                                                   │
│  📥 拉取最新：                                    │
│    git checkout develop                           │
│    git pull origin develop                        │
│                                                   │
│  💾 提交代码：                                    │
│    git add .                                      │
│    git commit -m "feat(scope): 描述"              │
│    git push                                       │
│                                                   │
│  🔄 同步 develop：                                │
│    git checkout feature/xxx                       │
│    git merge develop                              │
│                                                   │
│  🚨 撤销修改：                                    │
│    git checkout -- <file>    (撤销文件修改)        │
│    git reset HEAD <file>     (撤销暂存)            │
│                                                   │
│  📋 查看状态：                                    │
│    git status                                     │
│    git log --oneline --graph --all                │
└──────────────────────────────────────────────────┘
```

---

> **文档维护**：随着项目推进持续更新本规范，遇到问题及时补充。
