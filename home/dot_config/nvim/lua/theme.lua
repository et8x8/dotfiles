-- VSCodeテーマを設定する。
return {
  "Mofiqul/vscode.nvim",
  lazy = false,
  priority = 1000,
  config = function()
    vim.o.background = "dark"
    require("vscode").setup()
    vim.cmd.colorscheme("vscode")
  end,
}
