" Vim syntax file for BLE rules.
"
" Language: BLE

" Quit if the syntax file has already been loaded.
if exists("b:current_syntax")
	finish
endif

inoremap {<CR> {<C-o>o}<C-o>O

syntax case match

" Keywords
syntax keyword bleKeyword class include as and or not if then elif else for to step each in while do fn mut builtin disp input getch kbhit rand int float str type read readb write writeb cls time cli os

" Identifiers
syntax match bleIdentifier /$[a-zA-Z0-9_]*/

" Strings
syntax region bleString start=/"/ end=/"/ skip=/\(\\\\\|\\"\)/

" Numbers
syntax match bleInt /\<\([0-9]\+\|0x[0-9a-fA-F]\+\)\>/
syntax match bleFloat /\<[0-9]\+\.[0-9]\+\>/

" Comments
syntax match bleComment /#.*/

highlight default link bleKeyword Keyword
highlight default link bleIdentifier Identifier
highlight default link bleString Character
highlight default link bleInt Number
highlight default link bleFloat Number
highlight default link bleComment Comment

" Make sure that the syntax file is loaded at most once.
let b:current_syntax = "ble"

