import logging
from django.utils.deprecation import MiddlewareMixin
import time


application_logger = logging.getLogger('application-logger')
error_logger = logging.getLogger('error-logger')
performance_logger = logging.getLogger('performance-logger')


class MyMiddleware(MiddlewareMixin):

    # viewを呼び出す前に実行される
    def process_view(self, request, view_func, view_args, view_kwargs):
        application_logger.info(request.get_full_path()
                                )  # どのパスのviewが呼び出されたかを出力
        # print(dir(request))

    def process_exception(self, request, exception):
        error_logger.error(exception, exc_info=True)


# 各Viewのパフォーマンスを図るためのログ出力 処理時間を計算して出力する
class PerformanceMiddleware(MiddlewareMixin):

    def process_view(self, request, view_func, view_args, view_kwargs):
        start_time = time.time()
        # requestに新たにstart_timeというプロパティを与える
        request.start_time = start_time

    def process_template_response(self, request, response):
        response_time = time.time() - request.start_time
        performance_logger.info(f'{request.get_full_path()}: {response_time}s')
        return response
