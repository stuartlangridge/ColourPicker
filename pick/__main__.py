import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf, Gio
try:
    gi.require_version('Unity', '7.0')
    from gi.repository import Unity
except:
    Unity = False
import cairo, math, json, os, codecs, time, subprocess, sys, base64, colorsys

__VERSION__ = "1.51"

if "--snark" in sys.argv:
    from .snark import COLOUR_NAMES
else:
    from .colours import COLOUR_NAMES


def rgb_to_lab(r, g, b):
    """Convert RGB colours to LAB colours
       thank you Roman Nazarkin, http://stackoverflow.com/a/16020102/1418014"""
    inputColor = [r, g, b]
    num = 0
    RGB = [0, 0, 0]
    for value in inputColor:
        value = float(value) / 255
        if value > 0.04045:
            value = ((value + 0.055) / 1.055) ** 2.4
        else:
            value = value / 12.92
        RGB[num] = value * 100
        num = num + 1
    XYZ = [0, 0, 0]
    X = RGB[0] * 0.4124 + RGB[1] * 0.3576 + RGB[2] * 0.1805
    Y = RGB[0] * 0.2126 + RGB[1] * 0.7152 + RGB[2] * 0.0722
    Z = RGB[0] * 0.0193 + RGB[1] * 0.1192 + RGB[2] * 0.9505
    XYZ[0] = round(X, 4)
    XYZ[1] = round(Y, 4)
    XYZ[2] = round(Z, 4)

    XYZ[0] = float(XYZ[0]) / 95.047   # ref_X =  95.047
    # XYZ[0]: Observer= 2deg, Illuminant= D65
    XYZ[1] = float(XYZ[1]) / 100.0    # ref_Y = 100.000
    XYZ[2] = float(XYZ[2]) / 108.883  # ref_Z = 108.883

    num = 0
    for value in XYZ:
        if value > 0.008856:
            value = value ** (0.3333333333333333)
        else:
            value = (7.787 * value) + (16 / 116)
        XYZ[num] = value
        num = num + 1

    Lab = [0, 0, 0]
    L = (116 * XYZ[1]) - 16
    a = 500 * (XYZ[0] - XYZ[1])
    b = 200 * (XYZ[1] - XYZ[2])

    Lab[0] = round(L, 4)
    Lab[1] = round(a, 4)
    Lab[2] = round(b, 4)

    return Lab


def deltaE(labA, labB):
    """deltaE is the standard way to compare two colours
    for how visibly alike they are"""
    deltaL = labA[0] - labB[0]
    deltaA = labA[1] - labB[1]
    deltaB = labA[2] - labB[2]
    c1 = math.sqrt(labA[1] * labA[1] + labA[2] * labA[2])
    c2 = math.sqrt(labB[1] * labB[1] + labB[2] * labB[2])
    deltaC = c1 - c2
    deltaH = deltaA * deltaA + deltaB * deltaB - deltaC * deltaC
    if deltaH < 0:
        deltaH = 0
    else:
        deltaH = math.sqrt(deltaH)
    sc = 1.0 + 0.045 * c1
    sh = 1.0 + 0.015 * c1
    deltaLKlsl = deltaL / (1.0)
    deltaCkcsc = deltaC / (sc)
    deltaHkhsh = deltaH / (sh)
    i = (deltaLKlsl * deltaLKlsl + deltaCkcsc * deltaCkcsc +
         deltaHkhsh * deltaHkhsh)
    if i < 0:
        return 0
    else:
        return math.sqrt(i)


LAB_COLOUR_NAMES = [(rgb_to_lab(x[0], x[1], x[2]), x[3]) for x in COLOUR_NAMES]


class Main(object):
    def __init__(self):
        # useful globals
        self.snapsize = (120, 120)  # must both be even, and must be square
        self.closest_name_cache = {}
        self.history = []
        self.colour_text_labels = []
        self.grabbed = False
        self.zoomlevel = 2
        self.resize_timeout = None
        self.window_metrics = None
        self.window_metrics_restored = False

        # create application
        self.app = Gtk.Application.new(
            "org.kryogenix.pick-colour-picker",
            Gio.ApplicationFlags.HANDLES_COMMAND_LINE)
        self.app.connect("command-line", self.handle_commandline)

    def pick_after_window_mapped(self, window, _):
        window.disconnect_by_func(self.pick_after_window_mapped)
        self.grab(self.btngrab)

    def handle_commandline(self, app, cmdline):
        if hasattr(self, "w"):
            # already started
            if "--about" in cmdline.get_arguments():
                self.show_about_dialog()
            if "--pick" in cmdline.get_arguments():
                GLib.idle_add(self.grab, self.btngrab)
            return 0
        # First time startup
        if "--pick" in cmdline.get_arguments():
            self.start_everything_first_time(self.pick_after_window_mapped)
        else:
            self.start_everything_first_time()
        if "--about" in cmdline.get_arguments():
            self.show_about_dialog()
        return 0

    def start_everything_first_time(self, on_window_map=None):
        GLib.set_application_name("Pick")

        # the window
        self.w = Gtk.ApplicationWindow.new(self.app)
        self.w.set_title("Pick")
        self.w.set_size_request((self.snapsize[0]/2) * 2 + 200,
                                (self.snapsize[1]/2) * 5 + 200)
        self.w.connect("motion-notify-event", self.magnifier_move)
        self.w.connect("button-press-event", self.magnifier_clicked)
        self.w.connect("scroll-event", self.magnifier_scrollwheel)
        self.w.connect("key-press-event", self.magnifier_keypress)
        self.w.connect("configure-event", self.window_configure)
        self.w.connect("destroy", lambda a: self.app.quit())
        if on_window_map:
            self.w.connect("map-event", on_window_map)

        # Get the actual cursor scale from gconf so we don't get over the size limit (issue #6)
        try:
            cursor_scale = 1.0
            if os.getenv("CURSOR_SCALE") != None:
                cursor_scale = float(os.getenv("CURSOR_SCALE"))
            else:
                cursor_scale = self.w.get_screen().get_display().get_default_cursor_size() / float(Gio.Settings("org.gnome.desktop.interface").get_int("cursor-size"))
            if cursor_scale != 1.0:
                cursor_scaled_snapsize = int(math.ceil(self.snapsize[0] / 2 / cursor_scale) * 2)
                print "Adjusted cursor size: " + str(cursor_scaled_snapsize)
                self.snapsize = (cursor_scaled_snapsize, cursor_scaled_snapsize)
        except:
            # No gnome/dconf?!
            print "Couldn't determine correct cursor size. If you experience any flickering, try launching with CURSOR_SCALE=2"

        devman = self.w.get_screen().get_display().get_device_manager()
        self.pointer = devman.get_client_pointer()
        keyboards = [
            x for x in devman.list_devices(Gdk.DeviceType.MASTER)
            if x.get_property("input-source") == Gdk.InputSource.KEYBOARD
        ]
        self.keyboard = None
        if len(keyboards) > 0:
            self.keyboard = keyboards[0]
            # bit lairy, that, but it should be OK in normal use cases

        # The lowlight colour: used for subsidiary text throughout,
        # and looked up from the theme
        ok, col = self.w.get_style_context().lookup_color("theme_text_color")
        if ok:
            self.lowlight_rgba = col
        else:
            self.lowlight_rgba = Gdk.RGBA(red=0.5, green=0.5,
                                          blue=0.5, alpha=1)
        ok, col = self.w.get_style_context().lookup_color("theme_fg_color")
        if ok:
            self.highlight_rgba = col
        else:
            self.highlight_rgba = self.w.get_style_context().get_color(
                Gtk.StateFlags.NORMAL)

        # The CSS
        highlight_average = (self.highlight_rgba.red +
                             self.highlight_rgba.green +
                             self.highlight_rgba.blue) / 3
        if highlight_average > 0.5:
            ROWBGCOL = "rgba(0, 0, 0, 0.6)"
        else:
            ROWBGCOL = "rgba(255, 255, 255, 0.6)"
        style_provider = Gtk.CssProvider()
        css = """
            GtkLabel { transition: 250ms ease-in-out; }
            GtkLabel.highlighted { background-color: rgba(255, 255, 0, 0.4); }
            GtkLabel#empty-heading { font-size: 200%; }
            GtkFrame {
                background-color: ROWBGCOL
            }
            GtkEventBox GtkFrame {
                border-width: 0 0 1px 0;
                padding: 6px 0;
            }
            GtkEventBox:focus {
                background: rgba(0, 0, 0, 0.2);
            }
            GtkEventBox:nth-child(5) GtkFrame {
                border-width: 0;
                padding: 6px 0;
            }
        """.replace("ROWBGCOL", ROWBGCOL).encode("utf-8")
        style_provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # the headerbar
        head = Gtk.HeaderBar()
        head.set_show_close_button(True)
        head.props.title = "Pick"
        self.w.set_titlebar(head)
        btngrab = Gtk.Button()
        self.btngrab = btngrab
        icon = Gio.ThemedIcon(name="pick-colour-picker-symbolic")
        theme_icon = Gtk.IconTheme.get_default().lookup_by_gicon(icon, 0, 0)
        if theme_icon:
            # our symbolic icon is included in the theme, so use it
            image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        else:
            # not in the theme, so we're probably running locally;
            # use the local one
            image = Gtk.Image.new_from_file(os.path.join(
                os.path.split(__file__)[0], "..",
                "data", "icons", "scalable", "apps",
                "pick-colour-picker-symbolic.svg"))
        btngrab.add(image)
        head.pack_start(btngrab)
        btngrab.connect("clicked", self.grab)

        # the box that contains everything
        self.vb = Gtk.VBox()

        # The menu
        if Unity:
            self.add_desktop_menu()

        # the status bar and its formats list
        hb = Gtk.HBox()
        self.formatters = {
            "CSS hex": lambda r, g, b: "#%02x%02x%02x" % (
                int(r), int(g), int(b)),
            "CSS uppercase hex": lambda r, g, b: ("#%02x%02x%02x" % (
                int(r), int(g), int(b))).upper(),
            "CSS rgb": lambda r, g, b: "rgb(%s, %s, %s)" % (
                int(r), int(g), int(b)),
            "CSS rgba": lambda r, g, b: "rgba(%s, %s, %s, 1)" % (
                int(r), int(g), int(b)),
            "CSS rgb (new-style)": lambda r, g, b: "rgb(%s  %s  %s)" % (
                int(r), int(g), int(b)),
            "CSS rgba (new-style)": lambda r, g, b: "rgb(%s  %s  %s / 100%%)" % (
                int(r), int(g), int(b)),
            "CSS lab": lambda r, g, b: "lab({:.0f}%  {:.0f}  {:.0f} / 100%)".format(*rgb_to_lab(
                int(r), int(g), int(b))),
            "CSS hsl": lambda r, g, b: "hsl({:.0f}deg  {:.0f}%  {:.0f}%)".format(
                colorsys.rgb_to_hls(r/255.0, g/255.0, b/255.0)[0] * 360,
                colorsys.rgb_to_hls(r/255.0, g/255.0, b/255.0)[2] * 100,
                colorsys.rgb_to_hls(r/255.0, g/255.0, b/255.0)[1] * 100),
            "GDK.RGBA": lambda r, g, b: "Gdk.RGBA(%.3f, %.3f, %.3f, 1.0)" % (
                r/255.0, g/255.0, b/255.0),
            "QML Qt.rgba": lambda r, g, b: "Qt.rgba(%.3f, %.3f, %.3f, 1.0)" % (
                r/255.0, g/255.0, b/255.0),
            "Android resource": lambda r, g, b:
                "<color name=\"%s\">#%02x%02x%02x</color>" % (
                    self.closest_name(r, g, b).lower(), r, g, b)
        }
        formats = Gtk.ListStore(str)
        for fr, fn in self.formatters.items():
            formats.append((fr,))
        self.fcom = Gtk.ComboBox.new_with_model(formats)
        fcell = Gtk.CellRendererText()
        self.fcom.pack_start(fcell, expand=True)
        self.fcom.add_attribute(fcell, "text", 0)
        vcell = Gtk.CellRendererText()
        self.fcom.pack_start(vcell, True)
        self.fcom.set_cell_data_func(vcell, self.formatRGB)
        vcell.set_property('xalign', 1.0)
        vcell.set_property("foreground_rgba", self.lowlight_rgba)
        self.active_formatter = "CSS rgb"
        self.fcom.set_active(list(self.formatters.keys()).index(
            self.active_formatter))
        self.fcom.connect("changed", self.change_format)
        hb.pack_start(Gtk.Label("Format:"), False, False, 12)
        hb.pack_start(self.fcom, False, False, 12)
        self.vb.pack_start(hb, False, False, 12)

        # the box that history items go in
        hb3 = Gtk.HBox()
        f = Gtk.Frame()
        self.container_vb = Gtk.VBox()
        self.vb.pack_start(hb3, True, True, 0)
        hb3.pack_start(f, True, True, 12)
        f.add(self.container_vb)
        self.container_vb.get_style_context().add_class("container_vb")

        # The clear history button
        self.btnclear = Gtk.Button("Clear history")
        self.btnclear.set_sensitive(False)
        self.btnclear.connect("clicked", self.clear_history)
        hb2 = Gtk.HBox()
        hb2.pack_end(self.btnclear, False, False, 12)
        self.vb.pack_end(hb2, False, False, 12)

        # the empty state, which we always show now because we don't
        # know if there is history until we've loaded it, which is done lazily
        self.empty = Gtk.VBox()
        icon = Gio.ThemedIcon(name="pick-colour-picker")
        theme_icon = Gtk.IconTheme.get_default().lookup_by_gicon(icon, 48, 0)
        if theme_icon and False:
            # print("Theme icon exists")
            image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.DIALOG)
            # and get a pixbuf from it to use as the default icon
            self.w.set_default_icon(theme_icon.load_icon())
        else:
            image = None
            # not in the theme, so we're probably running locally;
            # use the local one
            licon = os.path.join(
                os.path.split(__file__)[0], "..",
                "data", "icons", "48x48", "apps", "pick-colour-picker.png")
            if os.path.exists(licon):
                # print("Using local icon", licon)
                image = Gtk.Image.new_from_file(licon)
            else:
                # probably we're in a snap
                sicon = os.path.join(
                    os.path.split(__file__)[0],
                    os.environ.get('SNAP'), "usr", "share", "icons", "hicolor",
                    "48x48", "apps", "pick-colour-picker.png")
                if os.path.exists(sicon):
                    # print("Using local snap icon", sicon)
                    image = Gtk.Image.new_from_file(sicon)
            # and set this as the default icon if it exists
            if image:
                self.w.set_default_icon(image.get_pixbuf())
        image.set_property("valign", Gtk.Align.END)
        self.empty.pack_start(image, True, True, 0)
        nocol1 = Gtk.Label("No Colours")
        nocol1.set_name("empty-heading")
        self.empty.pack_start(nocol1, False, False, 12)
        nocol2 = Gtk.Label("You haven't picked any colours.")
        nocol2.set_property("valign", Gtk.Align.START)
        self.empty.pack_start(nocol2, True, True, 0)
        self.w.add(self.empty)

        # and, go
        self.w.show_all()
        GLib.idle_add(self.load_history)

    def window_configure(self, window, ev):
        if not self.window_metrics_restored:
            return False
        if self.resize_timeout:
            GLib.source_remove(self.resize_timeout)
        self.resize_timeout = GLib.timeout_add_seconds(
            1, self.save_window_metrics_after_timeout,
            {"x": ev.x, "y": ev.y, "w": ev.width, "h": ev.height})

    def save_window_metrics_after_timeout(self, props):
        GLib.source_remove(self.resize_timeout)
        self.resize_timeout = None
        self.save_window_metrics(props)

    def save_window_metrics(self, props):
        scr = self.w.get_screen()
        sw = float(scr.get_width())
        sh = float(scr.get_height())
        # We save window dimensions as fractions of the screen dimensions,
        # to cope with screen resolution changes while we weren't running
        self.window_metrics = {
            "ww": props["w"] / sw,
            "wh": props["h"] / sh,
            "wx": props["x"] / sw,
            "wy": props["y"] / sh
        }
        self.serialise()

    def moveit(self, x, y):
        self.w.move(x, y)

    def sizeit(self, w, h):
        self.w.resize(w, h)

    def restore_window_metrics(self, metrics):
        scr = self.w.get_screen()
        sw = float(scr.get_width())
        sh = float(scr.get_height())
        GLib.timeout_add(50, self.moveit,
                         int(sw * metrics["wx"]), int(sh * metrics["wy"]))
        GLib.timeout_add(55, self.sizeit,
                         int(sw * metrics["ww"]), int(sh * metrics["wh"]))

    def add_desktop_menu(self):
        action_group = Gtk.ActionGroup("menu_actions")
        action_filemenu = Gtk.Action("FileMenu", "File", None, None)
        action_group.add_action(action_filemenu)
        action_new = Gtk.Action("FileCapture", "_Capture",
                                "Capture a pixel colour", Gtk.STOCK_NEW)
        action_new.connect("activate", self.grab)
        action_group.add_action_with_accel(action_new, None)
        action_filequit = Gtk.Action("FileQuit", None, None, Gtk.STOCK_QUIT)
        action_filequit.connect("activate", lambda a: self.app.quit())
        action_group.add_action(action_filequit)
        action_group.add_actions([
            ("HelpMenu", None, "Help"),
            ("HelpAbout", None, "About", None, None, self.show_about_dialog)
        ])
        uimanager = Gtk.UIManager()
        uimanager.add_ui_from_string("""
            <ui>
              <menubar name='MenuBar'>
                <menu action='FileMenu'>
                  <menuitem action='FileCapture' />
                  <menuitem action='FileQuit' />
                </menu>
                <menu action='HelpMenu'>
                  <menuitem action='HelpAbout' />
                </menu>
              </menubar>
            </ui>""")
        accelgroup = uimanager.get_accel_group()
        self.w.add_accel_group(accelgroup)
        uimanager.insert_action_group(action_group)
        menubar = uimanager.get_widget("/MenuBar")
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.pack_start(menubar, False, False, 0)
        self.vb.pack_start(box, False, False, 0)

    def show_about_dialog(self, *args):
        about_dialog = Gtk.AboutDialog()
        about_dialog.set_artists(["Sam Hewitt"])
        about_dialog.set_authors(["Stuart Langridge"])
        about_dialog.set_version(__VERSION__)
        about_dialog.set_license_type(Gtk.License.MIT_X11)
        about_dialog.set_website("https://www.kryogenix.org/code/pick")
        about_dialog.run()
        if about_dialog:
            about_dialog.destroy()

    def play_sound(self, soundid):
        # Normally shelling uot is a terrible thing to do, but GI bindings
        # for GSound require Ubuntu 16.04 or later and aren't installed
        # by default, and we're not passing user input to this function,
        # and it's fire-and-forget, and we don't care if it
        # fails, so it's fine.
        try:
            subprocess.Popen(["canberra-gtk-play", "-i", soundid])
        except:
            pass

    def clear_history(self, button):
        self.history = []
        for c in self.container_vb.get_children():
            c.get_parent().remove(c)
        self.w.remove(self.vb)
        self.w.add(self.empty)
        self.serialise()

    def grab(self, btn):
        self.grabbed = True
        # we grab the keyboard so that we get the Escape keypress to cancel
        # a pick even though we're transparent
        if self.keyboard:
            self.keyboard.grab(
                self.w.get_window(),
                Gdk.GrabOwnership.APPLICATION,
                True,
                Gdk.EventMask.KEY_PRESS_MASK,
                None,
                Gdk.CURRENT_TIME)
        self.w.set_opacity(0.0)
        self.set_magnifier_cursor()
        # grab cursor img again after win is transparent
        # even if mouse doesn't move
        GLib.timeout_add(250, self.set_magnifier_cursor)

    def set_magnifier_cursor(self):
        root = Gdk.get_default_root_window()
        pointer, px, py = self.pointer.get_position()

        # Screenshot where the cursor is, at snapsize
        self.latest_pb = self.snap(
            px-(self.snapsize[0]/2), py-(self.snapsize[1]/2),
            self.snapsize[0], self.snapsize[1])

        # Zoom that screenshot up, and grab a
        # snapsize-sized piece from the middle
        scaled_pb = self.latest_pb.scale_simple(
            self.snapsize[0] * 2, self.snapsize[1] * 2,
            GdkPixbuf.InterpType.NEAREST)
        scaled_pb_subset = scaled_pb.new_subpixbuf(
            self.snapsize[0] / 2 + 1, self.snapsize[1] / 2 + 1,
            self.snapsize[0], self.snapsize[1])

        # Create the base surface for our cursor
        base = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                  self.snapsize[0] * self.zoomlevel,
                                  self.snapsize[1] * self.zoomlevel)
        base_context = cairo.Context(base)
        base_context.scale(self.zoomlevel, self.zoomlevel)

        # Create the circular path on our base surface
        base_context.arc(self.snapsize[0] / 2, self.snapsize[1] / 2,
                         self.snapsize[0] / 2, 0, 2*math.pi)

        # Paste in the screenshot
        Gdk.cairo_set_source_pixbuf(base_context, scaled_pb_subset, 0, 0)

        # Save the context now, before clipping, so we can restore it later
        base_context.save()

        # Clip to that circular path, keeping the path around for later,
        # and paint the pasted screenshot
        base_context.clip_preserve()
        base_context.paint()

        # set scale back for when we're drawing the borders
        base_context.scale(1, 1)

        # Draw the outside border of the magnifier
        base_context.set_source_rgba(0, 0, 0, 1)
        base_context.set_line_width(4)
        base_context.stroke()

        # Restore the context, thus removing the clip region
        base_context.restore()

        # Draw the inside square border of the magnifier
        base_context.set_source_rgba(255, 0, 0, 0.5)
        base_context.set_line_width(1)
        base_context.move_to(self.snapsize[0]/2 - 2, self.snapsize[1]/2 - 2)
        base_context.rel_line_to(3, 0)
        base_context.rel_line_to(0, 3)
        base_context.rel_line_to(-3, 0)
        base_context.rel_line_to(0, -3)
        base_context.stroke()

        # Get the current colour and write it on the magnifier,
        # in the default font with a black rectangle under it
        rect_border_width = 2
        col = self.get_colour_from_pb(self.latest_pb)
        text = self.formatters[self.active_formatter](col[0], col[1], col[2])
        # calculate maximum text size
        nfs = 6
        loopcount = 0
        max_rwidth = self.snapsize[0] * 0.7
        while True:
            x_bearing, y_bearing, text_width, text_height, x_advance, y_advance = \
                base_context.text_extents(text)
            rwidth = text_width + (2 * rect_border_width)
            if rwidth > max_rwidth:
                nfs = nfs - 1
                break
            nfs += 1
            base_context.set_font_size(nfs)
            loopcount += 1
            if loopcount > 50:
                # probably an infinite loop
                nfs = 6
                break

        base_context.set_font_size(nfs)
        x_bearing, y_bearing, text_width, text_height, x_advance, y_advance = \
            base_context.text_extents(text)
        text_draw_x = ((base.get_width() / self.zoomlevel) * 0.98) - text_width
        text_draw_y = (((base.get_height() / self.zoomlevel) * 0.95) -
                       text_height)
        base_context.rectangle(
            text_draw_x - rect_border_width + x_bearing,
            text_draw_y - rect_border_width + y_bearing,
            text_width + (2 * rect_border_width),
            text_height + (2 * rect_border_width)
        )
        base_context.set_source_rgba(0, 0, 0, 0.7)
        base_context.fill()
        base_context.set_source_rgba(255, 255, 255, 1.0)
        base_context.move_to(text_draw_x, text_draw_y)
        base_context.show_text(text)
        # and draw colour swatch next to colour name
        base_context.rectangle(
            text_draw_x - rect_border_width + x_bearing - (
                text_height + (2 * rect_border_width)),
            text_draw_y - rect_border_width + y_bearing,
            text_height + (2 * rect_border_width),
            text_height + (2 * rect_border_width)
        )
        base_context.set_source_rgba(col[0]/255.0, col[1]/255.0,
                                     col[2]/255.0, 1.0)
        base_context.fill()

        # turn the base surface into a pixbuf and thence a cursor
        drawn_pb = Gdk.pixbuf_get_from_surface(base, 0, 0, base.get_width(),
                                               base.get_height())
        zoom_pb = drawn_pb.scale_simple(
            self.snapsize[0] * self.zoomlevel, self.snapsize[1] * self.zoomlevel,
            GdkPixbuf.InterpType.TILES)
        magnifier = Gdk.Cursor.new_from_pixbuf(
            self.w.get_screen().get_display(),
            zoom_pb,
            zoom_pb.get_width()/2, zoom_pb.get_height()/2)

        # Set the cursor
        res = self.pointer.grab(
            self.w.get_window(),
            Gdk.GrabOwnership.APPLICATION,
            True,
            (Gdk.EventMask.BUTTON_PRESS_MASK |
             Gdk.EventMask.POINTER_MOTION_MASK |
             Gdk.EventMask.SCROLL_MASK),
            magnifier,
            Gdk.CURRENT_TIME)

    def ungrab(self, *args, **kwargs):
        self.pointer.ungrab(Gdk.CURRENT_TIME)
        if self.keyboard:
            self.keyboard.ungrab(Gdk.CURRENT_TIME)
        self.grabbed = False
        self.w.set_opacity(1.0)
        self.w.present()

    def get_cache_file(self):
        return os.path.join(GLib.get_user_cache_dir(), "colour-picker.json")

    def serialise(self, *args, **kwargs):
        # yeah, yeah, supposed to use Gio's async file stuff here. But it
        # was writing corrupted files, and I have no idea why; probably the
        # Python var containing the data was going out of scope or something.
        # Anyway, we're only storing five small images, so life's too short
        # to hammer on this; we'll write with Python and take the hit.
        fp = codecs.open(self.get_cache_file(), encoding="utf8", mode="w")
        data = {"colours": self.history, "formatter": self.active_formatter}
        if self.window_metrics:
            data["metrics"] = self.window_metrics
        json.dump(data, fp, indent=2)
        fp.close()

    def rounded_path(self, surface, w, h):
        radius = w / 10
        # https://www.cairographics.org/samples/rounded_rectangle/
        surface.arc(w - radius, radius, radius, -90 * math.pi / 180, 0)
        surface.arc(w - radius, h - radius, radius, 0, 90 * math.pi / 180)
        surface.arc(radius, h - radius, radius, 90 * math.pi / 180,
                    180 * math.pi / 180)
        surface.arc(radius, radius, radius, 180 * math.pi / 180,
                    270 * math.pi / 180)
        surface.close_path()

    def rectangle_draw(self, da, surface, r, g, b):
        w, h = da.get_size_request()
        self.rounded_path(surface, w, h)
        surface.set_source_rgb(r/255.0, g/255.0, b/255.0)
        surface.clip_preserve()
        surface.fill_preserve()
        surface.set_line_width(2)
        surface.set_source_rgba(0, 0, 0, 0.1)
        surface.stroke()

    def image_draw(self, da, surface, pixbuf):
        w, h = da.get_size_request()
        self.rounded_path(surface, w, h)
        Gdk.cairo_set_source_pixbuf(surface, pixbuf, 0, 0)
        surface.clip_preserve()
        surface.paint()
        surface.set_line_width(2)
        surface.set_source_rgba(0, 0, 0, 0.1)
        surface.stroke()

    def add_history_item(self, r, g, b, base64_imgdata=None, pixbuf=None):
        def show_copy(eb, ev, img): img.set_opacity(1)

        def hide_copy(eb, ev, img): img.set_opacity(0)

        def clipboard(button, r, g, b, label):
            def unfade(label):
                label.get_style_context().remove_class("highlighted")
            colour = self.formatters[self.active_formatter](r, g, b)
            Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD).set_text(
                colour, len(colour))
            label.get_style_context().add_class("highlighted")
            GLib.timeout_add(300, unfade, label)
            self.play_sound("dialog-information")

        eb = Gtk.EventBox()
        hb = Gtk.HBox()
        f = Gtk.Frame()
        eb.add(f)
        f.add(hb)

        if base64_imgdata:
            loader = GdkPixbuf.PixbufLoader.new_with_type("png")
            loader.write(base64.b64decode(base64_imgdata.encode("utf-8")))
            pixbuf = loader.get_pixbuf()
            loader.close()
        elif pixbuf:
            success, data = pixbuf.save_to_bufferv("png", [], [])
            base64_imgdata = base64.b64encode(data).decode("utf-8")
        else:
            raise Exception(
                "A history item must have either imgdata or a pixbuf")

        i = Gtk.DrawingArea()
        i.set_size_request(self.snapsize[0]/2, self.snapsize[1]/2)
        i.connect("draw", self.image_draw, pixbuf)
        hb.pack_start(i, False, False, 6)

        area = Gtk.DrawingArea()
        area.set_size_request(self.snapsize[0]/2, self.snapsize[1]/2)
        area.connect("draw", self.rectangle_draw, r, g, b)
        hb.pack_start(area, False, False, 6)

        lbl = Gtk.Label()
        self.colour_text_labels.append(lbl)
        self.set_colour_label_text(lbl, r, g, b)
        lbl.set_halign(Gtk.Align.START)
        hb.pack_start(lbl, True, True, 6)

        copy = Gtk.Button.new_from_icon_name("edit-copy-symbolic", 0)
        copy.set_label("Copy")
        copy.set_opacity(0)
        copy.connect("clicked", clipboard, r, g, b, lbl)
        copy.connect("enter-notify-event", show_copy, copy)
        copy.connect("leave-notify-event", hide_copy, copy)
        hb.pack_start(copy, False, False, 6)

        eb.connect("enter-notify-event", show_copy, copy)
        eb.connect("leave-notify-event", hide_copy, copy)
        eb.set_tooltip_text("Copy to clipboard")

        eb.set_property("can_focus", True)
        eb.connect("focus-in-event", show_copy, copy)
        eb.connect("focus-out-event", hide_copy, copy)

        revealer = Gtk.Revealer()
        revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_DOWN)
        revealer.add(eb)

        self.container_vb.pack_start(revealer, False, False, 0)
        self.container_vb.reorder_child(revealer, 0)
        self.vb.show_all()
        eb.show_all()
        revealer.set_reveal_child(True)

        self.history.append({
            "imgdata": base64_imgdata,
            "colour": [r, g, b]
        })

        while len(self.history) > 5:
            del self.history[0]
            del self.colour_text_labels[0]
            self.container_vb.get_children()[5].destroy()

        if self.empty.get_parent():
            self.empty.get_parent().remove(self.empty)
        if not self.vb.get_parent():
            self.w.add(self.vb)
            self.vb.show_all()
        self.btnclear.set_sensitive(True)

    def set_colour_label_text(self, lbl, r, g, b):
        mk = '<span color="%s">%s</span>\n<span color="%s">%s</span>'
        lbl.set_markup(mk % (
            self.formatters["CSS hex"](
                255 * self.highlight_rgba.red,
                255 * self.highlight_rgba.green,
                255 * self.highlight_rgba.blue),
            self.closest_name(r, g, b),
            self.formatters["CSS hex"](
                255 * self.lowlight_rgba.red,
                255 * self.lowlight_rgba.green,
                255 * self.lowlight_rgba.blue),
            self.formatters[self.active_formatter](r, g, b).replace(
                "<", "&lt;")
        ))

    def finish_loading_history(self, f, res):
        try:
            try:
                success, contents, _ = f.load_contents_finish(res)
            except GLib.Error as e:
                print(("couldn't restore settings (error: %s),"
                       " so assuming they're blank") % (e,))
                contents = "{}"  # fake contents

            try:
                data = json.loads(contents)
            except:
                print("Failed to restore data")
                data = {}
            colours = data.get("colours")
            if colours:
                for item in colours:
                    self.add_history_item(
                        item["colour"][0],
                        item["colour"][1],
                        item["colour"][2],
                        base64_imgdata=item["imgdata"]
                    )
            f = data.get("formatter")
            if f and f in self.formatters.keys():
                self.active_formatter = f
                self.fcom.set_active(list(self.formatters.keys()).index(f))
            metrics = data.get("metrics")
            if metrics:
                self.restore_window_metrics(metrics)
            self.window_metrics_restored = True

        except:
            # print "Failed to restore data"
            raise

    def load_history(self):
        f = Gio.File.new_for_path(self.get_cache_file())
        f.load_contents_async(None, self.finish_loading_history)

    def magnifier_scrollwheel(self, window, ev):
        if self.grabbed:
            if ev.direction == Gdk.ScrollDirection.SMOOTH:
                return
            if ev.direction == Gdk.ScrollDirection.UP:
                self.zoomlevel += 1
                if self.zoomlevel > 7:
                    self.zoomlevel = 7
            elif ev.direction == Gdk.ScrollDirection.DOWN:
                self.zoomlevel -= 1
                if self.zoomlevel < 2:
                    self.zoomlevel = 2
            else:
                return
            self.set_magnifier_cursor()

    def magnifier_keypress(self, window, ev):
        if self.grabbed:
            if ev.keyval == Gdk.KEY_Escape:
                self.ungrab()

    def magnifier_clicked(self, window, ev):
        if self.grabbed:
            self.ungrab()
            if ev.button != 1:
                return  # if this is not the primary button, bail
            colour = self.get_colour_from_pb(self.latest_pb)
            pbcopy = self.latest_pb.scale_simple(
                self.snapsize[0] / 2,
                self.snapsize[1] / 2,
                GdkPixbuf.InterpType.TILES)
            self.add_history_item(colour[0], colour[1], colour[2],
                                  pixbuf=pbcopy)
            GLib.idle_add(self.serialise)
            self.play_sound("camera-shutter")

    def get_colour_from_pb(self, pb):
        pixel_data = pb.get_pixels()
        offset = (
            (pb.get_rowstride() * (self.snapsize[1] / 2)) +
            ((self.latest_pb.get_rowstride() / self.snapsize[0]) *
                (self.snapsize[0] / 2)))
        offset = int(offset)
        rgb_vals = []
        # pixel data gets returned as bytes or int depending
        # on which Python version we're in
        for x in pixel_data[offset:offset+3]:
            if type(x) == int:
                rgb_vals.append(x)
            else:
                rgb_vals.append(ord(x))
        rgb_vals = tuple(rgb_vals)
        return rgb_vals

    def magnifier_move(self, *args, **kwargs):
        if not self.grabbed:
            return
        self.set_magnifier_cursor()

    def change_format(self, cb):
        self.active_formatter = cb.get_model().get_value(
            cb.get_active_iter(), 0)
        for lbl, hist in zip(self.colour_text_labels, self.history):
            self.set_colour_label_text(lbl, hist["colour"][0],
                                       hist["colour"][1], hist["colour"][2])
        GLib.idle_add(self.serialise)

    def closest_name(self, r, g, b):
        max_deltaE_found = 999999999
        col = self.closest_name_cache.get((r, g, b))
        if col is not None:
            return col
        labcol = rgb_to_lab(r, g, b)
        for reflabcol, name in LAB_COLOUR_NAMES:
            dE = deltaE(labcol, reflabcol)
            if dE < max_deltaE_found:
                col = name
                max_deltaE_found = dE
        self.closest_name_cache[(r, g, b)] = col
        return col

    def formatRGB(self, column, cell_renderer, model, iter):
        formatter = self.formatters.get(model.get_value(iter, 0))
        text = "?"
        if formatter:
            text = formatter(255, 255, 255)
        cell_renderer.set_property("text", text)

    def snap(self, x, y, w, h):
        display = Gdk.Display.get_default()
        (screen, self.x, self.y, modifier) = display.get_pointer()
        root = Gdk.get_default_root_window()
        screenshot = Gdk.pixbuf_get_from_window(root, x, y, w, h)
        return screenshot


def main():
    m = Main()
    m.app.run(sys.argv)


if __name__ == "__main__": main()
