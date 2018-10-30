execfile('UpgradeOltFtpClient.py')
t = UpgradeOltFtpClient()
t.connect('172.17.2.150',False,'','suma','suma','172.17.2.2','c','c')
t.connect('172.17.2.150',False,'','suma','suma','./V1.9.0.26')
t.connect('172.17.2.152',True,'admin','admin','','./V1.9.0.26')
t.downloadImage()

t.openFtpServer()
t.loginIntoFtp()

t.syncFile()

t.upgradeBootrom()

select ip,IFNULL(isAAA,globalIsAAA) as isAAA,IFNULL(username,globalUsername) as username
,IFNULL(password,globalPassword) as password,IFNULL(enablePassword,globalEnablePassword) as enablePassword
from (select e.ip,(select value from systempreferences where name = 'telnetUserName') as globalUsername 
,(select value from systempreferences where name = 'telnetPassword') as globalPassword
,(select value from systempreferences where name = 'telnetEnablePassword') as globalEnablePassword
,(select value from systempreferences where name = 'telnetIsAAA') as globalIsAAA,tlc.username,tlc.password,tlc.enablePassword,tlc.isAAA from entity e 
LEFT JOIN telnetloginconfig tlc on e.ip = tlc.ipString
where e.typeId in (select typeId from entitytyperelation where type = 10000) ) a into outfile '/home/nm3000/ems/abc.txt'