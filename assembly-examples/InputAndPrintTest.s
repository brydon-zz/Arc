	_EXIT = 1
	_PRINTF = 127
	_GETCHAR = 117

.SECT .TEXT

	PUSH inGreet
	PUSH str
	PUSH _PRINTF
	SYS

	ADD SP,6

	MOV DI, printBuffer
	PUSH _GETCHAR

getInput:
	SYS
	CMPB AL,'\n'
	JE doneInput
	STOSB
	JMP getInput

doneInput:
	ADD SP,2

	PUSH printBuffer
	PUSH str
	PUSH _PRINTF
	SYS

	ADD SP,6

	PUSH _EXIT
	SYS


.SECT .DATA
	str: 		.ASCIZ "%s\n"
	inGreet:	.ASCIZ "Enter something to see printed:"

.SECT .BSS
	printBuffer:	.SPACE 15
