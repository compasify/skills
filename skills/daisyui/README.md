# DaisyUI Component Library

Skill này cung cấp hướng dẫn nhanh cho AI agent khi làm việc với **daisyUI** trong các dự án dùng Tailwind CSS. Nội dung tập trung vào component semantics, theme system, dark mode, và các pattern UI phổ biến để dựng giao diện nhanh hơn.

## Vấn đề

Khi làm UI với Tailwind CSS, agent thường gặp một trong hai vấn đề:

- Viết quá nhiều utility classes cho các component lặp lại
- Không nhất quán giữa button, card, modal, form, và theme
- Thiếu ngữ cảnh về cách dùng `btn`, `card`, `modal`, `drawer`, `alert` hoặc hệ thống `data-theme`

Skill này gom các pattern daisyUI phổ biến vào một chỗ để agent có thể chọn đúng component, đúng class semantic, và đúng cách cấu hình theme.

## Cách hoạt động

1. **Cung cấp ngữ cảnh** về daisyUI như một Tailwind CSS component library với semantic class names
2. **Đưa ví dụ nhanh** cho các component phổ biến như button, card, modal, form, navigation, layout, và feedback
3. **Hướng dẫn theme system** gồm built-in themes, dark mode, custom theme, và `data-theme`
4. **Tóm tắt pattern tích hợp** cho React, Vue, Svelte, hoặc HTML thuần

## Cài đặt

### skills.sh (Recommended)

```bash
npx skills add compasify/skills --skill daisyui
```

### Manual Copy

```bash
# OpenCode (project-level)
cp -r skills/daisyui .opencode/skills/

# OpenCode (user-level, all projects)
cp -r skills/daisyui ~/.config/opencode/skills/

# Claude Code
cp -r skills/daisyui ~/.claude/skills/

# Cursor
cp -r skills/daisyui ~/.cursor/skills/

# Universal (.agents/ convention)
cp -r skills/daisyui ~/.agents/skills/
```

## Yêu cầu

- Dự án đang dùng **Tailwind CSS**
- Gói `daisyui` đã được cài trong project UI
- Agent cần truy cập `SKILL.md` để lấy component examples và theme patterns

## Quick Start

### 1. Cài package

```bash
npm install -D daisyui@latest
```

### 2. Thêm plugin vào `tailwind.config.js`

```javascript
module.exports = {
  plugins: [require("daisyui")],
}
```

### 3. Dùng semantic component classes

```html
<button class="btn btn-primary">Primary Button</button>

<div class="card w-96 bg-base-100 shadow-xl">
  <div class="card-body">
    <h2 class="card-title">Card Title</h2>
    <p>Card description goes here</p>
  </div>
</div>
```

### 4. Đổi theme bằng `data-theme`

```html
<html data-theme="dark">
  <!-- Your app -->
</html>
```

## Khi nào nên dùng skill này

- Cần dựng UI nhanh bằng Tailwind CSS nhưng muốn dùng component classes có ý nghĩa như `btn`, `card`, `input`, `alert`
- Cần built-in themes, dark mode, hoặc custom theme qua `data-theme`
- Cần agent tham chiếu nhanh các pattern modal, drawer, navbar, table, badge, toast, loading, và form controls

## File Structure

```text
daisyui/
├── SKILL.md          # Core instructions + examples cho daisyUI
└── README.md         # This file
```

## License

MIT License — xem [LICENSE](../../LICENSE) để biết chi tiết.

## Author

**Compasify** — [github.com/compasify](https://github.com/compasify)
