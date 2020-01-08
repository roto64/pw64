# PilotWings 64 Mission (Task) Editing Tools

UPWT is internal code for (what we believe to be) "Ultravision PilotWings Task". This was deduced based on various strings throughout the ROM.

A UPWT "file" is a form of "container" with definitions for things such as the level model to load, the vehicle to be used, weather/time, a task's objects (e.g. how many Balloons or Rings are loaded in test), takeoff/landing locations, level end destinations, etc.
A UPWT file is complimentary to UWPL which sets up some environmental things such as Audio triggers, Birdman Bonus star, "toys" (animated objects such as Oil Pump or water wheel), etc.

This repo contains some rough code to help understand and modify UPWT data and some scripts are described below.

## pw64_upwt_parser.py
A script to dump and translate various facts about individual game missions (called "Test" in game, "tasks" in game code).
It will give you floating point coordinates of objects (such as Rings/Ballons/Landing Strips/etc).
It will show information about each specific object(ive) if there are multiples such as >1 Ring.
It will attempt to decode the object attributes ("what color is the balloon?", "how big is the ring?").
This code now also dumps out a rough approximation of the task data (UPWT setup) to JSON format with the extension of the given Task ID (e.g. "E_GC_1.json")

Here's a parsed representation of the Beginner RocketPack level, it's various attributes, some coordinates for things, and the target object (Balloon) the task contains:
```-------
Marker: FORM
	Length: 00000590
	Data Offset: 0x3533bc
-------
Marker: UPWT
	Length: 0
	Data Offset: 0x3533bc
-------
Marker: PAD 
	Length: 00000004
	Data Offset: 0x3533c8
-------
Marker: JPTX
	Length: 00000008
	Data Offset: 0x3533d4
		* Test ID: E_RP_1

		* Test Name (E_RP_1_N) and Mission Text / Message (E_RP_1_M):
		----------------------------------
		 Balloon Crash
		----------------------------------
		 Hit the balloon floating above
		 the castle and land on the
		 landing point.
		 You must hit the balloon to
		 receive time points.
		----------------------------------
-------
Marker: NAME
	Length: 00000008
	Data Offset: 0x3533e4
		Data: RP Exp
-------
Marker: INFO
	Length: 00000040
	Data Offset: 0x3533f4
		Data: pop the balloon land and land on the designated landing area
-------
Marker: COMM
	Length: 00000430
	Data Offset: 0x35343c
		Data: 
			Array Index | Data         | Data Description
			---------------------------------------------
			    (0)       00010000       Pilot Class / Vehicle / Test Number / Level
			    (1)       02000000       
			    (2)       01000000       Weather (Time of Day) / Snow
			    (3)       3f800000       
			    (4)       00000000       West/East Wind
			    (5)       00000000       South/North Wind
			    (6)       00000000       Up/Down Wind
			    (7)       00000000       
			    (8)       00000000       
			    (9)       00000000       
			    (10)       00000000       
			    (11)       c3e60000       
			    (12)       c37f0000       
			    (13)       00000000       
			    (14)       c28c0000       
			    (15)       43aa0000       
			    (16)       43390000       
			    (17)       00000000       
			    (18)       00000006       
			    (19)       00000000       
			    (20)       41f00000       
			    (21)       40400000       
			    (22)       41f00000       
			    (23)       41000000       
			    (24)       41a00000       
			    (25)       41900000       
			    (26)       41200000       
			    (27)       41c80000       
			    (28)       40a00000       
			    (29)       41c80000       
			    <... Snip a bunch of stuff for shorter example ...>  
			    (259)       00000000       
			    (260)       00000000       
			    (261)       40000000       
			    (262)       00000000       
			    (263)       00000101       THER / LWND / TPAD / LPAD
			    (264)       00000100       LSTP / RNGS / BALS / TARG
			    (265)       00000000       HPAD / BTGT / PHTS / FALC
			    (266)       00000000       UNKNOWN / CNTG / HOPD
			    (267)       00000000       
	-------
	Mission / Test Details:
		Class: Beginner (00)
		Vehicle: Rocket Pack (01)
		Test Number: 1 (00)
		Level: Holiday Island (00)
		Weather / Time: Sunny Part 2 (01)
	-------
	Mission Parameters:
		Hang Glider Thermals: 0
		Local Winds: 0
		Takeoff Pads/Strips: 1
		Landing Pads: 1
		Landing Strips: 0
		Rings: 0
		Balloons: 1
		Rocket Targets: 0
		Floating Pads: 0
		Ball Targets: 0
		Photo Targets: 0
		"Falcos Domains" (Meca Hawk): 0
		UNKNOWN: 0
		Cannon Targets: 0
		Jumble Hopper Goals: 0
-------
Marker: TPAD
	Length: 00000030
	Data Offset: 0x353874
		X: -463.26001
		Y: 5.0
		Z: 27.2873
		Yaw: -39.0
		Pitch: 0.0
		Roll: 0.0
-------
Marker: LPAD
	Length: 00000030
	Data Offset: 0x3538ac
		X: -168.0
		Y: 10.0
		Z: -252.0
		Yaw: 0.0
		Pitch: 0.0
		Roll: 0.0
-------
Marker: BALS
	Length: 00000068
	Data Offset: 0x3538e4

		Ball # 1:
		Ball Data: 
			Array Index | Data         | Data Description
			---------------------------------------------
			    (0)       c2902106       X
			    (1)       43a74d71       Z
			    (2)       43360000       Y
			    (3)       80000000       
			    (4)       00000000       
			    (5)       00000000       
			    (6)       00000000       
			    (7)       41200000       
			    (8)       00000000       Color / Type (Single or Splits into multiple balloons)
			    (9)       3c23d70a       Solid or Poppable
			    (10)       00000000       Weight
			    (11)       00000000       Force needed to Pop Balloon
			    (12)       40200000       Scale (Size)
			    (13)       0000001e       
			    (14)       00000000       
			    (15)       00000000       
			    (16)       411ccccd       
			    (17)       00000000       
			    (18)       00000000       
			    (19)       00000000       
			    (20)       00000000       
			    (21)       00000000       
			    (22)       00000000       
			    (23)       3f800000       
			    (24)       00000000       
			    (25)       411ccccd       
		Ball / Balloon Color: Orange (00)
		Ball / Balloon Type: Normal (00)
		Ball / Balloon Can Pop: YES
		X: -72.064499
		Y: 182.0
		Z: 334.605011
		Scale: 2.5
```


Here's a sample of the Task listing:
```roto@roto-System-Product-Name:~/pw64$ ./pw64_upwt_parser.py 
Please provide a Test ID!

Here's some options:

A_BD_1, A_BD_2, A_BD_3, A_BD_4, A_EX_1, A_EX_1-0x34331c, A_EX_1-0x343814, A_EX_1-0x343d0c, A_EX_2, A_EX_2-0x3446f4, A_EX_2-0x344bec, A_EX_2-0x3450e4, A_EX_3, A_EX_3-0x345acc, A_EX_3-0x345fc4, A_EX_3-0x3464bc, A_GC_1, A_GC_2, A_HG_1, A_HG_2, A_RP_1, A_RP_2, B_BD_1, B_BD_2, B_BD_3, B_BD_4, B_EX_1, B_EX_2, B_EX_3, B_GC_1, B_GC_2, B_GC_3, B_HG_1, B_HG_2, B_HG_3, B_RP_1, B_RP_2, B_RP_3, E_BD_1, E_BD_2, E_BD_3, E_BD_4, E_GC_1, E_HG_1, E_RP_1, P_BD_1, P_BD_2, P_BD_3, P_BD_4, P_EX_1, P_EX_2, P_EX_3, P_GC_1, P_GC_2, P_GC_3, P_HG_1, P_HG_2, P_HG_3, P_RP_1, P_RP_2, P_RP_3

And here is the list in the FS:

  FS ID   	|	File Type 	|	Offset in ROM	|	File Size 	|	 Task ID	 
--------------------------------------------------------------------------------------------------------------
   1063   	|	   UPWT   	|	 0x342e2c 	|	0x4f0     	|	  A_EX_1  
   1064   	|	   UPWT   	|	 0x34331c 	|	0x4f8     	|	  A_EX_1  
   1065   	|	   UPWT   	|	 0x343814 	|	0x4f8     	|	  A_EX_1  
   1066   	|	   UPWT   	|	 0x343d0c 	|	0x4f8     	|	  A_EX_1  
   1067   	|	   UPWT   	|	 0x344204 	|	0x4f0     	|	  A_EX_2  
   1068   	|	   UPWT   	|	 0x3446f4 	|	0x4f8     	|	  A_EX_2  
   1069   	|	   UPWT   	|	 0x344bec 	|	0x4f8     	|	  A_EX_2  
   1070   	|	   UPWT   	|	 0x3450e4 	|	0x4f8     	|	  A_EX_2  
   1071   	|	   UPWT   	|	 0x3455dc 	|	0x4f0     	|	  A_EX_3  
   1072   	|	   UPWT   	|	 0x345acc 	|	0x4f8     	|	  A_EX_3  
   1073   	|	   UPWT   	|	 0x345fc4 	|	0x4f8     	|	  A_EX_3  
   1074   	|	   UPWT   	|	 0x3464bc 	|	0x4f8     	|	  A_EX_3  
   1075   	|	   UPWT   	|	 0x3469b4 	|	0x500     	|	  B_EX_1  
   1076   	|	   UPWT   	|	 0x346eb4 	|	0x500     	|	  B_EX_2  
   1077   	|	   UPWT   	|	 0x3473b4 	|	0x4f8     	|	  B_EX_3  
   1078   	|	   UPWT   	|	 0x3478ac 	|	0x4e0     	|	  P_EX_1  
   1079   	|	   UPWT   	|	 0x347d8c 	|	0x4e0     	|	  P_EX_2  
   1080   	|	   UPWT   	|	 0x34826c 	|	0x4e0     	|	  P_EX_3  
   1081   	|	   UPWT   	|	 0x34874c 	|	0x4c8     	|	  E_BD_1  
   1082   	|	   UPWT   	|	 0x348c14 	|	0x4c8     	|	  E_BD_2  
   1083   	|	   UPWT   	|	 0x3490dc 	|	0x4c8     	|	  E_BD_3  
   1084   	|	   UPWT   	|	 0x3495a4 	|	0x4c8     	|	  E_BD_4  
   1085   	|	   UPWT   	|	 0x349a6c 	|	0x4c8     	|	  A_BD_1  
   1086   	|	   UPWT   	|	 0x349f34 	|	0x4c8     	|	  A_BD_2  
   1087   	|	   UPWT   	|	 0x34a3fc 	|	0x4c8     	|	  A_BD_3  
   1088   	|	   UPWT   	|	 0x34a8c4 	|	0x4c8     	|	  A_BD_4  
   1089   	|	   UPWT   	|	 0x34ad8c 	|	0x4c8     	|	  B_BD_1  
   1090   	|	   UPWT   	|	 0x34b254 	|	0x4c8     	|	  B_BD_2  
   1091   	|	   UPWT   	|	 0x34b71c 	|	0x4c8     	|	  B_BD_3  
   1092   	|	   UPWT   	|	 0x34bbe4 	|	0x4c8     	|	  B_BD_4  
   1093   	|	   UPWT   	|	 0x34c0ac 	|	0x4c8     	|	  P_BD_1  
   1094   	|	   UPWT   	|	 0x34c574 	|	0x528     	|	  P_BD_2  
   1095   	|	   UPWT   	|	 0x34ca9c 	|	0x4c8     	|	  P_BD_3  
   1096   	|	   UPWT   	|	 0x34cf64 	|	0x528     	|	  P_BD_4  
   1097   	|	   UPWT   	|	 0x34d48c 	|	0x898     	|	  E_GC_1  
   1098   	|	   UPWT   	|	 0x34dd24 	|	0xce0     	|	  A_GC_1  
   1099   	|	   UPWT   	|	 0x34ea04 	|	0x580     	|	  A_GC_2  
   1100   	|	   UPWT   	|	 0x34ef84 	|	0x1078    	|	  B_GC_1  
   1101   	|	   UPWT   	|	 0x34fffc 	|	0x770     	|	  B_GC_2  
   1102   	|	   UPWT   	|	 0x35076c 	|	0x930     	|	  B_GC_3  
   1103   	|	   UPWT   	|	 0x35109c 	|	0x1188    	|	  P_GC_1  
   1104   	|	   UPWT   	|	 0x352224 	|	0x8e8     	|	  P_GC_2  
   1105   	|	   UPWT   	|	 0x352b0c 	|	0xa88     	|	  P_GC_3  
   1106   	|	   UPWT   	|	 0x353594 	|	0x598     	|	  E_RP_1  
   1107   	|	   UPWT   	|	 0x353b2c 	|	0x9d0     	|	  A_RP_1  
   1108   	|	   UPWT   	|	 0x3544fc 	|	0x7b0     	|	  A_RP_2  
   1109   	|	   UPWT   	|	 0x354cac 	|	0x600     	|	  B_RP_1  
   1110   	|	   UPWT   	|	 0x3552ac 	|	0xcf0     	|	  B_RP_2  
   1111   	|	   UPWT   	|	 0x355f9c 	|	0x568     	|	  B_RP_3  
   1112   	|	   UPWT   	|	 0x356504 	|	0x6e8     	|	  P_RP_1  
   1113   	|	   UPWT   	|	 0x356bec 	|	0x588     	|	  P_RP_2  
   1114   	|	   UPWT   	|	 0x357174 	|	0x7b0     	|	  P_RP_3  
   1115   	|	   UPWT   	|	 0x357924 	|	0x730     	|	  E_HG_1  
   1116   	|	   UPWT   	|	 0x358054 	|	0x690     	|	  A_HG_1  
   1117   	|	   UPWT   	|	 0x3586e4 	|	0xc40     	|	  A_HG_2  
   1118   	|	   UPWT   	|	 0x359324 	|	0x5f8     	|	  B_HG_1  
   1119   	|	   UPWT   	|	 0x35991c 	|	0x6f0     	|	  B_HG_2  
   1120   	|	   UPWT   	|	 0x35a00c 	|	0x5d0     	|	  B_HG_3  
   1121   	|	   UPWT   	|	 0x35a5dc 	|	0x6d8     	|	  P_HG_1  
   1122   	|	   UPWT   	|	 0x35acb4 	|	0xdc0     	|	  P_HG_2  
   1123   	|	   UPWT   	|	 0x35ba74 	|	0x7f8     	|	  P_HG_3  
```
The script tries to and mostly works on parsing and decoding a lot of data, but there's still lots of work to do.
You can use it to your advantage such as say dumping and vimdiff'ing arrays of data between different tasks to see what values differ, then work through the differences in a debugger.

It can also be helpful to find things specific to a task. Such as lets find which missions you battle Meca Hawk in:
```
roto@roto-System-Product-Name:~/pw64$ for i in A_BD_1 A_BD_2 A_BD_3 A_BD_4 A_EX_1 A_EX_1-0x34331c A_EX_1-0x343814 A_EX_1-0x343d0c A_EX_2 A_EX_2-0x3446f4 A_EX_2-0x344bec A_EX_2-0x3450e4 A_EX_3 A_EX_3-0x345acc A_EX_3-0x345fc4 A_EX_3-0x3464bc A_GC_1 A_GC_2 A_HG_1 A_HG_2 A_RP_1 A_RP_2 B_BD_1 B_BD_2 B_BD_3 B_BD_4 B_EX_1 B_EX_2 B_EX_3 B_GC_1 B_GC_2 B_GC_3 B_HG_1 B_HG_2 B_HG_3 B_RP_1 B_RP_2 B_RP_3 E_BD_1 E_BD_2 E_BD_3 E_BD_4 E_GC_1 E_HG_1 E_RP_1 P_BD_1 P_BD_2 P_BD_3 P_BD_4 P_EX_1 P_EX_2 P_EX_3 P_GC_1 P_GC_2 P_GC_3 P_HG_1 P_HG_2 P_HG_3 P_RP_1 P_RP_2 P_RP_3; do echo -n "$i: "; ./pw64_upwt_parser.py $i | strings | grep -i "Hawk"; done
A_BD_1: 		"Falcos Domains" (Meca Hawk): 0
A_BD_2: 		"Falcos Domains" (Meca Hawk): 0
A_BD_3: 		"Falcos Domains" (Meca Hawk): 0
A_BD_4: 		"Falcos Domains" (Meca Hawk): 0
A_EX_1: 		"Falcos Domains" (Meca Hawk): 0
A_EX_1-0x34331c: 		"Falcos Domains" (Meca Hawk): 0
A_EX_1-0x343814: 		"Falcos Domains" (Meca Hawk): 0
A_EX_1-0x343d0c: 		"Falcos Domains" (Meca Hawk): 0
A_EX_2: 		"Falcos Domains" (Meca Hawk): 0
A_EX_2-0x3446f4: 		"Falcos Domains" (Meca Hawk): 0
A_EX_2-0x344bec: 		"Falcos Domains" (Meca Hawk): 0
A_EX_2-0x3450e4: 		"Falcos Domains" (Meca Hawk): 0
A_EX_3: 		"Falcos Domains" (Meca Hawk): 0
A_EX_3-0x345acc: 		"Falcos Domains" (Meca Hawk): 0
A_EX_3-0x345fc4: 		"Falcos Domains" (Meca Hawk): 0
A_EX_3-0x3464bc: 		"Falcos Domains" (Meca Hawk): 0
A_GC_1: 		"Falcos Domains" (Meca Hawk): 0
A_GC_2: 		"Falcos Domains" (Meca Hawk): 0
A_HG_1: 		"Falcos Domains" (Meca Hawk): 0
A_HG_2: 		"Falcos Domains" (Meca Hawk): 0
A_RP_1: 		"Falcos Domains" (Meca Hawk): 0
A_RP_2: 		"Falcos Domains" (Meca Hawk): 0
B_BD_1: 		"Falcos Domains" (Meca Hawk): 0
B_BD_2: 		"Falcos Domains" (Meca Hawk): 0
B_BD_3: 		"Falcos Domains" (Meca Hawk): 0
B_BD_4: 		"Falcos Domains" (Meca Hawk): 0
B_EX_1: 		"Falcos Domains" (Meca Hawk): 0
B_EX_2: 		"Falcos Domains" (Meca Hawk): 0
B_EX_3: 		"Falcos Domains" (Meca Hawk): 0
B_GC_1: 		"Falcos Domains" (Meca Hawk): 0
B_GC_2: 		"Falcos Domains" (Meca Hawk): 0
B_GC_3: 		 Hawk Attack
		 The giant robot, Meca Hawk, is 
		 Hit Meca Hawk with 5 missiles!
		"Falcos Domains" (Meca Hawk): 6
B_HG_1: 		"Falcos Domains" (Meca Hawk): 0
B_HG_2: 		"Falcos Domains" (Meca Hawk): 0
B_HG_3: 		"Falcos Domains" (Meca Hawk): 0
B_RP_1: 		"Falcos Domains" (Meca Hawk): 0
B_RP_2: 		"Falcos Domains" (Meca Hawk): 0
B_RP_3: 		"Falcos Domains" (Meca Hawk): 0
E_BD_1: 		"Falcos Domains" (Meca Hawk): 0
E_BD_2: 		"Falcos Domains" (Meca Hawk): 0
E_BD_3: 		"Falcos Domains" (Meca Hawk): 0
E_BD_4: 		"Falcos Domains" (Meca Hawk): 0
E_GC_1: 		"Falcos Domains" (Meca Hawk): 0
E_HG_1: 		"Falcos Domains" (Meca Hawk): 0
E_RP_1: 		"Falcos Domains" (Meca Hawk): 0
P_BD_1: 		"Falcos Domains" (Meca Hawk): 0
P_BD_2: 		"Falcos Domains" (Meca Hawk): 0
P_BD_3: 		"Falcos Domains" (Meca Hawk): 0
P_BD_4: 		"Falcos Domains" (Meca Hawk): 0
P_EX_1: 		"Falcos Domains" (Meca Hawk): 0
P_EX_2: 		"Falcos Domains" (Meca Hawk): 0
P_EX_3: 		"Falcos Domains" (Meca Hawk): 0
P_GC_1: 		"Falcos Domains" (Meca Hawk): 0
P_GC_2: 		"Falcos Domains" (Meca Hawk): 0
P_GC_3: 		 Meca Hawk Again
		 Meca Hawk has returned!
		"Falcos Domains" (Meca Hawk): 8
P_HG_1: 		"Falcos Domains" (Meca Hawk): 0
P_HG_2: 		"Falcos Domains" (Meca Hawk): 0
P_HG_3: 		"Falcos Domains" (Meca Hawk): 0
P_RP_1: 		"Falcos Domains" (Meca Hawk): 0
P_RP_2: 		"Falcos Domains" (Meca Hawk): 0
P_RP_3: 		"Falcos Domains" (Meca Hawk): 0
```
So looks like B_GC_3 and P_GC_3. Yay! Yes, I know there's a problem with the output that makes grep think it is binary data (thus a pipe to *strings* is needed). And this operation could probably be written into a function quite easily...

## pw64_lib.py
This is a module that has some functions shared between a few scripts.
It has functions to construct and show a table of the "filesystem" with file types, sizes and offsets (it parses TABL chunk and sticks the files/sizes/offsets indexed by int into a dictionary). It has a func that can show all files in the FS or specific file types as requested, it can decompress/update/re-compress the TABL chunk (MIO0 compressed) with new file sizes after modification, can encoded/decode ADAT (game strings), can patch the game code with new FS size offsets so that DMA reads have proper addresses (otherwise if you add data to the ROM, the hardcoded offsets all break!), and much, much more.

## pw64_taskmod_poc.py (Old...)
This script is my attempt at modifying a task and hard-patching a new object into an already existing task in the ROM.
The task is "E_GC_1" which is the Beginner GyroCopter level. 
It has 3 rings to fly through.
I've inserted a poppable Ballooon that I took out of the Beginner Rocket Pack level.

This script was a test to see if the following would work:
1) Adding an object to a mission from another mission (This one normally only has 3 Rings but now we add a Balloon on top of the castle).
2) Making that object visible by modifying the COMM section as needed. (If there's 0 balloons defined in COMM, and even if the BALS data is in the UPWT chunk, the balloon won't show)
3) Resizing the "filesystem".
4) Hard-patching various addresses in the game program code that reference specific FS sizes and offsets. 

The modifications worked in an Emulator and the patched ROM works on real N64 hardware.

## pw64_taskmod_json_poc.py (New!)
For the most part it duplicates the script above but this code now ingests JSON produced by the *pw64_upwt_parser.py* tool and attempts to re-build a UPWT from scratch with the given input.

This script should be able to add object(ive)s dynamically by letting the user create or modify a JSON file.
As of right now it is only able to add/remove Balloons and Rings to one level. You can't insert other object(ive)s because they're not parsed or exported by the parser tool. This is very much a WIP.

Here's an example of a modified E_GC_1 (Beginner GyroCopter test) task expressed in JSON format.
This JSON data represented here modifies this test to have a total of 5 Rings and 2 Balloons.
Data that is not yet decoded or requires more processing, such as with a lookup table, remains in Hex:
```{
  "task_id": "E_GC_1",
  "COMM": {
    "pilot_class": "00",
    "vehicle": "02",
    "test_number": "00",
    "level": "00",
    "skybox": "00",
    "snow": "00",
    "wind_WE": 0.0,
    "wind_SN": 0.0,
    "wind_UD": 0.0,
    "THER": 0,
    "LWND": 0,
    "TPAD": 1,
    "LPAD": 0,
    "LSTP": 1,
    "RNGS": 5,
    "BALS": 2,
    "TARG": 0,
    "HPAD": 0,
    "BTGT": 0,
    "PHTS": 0,
    "FALC": 0,
    "UNKN": 0,
    "CNTG": 0,
    "HOPD": 0
  },
  "TPAD": {
    "x": -40.73,
    "z": 10.0,
    "y": -405.723999,
    "yaw": 24.0,
    "pitch": 0.0,
    "roll": 0.0
  },
  "RNGS": {
    "1": {
      "x": -293.821991,
      "y": 55.0,
      "z": 175.014999,
      "yaw": 23.0,
      "pitch": 0.0,
      "roll": 0.0,
      "size": "02",
      "state": "01",
      "motion_axis": "6e",
      "motion_rad_start": "00000000",
      "motion_rad_end": "00000000",
      "rotation": "79",
      "rotation_speed": "40000000",
      "ring_special": "00",
      "next_ring_unknown": "00",
      "next_ring_order_count": "01",
      "next_ring_index": {
        "0": "00000001"
      }
    },
    "2": {
      "x": -372.035004,
      "y": 70.0,
      "z": 349.994995,
      "yaw": 23.0,
      "pitch": 0.0,
      "roll": 0.0,
      "size": "02",
      "state": "00",
      "motion_axis": "6e",
      "motion_rad_start": "00000000",
      "motion_rad_end": "00000000",
      "rotation": "79",
      "rotation_speed": "40000000",
      "ring_special": "00",
      "next_ring_unknown": "00",
      "next_ring_order_count": "01",
      "next_ring_index": {
        "0": "00000002"
      }
    },
    "3": {
      "x": -477.516998,
      "y": 105.0,
      "z": 589.724976,
      "yaw": 23.0,
      "pitch": 0.0,
      "roll": 0.0,
      "size": "02",
      "state": "00",
      "motion_axis": "6e",
      "motion_rad_start": "00000000",
      "motion_rad_end": "00000000",
      "rotation": "79",
      "rotation_speed": "40000000",
      "ring_special": "01",
      "next_ring_unknown": "01",
      "next_ring_order_count": "01",
      "next_ring_index": {
        "0": "00000003"
	}
    },
    "4": {
      "x": -572.035004,
      "y": 120.0,
      "z": 689.994995,
      "yaw": 23.0,
      "pitch": 0.0,
      "roll": 0.0,
      "size": "02",
      "state": "00",
      "motion_axis": "7a",
      "motion_rad_start": "40800000",
      "motion_rad_end": "40c00000",
      "rotation": "79",
      "rotation_speed": "40000000",
      "ring_special": "00",
      "next_ring_unknown": "00",
      "next_ring_order_count": "01",
      "next_ring_index": {
        "0": "00000004"
      }
    },
    "5": {
      "x": -672.035004,
      "y": 140.0,
      "z": 849.994995,
      "yaw": 23.0,
      "pitch": 0.0,
      "roll": 0.0,
      "size": "02",
      "state": "00",
      "motion_axis": "6e",
      "motion_rad_start": "00000000",
      "motion_rad_end": "00000000",
      "rotation": "79",
      "rotation_speed": "40000000",
      "ring_special": "03",
      "next_ring_unknown": "00",
      "next_ring_order_count": "00"
      }
  },
  "LSTP": {
    "x": -28.82,
    "z": 10.0,
    "y": -432.110992,
    "yaw": -150.841003,
    "pitch": -158.048004,
    "roll": 10.0
  },
  "BALS": {
    "1": {
      "x": -72.064499,
      "y": 182.0,
      "z": 334.605011,
      "scale": 2.5,
      "color": "00",
      "type": "00",
      "solidity": "3c23d70a",
      "weight": "00000000",
      "popforce": "00000000"
    },
    "2": {
      "x": -72.064499,
      "y": 202.0,
      "z": 334.605011,
      "scale": 2.5,
      "color": "02",
      "type": "00",
      "solidity": "3c23d70a",
      "weight": "00000000",
      "popforce": "00000000"
    }
  }
}
```

Here's what the above JSON looks like once parsed, processed and injected back into the ROM:
![Test select map preview](https://i.imgur.com/ZpsK7hj.png) ![In-game view of the 5 rings and 2 balloons](https://i.imgur.com/WkenGIs.png)

You can see there's now 5 rings instead of 3 and two balloons atop the castle in the Beginner GyroCopter test/mission.

## Q&A
**Q**: Does this work on N64 hardware?

**A**: Yes. The "filesystem" table (TABL chunk) is updated with the modified task's new size and then re-compressed, new data is injected at the proper offset(s), ROM padding is truncated if necessary (to maintain original ROM filesize), various addresses are patched in the game code to account for the modified FS size, and the ROM's checksum is fixed. It works.

**Q**: Why aren't you doing a full **DeCoMp** like all the cool kids are doing these days?

**A**: I don't know MIPS assembly. It took me two weeks to hunt down and patch the addresses that need to be modified when resizing the FS and injecting things into the ROM. I think I chose a pretty interesting portion of the game engine (the "tasks") and that has taken me >5 months (when I could find time!) to learn and get to the point where I can do what I am doing here.

**Q**: Why is your code bad/not OOP/repetitive/etc/etc?

**A**: Because I'm not a Software Developer or Software Engineer, this is a hobby. Feel free to take over and fix it yourself.

**Q**: Why don't you continue updating the NOCLIP Wiki and more document more details on things you've found/learned?

**A**: I can barely stomach writing documentation for my day job. I'm not particularly excited to do this for a hobby. Maybe if I find some extra time after I'm done exploring...

**Q**: What's next?

**A**: More JSON work... need to export all the other objects. More research on various object attributes (not everything is decoded). I need to figure out where the final scores are stored in a task (right now you can have 100 rings and only get points for 3 when you finish the test). So... a LOT of stuff.
