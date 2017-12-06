# -*- coding: utf-8 -*-
import pynotify

pynotify.init("icon-summary-body")

for i in range(100):
    pynotify.Notification("Hello", "乱入了啊啊啊啊", "notification-message-im").show()
