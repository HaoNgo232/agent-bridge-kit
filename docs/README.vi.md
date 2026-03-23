# Agent Bridge

> Công cụ chuyển đổi đa năng cho kiến thức AI agent với đồng bộ hai chiều giữa định dạng `.agent/` và cấu hình nhiều IDE khác nhau.

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](../LICENSE)
[![Tests: 137 passing](https://img.shields.io/badge/tests-137%20passing-brightgreen.svg)](#kiểm-thử)

---

## Mục Lục

- [Tổng Quan](#tổng-quan)
- [Kiến Trúc](#kiến-trúc)
- [Công Nghệ Sử Dụng](#công-nghệ-sử-dụng)
- [Các Module Chính](#các-module-chính)
- [Cài Đặt](#cài-đặt)
- [Bắt Đầu Nhanh](#bắt-đầu-nhanh)
- [IDE Được Hỗ Trợ](#ide-được-hỗ-trợ)
- [Tham Chiếu Lệnh](#tham-chiếu-lệnh)
- [Quy Trình Đồng Bộ Hai Chiều](#quy-trình-đồng-bộ-hai-chiều)
- [Knowledge Vaults](#knowledge-vaults)
- [Tích Hợp MCP](#tích-hợp-mcp)
- [Hệ Thống Plugin](#hệ-thống-plugin)
- [Cấu Hình](#cấu-hình)
- [Hướng Dẫn Phát Triển](#hướng-dẫn-phát-triển)
- [Kiểm Thử](#kiểm-thử)
- [Xử Lý Sự Cố](#xử-lý-sự-cố)
- [Đóng Góp](#đóng-góp)
- [Ghi Nhận](#ghi-nhận)
- [Giấy Phép](#giấy-phép)

---

## Tổng Quan

**Agent Bridge** giải quyết một vấn đề quan trọng trong phát triển AI đa IDE: mỗi IDE (Cursor, Copilot, Kiro, OpenCode, Windsurf) sử dụng định dạng riêng cho cấu hình AI agent. Việc duy trì kiến thức agent trên nhiều IDE đồng nghĩa với việc phải sao chép và đồng bộ thủ công các file cấu hình.

Agent Bridge cung cấp một **nguồn chân lý duy nhất** (thư mục `.agent/`) và tự động chuyển đổi sang định dạng gốc của từng IDE. Nó cũng hỗ trợ **chuyển đổi ngược** — nắm bắt các thay đổi trong cấu hình IDE trở lại `.agent/`, cho phép đồng bộ hai chiều thực sự.

### Tính Năng Chính

- **Chuyển Đổi Xuôi**: `.agent/` → định dạng IDE cụ thể (hỗ trợ 5 IDE)
- **Nắm Bắt Ngược**: Cấu hình IDE → `.agent/` (Cursor, Kiro, Copilot)
- **Quản Lý Snapshot**: Lưu, khôi phục và quản lý phiên bản trạng thái `.agent/`
- **Knowledge Vaults**: Đăng ký git repo hoặc thư mục local làm nguồn kiến thức agent
- **Tích Hợp MCP**: Phân phối cấu hình Model Context Protocol
- **Hệ Thống Plugin**: Cài đặt skill bên ngoài theo khai báo qua `plugins.json`
- **TUI Tương Tác**: Trình hướng dẫn thiết lập dựa trên Questionary
- **Giải Quyết Xung Đột**: Chiến lược `ide_wins` hoặc `agent_wins`

---

## Kiến Trúc

```
┌─────────────────────────────────────────────────────┐
│                     CLI (cli.py)                     │
│           Bộ điều phối nhẹ / argparse                │
├──────────┬──────────┬───────────┬───────────────────┤
│ TUI      │ Services │ Vault     │ Utils             │
│ (tui.py) │          │           │                   │
│          │ init     │ manager   │ colors, display   │
│          │ sync     │ merger    │ filesystem, mcp   │
│          │ capture  │ sources   │                   │
│          │ snapshot │           │                   │
│          │ status   │           │                   │
├──────────┴──────────┴───────────┴───────────────────┤
│                   Tầng Core                          │
│  types.py │ agent_registry.py │ converter.py        │
│  frontmatter.py │ plugins.py                        │
├─────────────────────────────────────────────────────┤
│                  Converters                           │
│  cursor.py  │ copilot.py │ kiro.py                  │
│  opencode.py │ windsurf.py                          │
│  _cursor_impl.py │ _copilot_impl.py │ _kiro_impl.py│
│  _opencode_impl.py │ _windsurf_impl.py              │
└─────────────────────────────────────────────────────┘
```

### Quyết Định Thiết Kế

1. **Converter Tự Đăng Ký**: Mỗi converter tự đăng ký với `ConverterRegistry` khi import. Thêm IDE mới không cần thay đổi gì ở services hay CLI — chỉ cần tạo hai file (`converters/my_ide.py` + `converters/_my_ide_impl.py`).

2. **Agent Registry Tập Trung**: `core/agent_registry.py` là nguồn chân lý duy nhất cho vai trò và khả năng của agent. Tất cả converter đều dẫn xuất cấu hình IDE cụ thể từ registry này.

3. **Tách Biệt Tầng Service**: Logic nghiệp vụ nằm trong `services/`, hoàn toàn tách rời khỏi phân tích CLI. Điều này cho phép kiểm thử mà không cần mô phỏng lệnh CLI.

4. **Mẫu Strategy cho Vaults**: `vault/sources.py` triển khai `GitSource`, `LocalSource` và `BuiltinSource`, mỗi nguồn tự biết cách đồng bộ.

5. **Module Frontmatter Chung**: `core/frontmatter.py` cung cấp phân tích YAML frontmatter thống nhất cho tất cả converter, loại bỏ các mẫu regex trùng lặp.

---

## Công Nghệ Sử Dụng

| Thành phần         | Công nghệ        | Mục đích                      |
| ------------------ | ---------------- | ----------------------------- |
| Ngôn ngữ           | Python 3.8+      | Tương thích đa nền tảng       |
| Framework CLI      | argparse         | Phân tích tham số nhẹ         |
| UI tương tác       | questionary 2.0+ | Prompt checkbox/select        |
| Đầu ra Rich        | rich 13.0+       | Đầu ra terminal có màu        |
| Phân tích cấu hình | PyYAML           | Xử lý YAML frontmatter        |
| Lint               | Ruff 0.1+        | Linter/formatter Python nhanh |
| Kiểm tra kiểu      | mypy 1.0+        | Phân tích kiểu tĩnh           |
| Kiểm thử           | pytest 8.3+      | Framework kiểm thử            |

---

## Các Module Chính

### Core (`src/agent_bridge/core/`)

| File                | Mục đích                                                                                                                          |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `types.py`          | Cấu trúc dữ liệu dùng chung: `AgentRole`, `ConversionResult`, `CapturedFile`, `SnapshotInfo`, `IDEFormat`, enum `CaptureStatus`   |
| `agent_registry.py` | Định nghĩa vai trò agent tập trung với khả năng (đọc/ghi/thực thi/tìm kiếm), lệnh cho phép, đường dẫn, subagents, handoff targets |
| `converter.py`      | ABC `BaseConverter` và `ConverterRegistry` — điểm mở rộng cho IDE mới                                                             |
| `frontmatter.py`    | `FrontmatterParser` cho trích xuất, tạo và loại bỏ YAML/MDC frontmatter                                                           |
| `plugins.py`        | Hệ thống plugin skill bên ngoài theo khai báo — đọc `.agent/plugins.json`, cài đặt tiên quyết, chạy lệnh IDE cụ thể               |

### Converters (`src/agent_bridge/converters/`)

Mỗi converter gồm một module public (ví dụ `cursor.py`) chứa lớp con `BaseConverter`, và một module implementation private (ví dụ `_cursor_impl.py`) chứa logic chuyển đổi.

| IDE            | Module Public | Module Impl         | Thư mục đầu ra | Hỗ trợ Capture |
| -------------- | ------------- | ------------------- | -------------- | -------------- |
| Cursor AI      | `cursor.py`   | `_cursor_impl.py`   | `.cursor/`     | Có             |
| GitHub Copilot | `copilot.py`  | `_copilot_impl.py`  | `.github/`     | Có             |
| Kiro CLI       | `kiro.py`     | `_kiro_impl.py`     | `.kiro/`       | Có             |
| OpenCode       | `opencode.py` | `_opencode_impl.py` | `.opencode/`   | Không          |
| Windsurf       | `windsurf.py` | `_windsurf_impl.py` | `.windsurf/`   | Không          |

### Services (`src/agent_bridge/services/`)

| File                  | Mục đích                                                                                      |
| --------------------- | --------------------------------------------------------------------------------------------- |
| `init_service.py`     | `run_init()` — chuẩn bị `.agent/`, chạy converters, cài MCP, ghi `.bridge-meta.json`          |
| `sync_service.py`     | `run_update()` — đồng bộ vaults, merge vào project, tự động làm mới cấu hình IDE đã phát hiện |
| `capture_service.py`  | `scan_for_captures()` / `execute_capture()` — đồng bộ ngược thay đổi IDE về `.agent/`         |
| `snapshot_service.py` | Thao tác CRUD cho snapshot `.agent/` với theo dõi manifest                                    |
| `status_service.py`   | `collect_status()` — thu thập dữ liệu trạng thái dự án                                        |
| `status_display.py`   | `display_status()` — đầu ra terminal có định dạng cho status                                  |

### Vault (`src/agent_bridge/vault/`)

| File         | Mục đích                                                                                |
| ------------ | --------------------------------------------------------------------------------------- |
| `manager.py` | `VaultManager` — registry, điều phối đồng bộ, điều phối merge                           |
| `sources.py` | `GitSource`, `LocalSource`, `BuiltinSource` — mẫu strategy                              |
| `merger.py`  | `merge_source_into_project()` với chiến lược `PROJECT_WINS`, `VAULT_WINS`, `VAULT_ONLY` |

---

## Cài Đặt

### Từ GitHub (khuyến nghị)

```bash
pipx install git+https://github.com/HaoNgo232/agent-bridge
```

### Từ mã nguồn (phát triển)

```bash
git clone https://github.com/HaoNgo232/agent-bridge.git
cd agent-bridge
pip install -e ".[dev]"
```

### Script thiết lập nhanh

```bash
make setup  # Kiểm tra môi trường, cài dependencies, chạy lint
```

### Yêu cầu

- Python 3.8 trở lên
- Git (để đồng bộ vault)
- Node.js/npm (tùy chọn, cho plugin skill bên ngoài)

---

## Bắt Đầu Nhanh

```bash
cd your-project

# Thiết lập tương tác (khuyến nghị)
agent-bridge init

# Hoặc chỉ định IDE trực tiếp
agent-bridge init --cursor
agent-bridge init --kiro
agent-bridge init --all

# Kiểm tra trạng thái dự án
agent-bridge status

# Kéo kiến thức mới nhất và làm mới cấu hình
agent-bridge update
```

---

## IDE Được Hỗ Trợ

| IDE            | Thư mục đầu ra | Định dạng                        | Trạng thái | Capture |
| -------------- | -------------- | -------------------------------- | ---------- | ------- |
| Cursor AI      | `.cursor/`     | Markdown + MDC rules             | Beta       | Có      |
| GitHub Copilot | `.github/`     | YAML frontmatter markdown        | Beta       | Có      |
| Kiro CLI       | `.kiro/`       | JSON agents + markdown prompts   | Beta       | Có      |
| OpenCode       | `.opencode/`   | YAML frontmatter markdown + JSON | Beta       | Không   |
| Windsurf       | `.windsurf/`   | Markdown với chế độ kích hoạt    | Beta       | Không   |

### Chi Tiết Định Dạng

**Cursor**: Agents đi vào `.cursor/agents/*.md` với frontmatter name/description. Skills trở thành MDC rules (`.cursor/rules/*.mdc` với frontmatter `alwaysApply`/`globs`) hoặc slash-command skills (`.cursor/skills/*/SKILL.md`). Workflows trở thành skills.

**Copilot**: Agents có YAML frontmatter đầy đủ (name, description, tools, agents, handoffs). Skills đi vào `.github/skills/*/SKILL.md`. Workflows trở thành `.github/prompts/*.prompt.md`. Rules trở thành `.github/instructions/*.instructions.md`.

**Kiro**: Agents trở thành file JSON với tools, allowedTools, toolsSettings, hooks và resources. Skills được sao chép trực tiếp. Workflows trở thành prompts với cú pháp template Kiro. Rules đi vào steering với frontmatter `inclusion: always`.

**OpenCode**: Agents có frontmatter mode (primary/subagent), tools và permission. Workflows trở thành commands. Skills được sao chép trực tiếp.

**Windsurf**: Mọi thứ trở thành rules với chế độ kích hoạt (Always On, Glob, Model Decision, Manual). Workflows được trích xuất steps. File `.windsurfrules` gốc cũng được tạo.

---

## Tham Chiếu Lệnh

### `agent-bridge init`

Thiết lập cấu hình agent cho dự án.

```bash
agent-bridge init                    # TUI tương tác
agent-bridge init --cursor           # Chỉ Cursor
agent-bridge init --kiro --copilot   # Nhiều IDE
agent-bridge init --all              # Tất cả IDE
agent-bridge init --from my-snapshot # Từ snapshot đã lưu
agent-bridge init --force            # Ghi đè bắt buộc
agent-bridge init --no-interactive   # Bỏ qua TUI
```

### `agent-bridge update`

Kéo kiến thức mới nhất từ vaults và làm mới cấu hình IDE hiện có.

```bash
agent-bridge update
agent-bridge update --target .agent
```

### `agent-bridge capture`

Đồng bộ ngược: nắm bắt thay đổi từ cấu hình IDE về `.agent/`.

```bash
agent-bridge capture                              # Tương tác
agent-bridge capture --cursor                     # Chỉ Cursor
agent-bridge capture --all                        # Tất cả IDE
agent-bridge capture --strategy ide_wins          # Thay đổi IDE thắng
agent-bridge capture --strategy agent_wins        # Bỏ qua không đổi
agent-bridge capture --dry-run                    # Chỉ xem trước
```

### `agent-bridge snapshot`

Lưu và quản lý snapshot `.agent/`.

```bash
agent-bridge snapshot save my-snapshot -d "Mô tả"
agent-bridge snapshot save tagged -t "framework:flutter" -t "lang:dart"
agent-bridge snapshot list
agent-bridge snapshot info my-snapshot
agent-bridge snapshot restore my-snapshot
agent-bridge snapshot delete my-snapshot
```

### `agent-bridge status`

Hiển thị bảng điều khiển dự án.

```bash
agent-bridge status          # Đầu ra có định dạng
agent-bridge status --json   # JSON cho máy đọc
```

### `agent-bridge vault`

Quản lý knowledge vaults.

```bash
agent-bridge vault list
agent-bridge vault add my-team git@github.com:myorg/ai-agents.git
agent-bridge vault add local-agents /path/to/agents -p 50
agent-bridge vault remove my-team
agent-bridge vault sync
agent-bridge vault sync --name my-team
```

### `agent-bridge mcp`

Cài đặt cấu hình MCP.

```bash
agent-bridge mcp --all
agent-bridge mcp --cursor --kiro
agent-bridge mcp --force
```

### `agent-bridge clean`

Xóa cấu hình IDE đã tạo.

```bash
agent-bridge clean --all
agent-bridge clean --cursor
```

### `agent-bridge list`

Liệt kê tất cả định dạng IDE được hỗ trợ.

### Chuyển Đổi Trực Tiếp

```bash
agent-bridge cursor --source .agent
agent-bridge kiro --source .agent
agent-bridge copilot
```

---

## Quy Trình Đồng Bộ Hai Chiều

```bash
# 1. Khởi tạo cấu hình IDE từ .agent/
agent-bridge init --cursor

# 2. Làm việc trong Cursor IDE, thay đổi file agent
#    ... chỉnh sửa .cursor/agents/orchestrator.md ...

# 3. Nắm bắt thay đổi về .agent/
agent-bridge capture --ide cursor

# 4. Lưu snapshot trước thay đổi lớn
agent-bridge snapshot save "before-refactor" -d "Trạng thái ổn định"

# 5. Thực hiện thay đổi thử nghiệm
#    ... chỉnh sửa file .agent/ ...

# 6. Khôi phục nếu cần
agent-bridge snapshot restore "before-refactor"

# 7. Đẩy sang IDE khác
agent-bridge init --kiro
```

### Cơ Chế Bridge Meta

Khi `agent-bridge init` chạy, nó ghi `.agent/.bridge-meta.json` chứa:

- `generated_at`: Thời gian tạo
- `generated_for`: Danh sách tên IDE
- `file_map`: Ánh xạ đường dẫn file IDE → đường dẫn file `.agent/`

Service capture sử dụng metadata này để xác định trạng thái file:

- **new**: File không có trong `file_map` (người dùng tạo trong IDE)
- **modified**: File có trong `file_map` với mtime > `generated_at`
- **unchanged**: File có trong `file_map`, không bị sửa đổi kể từ khi tạo

---

## Knowledge Vaults

Vault là bất kỳ thư mục nào (git repo hoặc đường dẫn local) chứa cấu trúc `.agent/`:

```
.agent/
├── agents/          # File định nghĩa agent (*.md)
├── skills/          # Thư mục skill với SKILL.md
├── workflows/       # Template workflow (*.md)
├── rules/           # File rules (*.md)
├── mcp_config.json  # Cấu hình MCP server
└── plugins.json     # Khai báo plugin bên ngoài
```

### Vault Mặc Định

Agent Bridge đi kèm vault khởi đầu tối giản hoạt động offline không cần dependency bên ngoài. Nó có ưu tiên thấp nhất (999) và đóng vai trò dự phòng.

### Ưu Tiên Vault

Khi nhiều vault được đăng ký, file được merge với:

1. **File local của dự án** có ưu tiên cao nhất
2. **Vault theo thứ tự ưu tiên** (số thấp hơn = ưu tiên cao hơn)
3. Chiến lược merge có thể cấu hình: `PROJECT_WINS`, `VAULT_WINS`, `VAULT_ONLY`

### Lưu Trữ Vault

Vault được lưu trong `~/.config/agent-bridge/`:

- `vaults.json` — registry vault
- `cache/<name>/` — nội dung vault đã cache
- `snapshots/<name>/` — snapshot đã lưu

---

## Tích Hợp MCP

Agent Bridge phân phối cấu hình MCP (Model Context Protocol) từ `.agent/mcp_config.json` đến vị trí mong đợi của từng IDE với chuyển đổi định dạng:

| IDE      | Đường dẫn MCP                         | Định dạng Key           |
| -------- | ------------------------------------- | ----------------------- |
| Copilot  | `.vscode/mcp.json`                    | `{"servers": {...}}`    |
| Cursor   | `.cursor/mcp.json`                    | `{"mcpServers": {...}}` |
| Kiro     | `.kiro/settings/mcp.json`             | `{"mcpServers": {...}}` |
| OpenCode | Nhúng trong `.opencode/opencode.json` | Định dạng riêng         |
| Windsurf | `.windsurf/mcp_config.json`           | `{"mcpServers": {...}}` |

Định dạng nguồn (`.agent/mcp_config.json`):

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"]
    }
  }
}
```

---

## Hệ Thống Plugin

Skill bên ngoài có thể được khai báo trong `.agent/plugins.json`:

```json
{
  "plugins": [
    {
      "name": "ui-ux-pro-max",
      "description": "Bộ skill thiết kế UI/UX",
      "homepage": "https://github.com/nextlevelbuilder/ui-ux-pro-max-skill",
      "install": {
        "requires": "npm",
        "package": "uipro-cli",
        "global": true,
        "commands": {
          "kiro": "uipro init --ai kiro",
          "cursor": "uipro init --ai cursor"
        }
      },
      "condition": {
        "file_exists": ".agent/workflows/ui-ux-pro-max.md"
      },
      "prompt_before_install": true
    }
  ]
}
```

Plugin có các đặc điểm:

- **Khai báo**: Định nghĩa trong JSON, không phải Python code
- **Theo IDE**: Mỗi IDE có lệnh cài đặt riêng
- **Có điều kiện**: Chỉ cài khi điều kiện trigger được đáp ứng
- **An toàn**: Hỏi người dùng trước khi cài package global (trừ khi dùng `--force`)

---

## Cấu Hình

### Môi trường

Không cần biến môi trường cho sử dụng cơ bản. MCP servers có thể yêu cầu biến môi trường riêng (ví dụ `GITHUB_TOKEN`).

### Cấu Trúc Dự Án

```
your-project/
├── .agent/                    # Nguồn chân lý
│   ├── agents/*.md            # Định nghĩa agent
│   ├── skills/*/SKILL.md      # Bộ skill
│   ├── workflows/*.md         # Template workflow
│   ├── rules/*.md             # Rules toàn cục
│   ├── mcp_config.json        # MCP servers
│   ├── plugins.json           # Plugin bên ngoài
│   └── .bridge-meta.json      # File theo dõi đã tạo
├── .cursor/                   # Cấu hình Cursor đã tạo
├── .github/                   # Cấu hình Copilot đã tạo
├── .kiro/                     # Cấu hình Kiro đã tạo
├── .opencode/                 # Cấu hình OpenCode đã tạo
└── .windsurf/                 # Cấu hình Windsurf đã tạo
```

### Cấu Hình Toàn Cục

```
~/.config/agent-bridge/
├── vaults.json                # Registry vault
├── cache/                     # Nội dung vault đã cache
│   ├── builtin-starter/
│   └── my-team/
└── snapshots/                 # Snapshot đã lưu
    ├── before-refactor/
    └── stable-v1/
```

---

## Hướng Dẫn Phát Triển

### Thiết Lập

```bash
git clone https://github.com/HaoNgo232/agent-bridge.git
cd agent-bridge
make setup          # Hoặc thủ công:
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Phong Cách Code

- **Linter**: Ruff với pycodestyle, pyflakes, isort, flake8-bugbear, pyupgrade
- **Độ dài dòng**: 120 ký tự
- **Target**: Python 3.8
- **Type hints**: Tùy chọn nhưng khuyến khích

```bash
make lint           # Chạy linter
make format         # Tự sửa và format
make check          # Kiểm tra đầy đủ
make clean          # Xóa file cache
```

### Thêm IDE Converter Mới

1. Tạo `src/agent_bridge/converters/my_ide.py`:

```python
from agent_bridge.core.converter import BaseConverter, converter_registry
from agent_bridge.core.types import ConversionResult, IDEFormat

class MyIDEConverter(BaseConverter):
    @property
    def format_info(self) -> IDEFormat:
        return IDEFormat(name="myide", display_name="My IDE", output_dir=".myide")

    def convert(self, source_root, dest_root, verbose=True, force=False):
        # ... logic chuyển đổi ...
        return ConversionResult(agents=N, skills=N)

    def install_mcp(self, source_root, dest_root, force=False):
        from agent_bridge.utils import install_mcp_for_ide
        return install_mcp_for_ide(source_root, dest_root, "myide")

    def clean(self, project_path):
        # ... logic dọn dẹp ...
        return True

converter_registry.register(MyIDEConverter)
```

2. Tạo `src/agent_bridge/converters/_my_ide_impl.py` với các hàm chuyển đổi.

3. Thêm import vào `src/agent_bridge/converters/__init__.py`.

4. **Không cần thay đổi** gì ở CLI, services hay utils.

### Pre-commit Hook

```bash
ln -s ../../scripts/pre-commit.sh .git/hooks/pre-commit
```

---

## Kiểm Thử

```bash
# Chạy tất cả test
pytest tests/

# Chạy với đầu ra chi tiết
pytest tests/ -v

# Chạy bộ test cụ thể
pytest tests/test_capture_service.py
pytest tests/test_snapshot_service.py
pytest tests/test_roundtrip.py
pytest tests/test_plugins.py
pytest tests/test_status_service.py

# Chạy test khớp mẫu
pytest tests/ -k "roundtrip"

# Trạng thái hiện tại: 137/137 test đạt
```

### Cấu Trúc Test

| File Test                    | Phạm vi                                   |
| ---------------------------- | ----------------------------------------- |
| `test_agent_registry.py`     | Kiểm tra registry vai trò agent tập trung |
| `test_capture_service.py`    | Quét và thực thi đồng bộ ngược            |
| `test_cli_snapshot.py`       | Tích hợp lệnh snapshot CLI                |
| `test_converter_registry.py` | Đăng ký và tra cứu converter              |
| `test_converters.py`         | Chi tiết converter Copilot                |
| `test_copilot_converter.py`  | Chuyển đổi Copilot end-to-end             |
| `test_cursor_converter.py`   | Chuyển đổi Cursor end-to-end              |
| `test_init_service.py`       | Test ủy quyền bridge-meta                 |
| `test_kiro_converter.py`     | Chuyển đổi Kiro end-to-end                |
| `test_kiro_reverse_edge.py`  | Trường hợp biên chuyển đổi ngược Kiro     |
| `test_mcp_transform.py`      | Chuyển đổi định dạng MCP                  |
| `test_merger.py`             | Chiến lược merge vault                    |
| `test_plugins.py`            | Tải và thực thi hệ thống plugin           |
| `test_reverse_copilot.py`    | Chuyển đổi ngược Copilot                  |
| `test_reverse_cursor.py`     | Chuyển đổi ngược Cursor                   |
| `test_reverse_kiro.py`       | Chuyển đổi ngược Kiro                     |
| `test_roundtrip.py`          | Bảo toàn body xuôi → ngược                |
| `test_snapshot_service.py`   | Thao tác CRUD snapshot                    |
| `test_status_service.py`     | Thu thập và hiển thị trạng thái           |
| `test_utils.py`              | Test hàm tiện ích                         |

---

## Xử Lý Sự Cố

### "No .agent/ directory available"

Dự án của bạn không có thư mục `.agent/`. Có thể:

- Chạy `agent-bridge init` với tùy chọn nguồn `vault` để khởi tạo từ vault
- Tạo thủ công `.agent/agents/` và `.agent/skills/`
- Dùng `agent-bridge init --from <snapshot>` nếu có snapshot đã lưu

### "No vaults registered"

Chạy `agent-bridge vault add` để đăng ký nguồn kiến thức:

```bash
agent-bridge vault add my-team https://github.com/myorg/ai-agents.git
agent-bridge vault sync
```

### Capture hiển thị tất cả file là "new"

Điều này xảy ra khi `.agent/.bridge-meta.json` bị thiếu hoặc lỗi thời. Chạy lại `agent-bridge init` để tạo lại file theo dõi, sau đó capture sẽ phát hiện chính xác các thay đổi.

### Cấu hình MCP không hoạt động trong VS Code/Copilot

VS Code yêu cầu MCP servers dưới key `"servers"`, không phải `"mcpServers"`. Agent Bridge tự động xử lý chuyển đổi này. Kiểm tra `.vscode/mcp.json` có chứa `{"servers": {...}}`.

### Cài đặt plugin thất bại

1. Đảm bảo trình quản lý package cần thiết (npm/pip/cargo) đã được cài
2. Kiểm tra kết nối mạng cho cài đặt package global
3. Thử cài đặt thủ công: `npm install -g <package-name>`
4. Dùng flag `--force` để bỏ qua prompt xác nhận

### Cấu hình IDE lỗi thời

Chạy `agent-bridge status` để kiểm tra độ cũ, sau đó `agent-bridge update` để làm mới.

---

## Đóng Góp

1. Fork repository
2. Tạo nhánh tính năng: `git checkout -b feature/my-feature`
3. Thực hiện thay đổi theo hướng dẫn phong cách code
4. Thêm test cho chức năng mới
5. Chạy `make check` để xác minh lint đạt
6. Chạy `pytest tests/` để xác minh tất cả test đạt
7. Gửi pull request

---

## Ghi Nhận

- [Antigravity Kit](https://github.com/vudovn/antigravity-kit) bởi Vudovn (Giấy phép MIT)
- [UI-UX Pro Max](https://github.com/nextlevelbuilder) bởi NextLevelBuilder (Giấy phép MIT)

---

## Giấy Phép

MIT © HaoNgo232
