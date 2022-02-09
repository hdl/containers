#!/usr/bin/env python3

# Authors:
#   Unai Martinez-Corral
#
# Copyright 2021 Unai Martinez-Corral <unai.martinezcorral@ehu.eus>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

from sys import argv as sys_argv, exit as sys_exit

import tkinter as tk
from tkinter import messagebox as mbox
from tkinter import ttk as ttk, filedialog as fd

from pathlib import Path
from textwrap import dedent

from registry import DumpRegistryDataToJSON, TreeFromJSON


class HDLCE(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        parent.title("HDL Containers Explorer (HDLCE)")
        parent.state("zoomed")

        self.TreeView = ttk.Treeview(self)
        self.TreeView.pack(fill="both", side=tk.TOP, expand=True)

        self.pack(fill="both", expand=True)

        imgDir = Path(__file__).parent / "img"
        parent.iconphoto(False, tk.PhotoImage(file=imgDir / "icon.png"))

        self._initMenu(parent)
        self._initTreeView()

    def _initMenu(self, parent):
        """
        Initialise the main Menu.
        """

        def cbAbout():
            mbox.showinfo(
                "About",
                dedent(
                    """\
            HDL Containers Explorer (HDLCE)
            <github.com/hdl/containers>

            Copyright 2021 Unai Martinez-Corral
            <unai.martinezcorral@ehu.eus>

            Licensed under the Apache License, Version 2.0
            <apache.org/licenses/LICENSE-2.0>
            """
                ),
            )

        def askdirectoy():
            dirName = fd.askdirectory(mustexist=True)
            return Path(__file__).resolve().parent / 'registry' if dirName != "" else Path(dirName)

        def cbFetch():
            dirName = askdirectoy()
            DumpRegistryDataToJSON(dirName, 'hdl-containers')

        def cbLoad():
            dirName = askdirectoy()
            self.Data = TreeFromJSON(dirName)
            self.loadTree()

        self.Menu = tk.Menu(parent)
        parent.config(menu=self.Menu)

        fileMenu = tk.Menu(self.Menu, tearoff=0)
        fileMenu.add_command(label="Fetch data from registry...", command=cbFetch)
        fileMenu.add_command(label="Load registry data...", command=cbLoad)
        fileMenu.add_separator()
        fileMenu.add_command(label="About...", command=cbAbout)
        fileMenu.add_separator()
        fileMenu.add_command(label="Exit", command=parent.quit)
        self.Menu.add_cascade(label="File", menu=fileMenu)

    def _initTreeView(self):
        """
        Initialise the TreeView (define the columns).
        """
        ftw = self.TreeView
        ftw["columns"] = "tags"
        ftw.heading("#0", text="Image")
        ftw.heading("tags", text="Tags")

    def loadTree(self, parent=""):
        """
        Populate the TreeView with the hierarchical image, digest and tag data.
        """
        ftw = self.TreeView

        def addTreeItem(parent, text, isOpen=True, data=()):
            return ftw.insert(
                parent,
                tk.END,
                text=text,
                values=data,
                open=isOpen,
            )

        def traversePath(parent, name, data):
            if data != {}:
                item = addTreeItem(parent, name)
                for name, data in data.items():
                    if name != 'data':
                        traversePath(item, name, data)
                    else:
                        for name, content in data['items'].items():
                            if name != 'name':
                                other = addTreeItem(item, data['name'], isOpen=False, data=(content['tags']))
                                addTreeItem(other, name)
                                for name, tags in content['other'].items():
                                    addTreeItem(other, name, data=(tags))

        for name, data in self.Data.items():
            traversePath(parent, name, data)


if __name__ == "__main__":
    sys_exit(HDLCE(tk.Tk()).mainloop())
