vim.opt.number = true
vim.opt.relativenumber = true
vim.opt.clipboard = "unnamedplus"
vim.opt.autoindent = true
vim.opt.cursorline = true

require("theme")

-- インデントには空白4文字を使用し、Shift+Tabでインデントを減らす。
vim.opt.expandtab = true
vim.opt.shiftwidth = 4
vim.opt.softtabstop = 4
vim.opt.tabstop = 4
vim.keymap.set("i", "<S-Tab>", "<C-D>", { desc = "Decrease indentation" })

-- 通常の空白で画面が煩雑にならないようにしつつ、空白文字を可視化する。
vim.opt.list = true
vim.opt.listchars = {
  eol = "↲",
  extends = "⟩",
  nbsp = "␣",
  precedes = "⟨",
  tab = "→ ",
  trail = "·",
}

-- ゼロ幅文字などの不可視Unicode文字を控えめなドットで可視化する。
vim.opt.conceallevel = 2
vim.opt.concealcursor = ""
vim.cmd([[syntax match InvisibleWhitespace /\%u200B\|\%u200C\|\%u200D\|\%u2060\|\%uFEFF/ conceal cchar=·]])
vim.api.nvim_set_hl(0, "InvisibleWhitespace", { ctermfg = 240, fg = "#585858" })

require("lsp")

-- ペーストで挿入された行を自動的に再インデントする。
local default_paste = vim.paste
vim.paste = function(lines, phase)
  local pasted = default_paste(lines, phase)
  if pasted ~= false and (phase == -1 or phase == 3) then
    vim.schedule(function()
      vim.cmd("silent! normal! '[=']")
    end)
  end
  return pasted
end
