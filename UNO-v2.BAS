10 REM *** UNO CARD GAME FOR MS-DOS ***
20 REM Written in GW-BASIC
30 REM 
40 REM This program implements the UNO card game with:
50 REM - Color graphics
60 REM - Sound effects
70 REM - Computer players
80 REM - House rules support
90 REM
100 REM *** INITIALIZATION ***
110 REM
120 GOTO 1000 : REM Go to main program
130 REM
140 REM *** GLOBAL VARIABLES ***
150 REM
160 REM CARD ARRAYS
170 REM DECK VARIABLES
180 REM C$ = Deck of all cards string representation
190 REM CV = Deck of all cards values (0-9, 10=Skip, 11=Rev, 12=Draw2, 13=Wild, 14=Draw4)
200 REM CC = Deck of all cards colors (1=Red, 2=Blue, 3=Green, 4=Yellow, 5=Wild)
210 REM 
220 REM PLAYER VARIABLES
230 REM PH(P,X) = Card indices in player P's hand at position X
240 REM PL = Current player (1 to NP)
250 REM NP = Number of players (2-4)
260 REM NC(P) = Number of cards in player P's hand
270 REM
280 REM GAME STATE VARIABLES  
290 REM TD = Top discard card index
300 REM DR = Direction (1=clockwise, -1=counter-clockwise)
310 REM DC = Number of cards in draw pile
320 REM HR(X) = House rules enabled (1=yes, 0=no)
330 REM
340 REM *** SUBROUTINES ***
350 REM
360 REM 5000: Initialize Game
370 REM 6000: Draw Card
380 REM 7000: Display Game State
390 REM 8000: Player Turn
400 REM 9000: Computer Turn
410 REM 10000: Process Card
420 REM 11000: Check Win
430 REM 12000: Sound Effects
440 REM 13000: Display Title
450 REM 14000: House Rules Menu
460 REM 15000: Game Setup
470 REM 17000: Instructions
480 REM 18000: Scoreboard
490 REM 19000: Display Card
500 REM

1000 REM *** MAIN PROGRAM ***
1010 KEY OFF: CLS: RANDOMIZE TIMER
1020 DIM C$(108), CV(108), CC(108) : REM Card descriptions, values, colors
1030 DIM PH(4,20), NC(4), NM$(4) : REM Player hands, hand counts, names (max 4 players, 20 cards)
1040 DIM CL$(5), HR(5), HS$(5) : REM Color names, house rules
1050 REM
1060 REM Set color names
1070 CL$(1) = "RED": CL$(2) = "BLUE": CL$(3) = "GREEN": CL$(4) = "YELLW": CL$(5) = "WILD"
1080 REM
1090 REM Set house rule descriptions
1100 HS$(1) = "Progressive Draw 2/4 (stack drawing cards)" 
1110 HS$(2) = "Jump-In (play identical cards out of turn)"
1120 HS$(3) = "7-0 (swap hands on 7, rotate hands on 0)"
1130 HS$(4) = "No Bluffing on Wild Draw 4"
1140 HS$(5) = "Draw Until You Can Play"
1150 REM
1160 REM Set player names
1170 NM$(1) = "YOU"
1180 NM$(2) = "COM1"
1190 NM$(3) = "COM2"
1200 NM$(4) = "COM3"
1210 REM
1220 REM Initialize house rules to NO
1230 FOR I = 1 TO 5: HR(I) = 0: NEXT I
1240 REM
1250 GOSUB 13000 : REM Display title screen
1260 REM
1270 REM Main game loop
1280 WHILE 1
1290   GOSUB 15000 : REM Game setup
1300   GOSUB 5000  : REM Initialize game
1310   REM
1320   REM Main play loop
1330   GMOVR = 0
1340   WHILE GMOVR = 0
1350     GOSUB 7000 : REM Display game state
1360     IF PL = 1 THEN GOSUB 8000 ELSE GOSUB 9000 : REM Player or computer turn
1370     REM
1380     REM Check for winner
1390     GOSUB 11000
1400     REM
1410     REM Next player (if game not over)
1420     IF GMOVR <> 0 THEN GOTO 1460
1430     IF DR = 1 THEN PL = PL + 1: IF PL > NP THEN PL = 1
1440     IF DR = -1 THEN PL = PL - 1: IF PL < 1 THEN PL = NP
1460   WEND
1470   REM
1480   REM Play again prompt
1490   LOCATE 22, 5: PRINT "Play again? (Y/N)";
1500   K$ = "": WHILE K$ = "": K$ = INKEY$: WEND
1510   IF K$ <> "Y" THEN END
1520 WEND
1530 END

5000 REM *** INITIALIZE GAME ***
5010 CLS
5020 PRINT "Setting up game..."
5030 REM
5040 REM Create card deck
5050 CNT = 1 : REM Card counter
5060 REM
5070 REM Create number cards (0-9) for each color
5080 FOR CLR = 1 TO 4
5090   REM Add one zero card per color
5100   C$(CNT) = "0 " + CL$(CLR)
5110   CV(CNT) = 0: CC(CNT) = CLR: CNT = CNT + 1
5120   REM
5130   REM Add two of each 1-9 card per color
5140   FOR N = 1 TO 9
5150     FOR D = 1 TO 2
5160       C$(CNT) = STR$(N) + " " + CL$(CLR)
5170       CV(CNT) = N: CC(CNT) = CLR: CNT = CNT + 1
5180     NEXT D
5190   NEXT N
5200 NEXT CLR
5210 REM
5220 REM Create special cards for each color
5230 FOR CLR = 1 TO 4
5240   REM Add two Skip, Reverse, Draw 2 cards per color
5250   FOR D = 1 TO 2
5260     REM Skip cards
5270     C$(CNT) = "SKIP " + CL$(CLR)
5280     CV(CNT) = 10: CC(CNT) = CLR: CNT = CNT + 1
5290     REM Reverse cards
5300     C$(CNT) = "REV " + CL$(CLR)
5310     CV(CNT) = 11: CC(CNT) = CLR: CNT = CNT + 1
5320     REM Draw 2 cards
5330     C$(CNT) = "D2 " + CL$(CLR)
5340     CV(CNT) = 12: CC(CNT) = CLR: CNT = CNT + 1
5350   NEXT D
5360 NEXT CLR
5370 REM
5380 REM Create wild cards
5390 FOR D = 1 TO 4
5400   REM Wild cards
5410   C$(CNT) = "WILD"
5420   CV(CNT) = 13: CC(CNT) = 5: CNT = CNT + 1
5430   REM Wild Draw 4 cards
5440   C$(CNT) = "W+4"
5450   CV(CNT) = 14: CC(CNT) = 5: CNT = CNT + 1
5460 NEXT D
5470 REM
5480 REM Total number of cards initialized 
5490 PRINT "Initialized"; CNT-1; "cards"
5500 TCARD = CNT - 1
5510 REM
5520 REM Shuffle cards - using Fisher-Yates algorithm
5530 PRINT "Shuffling deck...";
5540 FOR I = TCARD TO 2 STEP -1
5550   J = INT(RND * I) + 1 : REM Random card from remaining deck
5560   REM Swap cards I and J
5570   TMP$ = C$(I): C$(I) = C$(J): C$(J) = TMP$
5580   TMPV = CV(I): CV(I) = CV(J): CV(J) = TMPV
5590   TMPC = CC(I): CC(I) = CC(J): CC(J) = TMPC
5600 NEXT I
5610 REM
5620 REM Deal cards to players
5630 PRINT "Dealing cards...";
5640 REM Clear hands
5650 FOR P = 1 TO NP
5660   NC(P) = 0
5670 NEXT P
5680 REM 
5690 REM Track current card position in deck
5700 CPOS = 1
5710 REM
5720 REM Deal 7 cards to each player
5730 FOR I = 1 TO 7
5740   FOR P = 1 TO NP
5750     NC(P) = NC(P) + 1
5760     PH(P, NC(P)) = CPOS : REM Store index of card
5770     CPOS = CPOS + 1
5780   NEXT P
5790 NEXT I
5800 REM
5810 REM Set up discard pile with top card
5820 REM Make sure first card isn't a wild
5830 TD = CPOS : REM Top discard is next card
5840 IF CC(TD) <> 5 THEN GOTO 5940
5850   REM Find first non-wild card to swap with
5860   FOR I = CPOS + 1 TO TCARD
5870     IF CC(I) <> 5 THEN GOTO 5880 ELSE GOTO 5930
5880       TMP$ = C$(TD): C$(TD) = C$(I): C$(I) = TMP$
5890       TMPV = CV(TD): CV(TD) = CV(I): CV(I) = TMPV
5900       TMPC = CC(TD): CC(TD) = CC(I): CC(I) = TMPC
5910       GOTO 5940
5930   NEXT I
5940 REM
5950 REM Advance past the discard card
5960 CPOS = CPOS + 1
5970 REM
5980 REM Set draw pile count
5990 DC = TCARD - CPOS + 1 : REM Cards remaining in draw pile
6000 REM
6010 REM Initialize game variables
6020 DR = 1 : REM Direction (1=clockwise, -1=counter-clockwise)
6030 PL = 1 : REM Player 1 (human) goes first
6040 LSTCD = 0 : REM Last card played
6050 REM
6060 REM Process the first card effects (Skip, Reverse, Draw 2)
6070 IF CV(TD) <> 10 THEN GOTO 6130
6080   PRINT "First card is Skip! Player 2 misses a turn."
6090   IF NP = 2 THEN GOTO 6120
6100   PL = 2 : REM Skip to player 3
6120   GOSUB 12000 : REM Sound effect
6121   FOR I = 1 TO 2000: NEXT I
6130 REM
6140 IF CV(TD) <> 11 THEN GOTO 6270
6150   PRINT "First card is Reverse! Direction is counter-clockwise."
6160   DR = -1
6170   IF NP <> 2 THEN GOTO 6220
6180     REM In 2-player game, acts like Skip
6190     PRINT "With 2 players, Reverse acts like Skip."
6200     GOTO 6250
6220     REM Last player goes first
6230     PL = NP
6250   GOSUB 12000 : REM Sound effect
6260   FOR I = 1 TO 2000: NEXT I
6270 REM
6280 IF CV(TD) <> 12 THEN GOTO 6480
6290   PRINT "First card is Draw 2! Player 2 draws 2 cards."
6300   GOSUB 12000 : REM Sound effect
6310   REM Find who draws
6320   DRWPL = 2 : REM Usually player 2
6330   IF NP = 2 AND DR = -1 THEN DRWPL = 1 : REM 2-player reverse means player 1 draws
6340   REM
6350   REM Player draws 2 cards
6360   FOR I = 1 TO 2
6370     REM Add card to player's hand
6380     NC(DRWPL) = NC(DRWPL) + 1
6390     PH(DRWPL, NC(DRWPL)) = CPOS
6400     CPOS = CPOS + 1
6410     DC = DC - 1
6420   NEXT I
6430   REM
6440   REM That player also loses a turn
6450   IF NP = 2 THEN GOTO 6470
6460   PL = 2 : REM Skip to player 3
6470   FOR I = 1 TO 2000: NEXT I
6480 REM
6490 RETURN

7000 REM *** DISPLAY GAME STATE ***
7010 CLS
7020 REM
7030 REM Display top card
7040 LOCATE 4, 30
7050 CID = TD : REM Card to display
7060 GOSUB 19000 : REM Display card
7070 REM
7080 REM Display direction
7090 IF DR <> 1 THEN GOTO 7120
7100   LOCATE 6, 40: PRINT "-> CLOCKWISE ->"
7110   GOTO 7130
7120   LOCATE 6, 40: PRINT "<- COUNTER <-"
7130 REM
7140 REM Display draw pile
7150 LOCATE 4, 55: PRINT "+------+"
7160 LOCATE 5, 55: PRINT "| DRAW |"
7170 LOCATE 6, 55: PRINT "| PILE |"
7180 LOCATE 7, 55: PRINT "|      |"
7190 LOCATE 8, 55: PRINT "| " + STR$(DC) + "    |"
7200 LOCATE 9, 55: PRINT "+------+"
7210 REM
7220 REM Display player info
7230 FOR P = 1 TO NP
7240   IF P <> 1 THEN GOTO 7270
7250     ROW = 15: COL = 30
7260     GOTO 7330
7270   IF P <> 2 THEN GOTO 7300
7280     ROW = 7: COL = 10
7290     GOTO 7330
7300   IF P <> 3 THEN GOTO 7320
7310     ROW = 2: COL = 30: GOTO 7330
7320     ROW = 7: COL = 50
7330   REM Highlight current player
7340   IF P <> PL THEN GOTO 7370
7350     LOCATE ROW, COL - 2: PRINT ">" + NM$(P) + "<"
7360     GOTO 7380
7370     LOCATE ROW, COL - 2: PRINT " " + NM$(P) + " "
7380   LOCATE ROW + 1, COL - 2: PRINT "Cards:" + STR$(NC(P))
7390 NEXT P
7400 REM
7410 REM Display player's hand
7420 IF PL <> 1 THEN GOTO 7640
7430   LOCATE 17, 5: PRINT "Your hand:"
7440   FOR I = 1 TO NC(1)
7450     COL = 5 + (I - 1) * 7
7460     IF COL <= 75 THEN GOTO 7520
7470       REM Wrap to next line if too many cards
7480       ROW = 19 + INT((I - 1) * 7 / 70)
7490       COL = 5 + ((I - 1) * 7) MOD 70
7500       GOTO 7530
7520       ROW = 19
7530     REM
7540     REM Display card
7550     CID = PH(1, I) : REM Card index to display
7560     X = COL : Y = ROW
7570     GOSUB 19100 : REM Display mini card
7580     REM
7590     REM Show card number under it
7600     LOCATE Y + 3, X + 1: PRINT I;
7610   NEXT I
7640 REM
7650 RETURN

8000 REM *** PLAYER TURN ***
8010 LOCATE 22, 5: PRINT "Your turn! (D)raw card, (P)lay card, or (U)no declaration"
8020 REM
8030 REM Check if player has one card and should say UNO
8040 IF NC(1) = 1 AND LSTCD = 0 THEN SHUNO = 1 ELSE SHUNO = 0
8050 REM
8060 REM Get player input
8070 K$ = "": WHILE K$ = "": K$ = INKEY$: WEND
8075 REM Ensure K$ is not empty before applying UCASE$
8080 IF K$ <> "" THEN K1$ = K$ ELSE K1$ = ""
8085 REM Use K1$ instead of K$ for comparisons
8090 REM
8100 IF K1$ <> "D" THEN GOTO 8580
8110   REM Player draws a card
8120   IF DC <= 0 THEN GOTO 8550
8130     LOCATE 23, 5: PRINT "You draw a card."
8140     REM Add card to hand
8150     NC(1) = NC(1) + 1
8160     PH(1, NC(1)) = CPOS
8170     CPOS = CPOS + 1
8180     DC = DC - 1
8190     REM
8200     REM If house rule 5 is enabled (Draw until can play), keep drawing
8210     IF HR(5) <> 1 THEN GOTO 8430
8220       CANPL = 0
8230       REM Check if any card can be played
8240       FOR I = 1 TO NC(1)
8250         REM Card can be played if:
8260         REM - Same color as top discard
8270         REM - Same value as top discard
8280         REM - It's a wild card
8290         CID = PH(1, I)
8300         IF CC(CID) = CC(TD) OR CV(CID) = CV(TD) OR CC(CID) = 5 THEN CANPL = 1: GOTO 8350
8340       NEXT I
8350       REM
8360       REM If can't play any card, draw another
8370       IF CANPL <> 0 OR DC <= 0 THEN GOTO 8430
8380         LOCATE 23, 25: PRINT "You can't play. Draw again."
8390         FOR I = 1 TO 1000: NEXT I
8400         GOTO 8110 : REM Draw again
8430     REM
8440     REM Show the drawn card
8450     LOCATE 23, 25
8460     CID = PH(1, NC(1))
8470     COLR = CC(CID)
8480     COLOR COLR + 1
8490     PRINT "You drew: " + C$(CID)
8500     COLOR 7
8510     REM
8520     REM Sound effect
8530     GOSUB 12000
8540     GOTO 8570
8550     LOCATE 23, 5: PRINT "Draw pile is empty! Reshuffling discard pile..."
8560     REM TODO: Implement reshuffling discard
8570   GOTO 8760
8580 IF K1$ <> "P" THEN GOTO 8740
8590   REM Player tries to play a card
8600   LOCATE 23, 5: PRINT "Enter card number: ";
8610   INPUT CN
8620   REM
8630   REM Validate card number
8640   IF CN < 1 OR CN > NC(1) THEN GOTO 8670
8650     GOTO 8690
8670     LOCATE 23, 5: PRINT "Invalid card number! Try again.           "
8680     FOR I = 1 TO 1000: NEXT I: GOTO 8060 : REM Try again
8690   REM
8700   REM Check if card is playable
8710   REM Card can be played if:
8720   REM - Same color as top discard
8730   REM - Same value as top discard
8740   REM - It's a wild card
8750   CDOK = 0
8760   CID = PH(1, CN)
8770   IF CC(CID) = CC(TD) OR CV(CID) = CV(TD) OR CC(CID) = 5 THEN CDOK = 1
8780   REM
8790   REM Check special case for Wild Draw 4
8800   IF CV(CID) <> 14 OR HR(4) <> 1 THEN GOTO 8950
8810     REM In "No Bluffing" house rule, can only play Wild+4 if no matching color
8820     HCLR = 0
8830     FOR I = 1 TO NC(1)
8840       TMPC = PH(1, I)
8850       IF I <> CN AND CC(TMPC) = CC(TD) THEN HCLR = 1: GOTO 8870
8860       REM CONTINUE
8870     NEXT I
8880     REM
8890     IF HCLR <> 1 THEN GOTO 8950
8900       LOCATE 23, 5: PRINT "You have matching colors! Can't play Wild+4"
8910       FOR I = 1 TO 2000: NEXT I
8920       CDOK = 0
8950   REM
8960   IF CDOK <> 1 THEN GOTO 9010
8970     REM Card is playable, process it
8980     LOCATE 23, 5: PRINT "You played: " + C$(CID) + SPACE$(20)
8990     REM
9000     REM If it's a wild card, ask for color
9010     IF CC(CID) <> 5 THEN GOTO 9230
9020       LOCATE 24, 5: PRINT "Choose color: (R)ed, (B)lue, (G)reen, (Y)ellow"
9030       K$ = "": WHILE K$ = "": K$ = INKEY$: WEND
9035       REM Safe UCASE$ handling
9040       IF K$ <> "" THEN K$ = K$ ELSE K$ = ""
9050       REM
9060       REM Safe UCASE$ for color selection
9065       IF K$ <> "" THEN K2$ = K$ ELSE K2$ = ""
9070       IF K2$ <> "R" THEN GOTO 9090
9075         NCOL = 1
9080         GOTO 9210
9090       IF K2$ <> "B" THEN GOTO 9120
9100         NCOL = 2
9110         GOTO 9210
9120       IF K2$ <> "G" THEN GOTO 9150
9130         NCOL = 3
9140         GOTO 9210
9150       IF K2$ <> "Y" THEN GOTO 9180
9160         NCOL = 4
9170         GOTO 9210
9180         REM Default to red if invalid
9190         NCOL = 1
9210       REM Update the card's color
9220       CC(CID) = NCOL
9221       LOCATE 24, 5: PRINT "You chose " + CL$(NCOL) + SPACE$(30)
9230     REM
9240     REM Move card to discard pile
9250     TD = CID
9260     REM Remove card from hand
9270     FOR I = CN TO NC(1) - 1
9280       PH(1, I) = PH(1, I + 1)
9290     NEXT I
9300     NC(1) = NC(1) - 1
9310     REM
9320     REM Process card effects
9330     GOSUB 10000
9340     REM
9350     REM Sound effect
9360     GOSUB 12000
9370     REM
9380     REM Check if should have called UNO
9390     IF SHUNO <> 1 OR NC(1) <> 0 THEN GOTO 9510
9400       LOCATE 23, 5: PRINT "You forgot to call UNO! Draw 2 penalty cards."
9410       REM Draw 2 penalty cards
9420       FOR I = 1 TO 2
9430         IF DC <= 0 THEN GOTO 9480
9440           NC(1) = NC(1) + 1
9450           PH(1, NC(1)) = CPOS
9460           CPOS = CPOS + 1
9470           DC = DC - 1
9480       NEXT I
9490       FOR I = 1 TO 2000: NEXT I
9510     RETURN
9520   GOTO 9010
9530     LOCATE 23, 5: PRINT "You can't play that card! Try again.           "
9540     FOR I = 1 TO 1000: NEXT I
9550     GOTO 8060 : REM Try again
9740 IF K1$ <> "U" THEN GOTO 8010
9750   REM Player declares UNO
9760   LOCATE 23, 5: PRINT "UNO!" + SPACE$(40)
9770   PLAY "L16 C D E F G"
9780   LSTCD = 1
9790   FOR I = 1 TO 1000: NEXT I
9800   REM Return to turn options
9810   GOTO 8010
9820 REM
9830 RETURN

10000 REM *** PROCESS CARD EFFECTS ***
10010 REM Process effects of the card just played (TD)
10020 REM
10030 REM Skip
10040 IF CV(TD) <> 10 THEN GOTO 10180
10050   REM Skip next player
10060   LOCATE 24, 5: PRINT "SKIP! Next player misses a turn."
10070   IF NP <> 2 THEN GOTO 10100
10080     REM In 2-player, skip back to current player
10090     GOTO 10170
10100     REM Skip next player
10110     IF DR <> 1 THEN GOTO 10140
10120       PL = PL + 1: IF PL > NP THEN PL = 1
10130       GOTO 10170
10140       PL = PL - 1: IF PL < 1 THEN PL = NP
10170   RETURN
10180 REM
10190 REM Reverse
10200 IF CV(TD) <> 11 THEN GOTO 10320
10210   REM Reverse direction
10220   LOCATE 24, 5: PRINT "REVERSE! Direction changes."
10230   DR = -DR : REM Flip direction
10240   REM
10250   REM In 2-player game, Reverse acts like Skip
10260   IF NP <> 2 THEN GOTO 10300
10270     REM Skip next player (back to current player)
10280     LOCATE 24, 25: PRINT "With 2 players, Reverse acts like Skip."
10290     GOTO 10310
10300     REM No special handling for multi-player
10310   RETURN
10320 REM
10330 REM Draw 2
10340 IF CV(TD) <> 12 THEN GOTO 10620
10350   REM Next player draws 2 cards
10360   NXPL = PL
10370   IF DR <> 1 THEN GOTO 10400
10380     NXPL = PL + 1: IF NXPL > NP THEN NXPL = 1
10390     GOTO 10420
10400     NXPL = PL - 1: IF NXPL < 1 THEN NXPL = NP
10420   REM
10430   LOCATE 24, 5: PRINT "DRAW 2! Player " + STR$(NXPL) + " draws 2 cards."
10440   REM Draw 2 cards
10450   FOR I = 1 TO 2
10460     REM Check if draw pile has cards
10470     IF DC > 0 THEN GOTO 10520
10480       LOCATE 24, 35: PRINT "Draw pile empty!"
10490       GOTO 10570
10520     REM Draw a card
10530     NC(NXPL) = NC(NXPL) + 1
10540     PH(NXPL, NC(NXPL)) = CPOS
10550     CPOS = CPOS + 1
10560     DC = DC - 1
10570   NEXT I
10580   REM
10590   REM That player also loses a turn
10600   PL = NXPL
10610   RETURN
10620 REM
10630 REM Wild Draw 4
10640 IF CV(TD) <> 14 THEN GOTO 10930
10650   REM Next player draws 4 cards
10660   NXPL = PL
10670   IF DR <> 1 THEN GOTO 10700
10680     NXPL = PL + 1: IF NXPL > NP THEN NXPL = 1
10690     GOTO 10720
10700     NXPL = PL - 1: IF NXPL < 1 THEN NXPL = NP
10720   REM
10730   LOCATE 24, 5: PRINT "WILD DRAW 4! Player " + STR$(NXPL) + " draws 4 cards."
10740   REM Draw 4 cards
10750   FOR I = 1 TO 4
10760     REM Check if draw pile has cards
10770     IF DC > 0 THEN GOTO 10820
10780       LOCATE 24, 35: PRINT "Draw pile empty!"
10790       GOTO 10870
10820     REM Draw a card
10830     NC(NXPL) = NC(NXPL) + 1
10840     PH(NXPL, NC(NXPL)) = CPOS
10850     CPOS = CPOS + 1
10860     DC = DC - 1
10870   NEXT I
10880   REM
10890   REM That player also loses a turn
10900   PL = NXPL
10910   RETURN
10930 REM No special effects for other cards
10940 RETURN

11000 REM *** CHECK WIN ***
11010 REM Check if any player has won
11020 FOR P = 1 TO NP
11030   IF NC(P) <> 0 THEN GOTO 11190
11040     REM This player has won
11050     CLS
11060     IF P <> 1 THEN GOTO 11100
11070       LOCATE 10, 30: PRINT "YOU WIN!!!"
11080       PLAY "O3 L8 C E G >C"
11090       GOTO 11120
11100       LOCATE 10, 30: PRINT "PLAYER " + STR$(P) + " WINS!"
11110       PLAY "O2 L8 E C"
11120     REM
11130     LOCATE 12, 20: PRINT "Press any key to continue..."
11140     K$ = "": WHILE K$ = "": K$ = INKEY$: WEND
11150     GMOVR = 1
11160     RETURN
11190 NEXT P
11200 RETURN

12000 REM *** SOUND EFFECTS ***
12010 REM Different sounds for different cards
12020 REM
12030 REM Skip
12040 IF CV(TD) = 10 THEN PLAY "L16 C D E F G"
12050 REM
12060 REM Reverse
12070 IF CV(TD) = 11 THEN PLAY "L16 G F E D C"
12080 REM
12090 REM Draw 2
12100 IF CV(TD) = 12 THEN PLAY "L8 C C"
12110 REM
12120 REM Wild
12130 IF CV(TD) = 13 THEN PLAY "L8 C E G"
12140 REM
12150 REM Wild Draw 4
12160 IF CV(TD) = 14 THEN PLAY "L8 C E G >C"
12170 REM
12180 REM Regular number card
12190 IF CV(TD) >= 0 AND CV(TD) <= 9 THEN PLAY "L16 C"
12200 REM
12210 RETURN

13000 REM *** DISPLAY TITLE ***
13010 CLS
13020 LOCATE 5, 30: PRINT "U N O"
13030 LOCATE 7, 20: PRINT "The Classic Card Game"
13040 LOCATE 9, 15: PRINT "Implemented in GW-BASIC for MS-DOS"
13050 REM
13060 LOCATE 12, 15
13070 COLOR 4: PRINT "RED ";
13080 COLOR 1: PRINT "BLUE ";
13090 COLOR 2: PRINT "GREEN ";
13100 COLOR 6: PRINT "YELLOW"
13110 COLOR 7
13120 REM
13130 LOCATE 15, 10: PRINT "1. Start New Game"
13140 LOCATE 16, 10: PRINT "2. House Rules"
13150 LOCATE 17, 10: PRINT "3. Instructions"
13160 LOCATE 18, 10: PRINT "4. Quit"
13170 REM
13180 REM Get menu choice
13190 LOCATE 20, 10: PRINT "Enter your choice (1-4): ";
13200 INPUT C
13210 IF C = 1 THEN RETURN
13220 IF C = 2 THEN GOSUB 14000: GOTO 13000
13230 IF C = 3 THEN GOSUB 17000: GOTO 13000
13240 IF C = 4 THEN END
13250 GOTO 13000

14000 REM *** HOUSE RULES MENU ***
14010 CLS
14020 LOCATE 5, 30: PRINT "HOUSE RULES"
14030 LOCATE 7, 10: PRINT "Customize game rules:"
14040 REM
14050 REM Display current settings
14060 FOR I = 1 TO 5
14070   LOCATE 9 + I, 10
14080   PRINT STR$(I) + ". " + HS$(I)
14090   LOCATE 9 + I, 60
14100   IF HR(I) <> 1 THEN GOTO 14130
14110     PRINT "ENABLED"
14120     GOTO 14140
14130     PRINT "DISABLED"
14140 NEXT I
14150 REM
14160 LOCATE 17, 10: PRINT "0. Return to main menu"
14170 REM
14180 LOCATE 19, 10: PRINT "Enter rule number to toggle (0-5): ";
14190 INPUT R
14200 REM
14210 IF R = 0 THEN RETURN
14220 IF R < 1 OR R > 5 THEN GOTO 14270
14230   REM Toggle rule status
14240   IF HR(R) = 0 THEN HR(R) = 1 ELSE HR(R) = 0
14270 GOTO 14000

15000 REM *** GAME SETUP ***
15010 CLS
15020 LOCATE 5, 30: PRINT "GAME SETUP"
15030 REM
15040 REM Number of players
15050 LOCATE 8, 10: PRINT "How many players (2-4)? ";
15060 INPUT NP
15070 IF NP < 2 THEN NP = 2
15080 IF NP > 4 THEN NP = 4
15090 REM
15100 RETURN

17000 REM *** INSTRUCTIONS ***
17010 CLS
17020 LOCATE 3, 30: PRINT "HOW TO PLAY UNO"
17030 LOCATE 5, 5: PRINT "OBJECTIVE:"
17040 LOCATE 6, 10: PRINT "Be the first player to get rid of all your cards!"
17050 REM
17060 LOCATE 8, 5: PRINT "CARD TYPES:"
17070 LOCATE 9, 10: PRINT "Number cards (0-9): Play on matching color or number"
17080 LOCATE 10, 10: PRINT "Skip: Next player loses a turn"
17090 LOCATE 11, 10: PRINT "Reverse: Change direction of play"
17100 LOCATE 12, 10: PRINT "Draw 2: Next player draws 2 cards and loses a turn"
17110 LOCATE 13, 10: PRINT "Wild: Change the current color"
17120 LOCATE 14, 10: PRINT "Wild Draw 4: Change color AND next player draws 4 cards"
17130 REM
17140 LOCATE 16, 5: PRINT "PLAYING THE GAME:"
17150 LOCATE 17, 10: PRINT "1. Each player gets 7 cards"
17160 LOCATE 18, 10: PRINT "2. Match the top card by color or number"
17170 LOCATE 19, 10: PRINT "3. If you can't play, draw a card"
17180 LOCATE 20, 10: PRINT "4. When you have 1 card left, call UNO!"
17190 LOCATE 21, 10: PRINT "5. First player to get rid of all cards wins"
17200 REM
17210 LOCATE 23, 10: PRINT "Press any key to continue..."
17220 K$ = "": WHILE K$ = "": K$ = INKEY$: WEND
17230 RETURN

19000 REM *** DISPLAY CARD (NORMAL SIZE) ***
19010 LOCATE 4, 30: PRINT "+------+"
19020 LOCATE 5, 30: PRINT "|      |"
19030 LOCATE 6, 30: PRINT "| TOP  |"
19040 LOCATE 7, 30
19050 COLR = CC(CID)
19060 COLOR COLR + 1
19070 PRINT "| " + LEFT$(C$(CID) + "    ", 4) + " |"
19080 COLOR 7
19090 LOCATE 8, 30: PRINT "|      |"
19095 LOCATE 9, 30: PRINT "+------+"
19097 RETURN
19100 REM *** DISPLAY MINI CARD ***
19110 LOCATE Y, X: PRINT "+--+"
19120 LOCATE Y + 1, X
19130 COLR = CC(CID)
19140 COLOR COLR + 1
19150 CT$ = LEFT$(C$(CID) + "  ", 2)
19160 PRINT "|" + CT$ + "|"
19170 COLOR 7
19180 LOCATE Y + 2, X: PRINT "+--+"
19190 RETURN

9000 REM *** COMPUTER TURN ***
9010 REM Simple computer player AI
9020 LOCATE 22, 5: PRINT "Computer player " + STR$(PL) + " is thinking..."
9030 FOR I = 1 TO 2000: NEXT I
9040 REM
9050 REM Try to play a card first
9060 PLAYD = 0
9070 CARDT = 0
9080 REM Look for matching cards in hand
9090 FOR C = 1 TO NC(PL)
9100   REM Get card info
9110   CID = PH(PL, C)
9120   REM Check if card can be played
9130   IF CC(CID) <> CC(TD) AND CV(CID) <> CV(TD) AND CC(CID) <> 5 THEN GOTO 9180
9140     PLAYD = 1
9150     CARDT = C
9160     GOTO 9190
9180 NEXT C
9190 REM
9200 IF PLAYD <> 1 THEN GOTO 9640
9210   REM Computer found a card to play
9220   CID = PH(PL, CARDT)
9230   LOCATE 23, 5
9240   PRINT "Computer plays: " + C$(CID)
9250   REM If it's a wild, choose a color
9260   IF CC(CID) <> 5 THEN GOTO 9430
9270     REM Choose most frequent color in hand
9280     C1 = 0: C2 = 0: C3 = 0: C4 = 0
9290     FOR I = 1 TO NC(PL)
9300       TMPC = PH(PL, I)
9310       IF CC(TMPC) = 1 THEN C1 = C1 + 1
9320       IF CC(TMPC) = 2 THEN C2 = C2 + 1
9330       IF CC(TMPC) = 3 THEN C3 = C3 + 1
9340       IF CC(TMPC) = 4 THEN C4 = C4 + 1
9350     NEXT I
9360     REM Find max
9370     BEST = 1
9380     IF C2 > C1 THEN BEST = 2
9390     IF C3 > C2 AND C3 > C1 THEN BEST = 3
9400     IF C4 > C3 AND C4 > C2 AND C4 > C1 THEN BEST = 4
9410     CC(CID) = BEST
9420     LOCATE 23, 35: PRINT "Computer chose " + CL$(BEST)
9430   REM
9440   REM Move card to discard pile
9450   TD = CID
9460   REM Remove card from hand
9470   FOR I = CARDT TO NC(PL) - 1
9480     PH(PL, I) = PH(PL, I + 1)
9490   NEXT I
9500   NC(PL) = NC(PL) - 1
9510   REM
9520   REM Check if computer should declare UNO
9530   IF NC(PL) <> 1 THEN GOTO 9570
9540     LOCATE 23, 5: PRINT "Computer declares: UNO!"
9550     PLAY "L16 C D E F G"
9570   REM
9580   REM Process card effects
9590   GOSUB 10000
9600   REM
9610   REM Sound effect
9620   GOSUB 12000
9630   GOTO 10030
9640   REM Computer must draw a card
9650   LOCATE 23, 5: PRINT "Computer draws a card"
9660   IF DC <= 0 THEN GOTO 10000
9670     NC(PL) = NC(PL) + 1
9680     PH(PL, NC(PL)) = CPOS
9690     CPOS = CPOS + 1
9700     DC = DC - 1
9710     REM
9720     REM If house rule 5 is enabled (Draw until can play), try again
9730     IF HR(5) <> 1 THEN GOTO 10000
9740       REM Try to play the card just drawn
9750       CID = PH(PL, NC(PL))
9760       IF CC(CID) <> CC(TD) AND CV(CID) <> CV(TD) AND CC(CID) <> 5 THEN GOTO 10000
9770         LOCATE 23, 5: PRINT "Computer plays drawn card: " + C$(CID)
9780         REM If it's a wild, choose a color
9790         IF CC(CID) <> 5 THEN GOTO 9860
9800           REM Choose a random color 1-4
9810           BEST = INT(RND * 4) + 1
9820           CC(CID) = BEST
9830           LOCATE 23, 40: PRINT "Computer chose " + CL$(BEST)
9860         REM
9870         REM Move card to discard pile
9880         TD = CID
9890         REM Remove card from hand
9900         NC(PL) = NC(PL) - 1
9910         REM
9920         REM Process card effects
9930         GOSUB 10000
9940         REM
9950         REM Sound effect
9960         GOSUB 12000
9970         GOTO 10030
10000     LOCATE 23, 30: PRINT "Draw pile is empty!"
10030 REM
10040 REM End of computer turn
10050 FOR I = 1 TO 2000: NEXT I
10060 RETURN