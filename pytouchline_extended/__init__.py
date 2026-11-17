import asyncio
import logging
import xml.etree.ElementTree as ET
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import cchardet as chardet  # type: ignore[import-untyped]
import httpx

__author__ = 'brondum'

from httpx import AsyncClient

__all__ = [
	"Parameter",
	"PyTouchline",
	"TouchlineConnectionError",
	"TouchlineError",
	"TouchlineHTTPError",
	"TouchlineResponseError",
	"TouchlineTimeoutError",
]

logger = logging.getLogger(__name__)

_PARSE_ERRORS = (AttributeError, IndexError, TypeError, ValueError)


class TouchlineError(Exception):
	"""Base exception for all pytouchline errors."""


class TouchlineConnectionError(TouchlineError):
	"""The Touchline controller could not be reached."""


class TouchlineTimeoutError(TouchlineConnectionError):
	"""The request to the Touchline controller timed out."""


class TouchlineHTTPError(TouchlineError):
	"""The Touchline controller responded with a non-success HTTP status."""

	def __init__(self, message: str, status_code: int) -> None:
		super().__init__(f"{message} (HTTP {status_code})")
		self.status_code = status_code


class TouchlineResponseError(TouchlineError):
	"""The Touchline controller returned an empty or unparseable response."""


class PyTouchline(object):
	"""
	A Python interface for controlling a Roth Touchline heat pump controller.

	Attributes:
			id (int): The ID of the sensor.
			url (str): The URL of the heat pump controller.
			timeout (float): HTTP request timeout in seconds (default: 10.0).
			client (httpx.AsyncClient | None): Optional shared client. It is not
				closed by this class. When omitted, a new client is created per request.
	"""

	def __init__(
		self,
		id: int = 0,
		url: str = "",
		timeout: float = 10.0,
		client: AsyncClient | None = None,
	) -> None:
		self._id = id
		self._url = url
		self._timeout = timeout
		self._client = client
		self._temp_scale = 100
		self._header = {"Content-Type": "text/xml"}
		self._read_path = "/cgi-bin/ILRReadValues.cgi"
		self._write_path = "/cgi-bin/writeVal.cgi"
		self._parameter: dict[str, str] = {}
		self.devices: list[Any] = []
		self._xml_element_list: list[Parameter] = []
		self._xml_element_list.append(
			Parameter(name="name", desc="Name", type=Parameter.G))
		self._xml_element_list.append(
			Parameter(name="upass", desc="Password", type=Parameter.CD))
		self._xml_element_list.append(
			Parameter(name="SollTempMaxVal", desc="Setpoint max",
					  type=Parameter.G))
		self._xml_element_list.append(
			Parameter(name="SollTempMinVal", desc="Setpoint min",
					  type=Parameter.G))
		self._xml_element_list.append(
			Parameter(name="WeekProg", desc="Week program", type=Parameter.G))
		self._xml_element_list.append(
			Parameter(name="OPMode", desc="Operation mode", type=Parameter.G))
		self._xml_element_list.append(
			Parameter(name="SollTemp", desc="Setpoint", type=Parameter.G))
		self._xml_element_list.append(
			Parameter(name="RaumTemp", desc="Temperature", type=Parameter.G))
		self._xml_element_list.append(
			Parameter(name="kurzID", desc="Device ID", type=Parameter.G))
		self._xml_element_list.append(
			Parameter(name="ownerKurzID", desc="Controller ID",
					  type=Parameter.G))

	def get_async_client(self) -> AsyncClient:
		return httpx.AsyncClient(verify=False, timeout=self._timeout)

	@asynccontextmanager
	async def _async_client(self) -> AsyncIterator[AsyncClient]:
		if self._client is not None:
			yield self._client
			return
		async with self.get_async_client() as client:
			yield client

	async def _request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
		try:
			async with self._async_client() as client:
				return await client.request(
					method=method, url=url, timeout=self._timeout, **kwargs
				)
		except httpx.TimeoutException as e:
			raise TouchlineTimeoutError(
				f"Touchline controller timeout after {self._timeout} seconds at {self._url}: {e}") from e
		except httpx.RequestError as e:
			raise TouchlineConnectionError(f"Network error connecting to Touchline controller at {self._url}: {e}") from e

	async def get_number_of_devices_async(self) -> int:
		number_of_devices_items = []
		number_of_devices_items.append("<i><n>totalNumberOfDevices</n></i>")
		request = self._get_touchline_request(number_of_devices_items)
		response = await self._request_and_receive_xml(request)
		try:
			raw_count = self._parse_number_of_devices(response)
			if raw_count is None:
				raise ValueError("Missing number of devices")
			return int(raw_count)
		except _PARSE_ERRORS as e:
			raise TouchlineResponseError("Could not fetch the number of devices") from e

	def get_number_of_devices(self) -> int:
		return asyncio.run(self.get_number_of_devices_async())

	async def get_hostname_async(self) -> str | None:
		hostname_items = []
		hostname_items.append("<i><n>hw.HostName</n></i>")
		request = self._get_touchline_request(hostname_items)
		response = await self._request_and_receive_xml(request)
		try:
			return self._parse_number_of_devices(response)
		except _PARSE_ERRORS as e:
			raise TouchlineResponseError("Could not fetch the hostname") from e

	def get_hostname(self) -> str | None:
		return asyncio.run(self.get_hostname_async())

	async def get_status_async(self) -> str | None:
		status_items = []
		status_items.append("<i><n>R0.SystemStatus</n></i>")
		request = self._get_touchline_request(status_items)
		response = await self._request_and_receive_xml(request)
		try:
			return self._parse_number_of_devices(response)
		except _PARSE_ERRORS as e:
			raise TouchlineResponseError("Could not fetch the system status") from e

	def get_status(self) -> str | None:
		return asyncio.run(self.get_status_async())

	# update the roth touchline device, and parse desc, id etc.
	async def update_async(self) -> None:
		device_items = self._get_touchline_device_item(self._id)
		request = self._get_touchline_request(device_items)
		response = await self._request_and_receive_xml(request)
		try:
			return self._parse_device(response)
		except _PARSE_ERRORS as e:
			raise TouchlineResponseError(f"Could not parse device {self._id}") from e

	# update the roth touchline device, and parse desc, id etc.
	def update(self) -> None:
		return asyncio.run(self.update_async())

	def _parse_device(self, response: ET.Element) -> None:
		self.devices = []
		item_list = response.find('item_list')
		if item_list is None:
			raise ValueError("Missing item_list")
		for item in item_list.iterfind("i"):
			list_iterator = 0
			device_list = list(item)
			for parameter in self._xml_element_list:
				if device_list[list_iterator].tag != "n":
					list_iterator -= 1
					self._parameter[parameter.get_desc()] = "NA"
				else:
					self._parameter[parameter.get_desc()] = str(
						device_list[list_iterator + 1].text)
					if list_iterator == 0:
						tag_text = device_list[list_iterator].text
						if tag_text is None:
							raise ValueError("Missing device tag text")
						unique_id = tag_text.split(".")[0].split("G")[1]
						self._parameter["Unique ID"] = unique_id
				list_iterator += 2

	def _get_touchline_request(self, items: list[str]) -> str:
		request = "<body>"
		request += "<version>1.0</version>"
		request += "<client>IMaster6_02_00</client>"
		request += "<client_ver>6.02.0006</client_ver>"
		request += "<file_name>room</file_name>"
		request += "<item_list_size>0</item_list_size>"
		request += "<item_list>"
		for item in items:
			request += item
		request += "</item_list>"
		request += "</body>"
		return request

	async def write_parameter_async(self, parameter: str, value: str | int | float) -> bytes:
		response = await self._request(
			method="GET",
			url=self._url +
				self._write_path + "?" +
				"G" + str(self._parameter["Unique ID"]) +
				"." + str(parameter) + "=" + str(value),
		)

		if not response.is_success:
			raise TouchlineHTTPError(
				f"Failed to write parameter {parameter}: Roth Touchline did not respond successfully",
				response.status_code)

		return response.content

	def write_parameter(self, parameter: str, value: str | int | float) -> bytes:
		return asyncio.run(self.write_parameter_async(parameter, value))

	async def _request_and_receive_xml(self, req_key: str) -> ET.Element:
		logger.debug("Requesting URL: %s%s (timeout: %.1fs)", self._url, self._read_path, self._timeout)

		response = await self._request(
			method="POST",
			url=self._url + self._read_path,
			content=req_key,
			headers=self._header,
		)

		logger.debug("Response status: %s, content length: %d bytes",
					 response.status_code, len(response.content) if response.content else 0)

		if not response.is_success:
			raise TouchlineHTTPError("Roth Touchline did not respond successfully", response.status_code)

		content = response.content
		if not content or len(content) == 0:
			raise TouchlineResponseError("Touchline controller returned empty response")

		try:
			enc: str | None = chardet.detect(content)['encoding']
			return ET.XML(content, parser=ET.XMLParser(encoding=enc))
		except ET.ParseError as e:
			# The response is not included as it can contain the controller password
			raise TouchlineResponseError(f"Invalid XML response from Touchline controller: {e}") from e

	def _parse_number_of_devices(self, response: ET.Element) -> str | None:
		item_list = response.find('item_list')
		if item_list is None:
			raise ValueError("Missing item_list")
		item = item_list.find('i')
		if item is None:
			raise ValueError("Missing item")
		value = item.find('v')
		if value is None:
			raise ValueError("Missing value")
		return value.text

	def _get_touchline_device_item(self, id: int) -> list[str]:
		items = []
		parameters = ""
		for parameter in self._xml_element_list:
			if parameter.get_type() == Parameter.G:
				parameters += "<n>G%d.%s</n>" % (id, parameter.get_name())
			else:
				parameters += "<n>CD.%s</n>" % (parameter.get_name())
		items.append("<i>" + parameters + "</i>")
		return items

	def get_name(self) -> str | None:
		if "Name" in self._parameter:
			return self._parameter["Name"]
		else:
			return None

	async def set_name_async(self, value: str) -> bool:
		return (await self.write_parameter_async("name",
									value)).decode("utf-8") == str(value)

	def set_name(self, value: str) -> bool:
		return asyncio.run(self.set_name_async(value))

	def get_current_temperature(self) -> float | None:
		if "Temperature" in self._parameter:
			return int(self._parameter["Temperature"]) / self._temp_scale
		else:
			return None

	def get_target_temperature(self) -> float | None:
		if "Setpoint" in self._parameter:
			return int(self._parameter["Setpoint"]) / self._temp_scale
		else:
			return None

	async def set_target_temperature_async(self, value: float) -> bool:
		return (await self.write_parameter_async("SollTemp",
									float(value) *
									self._temp_scale)).decode("utf-8") == \
			   str(float(value) * self._temp_scale)

	def set_target_temperature(self, value: float) -> bool:
		return asyncio.run(self.set_target_temperature_async(value))

	def get_target_temperature_high(self) -> float | None:
		if "Setpoint max" in self._parameter:
			return int(self._parameter["Setpoint max"]) / self._temp_scale
		else:
			return None

	async def set_target_temperature_high_async(self, value: float) -> bool:
		return (await self.write_parameter_async("SollTempMaxVal",
									float(value) *
									self._temp_scale)).decode("utf-8") == \
			   str(float(value) * self._temp_scale)

	def set_target_temperature_high(self, value: float) -> bool:
		return asyncio.run(self.set_target_temperature_high_async(value))

	def get_target_temperature_low(self) -> float | None:
		if "Setpoint min" in self._parameter:
			return int(self._parameter["Setpoint min"]) / self._temp_scale
		else:
			return None

	async def set_target_temperature_low_async(self, value: float) -> bool:
		return (await self.write_parameter_async("SollTempMinVal",
									float(value) *
									self._temp_scale)).decode("utf-8") == \
			   str(float(value) * self._temp_scale)

	def set_target_temperature_low(self, value: float) -> bool:
		return asyncio.run(self.set_target_temperature_low_async(value))

	def get_week_program(self) -> int | None:
		if "Week program" in self._parameter:
			return int(self._parameter["Week program"])
		else:
			return None

	async def set_week_program_async(self, value: int) -> bool:
		return (await self.write_parameter_async("WeekProg",
									value)).decode("utf-8") == str(value)

	def set_week_program(self, value: int) -> bool:
		return asyncio.run(self.set_week_program_async(value))

	def get_operation_mode(self) -> int | None:
		if "Operation mode" in self._parameter:
			return int(self._parameter["Operation mode"])
		else:
			return None

	async def set_operation_mode_async(self, value: int) -> bool:
		return (await self.write_parameter_async("OPMode",
									value)).decode("utf-8") == str(value)

	def set_operation_mode(self, value: int) -> bool:
		return asyncio.run(self.set_operation_mode_async(value))

	def get_device_id(self) -> int | None:
		if "Device ID" in self._parameter:
			return int(self._parameter["Device ID"])
		else:
			return None

	def get_controller_id(self) -> int | None:
		if "Controller ID" in self._parameter:
			return int(self._parameter["Controller ID"])
		else:
			return None

class Parameter(object):
	CD = 0
	G = 1
	R = 2

	def __init__(self, name: str, desc: str, type: int) -> None:
		self._name = name
		self._desc = desc
		self._type = type

	def get_name(self) -> str:
		return self._name

	def get_desc(self) -> str:
		return self._desc

	def get_type(self) -> int:
		return self._type
