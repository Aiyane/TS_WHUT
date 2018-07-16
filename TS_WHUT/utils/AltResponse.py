from django.http import HttpResponse

headers = {"Access-Control-Allow-Origin": "*",
           "Access-Control-Allow-Methods": "POST",
           "Content-type": "application/json"}


class AltHttpResponse(HttpResponse):
    def __init__(self, *args, **keyargs):
        """
        替换HttpResponse类, 初始化的全局变量header
        """
        super().__init__(*args, **keyargs)
        for k, v in headers.items():
            self[k] = v