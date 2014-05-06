import unittest
import requests
import json
import time

baseurl = "http://localhost:5000/"
test_in_pin = "24"
test_out_pin = "25"
json_headers = {
	"Content-type": "application/json",
	"Accept": "application/json"
}
blinktime = 0.1

class RequestsTest(unittest.TestCase):
	
	def test_index_returns_html(self):
		response = requests.request("GET", baseurl)
		self.assertTrue(response.headers["Content-Type"].startswith("text/html"));

	def test_device_info(self):
		info = requests.request("GET", baseurl + "info").json()
		self.assertIsNotNone(info["type"])
		self.assertIsNotNone(info["id"])
		self.assertIsNotNone(info["ver"]["api"])
		self.assertIsNotNone(info["ver"]["fw"])

	def test_set_and_get_io_pinmodes(self):
		config = requests.post(baseurl + "conf/io", headers=json_headers, data=json.dumps({ 
					test_in_pin: {"mode": "in"}, 
					test_out_pin: {"mode": "out"} 
					})).json()
		self.assertEquals("in", config[test_in_pin]["mode"])
		self.assertEquals("out", config[test_out_pin]["mode"])

		config = requests.get(baseurl + "conf/io").json()
		self.assertEquals("in", config[test_in_pin]["mode"])
		self.assertEquals("out", config[test_out_pin]["mode"])

	def test_get_io_pins(self):
		requests.request("GET", baseurl + "io/pin").json()

	def test_get_io_pin(self):
		requests.request("GET", baseurl + "io/pin/" + test_in_pin)

	def test_set_and_clear_io_pins(self):
		response = requests.request("PUT", baseurl + "io/pin", headers=json_headers, data=json.dumps({
				test_out_pin: True
			}))
		self.assertEquals(200, response.status_code)
		time.sleep(blinktime)
		response = requests.request("PUT", baseurl + "io/pin", headers=json_headers, data=json.dumps({
				test_out_pin: False
			}))
		self.assertEquals(200, response.status_code)
		time.sleep(blinktime)

	def test_set_and_clear_io_pin(self):
		response = requests.put(baseurl + "io/pin/" + test_out_pin)
		self.assertEquals(200, response.status_code)
		time.sleep(blinktime)
		response = requests.delete(baseurl + "io/pin/" + test_out_pin)
		self.assertEquals(200, response.status_code)
		time.sleep(blinktime)
		requests.put(baseurl + "io/pin/" + test_out_pin)
		time.sleep(blinktime)
		requests.delete(baseurl + "io/pin/" + test_out_pin)

	def test_invalid_pin__get_io_pin__returns_404(self):
		response = requests.request("GET", baseurl + "io/pin/foo")
		self.assertEquals(404, response.status_code)

	def test_invalid_pin__set_io_pin__returns_404(self):
		response = requests.request("PUT", baseurl + "io/pin/foo")
		self.assertEquals(404, response.status_code)

if __name__ == "__main__":
    unittest.main()
