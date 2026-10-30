"""Temp Label Manager Phase 1 v3. Qt Designer .ui + offline UI simulator."""
import csv
import math
import sys
from datetime import datetime,timedelta
from pathlib import Path

from PyQt5 import QtCore,QtGui,QtWidgets,uic

BASE=Path(__file__).resolve().parent
OTHER=['device_configuration','data_download','history_viewer','device_information','settings']
STYLE='''
QMainWindow,QWidget {background:#f2f5fa;color:#1b2d44;font:12px "Segoe UI";}
QFrame#headerBar {background:#f9fbfd;border:1px solid #c9d3df;border-radius:7px;}
QLabel#appTitleLabel{font-size:17px;font-weight:700;background:transparent;}
QLabel#logoLabel {font-size:25px;background:transparent;}
QLabel#appVersionLabel,QLabel#adapterStatusLabel{background:transparent;color:#43566a;}
QLabel#headerSpacer{background:transparent;}
QToolButton,QPushButton {background:#086ee5;color:white;border:0;border-radius:5px;padding:9px 11px;}
QPushButton:hover {background:#005bc4;}
QPushButton:disabled{background:#c8d3df;color:#607286;}
QPushButton#menuToggleButton {background:#e9f1fc;color:#0c4a85;font-size:20px;font-weight:bold;min-width:40px;max-width:40px;}
QPushButton#settingsTopButton {background:#e9f1fc;color:#233b56;}
QFrame#sidebar{background:#18354f;border-radius:6px;min-width:188px;max-width:188px;}
QFrame#sidebar QLabel{background:transparent;color:#e9f4ff;}
QLabel#sideBrand{font-weight:bold;font-size:17px;padding:9px 5px;}
QLabel#sideFooter{color:#93aec5;font-size:10px;}
QFrame#sidebar QPushButton{text-align:left;background:transparent;border:0;color:#dcecf8;padding:15px 12px;font-weight:600;}
QFrame#sidebar QPushButton:hover{background:#1c5282;}
QFrame#scanCard,QFrame#deviceCard,QFrame#configCard,QFrame#chartCard,QFrame#downloadCard,QFrame#recordsCard{background:white;border:1px solid #d5dfea;border-radius:8px;}
QFrame#scanCard QLabel,QFrame#deviceCard QLabel,QFrame#configCard QLabel,QFrame#chartCard QLabel,QFrame#downloadCard QLabel,QFrame#recordsCard QLabel{background:transparent;}
QLabel#scanCardTitle,QLabel#deviceCardTitle,QLabel#configCardTitle,QLabel#chartCardTitle,QLabel#downloadCardTitle,QLabel#recordsCardTitle{font-size:15px;font-weight:700;color:#17324f;padding-bottom:3px;}
QTableWidget {background:white;alternate-background-color:#eef6ff;border:1px solid #dae3ed;gridline-color:#e8edf4;selection-background-color:#b6d9ff;selection-color:#122b46;}
QHeaderView::section{background:#e8f0f8;padding:7px;border:0;border-right:1px solid white;font-weight:bold;}
QLineEdit,QSpinBox,QDoubleSpinBox,QDateTimeEdit,QComboBox{background:white;border:1px solid #b8c9dd;border-radius:4px;padding:5px;min-height:19px;}
QProgressBar{background:#d8e1ed;border:0;border-radius:5px;text-align:center;min-height:19px;}
QProgressBar::chunk{background:#10bd67;border-radius:5px;}
QCheckBox{background:transparent;}
QGroupBox{background:white;border:1px solid #dbe4ee;border-radius:6px;margin-top:14px;padding:12px 8px 8px;font-weight:bold;}
QGroupBox::title{subcontrol-origin:margin;left:14px;padding:0 4px;}
'''

class MainWindow(QtWidgets.QMainWindow):
 def __init__(self):
  super().__init__()
  uic.loadUi(str(BASE/'ui/main_window.ui'),self)
  self.setStyleSheet(STYLE)
  self.setWindowTitle('Temp Label Manager — Phase 1 v3')
  logo=QtGui.QIcon(str(BASE/'assets/thermo_logo.png'))
  self.setWindowIcon(logo)
  self.logoLabel.setText('')
  self.logoLabel.setPixmap(logo.pixmap(32,32))
  self.sideBrand.setText('🌡  TEMP LABEL')
  self.d=uic.loadUi(str(BASE/'ui/dashboard.ui'))
  self.pageStack.addWidget(self.d)
  self.extra={}
  for name in OTHER:
   p=uic.loadUi(str(BASE/'ui'/f'{name}.ui'))
   self.extra[name]=p;self.pageStack.addWidget(p)
  self.buttons=[self.navDevices,self.navConfiguration,self.navDownload,self.navHistory,self.navDeviceInfo,self.navSettings]
  self.labels=['◉  Devices','⚙  Configuration','⬇  Data Download','▥  History & Graph','ⓘ  Device Info','⚙  Settings']
  self.symbols=['◉','⚙','⬇','▥','ⓘ','⚙']
  for i,b in enumerate(self.buttons):b.clicked.connect(lambda checked=False,i=i:self.navigate(i))
  self.menuToggleButton.clicked.connect(self.toggle_sidebar)
  self.settingsTopButton.clicked.connect(lambda:self.navigate(5))
  self.collapsed=False
  self.data=self.make_data(12450)
  self.cursor=0;self.running=False;self.interrupted=False
  self.timer=QtCore.QTimer(self);self.timer.setInterval(80);self.timer.timeout.connect(self.tick)
  self.configure()
  self.navigate(0)
  self.statusBar().showMessage('Phase 1 • Offline simulation • No live BLE/GATT connection')

 @staticmethod
 def make_data(count):
  initial=datetime(2026,10,1,8)
  out=[]
  for i in range(count):
   t=4.1+0.9*math.sin(i/43)+0.35*math.sin(i/9)
   if 650<=i%1750<=790:t+=7.8*math.sin(math.pi*(i%1750-650)/140)
   out.append((i+1,(initial+timedelta(minutes=i)).strftime('%Y-%m-%d %H:%M:%S'),round(t,2),t>8))
  return out

 def toggle_sidebar(self):
  self.collapsed=not self.collapsed
  w=62 if self.collapsed else 188
  self.sidebar.setStyleSheet(f'QFrame#sidebar{{min-width:{w}px;max-width:{w}px;}}')
  self.sidebar.setMinimumWidth(w);self.sidebar.setMaximumWidth(w)
  self.sideBrand.setVisible(not self.collapsed)
  self.sideFooter.setVisible(not self.collapsed)
  for b,text,symbol in zip(self.buttons,self.labels,self.symbols):
   b.setText(symbol if self.collapsed else text)
   b.setToolTip(text)
   b.setStyleSheet('text-align:center;padding:15px 0;' if self.collapsed else '')

 def navigate(self,i):
  self.pageStack.setCurrentIndex(i+1)
  for j,b in enumerate(self.buttons):
   if i==j:b.setStyleSheet(('text-align:center;padding:15px 0;' if self.collapsed else 'text-align:left;padding:15px 12px;')+'background:#056cdd;color:white;border-radius:5px;')
   else:b.setStyleSheet('text-align:center;padding:15px 0;' if self.collapsed else '')

 def configure(self):
  d=self.d
  d.filterEdit.setPlaceholderText('Filter device name')
  d.scanButton.clicked.connect(self.scan)
  d.stopScanButton.clicked.connect(lambda:self.statusBar().showMessage('Mock scanning stopped'))
  d.filterEdit.textChanged.connect(self.filter)
  d.deviceTable.itemSelectionChanged.connect(self.selected)
  d.disconnectButton.clicked.connect(lambda:self.statusBar().showMessage('Mock device disconnected'))
  d.readConfigButton.clicked.connect(lambda:self.dialog('Read Config','Configuration values loaded from simulator.'))
  d.writeConfigButton.clicked.connect(self.write_config)
  d.startDownloadButton.clicked.connect(self.start)
  d.pauseButton.clicked.connect(self.pause)
  d.interruptButton.clicked.connect(self.interrupt)
  d.resumeButton.clicked.connect(self.resume)
  d.exportButton.clicked.connect(self.export)
  d.historyButton.clicked.connect(lambda:self.navigate(3))
  d.autoResumeCheckBox.setChecked(True)
  d.deviceTimeEdit.setDateTime(QtCore.QDateTime.currentDateTime())
  d.chartHost.setMinimumHeight(230)
  d.scanCard.setMinimumWidth(580)
  d.deviceCard.setMinimumWidth(300)
  d.configCard.setMinimumWidth(365)
  d.chartCard.setMinimumWidth(530)
  d.downloadCard.setMinimumWidth(535)
  d.recordsCard.setMinimumWidth(455)
  d.deviceTable.setMinimumHeight(185)
  d.recordsTable.setMinimumHeight(148)
  for table in (d.deviceTable,d.recordsTable):
   table.horizontalHeader().setStretchLastSection(True)
   table.verticalHeader().hide()
   table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
  self.plot=None
  try:
   import pyqtgraph as pg
   pg.setConfigOptions(antialias=True)
   self.plot=pg.PlotWidget(background='w')
   self.plot.showGrid(x=True,y=True,alpha=.18)
   self.plot.setLabel('left','Temperature','°C')
   self.plot.setLabel('bottom','Sample index')
   self.plot.setYRange(-5,20)
   for y,color in ((8,'#e34444'),(2,'#338ee6')):
    self.plot.addItem(pg.InfiniteLine(pos=y,angle=0,pen=pg.mkPen(color,width=1,style=QtCore.Qt.DashLine)))
   sampled=self.data[::12]
   self.plot.plot([x[0] for x in sampled],[x[2] for x in sampled],pen=pg.mkPen('#0575e6',width=2))
   lay=QtWidgets.QVBoxLayout(d.chartHost);lay.setContentsMargins(0,0,0,0);lay.addWidget(self.plot)
  except ImportError:
   lay=QtWidgets.QVBoxLayout(d.chartHost)
   lay.addWidget(QtWidgets.QLabel('Install pyqtgraph to show temperature history.'))
  self.scan();self.render_transfer()
  # Legacy detail pages remain editable via Qt Designer and functional demo actions.
  c=self.extra['device_configuration'];c.payloadEdit.setText('01020304AABB');c.deviceTimeEdit.setText(datetime.now().isoformat(timespec='seconds'))
  c.readConfigButton.clicked.connect(lambda:self.dialog('Read Config','Simulator configuration loaded.'))
  c.writeConfigButton.clicked.connect(lambda:self.dialog('Write Config','Simulation only; real GATT write not implemented.'))
  c.resetConfigButton.clicked.connect(lambda:self.dialog('Reset Config','Use dashboard controls for Phase 1.'))
  dl=self.extra['data_download'];dl.startDownloadButton.clicked.connect(self.start);dl.pauseDownloadButton.clicked.connect(self.pause);dl.interruptButton.clicked.connect(self.interrupt);dl.resumeButton.clicked.connect(self.resume);dl.resetDownloadButton.clicked.connect(self.reset)
  h=self.extra['history_viewer'];h.loadHistoryButton.clicked.connect(self.load_history);h.exportCsvButton.clicked.connect(self.export)
  info=self.extra['device_information']
  for name,val in [('infoName','Label 001'),('infoAddress','A4:C1:38:2B:9F:01'),('infoFw','v1.0.0'),('infoBattery','85%'),('infoTemp','5.2 °C'),('infoSamples','12,450'),('infoAck','0'),('infoMode','Normal operation'),('infoAlarm','Normal'),('infoDisplay','Device ON')]:getattr(info,name+'Value').setText(val)
  self.load_history()

 def scan(self):
  items=[('Label 001','A4:C1:38:2B:4F:01','-45','85%','5.2 °C','Ready'),('Label 002','A4:C1:38:2B:4F:02','-62','72%','6.1 °C','Ready'),('Label 003','A4:C1:38:2B:4F:03','-78','45%','3.8 °C','Ready'),('Label 004','A4:C1:38:2B:4F:04','-81','12%','7.9 °C','Low battery'),('Label 005','A4:C1:38:2B:4F:05','-69','66%','4.1 °C','Ready')]
  self.devices=items;t=self.d.deviceTable;t.setRowCount(len(items))
  for r,vals in enumerate(items):
   for c,v in enumerate((str(r+1),*vals)):
    it=QtWidgets.QTableWidgetItem(v)
    if c==4:it.setForeground(QtGui.QColor('#12964e' if r<2 else '#e65d23'))
    if c==6:it.setForeground(QtGui.QColor('#e44747' if r==3 else '#169a51'))
    t.setItem(r,c,it)
  t.resizeColumnsToContents();t.selectRow(0)
  self.statusBar().showMessage('Demo: 5 simulated temperature labels discovered')

 def selected(self):
  r=self.d.deviceTable.currentRow()
  if r<0 or r>=len(self.devices):return
  vals=self.devices[r]
  fields={'deviceName':vals[0],'deviceAddress':vals[1],'firmware':'v1.0.3 (mock)','hardware':'BLE Label','battery':vals[3],'lastTemp':vals[4],'deviceTime':datetime.now().strftime('%Y-%m-%d %H:%M'),'totalRecords':'12,450','uploadedUntil':f'{self.cursor:,}','deviceStatus':'Normal Operation (demo)' if r!=3 else 'Low battery (demo)'}
  for n,v in fields.items():getattr(self.d,n+'Value').setText(v)

 def filter(self,txt):
  t=self.d.deviceTable
  for r in range(t.rowCount()):t.setRowHidden(r,txt.lower() not in t.item(r,1).text().lower())

 def write_config(self):
  if self.d.lowTempSpin.value()>=self.d.highTempSpin.value():
   return self.dialog('Invalid thresholds','Low threshold must be lower than high threshold.')
  self.dialog('Simulated write','Configuration accepted by UI simulator; no BLE device was written.')

 def start(self):
  if self.cursor and self.d.autoResumeCheckBox.isChecked():return self.resume()
  self.cursor=max(0,self.d.startRecordSpin.value()-1)
  self.interrupted=False;self.running=True;self.timer.start();self.render_transfer()
 def pause(self):
  self.running=False;self.timer.stop();self.render_transfer()
 def interrupt(self):
  self.pause();self.interrupted=True;self.render_transfer()
  reply=QtWidgets.QMessageBox.question(self,'Connection Lost (simulated)',f'Last verified record: {self.cursor}.\nResume from record {self.cursor+1}?',QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
  if reply==QtWidgets.QMessageBox.Yes:self.resume()
 def resume(self):
  self.interrupted=False;self.running=True;self.timer.start();self.render_transfer()
 def reset(self):
  self.pause();self.cursor=0;self.interrupted=False;self.render_transfer()
 def tick(self):
  end=min(len(self.data),self.d.endRecordSpin.value())
  if self.cursor>=end:return self.pause()
  self.cursor=min(end,self.cursor+50);self.render_transfer()
  if self.cursor>=end:self.pause()
 def render_transfer(self):
  d=self.d;start=d.startRecordSpin.value();end=max(start,min(len(self.data),d.endRecordSpin.value()));done=max(0,self.cursor-start+1);total=end-start+1
  d.downloadProgress.setValue(min(100,round(100*done/total)))
  d.transferText.setText(f'{done:,} / {total:,} records ({100*done/total:.0f}%)  •  Next: {self.cursor+1:,}')
  status='BLE interrupted — resume available' if self.interrupted else 'Downloading (mock ACK)' if self.running else 'Paused / Idle'
  d.transferStatus.setText('Status: '+status)
  d.uploadedUntilValue.setText(f'{self.cursor:,}')
  t=d.recordsTable;records=self.data[max(0,self.cursor-10):self.cursor];t.setRowCount(len(records))
  for r,rec in enumerate(records):
   for c,val in enumerate((str(rec[0]),rec[1],f'{rec[2]:.1f}', 'HIGH' if rec[3] else 'Normal')):t.setItem(r,c,QtWidgets.QTableWidgetItem(val))
  t.resizeColumnsToContents()
  self.extra['device_information'].infoAckValue.setText(str(self.cursor))
 def load_history(self):
  t=self.extra['history_viewer'].historyTable;t.setRowCount(180)
  for r,rec in enumerate(self.data[:180]):
   for c,v in enumerate((rec[0],rec[1],f'{rec[2]:.2f}','HIGH' if rec[3] else 'Normal')):t.setItem(r,c,QtWidgets.QTableWidgetItem(str(v)))
  t.resizeColumnsToContents()
 def export(self):
  name,_=QtWidgets.QFileDialog.getSaveFileName(self,'Export simulated history',str(BASE/'temperature_history_demo.csv'),'CSV files (*.csv)')
  if not name:return
  with open(name,'w',newline='',encoding='utf-8') as f:
   writer=csv.writer(f);writer.writerow(['record_id','timestamp','temperature_c','alarm_high']);writer.writerows(self.data)
  self.statusBar().showMessage('Saved '+name)
 def dialog(self,title,body):QtWidgets.QMessageBox.information(self,title,body)

if __name__=='__main__':
 app=QtWidgets.QApplication(sys.argv);app.setStyle('Fusion');w=MainWindow();w.show();sys.exit(app.exec_())
