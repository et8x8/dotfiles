-- テーマを管理し、Backpackテーマを適用する。
local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not vim.uv.fs_stat(lazypath) then
  vim.fn.system({
    "git",
    "clone",
    "--filter=blob:none",
    "https://github.com/folke/lazy.nvim.git",
    "--branch=stable",
    lazypath,
  })
end
vim.opt.rtp:prepend(lazypath)

require("lazy").setup({
  {
    "Mitch1000/backpack.nvim",
    lazy = false,
    priority = 1000,
    config = function()
      require("backpack").setup()
      vim.cmd.colorscheme("backpack")
    end,
  },
})
