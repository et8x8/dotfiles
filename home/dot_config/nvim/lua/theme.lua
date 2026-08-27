-- VSCodeテーマを設定する。
return {
  "Mofiqul/vscode.nvim",
  lazy = false,
  priority = 1000,
  config = function()
    vim.o.background = "dark"
    require("vscode").setup({
      -- カーソル行を背景色の差で見やすくする。
      group_overrides = {
        CursorLine = { bg = "#333842" },
        -- LSPのホバーテキストを本文と区別しやすくする。
        NormalFloat = { bg = "#252526" },
        FloatBorder = { fg = "#808080", bg = "#252526" },
      },
    })
    vim.cmd.colorscheme("vscode")
  end,
}
