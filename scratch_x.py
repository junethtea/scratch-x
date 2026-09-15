import os
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from .scratch_x_dialog import ScratchXDialog

class ScratchX:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.dialog = None
        self.action = None

    def initGui(self):
        icon_path = os.path.join(self.plugin_dir, 'icon.png')
        icon = QIcon(icon_path) if os.path.exists(icon_path) else QIcon()
        self.action = QAction(icon, 'Scratch-X', self.iface.mainWindow())
        self.action.setToolTip('Scratch-X – Scratch geometry tool')
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToVectorMenu('Scratch-X', self.action)

    def unload(self):
        self.iface.removePluginVectorMenu('Scratch-X', self.action)
        self.iface.removeToolBarIcon(self.action)

    def run(self):
        if self.dialog is None:
            self.dialog = ScratchXDialog(self.iface)
        self.dialog.show()
        self.dialog.raise_()
        self.dialog.activateWindow()
