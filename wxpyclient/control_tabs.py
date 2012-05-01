import wx


def class_instance_dispatch(class_type, *args, **kwargs):
    dispatch_table = {"buttonA": ("wx", "Button"),
                      "buttonB": ("button_base", "ButtonBase"),
                     }

    (module_name, class_name) = dispatch_table[class_type]

    module = __import__(module_name)
    class_ = getattr(module, class_name)
    print args, kwargs
    return class_(*args, **kwargs)


class TabPanel(wx.Panel):
    """
    This will be the first notebook tab
    """
    def __init__(self, parent):
        """"""

        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(class_instance_dispatch("buttonA", self, -1, 'Button1'), 1)
        box.Add(class_instance_dispatch("buttonB", self, -1, 'Button2'), 1)
        self.SetSizer(box)


class NotebookDemo(wx.Notebook):
    """
    Notebook class
    """
    def __init__(self, parent):
        wx.Notebook.__init__(self, parent, id=wx.ID_ANY, style=
                             wx.BK_DEFAULT
                             #wx.BK_TOP
                             #wx.BK_BOTTOM
                             #wx.BK_LEFT
                             #wx.BK_RIGHT
                             )

        # Create the first tab and add it to the notebook
        tabOne = TabPanel(self)
        tabOne.SetBackgroundColour("Gray")
        self.AddPage(tabOne, "TabOne")

        # Create and add the second tab
        tabTwo = TabPanel(self)
        self.AddPage(tabTwo, "TabTwo")

        # Create and add the third tab
        self.AddPage(TabPanel(self), "TabThree")

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanging)

    def OnPageChanged(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        print 'OnPageChanged,  old:%d, new:%d, sel:%d\n' % (old, new, sel)
        event.Skip()

    def OnPageChanging(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        print 'OnPageChanging, old:%d, new:%d, sel:%d\n' % (old, new, sel)
        event.Skip()


class ControlTabs(wx.Frame):
    def __init__(self, sysname):
        wx.Frame.__init__(self, None, title="%s" % sysname, id=wx.ID_ANY,
                          size=(600,400)
                          )
        panel = wx.Panel(self)

        notebook = NotebookDemo(panel)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(notebook, 1, wx.ALL|wx.EXPAND, 5)
        panel.SetSizer(sizer)
        self.Layout()

        self.Show()


#if __name__ == "__main__":
#    app = wx.PySimpleApp()
#    frame = DemoFrame()
#    app.MainLoop()
