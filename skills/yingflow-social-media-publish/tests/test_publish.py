import argparse
import importlib.util
import io
import os
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "publish.py"
spec = importlib.util.spec_from_file_location("publish", SCRIPT)
publish = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publish)


class PublishStatusTests(unittest.TestCase):
    REQUIRED_ARGS = [
        "--channel", "小红书", "--type", "图文", "--account", "测试账号",
        "--status", "待发布", "--title", "测试标题", "--content", "测试内容",
        "--tags", "#测试", "--image", "https://example.com/a.jpg",
    ]

    def setUp(self):
        self.environ = patch.dict(os.environ, {"YINGFLOW_MD_TOKEN": "md-test", "YINGFLOW_TABLE_TOKEN": "table-test"})
        self.environ.start()
        self.addCleanup(self.environ.stop)

    def argv(self):
        return [str(SCRIPT), *self.REQUIRED_ARGS]

    def test_each_supported_status_is_sent_as_single_item_list(self):
        for status in ("已发布", "待发布", "发布失败"):
            with self.subTest(status=status):
                args = argparse.Namespace(
                    channel="小红书", type="图文", account="测试账号",
                    status=status, title="测试", content="内容", tags="#测试",
                    image="https://example.com/a.jpg", cover="", publish_time=1789474176000,
                )
                self.assertIsNone(publish.validate(args))
                self.assertEqual(publish.build_fields(args)["发布状态"], [status])

    def test_supported_channels_and_types_pass_validation(self):
        for channel in ("小红书", "抖音", "百家号", "视频号"):
            for kind in ("图文", "视频"):
                with self.subTest(channel=channel, kind=kind):
                    args = argparse.Namespace(
                        channel=channel, type=kind, status="待发布", account="测试账号",
                        title="测试", content="内容", tags="#测试",
                        image="https://example.com/a.jpg", cover="", publish_time=1789474176000,
                    )
                    self.assertIsNone(publish.validate(args))
                    # 飞书枚举列以单元素数组提交
                    fields = publish.build_fields(args)
                    self.assertEqual(fields["发布渠道"], [channel])
                    self.assertEqual(fields["发布类型"], [kind])

    def test_valid_channel_type_and_status_pass_through_cli(self):
        argv = self.argv()
        for name, value in (("--channel", "百家号"), ("--type", "视频"), ("--status", "发布失败")):
            argv[argv.index(name) + 1] = value
        with patch("sys.argv", argv), patch.object(
            publish, "add_record", return_value={"code": 0, "data": {"record": {"record_id": "rec1"}}}
        ) as add_record, patch("builtins.print"):
            self.assertEqual(publish.main(), 0)
            self.assertEqual(add_record.call_args.args[:2], ("md-test", "table-test"))
            fields = add_record.call_args.args[2]
            self.assertEqual(fields["发布渠道"], ["百家号"])
            self.assertEqual(fields["发布类型"], ["视频"])
            self.assertEqual(fields["发布状态"], ["发布失败"])

    def test_unsupported_enums_are_rejected_before_request(self):
        for name, value in (("--channel", "微博"), ("--type", "直播"), ("--status", "已完成")):
            with self.subTest(name=name):
                argv = self.argv() + [name, value]
                with patch("sys.argv", argv), patch.object(publish, "add_record") as add_record, patch("builtins.print"):
                    self.assertEqual(publish.main(), 1)
                    add_record.assert_not_called()

    def test_missing_required_fields_are_rejected_before_request(self):
        for missing in ("--channel", "--type", "--account", "--status", "--title", "--content", "--tags", "--image"):
            with self.subTest(missing=missing):
                argv = self.argv()
                offset = argv.index(missing)
                del argv[offset:offset + 2]
                with patch("sys.argv", argv), patch.object(publish, "add_record") as add_record, patch("sys.stderr", new_callable=io.StringIO):
                    with self.assertRaises(SystemExit):
                        publish.main()
                    add_record.assert_not_called()

    def test_empty_tags_and_images_are_rejected_before_request(self):
        for option, value in (("--tags", ""), ("--image", ""), ("--image", ",")):
            with self.subTest(option=option, value=value):
                argv = self.argv()
                argv[argv.index(option) + 1] = value
                with patch("sys.argv", argv), patch.object(publish, "add_record") as add_record, patch("builtins.print"):
                    self.assertEqual(publish.main(), 1)
                    add_record.assert_not_called()

    def test_missing_environment_token_prevents_submission(self):
        for missing in ("YINGFLOW_MD_TOKEN", "YINGFLOW_TABLE_TOKEN"):
            with self.subTest(missing=missing), patch.dict(os.environ, {missing: ""}):
                argv = self.argv()
                with patch("sys.argv", argv), patch.object(publish, "add_record") as add_record, patch("builtins.print") as output:
                    self.assertEqual(publish.main(), 1)
                    add_record.assert_not_called()
                    self.assertIn(missing, output.call_args.args[0])

    def test_http_error_preserves_feishu_error_code(self):
        body = io.BytesIO(b'{"code":1254063,"message":"MultiSelectFieldConvFail"}')
        error = HTTPError(publish.API_URL, 502, "Bad Gateway", {}, body)
        with patch.object(publish.urllib.request, "urlopen", side_effect=error):
            result = publish.add_record("md", "table", {"发布状态": ["待发布"]})
        self.assertEqual(result["code"], 1254063)


if __name__ == "__main__":
    unittest.main()
