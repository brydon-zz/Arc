	_EXIT = 1
	_PRINTF = 127
	_GETCHAR = 117

.SECT .TEXT
	PUSH str
	PUSH inGreet
	PUSH _PRINTF
	SYS

	MOV DI, num
	MOV AX, 41h

loop:
	CMPB AL, 'Z'
	
	STOSB
	
	DEC DI
	PUSH dig
	PUSH num
	PUSH _PRINTF
	SYS
	
	ADD SP,6
	
	JE doneLoop
	INC AX
	JMP loop

doneLoop:
	ADD SP,2

	PUSH str
	PUSH goodByeMessage
	PUSH _PRINTF
	SYS

	ADD SP,6

	PUSH _EXIT
	SYS


.SECT .DATA
	str: 		.ASCIZ "%s\n"
	inGreet:	.ASCIZ "Let's do our ABCS\n"
	dig:		.ASCIZ "%d\n"
	goodByeMessage:	.ASCIZ "\nGoodBye."
	goodByeMessage2:.ASCIZ "\nGet Lost."
	goodByeMessage3:.ASCIZ "\nGo Away."
	goodByeMessage4:.ASCIZ "\nLeave Now."
	goodByeMessage5:.ASCIZ "\nBuzz off."
	
.SECT .BSS
	num:		.SPACE 3
