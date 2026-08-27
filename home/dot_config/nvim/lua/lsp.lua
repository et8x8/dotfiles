-- LSPサーバーを有効化し、接続後のバッファに操作キーを設定する。
if vim.fn.executable("gopls") == 1 then
  vim.lsp.enable("gopls")
end

-- LSPが接続したバッファで、よく使う操作を有効にする。
vim.api.nvim_create_autocmd("LspAttach", {
  callback = function(event)
    local opts = { buffer = event.buf, silent = true }
    vim.keymap.set("n", "gd", vim.lsp.buf.definition, opts)
    vim.keymap.set("n", "gr", vim.lsp.buf.references, opts)
    -- Kで表示するLSPホバーに明示的な枠線を付ける。
    vim.keymap.set("n", "K", function()
      vim.lsp.buf.hover({ border = "single" })
    end, opts)
    vim.keymap.set("n", "<leader>rn", vim.lsp.buf.rename, opts)
    vim.keymap.set("n", "<leader>ca", vim.lsp.buf.code_action, opts)
  end,
})
