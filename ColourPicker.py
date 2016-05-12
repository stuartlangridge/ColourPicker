from gi.repository import Gtk, Gdk, Keybinder, GLib, GdkPixbuf, Gio
import cairo, math, json, os, codecs, StringIO


class Main(object):
    def __init__(self):
        # Create window and widgets
        self.w = Gtk.Window()
        self.w.set_title("Colour Picker")
        self.w.set_size_request(460, 500)

        hb = Gtk.HBox()
        vbl = Gtk.VBox()
        vbr = Gtk.VBox()

        Keybinder.init()
        Keybinder.bind("<Ctrl><Alt>M", self.keypress)

        self.image = Gtk.Image()
        self.colour = Gtk.Label()

        vbl.add(self.image)
        vbl.add(self.colour)
        hb.add(vbl)

        self.remembered = Gtk.ListStore(GdkPixbuf.Pixbuf, str)
        lv = Gtk.TreeView(model=self.remembered)
        celli = Gtk.CellRendererPixbuf()
        coli = Gtk.TreeViewColumn(0, celli, pixbuf=0)
        cellc = Gtk.CellRendererText()
        colc = Gtk.TreeViewColumn(1, cellc, text=1)
        lv.append_column(coli)
        lv.append_column(colc)
        lv.set_headers_visible(False)
        lv.get_selection().set_select_function(self.row_clicked, None)
        vbr.add(Gtk.Label("Ctrl-Alt-M to save a colour"))
        vbr.add(lv)

        hb.add(vbr)

        self.w.add(hb)
        self.w.connect("destroy", Gtk.main_quit)
        self.w.show_all()

        self.pointer = self.w.get_screen().get_display().get_device_manager().get_client_pointer()
        self.snapsize = (80, 80)

        GLib.timeout_add(150, self.poll)
        GLib.idle_add(self.restore_colours)

    def row_clicked(self, sel, store, path, selected, data):
        colour = store.get_value(store.get_iter(path), 1)
        Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD).set_text(colour, len(colour))
        return False # don't actually select a row

    def finish_restoring(self, f, res):
        try:
            success, contents, _ = f.load_contents_finish(res)
            data = json.loads(contents)
            colours = data["colours"]
            for item in colours:
                loader = GdkPixbuf.PixbufLoader.new_with_type("png")
                loader.write(item["imgdata"].decode("base64"))
                pb = loader.get_pixbuf()
                loader.close()
                self.remembered.append((pb, item["colour"]))
        except:
            print "Failed to restore data"
            raise

    def restore_colours(self):
        f = Gio.File.new_for_path(self.get_cache_file())
        f.load_contents_async(None, self.finish_restoring)

    def snap(self, x, y, w, h):
        display=Gdk.Display.get_default()
        (screen,self.x,self.y,modifier) = display.get_pointer()
        root = Gdk.get_default_root_window()
        screenshot = Gdk.pixbuf_get_from_window(root, x, y, w, h)
        return screenshot

    def poll(self, *args, **kwargs):
        root = Gdk.get_default_root_window()
        pointer, px, py = self.pointer.get_position()
        self.latest_pb = self.snap(px-(self.snapsize[0]/2), py-(self.snapsize[1]/2), self.snapsize[0], self.snapsize[1])
        pbd = self.latest_pb.scale_simple(self.snapsize[0] * 2, self.snapsize[1] * 2, GdkPixbuf.InterpType.TILES)
        surface = Gdk.cairo_surface_create_from_pixbuf(pbd, 0, None)
        context = cairo.Context(surface)
        context.set_source_rgba(1, 0.5, 0.5, 1)
        context.set_line_width(4)
        context.arc(self.snapsize[0], self.snapsize[1], 8, 0, 2*math.pi)
        context.stroke()
        pbdc = Gdk.pixbuf_get_from_surface(surface, 0, 0, surface.get_width(), surface.get_height())
        self.image.set_from_pixbuf(pbdc)

        pixel_data = self.latest_pb.get_pixels()
        offset = (self.latest_pb.get_rowstride() * (self.snapsize[1] / 2)) + ((self.latest_pb.get_rowstride() / self.snapsize[0]) * (self.snapsize[0] / 2))
        rgb_vals = tuple([ord(x) for x in pixel_data[offset:offset+3]])
        hex_colour = '#%02x%02x%02x' % rgb_vals
        self.colour.set_text(hex_colour)

        return True

    def keypress(self, *args, **kwargs):
        pbcopy = self.latest_pb.scale_simple(self.snapsize[0], self.snapsize[1], GdkPixbuf.InterpType.TILES)
        self.remembered.prepend((pbcopy, self.colour.get_text()))
        itr = self.remembered.iter_nth_child(None, 5)
        while itr:
            self.remembered.remove(itr)
            itr = self.remembered.iter_nth_child(None, 5)

        GLib.idle_add(self.serialise)

    def get_cache_file(self):
        return os.path.join(GLib.get_user_cache_dir(), "colour-picker.json")

    def serialise(self, *args, **kwargs):
        #print "serialise", self.remembered
        lst = []
        for pb, col in self.remembered:
            success, data = pb.save_to_bufferv("png", [], [])
            lst.append({
                "imgdata": data.encode("base64"),
                "colour": col
            })
        # yeah, yeah, supposed to use Gio's async file stuff here. But it was writing
        # corrupted files, and I have no idea why; probably the Python var containing
        # the data was going out of scope or something. Anyway, we're only storing
        # five small images, so life's too short to hammer on this; we'll write with
        # Python and take the hit.
        fp = codecs.open(self.get_cache_file(), encoding="utf8", mode="w")
        json.dump({"colours": lst}, fp, indent=2)
        fp.close()

if __name__ == "__main__":
    Main()
    Gtk.main()

