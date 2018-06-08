from django.test import TestCase

from push_notifications.api.rest_framework import (
	APNSDeviceSerializer, GCMDeviceSerializer, ValidationError
)


class APNSDeviceSerializerTestCase(TestCase):
	def test_validation(self):
		# valid data - 32 bytes upper case
		serializer = APNSDeviceSerializer(data={
			"registration_id": "AEAEAEAEAEAEAEAEAEAEAEAEAEAEAEAEAEAEAEAEAEAEAEAEAEAEAEAEAEAEAEAE",
			"name": "Apple iPhone 6+",
			"device_id": "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF",
			"application_id": "XXXXXXXXXXXXXXXXXXXX",
		})
		self.assertTrue(serializer.is_valid())

		# valid data - 32 bytes lower case
		serializer = APNSDeviceSerializer(data={
			"registration_id": "aeaeaeaeaeaeaeaeaeaeaeaeaeaeaeaeaeaeaeaeaeaeaeaeaeaeaeaeaeaeaeae",
			"name": "Apple iPhone 6+",
			"device_id": "ffffffffffffffffffffffffffffffff",
			"application_id": "XXXXXXXXXXXXXXXXXXXX",
		})
		self.assertTrue(serializer.is_valid())

		# valid data - 100 bytes upper case
		serializer = APNSDeviceSerializer(data={
			"registration_id": "AE" * 100,
			"name": "Apple iPhone 6+",
			"device_id": "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF",
		})
		self.assertTrue(serializer.is_valid())

		# valid data - 100 bytes lower case
		serializer = APNSDeviceSerializer(data={
			"registration_id": "ae" * 100,
			"name": "Apple iPhone 6+",
			"device_id": "ffffffffffffffffffffffffffffffff",
		})
		self.assertTrue(serializer.is_valid())

		# invalid data - device_id, registration_id
		serializer = APNSDeviceSerializer(data={
			"registration_id": "invalid device token contains no hex",
			"name": "Apple iPhone 6+",
			"device_id": "ffffffffffffffffffffffffffffake",
			"application_id": "XXXXXXXXXXXXXXXXXXXX",
		})
		self.assertFalse(serializer.is_valid())


class GCMDeviceSerializerTestCase(TestCase):
	def test_device_id_validation_pass(self):
		serializer = GCMDeviceSerializer(data={
			"registration_id": "foobar",
			"name": "Galaxy Note 3",
			"device_id": "0x1031af3b",
			"application_id": "XXXXXXXXXXXXXXXXXXXX",
		})
		self.assertTrue(serializer.is_valid())

	def test_registration_id_unique(self):
		"""Validate that a duplicate registration id raises a validation error."""

		# add a device
		serializer = GCMDeviceSerializer(data={
			"registration_id": "foobar",
			"name": "Galaxy Note 3",
			"device_id": "0x1031af3b",
			"application_id": "XXXXXXXXXXXXXXXXXXXX",
		})
		serializer.is_valid(raise_exception=True)
		obj = serializer.save()

		# ensure updating the same object works
		serializer = GCMDeviceSerializer(obj, data={
			"registration_id": "foobar",
			"name": "Galaxy Note 5",
			"device_id": "0x1031af3b",
			"application_id": "XXXXXXXXXXXXXXXXXXXX",
		})
		serializer.is_valid(raise_exception=True)
		obj = serializer.save()

		# try to add a new device with the same token
		serializer = GCMDeviceSerializer(data={
			"registration_id": "foobar",
			"name": "Galaxy Note 3",
			"device_id": "0xdeadbeaf",
			"application_id": "XXXXXXXXXXXXXXXXXXXX",
		})

		with self.assertRaises(ValidationError):
			serializer.is_valid(raise_exception=True)
