from django.http import JsonResponse, HttpResponse
from django.views.generic import View
from django.conf import settings

import os
import traceback
import re
import datetime

# Create your views here.


class GuacamoleReplayFileView(View):
    def get(self, request, **kwargs):
        response = {}
        log_name = kwargs.get("log_name")
        with open(os.path.join(settings.ORI_GUACD_PATH, "logfile/" + log_name), 'rb') as f:
            c = f.read()
        response["data"] = c
        response["status_code"] = 0
        return HttpResponse(c)


class WinFile(View):
    def getFileInfo(self, filepath):
        info = {}
        info['TimeModified'] = datetime.datetime.fromtimestamp(os.path.getatime(filepath)).strftime("%Y-%m-%d %H:%M:%S")
        info['Size'] = os.path.getsize(filepath)
        info['Name'] = os.path.basename(filepath)
        return info

    def get(self, request, **kwargs):
        response = {}
        server_id = str(kwargs.get('server_id'))
        base_path = '/' + settings.ORI_GUACD_PATH.strip('/') + '/' + server_id
        if not os.path.exists(base_path + "/Download"):
            os.makedirs(base_path + "/Download")
        if kwargs.get("url"):
            path = kwargs.get("url").strip('/')
        else:
            path = "Download"
        if re.search('\.\./', path):
            response['status_info'] = "路径错误!"
            return JsonResponse(response)
        response['current_path'] = path
        full_path = os.path.join(base_path, path)
        if not os.path.exists(full_path):
            response['status_info'] = "文件夹不存在!"
        try:
            if os.path.isdir(full_path):
                ps = os.listdir(full_path)
                folder_list = {"path":[], "file":[]}
                for n in ps:
                    v = os.path.join(full_path, n)
                    if os.path.isdir(v):
                        folder_list["path"].append(n)
                    else:
                        folder_list["file"].append(n)
                response['status_code'] = 0
                response['data'] = folder_list
                return  JsonResponse(response)
            else:
                # 下载文件
                with open(full_path, 'rb') as f:
                    c = f.read()
                response = HttpResponse(c)
                response['Content-Type'] = 'application/octet-stream'
                response['Content-Disposition'] = 'attachment;filename=' + os.path.basename(full_path)
                return response
        except Exception as e:
            print(traceback.print_exc())
            response['status_code'] = 1
            response['status_info'] = str(e)
            return JsonResponse(response)

    def post(self, request, **kwargs):
        response = {}
        file_obj = request.FILES.get('fileupload', None)
        if not kwargs.get("url"):
            path = "Download"
        else:
            path = kwargs.get("url").strip('/')
        if re.search('\.\./', path):
            response['status_code'] = 1
            response['status_info'] = "路径错误!"
            return JsonResponse(response)
        server_id = str(kwargs.get('server_id'))
        base_path = '/' + settings.ORI_GUACD_PATH.strip('/') + '/' + server_id
        full_path = os.path.join(base_path, path)
        if not os.path.exists(full_path):
            response['status_info'] = "文件夹不存在!"
        with open(os.path.join(full_path, file_obj.name), 'wb') as f:
            for line in file_obj.chunks():
                f.write(line)
        f.close()
        response['status_code'] = 0
        response['status_info'] = "上传成功!"
        return JsonResponse(response)

    def delete(self, request, **kwargs):
        response = {}
        response['status_code'] = 1
        if not kwargs.get("url"):
            path = "Download"
        else:
            path = kwargs.get("url").strip('/')
        if re.search('\.\./', path) or path == "Download":
            response['status_info'] = "删除路径错误!请确认!"
            return JsonResponse(response)
        server_id = str(kwargs.get('server_id'))
        base_path = '/' + settings.ORI_GUACD_PATH.strip('/') + '/' + server_id
        full_path = os.path.join(base_path, path)
        if os.path.exists(full_path):
            response['status_code'] = 0
            if os.path.isdir(full_path):
                os.rmdir(full_path)
            else:
                os.remove(full_path)
        else:
            response['status_info'] = "删除的文件/文件夹不存在!"
        return JsonResponse(response)