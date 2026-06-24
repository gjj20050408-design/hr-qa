# HR制度智能问答系统 — Git 团队协作规范

> **适用团队**：课程设计小组（2-5人）  
> **分支模型**：功能分支模式（feature-branch workflow）  
> **远程仓库**：https://gitee.com/pure-dhmo/hr.git  
> **成员角色**：全部为 **Developer（开发者）**，无 Main 分支直接操作权限

---

## 一、仓库结构

```
https://gitee.com/pure-dhmo/hr.git
├── main          ← 生产就绪分支（🔒 保护，仅管理员可合并）
└── develop       ← 日常开发主线（🔒 保护，禁止直接推送）
    └── feature/姓名-功能    ← 个人功能分支（从 develop 切出，MR 合并回 develop）
```

> ⚠️ **组员只能创建 `feature/姓名-功能` 分支，无权操作 main 和 develop。**

## 二、分支命名规范

| 分支类型 | 命名格式 | 示例 |
|---------|---------|------|
| 主分支 | `main` | 生产环境代码（🔒 组员无权操作） |
| 开发分支 | `develop` | 日常开发主线（🔒 禁止直接推送） |
| 功能分支 | `feature/<姓名>-<功能>` | `feature/张三-问答引擎`, `feature/李四-用户登录` |

## 三、Commit Message 规范

采用 `feat/fix(模块): 描述` 格式：

```
<type>(<scope>): <描述>
```

### type 类型（核心）

| type | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat(qa): 添加智能问答引擎` |
| `fix` | Bug修复 | `fix(api): 修复回答匹配空指针` |
| `docs` | 文档更新 | `docs: 更新API接口文档` |
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

### 4.2 每日开始开发前

```bash
# 1. 先拉取 develop 最新代码
git checkout develop
git pull origin develop
```

### 4.3 开始一个新功能

```bash
# 1. 确保在 develop 且为最新
git checkout develop
git pull origin develop

# 2. 创建个人功能分支（命名：feature/姓名-功能）
git checkout -b feature/张三-问答引擎

# 3. 开发...写代码...

# 4. 提交代码
git add .
git commit -m "feat(qa): 实现关键词匹配问答引擎"

# 5. 推送到远程
git push -u origin feature/张三-问答引擎
```

### 4.4 提交 Merge Request（MR）

1. 访问 https://gitee.com/pure-dhmo/hr/pulls
2. 点击「新建 Pull Request」
3. **源分支**：`feature/张三-问答引擎` → **目标分支**：`develop`
4. **MR 描述必须包含**：
   - 🔧 **修改功能**：简要描述本次改动内容
   - ✅ **自测点**：列出已验证的测试项
   - ⚠️ **注意事项**：需要 reviewer 特别关注的地方
5. 指定 Reviewer（组长），等待审核
6. **审核不通过** → 根据意见修改后重新提交
7. **审核通过** → 由 reviewer 合并到 develop

### 4.5 合并后清理分支

```bash
# 合并通过后，删除本地功能分支
git checkout develop
git branch -d feature/张三-问答引擎

# 删除远程功能分支
git push origin --delete feature/张三-问答引擎
```

> 🗑️ **不保留废弃分支**：合并后立即删除临时功能分支，保持仓库整洁。

### 4.6 同步最新代码到功能分支

```bash
# 先拉取 develop 最新
git checkout develop
git pull origin develop

# 切回自己的功能分支，合并 develop
git checkout feature/张三-问答引擎
git merge develop
```

## 五、提交前自检 🧹

**每次 `git add` 和 `git commit` 前必须逐项确认：**

| # | 检查项 | 标准 |
|---|--------|------|
| 1 | 本地编译/运行 | ✅ 无报错、无警告 |
| 2 | 冗余注释 | ❌ 无整块注释掉的旧代码 |
| 3 | 测试垃圾文件 | ❌ 无 `.log`、缓存文件、本地配置文件 |
| 4 | .gitignore | ✅ 已配置过滤无关文件 |

> 仓库已预置 `.gitignore`，提交前用 `git status` 确认无无关文件混入。

---

## 六、冲突处理规则 🚫

### ⚠️ 核心原则：禁止强制覆盖他人代码！

```
┌────────────────────────────────────────────────────┐
│  出现冲突 → 线下和相关同学沟通 → 协商统一方案      │
│  ❌ 禁止私自覆盖  ❌ 禁止 git push --force           │
└────────────────────────────────────────────────────┘
```

### 标准冲突处理流程

```bash
# 1. 推送前必须先同步
git checkout develop
git pull origin develop

# 2. 切回功能分支合并 develop
git checkout feature/张三-问答引擎
git merge develop

# 如果出现冲突：
# CONFLICT (content): Merge conflict in xxx.md

# 3. 🛑 暂停操作，联系冲突代码的作者沟通
#    确认哪些改动该保留、哪些该调整

# 4. 手动编辑冲突文件，清除冲突标记
# <<<<<<< HEAD       ← 删掉
# 你的代码
# =======            ← 删掉
# 别人的代码
# >>>>>>> develop    ← 删掉

# 5. 标记已解决并提交
git add .
git commit -m "merge: 与李四沟通后解决xxx模块冲突"
```

### 冲突预防原则

- **推送前必须 `git pull`**，不做 Pull 不推送
- 小步提交，避免一个 MR 改动过大
- 与队友沟通正在修改的文件，避免同时编辑同一模块
- 每日开发前先拉取 develop 最新代码

---

## 七、分支保护规则（Gitee 配置）

| 分支 | 保护规则 |
|------|---------|
| `main` | 🔒 禁止直接推送<br>🔒 必须通过 MR 合并<br>🔒 至少 1 人 Review<br>🔒 禁止强制推送<br>🔒 **仅管理员可操作** |
| `develop` | 🔒 禁止直接推送<br>🔒 必须通过 MR 合并<br>🔒 至少 1 人 Review<br>🔒 禁止强制推送 |

> 配置路径：Gitee 仓库 → 管理 → 分支保护  
> ⚠️ **组员只能创建 `feature/姓名-功能` 分支，提交 MR 到 develop。**

---

## 八、版本发布规范

> 🔑 **版本发布由管理员（组长）操作，组员无权操作 main 分支。**

```bash
# 周期迭代完成后，管理员执行以下操作：

# 1. 将 develop 合并到 main
git checkout main
git pull origin main
git merge develop

# 2. 打版本 Tag
git tag -a v1.0.0 -m "首个可用版本：基础问答功能"

# 3. 推送 main 和 tag
git push origin main
git push origin v1.0.0
```

**版本号规则**：`v<主版本>.<次版本>.<修订号>`

| 版本 | 说明 |
|------|------|
| `v0.1.0` | 原型阶段 |
| `v1.0.0` | 首个正式版本 |
| `v1.1.0` | 功能增强 |
| `v1.1.1` | 问题修复 |

---

## 九、快速参考卡片

```
┌─────────────────────────────────────────────────────┐
│                日常开发速查表                          │
├─────────────────────────────────────────────────────┤
│  📥 每日开始：                                       │
│    git checkout develop                             │
│    git pull origin develop                          │
│                                                      │
│  🆕 新功能（命名：feature/姓名-功能）：              │
│    git checkout -b feature/张三-问答 develop         │
│    git push -u origin feature/张三-问答              │
│                                                      │
│  💾 提交代码：                                       │
│    git add .                                        │
│    git commit -m "feat(qa): 描述"                    │
│    git push                                         │
│                                                      │
│  🔄 同步 develop（每天必做）：                       │
│    git checkout develop                             │
│    git pull origin develop                          │
│    git checkout feature/张三-问答                    │
│    git merge develop                                │
│                                                      │
│  🗑️ 合并后清理：                                    │
│    git checkout develop                             │
│    git branch -d feature/张三-问答                   │
│    git push origin --delete feature/张三-问答        │
│                                                      │
│  🚨 冲突时（先沟通，不强制覆盖）：                   │
│    git checkout develop && git pull                 │
│    git checkout feature/张三-问答 && git merge dev   │
│    # 联系冲突代码作者，协商方案                       │
│                                                      │
│  📋 查看状态：                                       │
│    git status                                       │
│    git log --oneline --graph --all                   │
└─────────────────────────────────────────────────────┘
```

---

> **文档维护**：随着项目推进持续更新本规范，遇到问题及时补充。
