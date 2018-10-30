#$language = "VBScript"
#$interface = "1.0"
Option Explicit
crt.Screen.Synchronous = True

Const maxCmc = 128

Dim slotArray(128)
Dim ponArray(128)
Dim cmcArray(128)
Dim filterString
Dim cRow
Dim cmcCount
Dim i
Dim preSlot
Dim prePon
Dim cmcTotalCount
Dim cmcMacAddress

Sub Main

'	'set vlan & vlan-interface
	crt.Screen.Send("end") & chr(13)
	crt.Screen.Send("terminal length 0") & chr(13) & chr(13)
	crt.Screen.Send("config t") & chr(13)
	crt.Screen.WaitForString "(config)#"

'Get all online CC8800C-E	
	cmcTotalCount = 0
	
	For i = 1 to 8
		cmcCount = 0	
		crt.Screen.Send "show ccmts | include C" & i & ".*\bonline.*\bCC8800C*-*E\b" & chr(13)
		crt.Screen.WaitForString "(config)#"
		cRow = crt.Screen.CurrentRow
		filterString = crt.Screen.Get(cRow-1,1,cRow-1,9)
		While filterString <> "Filtering"
			cmcCount = cmcCount + 1
			cmcTotalCount = cmcTotalCount + 1
			slotArray(cmcTotalCount) = crt.Screen.Get(cRow-cmcCount,2,cRow-cmcCount,2)
			ponArray(cmcTotalCount) = crt.Screen.Get(cRow-cmcCount,4,cRow-cmcCount,4)
			cmcArray(cmcTotalCount) = crt.Screen.Get(cRow-cmcCount,6,cRow-cmcCount,6)
			filterString = crt.Screen.Get(cRow-cmcCount-1,1,cRow-cmcCount-1,9)			
		Wend
	Next
	crt.Screen.Send "find " & cmcTotalCount  & " online CC8800E " & chr(13)
	'crt.Screen.WaitForString("#")

	
	'IP config
	preSlot = 0
	prePon = 0
	For i=1 to cmcTotalCount
		if not (preSlot = slotArray(i) and prePon = ponArray(i)) Then
			preSlot = slotArray(i)
			prePon = ponArray(i)
			crt.Screen.Send "interface pon " & preSlot & "/" & prePon & chr(13)
			'crt.Sleep (500)
			crt.Screen.WaitForString "config-if-pon"
			crt.Screen.Send("vlan 400 transparent") & chr(13)
			crt.Screen.WaitForString "#"
			'crt.Sleep (500)
			crt.Screen.Send "exit" & chr(13)
		End If
		
	Next
	
	
	For i=1 to cmcTotalCount
		crt.Screen.Send "interface ccmts " & slotArray(i) & "/" & ponArray(i) & "/" & cmcArray(i) & chr(13)
		crt.Screen.WaitForString("config-if-ccmts")
		
		'关闭CC所有下行信道
		crt.Screen.Send "cable downstream 1-16 shutdown" & chr(13)
		crt.Sleep (5000)
		crt.Screen.WaitForString("config-if-ccmts") 
		'根据slot、pon、cmc配置ip
		crt.Screen.Send("onu-ipconfig ip-address 40.40." & slotArray(i) & "." & ponArray(i) & cmcArray(i) & " mask 255.255.0.0 gateway 40.40.40.40 cvlan  400") & chr(13)
		crt.Screen.WaitForString "config-if-ccmts"

	Next
	
	crt.Screen.Send chr(13) &  chr(13) &  chr(13) &  chr(13) 
	crt.Sleep(5000)
	crt.Dialog.MessageBox("ip config finished!")
	crt.Screen.Send chr(13) &  chr(13) &  chr(13) &  chr(13) 
	

End Sub