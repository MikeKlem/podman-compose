# SPDX-License-Identifier: GPL-2.0

import unittest
from unittest import mock

from podman_compose import container_to_args


def create_compose_mock():
    compose = mock.Mock()
    compose.project_name = "test_project_name"
    compose.dirname = "test_dirname"
    compose.container_names_by_service.get = mock.Mock(return_value=None)
    compose.prefer_volume_over_mount = False
    compose.default_net = None
    compose.networks = {}
    return compose


def get_minimal_container():
    return {
        "name": "project_name_service_name1",
        "service_name": "service_name",
        "image": "busybox",
    }


class TestContainerToArgs(unittest.IsolatedAsyncioTestCase):
    async def test_minimal(self):
        c = create_compose_mock()

        cnt = get_minimal_container()

        args = await container_to_args(c, cnt)
        self.assertEqual(
            args,
            [
                "--name=project_name_service_name1",
                "-d",
                "--net",
                "",
                "--network-alias",
                "service_name",
                "busybox",
            ],
        )

    async def test_runtime(self):
        c = create_compose_mock()

        cnt = get_minimal_container()
        cnt["runtime"] = "runsc"

        args = await container_to_args(c, cnt)
        self.assertEqual(
            args,
            [
                "--name=project_name_service_name1",
                "-d",
                "--net",
                "",
                "--network-alias",
                "service_name",
                "--runtime",
                "runsc",
                "busybox",
            ],
        )

    async def test_sysctl_list(self):
        c = create_compose_mock()

        cnt = get_minimal_container()
        cnt["sysctls"] = [
            "net.core.somaxconn=1024",
            "net.ipv4.tcp_syncookies=0",
        ]

        args = await container_to_args(c, cnt)
        self.assertEqual(
            args,
            [
                "--name=project_name_service_name1",
                "-d",
                "--net",
                "",
                "--network-alias",
                "service_name",
                "--sysctl",
                "net.core.somaxconn=1024",
                "--sysctl",
                "net.ipv4.tcp_syncookies=0",
                "busybox",
            ],
        )

    async def test_sysctl_map(self):
        c = create_compose_mock()

        cnt = get_minimal_container()
        cnt["sysctls"] = {
            "net.core.somaxconn": 1024,
            "net.ipv4.tcp_syncookies": 0,
        }

        args = await container_to_args(c, cnt)
        self.assertEqual(
            args,
            [
                "--name=project_name_service_name1",
                "-d",
                "--net",
                "",
                "--network-alias",
                "service_name",
                "--sysctl",
                "net.core.somaxconn=1024",
                "--sysctl",
                "net.ipv4.tcp_syncookies=0",
                "busybox",
            ],
        )

    async def test_sysctl_wrong_type(self):
        c = create_compose_mock()
        cnt = get_minimal_container()

        # check whether wrong types are correctly rejected
        for wrong_type in [True, 0, 0.0, "wrong", ()]:
            with self.assertRaises(TypeError):
                cnt["sysctls"] = wrong_type
                await container_to_args(c, cnt)

    async def test_pid(self):
        c = create_compose_mock()
        cnt = get_minimal_container()

        cnt["pid"] = "host"

        args = await container_to_args(c, cnt)
        self.assertEqual(
            args,
            [
                "--name=project_name_service_name1",
                "-d",
                "--net",
                "",
                "--network-alias",
                "service_name",
                "--pid",
                "host",
                "busybox",
            ],
        )

    async def test_http_proxy(self):
        c = create_compose_mock()

        cnt = get_minimal_container()
        cnt["http_proxy"] = False

        args = await container_to_args(c, cnt)
        self.assertEqual(
            args,
            [
                "--name=project_name_service_name1",
                "-d",
                "--http-proxy=false",
                "--net",
                "",
                "--network-alias",
                "service_name",
                "busybox",
            ],
        )
