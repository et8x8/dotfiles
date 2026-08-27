-- Goファイルで使用する、公式のGo言語LSPであるgoplsの設定。
return {
  cmd = { "gopls" },
  filetypes = { "go", "gomod", "gowork", "gotmpl" },
  root_markers = { "go.work", "go.mod", ".git" },
  settings = {
    gopls = {
      analyses = {
        unusedparams = true,
        unusedwrite = true,
      },
      gofumpt = true,
      staticcheck = true,
    },
  },
}
