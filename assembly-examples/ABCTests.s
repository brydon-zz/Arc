	_EXIT = 1
	_PRINTF = 127

.SECT .TEXT
	PUSH inGreet
	PUSH str
	PUSH _PRINTF
	SYS

	ADD SP,6

	MOV DI, num
	MOV AX, 41h

loop:
	CMPB AL, 'Z'
	
	STOSB
	
	DEC DI
	PUSH num
	PUSH str
	PUSH _PRINTF
	SYS
	
	ADD SP,6
	
	JE doneLoop
	INC AX
	JMP loop

doneLoop:

	PUSH goodByeMessage
	PUSH str
	PUSH _PRINTF
	SYS

	ADD SP,6

	PUSH _EXIT
	SYS


.SECT .DATA
	str: 		.ASCIZ "%s\n"
	inGreet:	.ASCIZ "Let's do our ABCS\n"
	goodByeMessage:	.ASCIZ "\nGoodBye."
	
.SECT .BSS
	num:		.SPACE 3
