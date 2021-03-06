import os
import string
import urllib2
import evas, ecore, esudo
import efl.elementary as elm
import debfile as debianfile

"""          Checks/Information Functions

Part of eDeb, a deb-package installer built on Python-EFL's.
By: AntCer (bodhidocs@gmail.com)

"""

HOME = os.getenv("HOME")

#----Popups
def generic_error_popup(win, string):
    popup = elm.Popup(win)
    popup.text = string
    popup.timeout = 2.3
    popup.show()

def no_net_popup(win):
    popup = elm.Popup(win)
    popup.text = "<b>Error</><br><br>No internet access.<br>Please try again when connected to internet."
    bt = elm.Button(win)
    bt.text = "OK"
    bt.callback_clicked_add(lambda o: popup.delete())
    popup.part_content_set("button1", bt)
    popup.show()

def not_installable_popup(win, msg):
    popup = elm.Popup(win)
    popup.text = "<b>Non-Eligibility Error</b><br><br>%s" %msg
    bt = elm.Button(win)
    if "Broken " in msg:
        bt.text = "Fix"
        bt.callback_clicked_add(lambda o: dependency_comp(popup, win))
        popup.part_content_set("button1", bt)
        bt = elm.Button(win)
    bt.text = "Close"
    bt.callback_clicked_add(lambda o: popup.delete())
    if "Broken " in msg:
        popup.part_content_set("button2", bt)
    else:
        popup.part_content_set("button1", bt)
    popup.show()

def dependency_popup(win, en):
    popup = elm.Popup(win)
    popup.text = "<b>Urgent</b><br><br>Attempt to install missing/unmet dependencies by clicking <b>Grab</b>."
    bt = elm.Button(win)
    bt.text = "Grab"
    bt.callback_clicked_add(lambda o: dependency_comp(popup, win, en))
    popup.part_content_set("button1", bt)
    popup.show()

#----Dependency Completion
def dependency_comp(popup, win, en):
    popup.delete()
    try:
        con = urllib2.urlopen("http://www.google.com/")
    #~ except urllib2.URLError, e:
    except IOError:
        print("No network activity detected")
        print("Please try again with an established Internet Connection.")
        no_net_popup(win)
    else:
        print("Starting attempt to fulfill dependencies:")
        dep_comp = "apt-get -f install"
        n = elm.InnerWindow(win)
        info_en = elm.Entry(win)
        info_en_bt = elm.Button(win)
        bt3 = elm.Button(win)
        bt4 = elm.Button(win)
        esudo.eSudo(bt3=bt3, bt4=bt4, info=info_en, en=en, info_bt=info_en_bt, command=dep_comp, window=win, start_callback=start_cb, end_callback=dep_cb, data=n)

#---End Callbacks
def dep_grab_cb(exit_code, win, *args, **kwargs):
    n  = kwargs["data"]
    info = kwargs["info"]
    bt = kwargs["info_bt"]
    deb = kwargs["deb"]
    dep_btn = kwargs["dep_btn"]
    dep_fx = kwargs["dep_fx"]
    depbt_chk = kwargs["depbt_chk"]

    if exit_code == 0:
        print("Successfully Grabbed Dependencies.")
        info.entry_append("<ps><ps><b>Dependencies were successfully met!</b>")
        deb.depends_check(True)
        depbt_chk = False
        dep_btn.delete()
        dep_fx(None)
        bt.disabled_set(False)
    else:
        print("Something went wrong while installing dependencies.")
        info.entry_append("<ps><ps><b>Error: Dependency-grabbing was not successful.</b><ps><ps>Please view all <b>Errors</b> above to find out why.")
        bt.text = "OK"
        bt.disabled_set(False)
def main_cb(exit_code, win, *args, **kwargs):
    en = kwargs["en"]
    n  = kwargs["data"]
    info = kwargs["info"]
    bt = kwargs["info_bt"]
    bt1 = kwargs["bt1"]
    bt2 = kwargs["bt2"]
    bt3 = kwargs["bt3"]
    bt4 = kwargs["bt4"]

    if bt1 != None:
        bt1.disabled_set(False)
        bt2.disabled_set(False)
        en.disabled_set(False)
    if exit_code == 0:
        print("Installation completed successfully!")
        info.entry_append("<ps><ps><b>Installation completed successfully!</b>")
        en.path_set(HOME)
    else:
        print("Something went wrong. Likely, dependencies that weren't met before attempting installation.")
        info.entry_append("<ps><ps><b>Urgent</b>: Something went wrong with installation. Likely, unmet dependencies.")
        bt.text = "Install Missing Dependencies"
        bt.callback_clicked_add(lambda o: dependency_popup(win, en))
    bt.disabled_set(False)
    bt3.disabled_set(False)
    bt4.disabled_set(False)
def dep_cb(exit_code, win, *args, **kwargs):
    en = kwargs["en"]
    n = kwargs["data"]
    info = kwargs["info"]
    bt = kwargs["info_bt"]

    if exit_code == 0:
        print("Successfully Grabbed Dependencies & Completed Installation.")
        info.entry_append("<ps><ps><b>Dependencies were met and installation completed successfully!</b>")
        bt.disabled_set(False)
        en.path_set(HOME)
    else:
        print("Something went wrong while attempting to complete installation.")
        info.entry_append("<ps><ps><b>Error: Dependency-grabbing was not successful.</b><ps><ps>Please view all <b>Errors</b> above to find out why.")
        bt.text = "OK"
        bt.disabled_set(False)

#---Start Callback
def start_cb(win, *args, **kwargs):
    n = kwargs["data"]
    en = kwargs["info"]
    bt = kwargs["info_bt"]

    box = elm.Box(win)
    box.size_hint_weight = 1.0, 1.0
    box.size_hint_align = -1.0, -1.0

    en.entry_set("<b>Starting installation...</b>")
    en.size_hint_weight = 1.0, 1.0
    en.size_hint_align = -1.0, -1.0
    en.line_wrap_set(2)
    en.input_panel_return_key_disabled = False
    en.editable_set(False)
    en.scrollable_set(True)
    box.pack_end(en)
    en.show()

    bt.text = "Done"
    bt.callback_clicked_add(lambda o: n.delete())
    bt.disabled_set(True)
    bt.size_hint_align = -1.0, -1.0
    bt.size_hint_weight = 1.0, 0.0
    box.pack_end(bt)
    bt.show()

    bx = elm.Box(win)
    bx.size_hint_weight = 1.0, 0.0
    bx.size_hint_align = -1.0, -1.0
    bx.horizontal_set(True)
    bx.homogeneous_set(True)
    box.pack_end(bx)
    bx.show()

    bt = kwargs["bt3"]
    bt.text = "Copy"
    bt.callback_clicked_add(lambda o: copying(en, win))
    bt.disabled_set(True)
    bt.size_hint_align = -1.0, -1.0
    bt.size_hint_weight = 0.0, 0.0
    bx.pack_end(bt)
    bt.show()

    bt = kwargs["bt4"]
    bt.text = "Export"
    bt.callback_clicked_add(lambda o: exporting(en, win))
    bt.disabled_set(True)
    bt.size_hint_align = -1.0, -1.0
    bt.size_hint_weight = 0.0, 0.0
    bx.pack_end(bt)
    bt.show()

    box.show()

    n.content = box
    n.show()
    n.activate()

#~ Copy/Export Functions
def copying(en, win):
    temp = elm.Entry(win)
    temp.entry = txt_format(en.entry_get(),0)
    temp.select_all()
    temp.selection_copy()
    temp.delete()

def exporting(en, win):
    lb = elm.Label(win)
    lb.text = "<b>...exported : %s/edeb.info</b>"%HOME
    with open("%s/edeb.info"%HOME, "w") as file:
        file.write(txt_format(en.entry_get(),1))
    n = elm.Notify(win)
    n.orient = 2
    n.content = lb
    n.timeout_set(3.0)
    n.show()

def txt_format(string, num):
    if num==0:
        string = string.replace("<ps>", "<br>")
    elif num==1:
        string = string.replace("<ps>", "\n")
    string = string.replace("</ps>", "")
    string = string.replace("<b>", "")
    string = string.replace("</b>", "")
    string = string.replace("         ", "")
    return string


class Checks(object):
    def __init__(self, command=False, window=False):
        self.win        = window
        self.file       = command
        self.depbtn     = False
        self.depcheck   = False
        self.chk        = 0

#----Package Info
    def pkg_information(self, deb):
        win = self.win

        try:
            filesinlist
        except NameError:
            filesinlist = "<br>       ".join(deb.filelist)

#----------------Desc
        try:
            raw_desc = string.split(deb["Description"], "\n")
            long_desc = "%s<br>" %raw_desc[0].replace("&", "&amp;").replace("<", "&lt;") ; del raw_desc[0]
            for line in raw_desc:
                tmp = string.strip(line).replace("&", "&amp;").replace("<", "&lt;")
                if len(tmp) == 1:
                    pass
                else:
                    long_desc += " " + tmp
        except:
            long_desc = "Not available"

        pkg_desc = "<br><b>Description:</> %s" % long_desc
#----------------Name
        try:
            pkg_name = "<b>Package:</> %s<ps>" % string.split(deb["Package"], "\n")[0]
        except:
            pkg_name = ""
#----------------Auth
        try:
            pkg_auth = "<b>Maintainer:</> %s<ps>" % string.split(deb["Maintainer"], "\n")[0]
        except:
            pkg_auth = ""
#----------------Ver
        try:
            pkg_ver = "<b>Version:</> %s<ps>" % string.split(deb["Version"], "\n")[0]
        except:
            pkg_ver = ""
#----------------Arch
        pkg_arch    = "<b>Architecture:</> %s<ps>" % string.split(deb["Architecture"], "\n")[0]
#----------------Sec
        try:
            pkg_sec = "<b>Section:</> %s<ps>" % string.split(deb["Section"], "\n")[0]
        except:
            pkg_sec = ""
#----------------Pri
        try:
            pkg_pri = "<b>Priority:</> %s<ps>" % string.split(deb["Priority"], "\n")[0]
        except:
            pkg_pri = ""
#----------------Size
        try:
            pkg_size = "<b>Installed-Size:</> %s<ps>" % string.split(deb["Installed-Size"] + " KB", "\n")[0]
        except:
            pkg_size = ""
#----------------Recc
        try:
            pkg_recc = "<b>Recommends:</> %s<ps>" % string.split(deb["Recommends"], "\n")[0]
        except:
            pkg_recc = ""
#----------------Conf
        try:
            pkg_conf = "<b>Conflicts:</> %s<ps>" % string.split(deb["Conflicts"], "\n")[0].replace("<", "&lt;")
        except:
            pkg_conf = ""
#----------------Repl
        try:
            pkg_repl = "<b>Replaces:</> %s<ps>" % string.split(deb["Replaces"], "\n")[0]
        except:
            pkg_repl = ""
#----------------Prov
        try:
            pkg_prov = "<b>Provides:</> %s<ps>" % string.split(deb["Provides"], "\n")[0]
        except:
            pkg_prov = ""
#----------------HP
        try:
            pkg_hp = "<b>Homepage:</> %s" % string.split(deb["Homepage"], "\n")[0]
        except:
            pkg_hp = ""
#----------------Dep
        #~ pkg_dep  = getoutput("dpkg -f %s | sed 's/<</less than/' | awk '/Depends:/' | sed 's/Depends:/ /' | sed 's/Pre-/ /'" %self.file)
#----------------FB
        if pkg_hp == "" and pkg_size == "" and pkg_recc == "" and pkg_prov == "" and pkg_conf == "" and pkg_repl == "":
            pkg_size = "None<ps>"


        def dependency_grab():
            try:
                con = urllib2.urlopen("http://www.google.com/")
            #~ except urllib2.URLError, e:
            except IOError:
                print("No network activity detected")
                print("Please try again with an established Internet Connection.")
                iw.delete()
                no_net_popup(self.win)
            else:
                missingdep = deb.missing_deps
                missdep = " ".join(missingdep)
                print("Starting Dependency Grab:")
                dep_grab = "apt-get install %s" %(missdep)
                n = elm.InnerWindow(win)
                info_en = elm.Entry(win)
                info_en_bt = elm.Button(win)
                bt3 = elm.Button(win)
                bt4 = elm.Button(win)
                esudo.eSudo(depbt_chk=self.depbtn, bt3=bt3, bt4=bt4, deb=deb, dep_fx=depends, dep_btn=bt2, info=info_en, info_bt=info_en_bt, command=dep_grab, window=self.win, start_callback=start_cb, end_callback=dep_grab_cb, data=n)

        def compare(btn):
            debcompare = deb.compare_to_version_in_cache(use_installed=True)
            debcomparerepo = deb.compare_to_version_in_cache(use_installed=False)

            pkg_info_en.entry_set("<b>VS. Installed Version<ps>")
            if debcompare == 1:
                pkg_info_en.entry_append("Outdated:</b> This version is lower than the version currently installed.")
            elif debcompare == 2:
                pkg_info_en.entry_append("Same:</b> The same version is already installed.")
            elif debcompare == 3:
                pkg_info_en.entry_append("Newer:</b> This version is higher than the version currently installed.")
            elif debcompare == 0:
                pkg_info_en.entry_append("None:</b> This application has not been installed.")
            else:
                pkg_info_en.entry_append("Not found:</b> A version installed or in the repository cannot be located for comparison.")

            pkg_info_en.entry_append("<ps><ps><b>VS. Repository Version<ps>")
            if debcomparerepo == 1:
                pkg_info_en.entry_append("Outdated:</b> This version is lower than the version available in the repository.")
            elif debcomparerepo == 2:
                pkg_info_en.entry_append("Same:</b> This version is the same as the version available in the repository.")
            elif debcomparerepo == 3:
                pkg_info_en.entry_append("Newer:</b> This version is higher than the version available in the repository.")
            elif debcomparerepo == 0:
                pkg_info_en.entry_append("None:</b> This application cannot be located in the repository.")
            else:
                pkg_info_en.entry_append("Not found:</b> A version installed or in the repository cannot be located for comparison.")

        def checks(btn):
            def real_checks(btn, pkg_info_en):
                try:
                    breaks = deb.check_breaks_existing_packages()
                    if breaks != True:
                        pkg_info_en.entry_set("<b>WARNING:</> Installing this package will break certain existing packages.<ps><ps><ps>%s"%breaks)
                    elif deb.check_conflicts() != True:
                        pkg_info_en.entry_set("<b>WARNING:</> There are conflicting packages.")
                        pkg_info_en.entry_append("<ps> %s" %deb.conflicts)
                    else:
                        pkg_info_en.entry_set("<b>CLEAR:</> You are cleared to go. The selected file has passed <b>ALL</> checks.")
                    btn.disabled_set(False)
                except:
                    print("eDeb Critical Error: Virtual group issue.\nExiting...")
                    elm.exit()
                    quit()

            self.chk += 1
            btn.disabled_set(True)
            pkg_info_en.entry_set("<b>Please wait...</>")
            et = ecore.Timer(0.1, real_checks, btn, pkg_info_en)

        def depends(btn):
            if not self.depcheck:
                self.depcheck = True
                deb.depends_check()

            pkg_dep = []
            for x in deb.depends:
                pkg_dep.append(x[0][0])
            pkg_dep     = ", ".join(pkg_dep)
            if pkg_dep == "":
                pkg_dep = "None"

            missdep     = ", ".join(deb.missing_deps)
            pkg_info_en.entry_set("<b>Dependencies:</> %s<ps><ps><b>Missing Dependencies:</> " %pkg_dep)
            #~ pkg_info_en.entry_set("<b>Dependencies:</> %s<ps><ps><b>Missing Dependencies:</> " %pkg_dep)
            if deb.missing_deps == []:
                pkg_info_en.entry_append("None<ps>")
            else:
                pkg_info_en.entry_append("%s<ps>" %missdep)
                if not self.depbtn:
                    bt2.text = "Attempt to Install Missing Dependencies"
                    bt2.show()
                    self.depbtn = True

        def info(btn):
            pkg_info_en.entry_set("%s%s%s%s%s%s%s<ps><ps><b><i>Extra Information:</i></b><ps>%s%s%s%s%s%s" \
                            %(pkg_name, pkg_auth, pkg_ver, pkg_arch, pkg_sec, pkg_pri, pkg_desc, pkg_size, pkg_recc, pkg_conf, pkg_repl, pkg_prov, pkg_hp))

        def files(btn):
            def real_files(btn, pkg_info_en):
                pkg_info_en.entry_set("<b>Files:</><ps>       %s<ps>" %filesinlist)
                btn.disabled_set(False)

            btn.disabled_set(True)
            et = ecore.Timer(0.3, real_files, btn, pkg_info_en)
            pkg_info_en.entry_set("<b>Loading file list...</>")

        def closebtn():
            self.depcheck = None
            pkgbox.delete()
            iw.delete()

        pkgbox = elm.Box(self.win)
        pkgbox.size_hint_weight_set(1.0, 1.0)
        pkgbox.show()

        pkgfr = elm.Frame(self.win)
        pkgfr.text_set("Package Information")
        pkgfr.size_hint_weight_set(0.0, 0.0)
        pkgfr.size_hint_align_set(0.5, -1.0)
        pkgbox.pack_end(pkgfr)
        pkgfr.show()

        tb = elm.Toolbar(self.win)
        tb.size_hint_weight_set(1.0, 0.0)
        tb.size_hint_align_set(-1.0, -1.0)
        tb.item_append("", "Info",    lambda x,y: info(y))
        tb.item_append("", "Checks",  lambda x,y: checks(y))
        tb.item_append("", "Compare", lambda x,y: compare(y))
        tb.item_append("", "Depends", lambda x,y: depends(y))
        tb.item_append("", "Files",   lambda x,y: files(y))
        tb.homogeneous_set(True)
        tb.select_mode_set(2)
        pkgbox.pack_end(tb)
        tb.show()

        pkg_info_en = elm.Entry(self.win)
        pkg_info_en.line_wrap_set(2)
        pkg_info_en.input_panel_return_key_disabled = False
        pkg_info_en.size_hint_align_set(-1.0, -1.0)
        pkg_info_en.size_hint_weight_set(1.0, 1.0)
        pkg_info_en.editable_set(False)
        pkg_info_en.scrollable_set(True)
        pkg_info_en.entry_set("%s%s%s%s%s%s%s<ps><ps><b><i>Extra Information:</i></b><ps>%s%s%s%s%s%s" \
                            %(pkg_name, pkg_auth, pkg_ver, pkg_arch, pkg_sec, pkg_pri, pkg_desc, pkg_size, pkg_recc, pkg_conf, pkg_repl, pkg_prov, pkg_hp))
        pkgbox.pack_end(pkg_info_en)
        pkg_info_en.show()

        iw = elm.InnerWindow(self.win)
        iw.content_set(pkgbox)
        iw.show()
        iw.activate()

        bt2 = elm.Button(self.win)
        bt2.size_hint_weight_set(1.0, 0.0)
        bt2.size_hint_align_set(-1.0, -1.0)
        bt2.callback_clicked_add(lambda o: dependency_grab())
        pkgbox.pack_end(bt2)
        if self.depbtn:
            bt2.text = "Attempt to Install Missing Dependencies"
            bt2.show()

        bt = elm.Button(self.win)
        bt.text = "OK"
        bt.size_hint_weight_set(1.0, 0.0)
        bt.size_hint_align_set(-1.0, -1.0)
        bt.callback_clicked_add(lambda o: closebtn() if self.chk>0 else generic_error_popup(win,"<b>For your own benefit...</><br><br>Please run <b>Checks</> before installing."))
        #~ bt.callback_clicked_add(lambda o: closebtn())
        pkgbox.pack_end(bt)
        bt.show()

#----Checks
    def check_file(self, fs, win, deb):
        if self.file == HOME:
            generic_error_popup(win, "<b>No File Selected</><br><br>Please select an appropriate file candidate for installation.")
        else:
            self.pkg_information(deb)

    def check_file_install(self, bt1, bt2, win, en):
        if self.file == HOME:
            generic_error_popup(win, "<b>No File Selected</><br><br>Please select an appropriate file candidate for installation.")
        else:
            bt1.disabled_set(True)
            bt2.disabled_set(True)
            en.disabled_set(True)
            self.bt1 = bt1
            self.bt2 = bt2
            print("Package: %s" %self.file)
            install_deb = 'dpkg -i %s'%self.file
            n = elm.InnerWindow(win)
            info_en = elm.Entry(win)
            info_en_bt = elm.Button(win)
            bt3 = elm.Button(win)
            bt4 = elm.Button(win)
            esudo.eSudo(bt3=bt3, bt4=bt4, info=info_en, info_bt=info_en_bt, command=install_deb, window=win, bt1=bt1, bt2=bt2, en=en, start_callback=start_cb, end_callback=main_cb, data=n)
