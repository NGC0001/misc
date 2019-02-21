" vim配置

syntax on

set tabstop=4     "文档中的\t宽为4"
set softtabstop=4 "键入的<Tab>宽为4"
set shiftwidth=4
set expandtab     "键入的<Tab>转换为对应数目的空格,而不是\t"

autocmd BufNewFile,BufRead GNUmakefile,makefile,Makefile set noexpandtab
autocmd BufNewFile,BufRead *.FOR,*.for setlocal noexpandtab
"autocmd类似于钩子,BufNewFile表示编辑新文件,BufRead表示读取已存在文件
"后面是pattern(用,分隔)以及要执行的命令(用|分隔)

set number
set relativenumber
set autoindent
set smartindent
set showmatch
set hlsearch

highlight Comment ctermfg=blue

set laststatus=2
if has("statusline")
        set statusline=%(%t%4m%)%=%-20(%5l,%c-%v%)%4P%9{strftime(\"%H:%M:%S\")}
endif

if has("autocmd")
  au BufReadPost * if line("'\"") > 1 && line("'\"") <= line("$") | exe "normal! g'\"" | endif
endif

