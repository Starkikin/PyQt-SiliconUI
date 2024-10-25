from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QGraphicsOpacityEffect

from siui.components import SiDenseVContainer, SiLabel
from siui.components.widgets.expands import SiVExpandWidget
from siui.core import Si, SiColor, SiExpAccelerateAnimation
from siui.gui import SiFont

from ..layer import SiLayer


class DenseVContainerBG(SiDenseVContainer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.background = SiLabel(self)
        self.background.setFixedStyleSheet("border-radius: 8px")
        self.background.setColor(SiColor.trans(self.getColor(SiColor.INTERFACE_BG_A), 0.8))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.background.resize(event.size())


class StateChangeOverlay(SiVExpandWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.container = DenseVContainerBG(self)

        self.title = SiLabel(self)
        self.title.setFont(SiFont.getFont(size=18, weight=QFont.Weight.Normal))
        self.title.setTextColor(self.getColor(SiColor.TEXT_B))
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFixedHeight(24)
        self.title.setSiliconWidgetFlag(Si.AdjustSizeOnTextChanged)

        self.subtitle = SiLabel(self)
        self.subtitle.setFont(SiFont.getFont(size=16, weight=QFont.Weight.Normal))
        self.subtitle.setTextColor(self.getColor(SiColor.TEXT_D))
        self.subtitle.setAlignment(Qt.AlignCenter)
        self.subtitle.setFixedHeight(16)
        self.subtitle.setSiliconWidgetFlag(Si.AdjustSizeOnTextChanged)

        self.div = SiLabel(self)
        self.div.setFixedStyleSheet("border-radius: 1px")
        self.div.resize(168, 2)
        self.div.setColor("#20FFFFFF")

        self.tip = SiLabel(self)
        self.tip.setFont(SiFont.getFont(size=12, weight=QFont.Weight.Normal))
        self.tip.setTextColor(self.getColor(SiColor.TEXT_D))
        self.tip.setAlignment(Qt.AlignCenter)
        self.tip.setFixedHeight(16)
        self.tip.setSiliconWidgetFlag(Si.AdjustSizeOnTextChanged)

        self.container.setSpacing(0)
        self.container.setAlignment(Qt.AlignCenter)
        self.container.addPlaceholder(16)
        self.container.addWidget(self.title)
        self.container.addPlaceholder(4)
        self.container.addWidget(self.subtitle)
        self.container.addPlaceholder(16)
        self.container.addWidget(self.div)
        self.container.addPlaceholder(10)
        self.container.addPlaceholder(16, side="bottom")
        self.container.addWidget(self.tip, side="bottom")

        self.setAttachment(self.container)

        self.fade_out_timer = QTimer(self)
        self.fade_out_timer.setSingleShot(True)
        self.fade_out_timer.setInterval(2000)
        self.fade_out_timer.timeout.connect(lambda: self.expandTo(0.8))
        self.fade_out_timer.timeout.connect(lambda: self.setOpacityTo(0))

        self.animationGroup().fromToken("expand").setAccelerateFunction(lambda x: (x / 10) ** 5)

        self.animation_opacity = SiExpAccelerateAnimation(self)
        self.animation_opacity.setAccelerateFunction(lambda x: (x / 10) ** 3)
        self.animation_opacity.setFactor(1/2)
        self.animation_opacity.setBias(0.01)
        self.animation_opacity.setCurrent(1)
        self.animation_opacity.setTarget(1)
        self.animation_opacity.ticked.connect(self.on_opacity_changed)

    def on_opacity_changed(self, opacity):
        effect = QGraphicsOpacityEffect()
        effect.setOpacity(opacity)
        self.setGraphicsEffect(effect)

    def fadeIn(self):
        self.expandTo(1)
        self.setOpacityTo(1)
        self.animation_opacity.start()

    def fadeOut(self):
        self.fade_out_timer.start()

    def resizeEvent(self, event):
        super().resizeEvent(event)


class LayerOverLays(SiLayer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.state_change_overlay = StateChangeOverlay(self)
        self.state_change_overlay.adjustSize()
        self.state_change_overlay.setFixedSize(216, 120)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.state_change_overlay.move((self.width() - self.state_change_overlay.width()) // 2, int((self.height() - self.state_change_overlay.height()) * 0.785))
        self.state_change_overlay.fadeIn()
        self.state_change_overlay.fadeOut()
        self.state_change_overlay.title.setText("设置窗口大小")
        self.state_change_overlay.tip.setText("无快捷键")
        self.state_change_overlay.subtitle.setText(f"{self.width()}x{self.height()}")