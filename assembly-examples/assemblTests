	_EXIT = 1
	_PRINTF = 127
	_GETCHAR = 117
	_SSCANF = 125
	_READ = 3
	_OPEN = 5
	_CLOSE = 6
	LINE_LENGTH = 15
	NUMOFFSET = 48
	STRINGOFFSET = 87

.SECT .TEXT
	CALL start
	PUSH 76
	POP BX
	CMPB BL, 'L'
	JMP t
start:
	PUSH str
	PUSH inGreet
	PUSH _PRINTF
	SYS
	ADD SP,6			! Print a velcome
	RET
t:
	CALL start
.SECT .DATA
	str: 		.ASCIZ "%s"
	pipestr:	.ASCIZ " |%s|\n"
	spacenum:	.ASCIZ " %s"
	num:	 	.ASCIZ "%d"
	inGreet: 	.ASCIZ "Enter a filename plx:\n"
	errStr:		.ASCIZ "There was an error opening the file: %s\n"
	finStr:		.ASCIZ "Succesfully read %d bytes and %d lines from %s.\n"

.SECT .BSS
	fdes:		.SPACE 2
	fn:			.SPACE 10
	line:		.SPACE 17
	bin:		.SPACE 2
	bout:		.SPACE 2
	lc:			.SPACE 2
	lineCount:	.SPACE 3
	bc:			.SPACE 3
	hex:		.SPACE 5	! a temp that get's used during the procedures
