from flask import Flask, jsonify, abort, request, make_response, Response, g
import hombit
import os
import sys
import threading

API_VERSION = 1

pidfile = None
stopFlag = threading.Event()

class BlinkThread(threading.Thread):
    def __init__(self, device, event):
        threading.Thread.__init__(self)
        self.device = device
        self.stopped = event

    def run(self):
        while not self.stopped.wait(self.device.min_command_interval):
            self.device.process_commands()

def serve(device, daemon=False):
    app = Flask(__name__)
    if not daemon:
        app.debug = True

    # GET index - web app root
    @app.route("/", methods=["GET"])
    def index():
        root = request.args.get("root", "http://" + request.host.replace(":5000", ":8000"))
        return "<html><body>\
        <script src='" + root + "/js/lib/jquery.js'></script>\
        <script>hombit_root='" + root + "'; $.get(hombit_root+'/app.html', function(a){$('body').html(a)});</script>\
        </body></html>"

    # GET device and version info
    @app.route("/info")
    def info():
        return jsonify({
            "type": device.get_device_type(),
            "id": device.get_device_id(),
            "ver": {
                "api": API_VERSION,
                "fw": hombit.FIRMWARE_VERSION
            }
        })

    # GET configuration of IO pins
    @app.route("/conf/io", methods=["GET"])
    def get_io_pins_config():
        return jsonify(device.get_io_pins_config())

    # PUT configuration of IO pins
    @app.route("/conf/io", methods=["PUT", "POST"])
    def set_io_pins_config():
        return jsonify(device.set_io_pins_config(request.json))

    # GET configuration of named IO pins
    @app.route("/conf/name", methods=["GET"])
    def get_named_io_pins_config():
        return jsonify(device.get_named_io_pins_config())

    # PUT configuration of named IO pins
    @app.route("/conf/name", methods=["PUT", "POST"])
    def set_named_io_pins_config():
        return jsonify(device.set_named_io_pins_config(request.json))

    # GET configuration of single IO pin
    @app.route("/conf/io/<pin>", methods=["GET"])
    def get_io_pin_config(pin):
        return jsonify(device.get_io_pin_config(pin))

    # PUT configuration of single IO pin
    @app.route("/conf/io/<pin>", methods=["PUT", "POST"])
    def set_io_pin_config(pin):
        return jsonify(device.set_io_pin_config(pin, request.json))

    # GET configuration of single IO pin
    @app.route("/conf/name/<name>", methods=["GET"])
    def get_named_pin_config(name):
        return jsonify(device.get_named_io_pin_config(name))

    # PUT configuration of single IO pin
    @app.route("/conf/name/<name>", methods=["PUT", "POST"])
    def set_named_pin_config(name):
        return jsonify(device.set_named_io_pin_config(name, request.json))

    # GET all IO pin values
    @app.route("/io/pin", methods=["GET"])
    def get_io_pins():
        return jsonify(device.get_io_pins())

    # PUT all IO pin values
    @app.route("/io/pin", methods=["PUT", "POST"])
    def set_io_pins():
        device.set_io_pins(request.json)
        return Response()

    # GET single IO pin value
    @app.route("/io/pin/<pin>", methods=["GET"])
    def get_io_pin(pin):
        try:
            if (device.get_io_pin(pin)):
                return Response()
            else:
                return Response(status=204)
        except KeyError:
            abort(404)

    # PUT set single IO pin value
    @app.route("/io/pin/<pin>", methods=["PUT", "POST"])
    def set_io_pin(pin):
        try:
            device.set_io_pin(pin, True);
            return Response()
        except KeyError:
            abort(404)

    # DELETE clear single IO pin value
    @app.route("/io/pin/<pin>", methods=["DELETE"])
    def clear_io_pin(pin):
        try:
            device.set_io_pin(pin, False);
            return Response()
        except KeyError:
            abort(404)

    # GET all named pin values
    @app.route("/io/name", methods=["GET"])
    def get_named_io_pins():
        return jsonify(device.get_named_io_pins())

    @app.route("/io/name", methods=["PUT", "POST"])
    def set_named_io_pins():
        device.set_named_io_pins(request.json)
        return Response()

    # GET single named pin value
    @app.route("/io/name/<name>", methods=["GET"])
    def get_named_io_pin(name):
        try:
            if (device.get_named_io_pin(name)):
                return Response()
            else:
                return Response(status=204)
        except KeyError:
            abort(404, e)

    # PUT set single named pin value
    @app.route("/io/name/<name>", methods=["PUT", "POST"])
    def set_named_io_pin(name):
        print "foo wtf " + name
        try:
            device.set_named_io_pin(name, True);
            return Response()
        except KeyError as e:
            print e
            abort(404)

    # DELETE clear single IO pin value
    @app.route("/io/name/<name>", methods=["DELETE"])
    def clear_named_io_pin(name):
        try:
            device.set_named_io_pin(name, False);
            return Response()
        except KeyError:
            abort(404)

    @app.errorhandler(404)
    def not_found(error):
        return error.description, 404

    @app.before_first_request
    def initialize():
        print "Called only once, when the first request comes in"
        thread = BlinkThread(device, stopFlag)
        thread.start()

    if pidfile:
        pidf = open(pidfile, "w")
        pidf.write(str(os.getpid()) + "\n")
        pidf.close()


    app.run(host="0.0.0.0" )
    stopFlag.set()


def terminate(foo, bar):
    if pidfile:
        os.remove(pidfile)
    # this will stop the timer
    stopFlag.set()
    print "Clean terminate"
    sys.exit(0)
