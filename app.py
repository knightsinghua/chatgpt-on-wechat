# encoding:utf-8

import os
import signal
import sys

from channel import channel_factory
from common.log import logger
from config import conf, load_config
from plugins import *


def sigterm_handler_wrap(_signo):
    # 使用下划线作为变量名的前缀是一种惯例，用于表示一个临时或不重要的变量。这种约定有助于代码的可读性，可以让读者知道该变量的值不会在后续的代码中使用到。（去掉不会影响代码的运行）
    old_handler = signal.getsignal(_signo)

    def func(_signo, _stack_frame):
        logger.info("signal {} received, exiting...".format(_signo))
        conf().save_user_datas()
        if callable(old_handler):  #  check old_handler
            return old_handler(_signo, _stack_frame)
        sys.exit(0)

    signal.signal(_signo, func)


def run():
    try:
        # load config
        load_config()
        # ctrl + c 通过注册信号处理程序来捕获并处理用户可能会发送的中断信号（SIGINT）或终止信号（SIGTERM）  并在接收到这些信号时执行相应的操作。这样做的目的是让程序能够优雅地响应用户或操作系统的信号，并进行适当的处理和清理，以确保程序的正确终止。
        sigterm_handler_wrap(signal.SIGINT)
        # kill signal
        sigterm_handler_wrap(signal.SIGTERM)

        # create channel
        channel_name = conf().get("channel_type", "wx")

        if "--cmd" in sys.argv:
            channel_name = "terminal"

        if channel_name == "wxy":
            os.environ["WECHATY_LOG"] = "warn"
            # os.environ['WECHATY_PUPPET_SERVICE_ENDPOINT'] = '127.0.0.1:9001'

        channel = channel_factory.create_channel(channel_name)
        if channel_name in ["wx", "wxy", "terminal", "wechatmp", "wechatmp_service", "wechatcom_app"]:
            PluginManager().load_plugins()

        # startup channel
        channel.startup()
    except Exception as e:
        logger.error("App startup failed!")
        logger.exception(e)


if __name__ == "__main__":
    run()
