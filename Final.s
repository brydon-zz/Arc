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

start:
	PUSH str
	PUSH inGreet
	PUSH _PRINTF
	SYS
	ADD SP,6			! Print a velcome

	MOV DI, fn
	PUSH _GETCHAR
getFile:				! Loopdy loop
	SYS
	CMPB AL,'\n'
	JE doneFile
	STOSB
	JMP getFile			! GET THE test.txt FILENAME store it in fn
doneFile:	
	ADD SP,2
	
	PUSH 0
	PUSH fn
	PUSH _OPEN
	SYS					! Open the file dog.

	ADD SP,6			! reset dat stack

	CMP AX,0			! If this is true, then Err0rz
	JL openError

	MOV (fdes),AX		! Store the destination

	MOV DI,line			! Set DI up so that we can fill a line
	MOV (lc),0
	
	PUSH (lc)
	PUSH 0
	CALL W2H
	PUSH str
	PUSH _PRINTF
	SYS
	ADD SP,8
! The readIn loop effectively grabs each consecutive byte at a time and does stuff to it.
! When it's ready to dump teh byte
readIn:					! here we read in the file 1 byte at a time
	PUSH 1				! we want 1 byte
	PUSH bin			! to store where DI points
	PUSH (fdes)			! from the files current pos
	PUSH _READ	
	SYS					! go!
	ADD SP,8			! reset
	INC (bc)			! Let's count our bytes!
	CMP AX,0			! AX holds the num of bytes read
	JNE 1f			
	STC					! if AX=0 then EOF, so throw the carry flag so we know!
	JMP printIt
1:	PUSH (bin)			! Convert this byte to hexadecimal
	PUSH bout			! Store it here
	CALL B2H			! GO!

	PUSH spacenum
	PUSH _PRINTF
	SYS					! print out our converted byte!
	ADD SP,8
	
	PUSH CX
	CMPB (bin),' '		! We gotta see if our Byte is legal
	JL 1f
	CMPB (bin),127
	JGE 1f
	MOV CX,(bin)		! store the actual text version of the bite so we can pump it out later!
	JMP 2f
1:	MOV CX,'.'
2:	MOV (DI),CX
	POP CX

	CMP DI,line+LINE_LENGTH
	JE printIt
	INC DI				! INC DI
	JMP readIn			! Loop
printIt:				! End of each line
	PUSHF				! we work with the flags, so let's preserve them!

	PUSH line			! put the line of /text/ on the stack
	PUSH pipestr
	PUSH _PRINTF		! and print it out enclosed in pipes | | with a newline
	SYS
	ADD SP,6
	ADD (lc),16			! Inc our lineCount
	MOV DI,line			! reset our DI
	POPF				! let's get our flags back
	INC (lineCount)		! Count our lines
	JC exit				! If we're done, leave
	PUSH (lc)
	PUSH 0
	CALL W2H
	PUSH str
	PUSH _PRINTF		! Print the next lines marker
	SYS
	ADD SP,8

	JMP readIn			! and go!
W2H:
	PUSH BP
	MOV BP,SP

	PUSH AX
	PUSH BX
	PUSH CX
	PUSH DX
	PUSH DI				! put the things on the stack that I'm about to break!

	MOV DX,0
	MOV CX,0
	MOV AX,6(BP)		! set the byte to convert in the AX register
						! We're gonna set convert to hex by repeated division by 16
	MOV BX,256			! now (since we're dealing with one byte) in AX there is the quotient 
	DIV BX				! anPOd in DX there is the remainder

	PUSH AX
	PUSH 0
	CALL B2H			! 4B on stack
	MOV AX,(hex)

	PUSH DX		
	PUSH 0
	CALL B2H			! 4B on stack
	MOV DX,(hex)
	
	ADD SP,8

	MOV (hex),AX
	MOV (hex+2),DX

	MOV 4(BP),hex

	POP DI
	POP DX
	POP CX
	POP BX
	POP AX
	POP BP
	RET
B2H:
	PUSH BP
	MOV BP,SP

	PUSH AX
	PUSH BX
	PUSH CX
	PUSH DX
	PUSH DI				! put the things on the stack that I'm about to break!

	MOV DX,0
	MOV CX,0
	MOV DI,hex			! set it to 0
	MOV AX,6(BP)		! set the byte to convert in the AX register
						! We're gonna set convert to hex by repeated division by 16
	MOV BX,16			! now (since we're dealing with one byte) in AX there is the quotient 
	DIV BX				! and in DX there is the remainder
						! so AXDX is the hex bit!
	CMP AX,9			! So let's see if ax>9
	JG 1f				! If so, go down to label 1
	ADD AX,NUMOFFSET	! else make it into a string
	JMP 2f			
1:	ADD AX,STRINGOFFSET	! If AX is A,B,C,D,E,F then make it into a string!
2:	CMP DX,9			! Now do the same with the remainder!
	JG 1f
	ADD DX,48
	JMP 2f
1:	ADD DX,87
2:	MOV (DI),AX			! And store AX first
	INC DI
	MOV (DI),DX			! Then DX, we've succesfully concatenated AX with DX

	MOV 4(BP),hex		! Put this result in the return val

	POP DI				! re-set the mucked vals
	POP DX
	POP CX
	POP BX
	POP AX	
	POP BP
	RET					! Return

openError:
	PUSH fn
	PUSH errStr
	PUSH _PRINTF
	SYS					! Print out error code
	ADD SP,6

exit:
	PUSH fn
	PUSH (lineCount)
	PUSH (bc)
	PUSH finStr
	PUSH _PRINTF
	SYS
	ADD SP,10			! Print out file stats
	PUSH _EXIT
	SYS

.SECT .DATA
	str: 		.ASCIZ "%s"
	pipestr:	.ASCIZ " |%s|\n"
	spacenum:	.ASCIZ " %s"
	num:	 	.ASCIZ "%d"
	inGreet: 	.ASCIZ "Enter a filename pl0x: "
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
