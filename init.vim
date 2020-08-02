
set number
set relativenumber

set expandtab
set tabstop=4
set softtabstop=4
set shiftwidth=4
augroup ClearExpandTab
    autocmd!
    autocmd BufNewFile,BufRead GNUmakefile,makefile,Makefile setlocal noexpandtab
    autocmd BufNewFile,BufRead *.FOR,*.for setlocal noexpandtab
augroup END

autocmd BufReadPost * if line("'\"") > 1 && line("'\"") <= line("$") | exe "normal! g'\"" | endif

