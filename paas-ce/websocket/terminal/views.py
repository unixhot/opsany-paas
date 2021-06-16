# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views import View
import json
import os
from django.db.models import Q
from datetime import datetime
import uuid
import re
import traceback
import io
import paramiko
from django.conf import settings
from blueapps.utils.logger import logger
from django.utils.timezone import now
from control.utils.esb_api import EsbApi

from control.models import AgentAdmin, HostGroup, UserAgentModel, UserInfo
from .models import SessionLog, CommandBlockList, CommandBlockHistory
from .utils import get_redis_instance
from django.core.exceptions import ObjectDoesNotExist
from control.utils.encryption import PasswordEncryption
from control.utils.status_code import success, SuccessStatusCode, error, ErrorStatusCode


def pagination(queryset, page_num=1, perpage=5, columns=[]):
    res_list = []
    perpage = int(perpage)
    page_num = int(page_num)
    # if 'page_num' in kwargs:
    #     page_num = kwargs['page_num']
    # else:
    #     page_num = 1
    startnum = (page_num - 1) * perpage
    endnum = page_num * perpage
    for record in queryset.order_by("-id").values(*columns)[startnum:endnum]:
        for i in record:
            if isinstance(record[i], datetime):
                record[i] = record[i].strftime("%Y-%m-%d %H:%M:%S")
        res_list.append(record)
    record_count = queryset.count()
    return page_num, perpage, record_count, res_list


class TreeView(View):
    def get(self, request):
        token = request.COOKIES.get("bk_token", '')
        bk_user = EsbApi(token).get_user_info_from_workbench()  # 获取当前登录用户的信息
        user_obj = UserInfo.fetch_one(username=bk_user.get("username"))
        response = {}
        res_dict = {}
        id_list = []
        # res_dict["默认分组"] = []
        aviable_host = []
        if user_obj.role != 1:  # 判断用户是否是管理员
            tmp_aviable_host = UserAgentModel.fetch_all(user_id=user_obj.id).values("agent_id")
            if tmp_aviable_host:
                aviable_host = [each.get("agent_id") for each in tmp_aviable_host]
        try:
            for group in HostGroup.objects.values("id", "name"):
                res_dict[group["name"]] = []
                id_list.append(group["id"])
                if user_obj.role != 1:
                    group_host_agent = AgentAdmin.objects.filter(group_id=group["id"], id__in=aviable_host).values("id", "name", "ip", "system_type", "show_name", "controller_id")
                else:
                    group_host_agent = AgentAdmin.objects.filter(group_id=group["id"]).values("id", "name", "ip", "system_type", "show_name", "controller_id")
                for host in group_host_agent:
                    host["session_uuid"] = str(uuid.uuid4())
                    if host["controller_id"]:
                        host.pop("controller_id")
                        res_dict[group["name"]].append(host)
            response["data"] = res_dict
            response["status_code"] = 0
        except Exception as e:
            logger.error(str(e))
            response["status_code"] = 1
            response["status_info"] = str(e)
        return JsonResponse(response)


class SessionView(View):
    def get(self, request, **kwargs):
        response = {}
        session_uuid = kwargs.get("session_uuid")
        status = kwargs.get("status")
        try:
            if session_uuid:
                # 单台服务器的连接状态信息
                response["data"] = SessionLog.objects.get(log_name=session_uuid).to_dict()
            else:
                perpage = 5 if not request.GET.get("perpage") else int(request.GET.get("perpage"))
                page_num = 1 if not request.GET.get("page_num") else int(request.GET.get("page_num"))
                startnum = (page_num - 1) * perpage
                endnum = page_num * perpage
                data = []
                if status == "finished":
                    queryset = SessionLog.objects.filter(is_finished=True).order_by("-id")
                elif status == "unfinished":
                    queryset = SessionLog.objects.filter(is_finished=False).order_by("-id")
                else:
                    # 所有连接的列表
                    queryset = SessionLog.objects.order_by("-id")
                for i in queryset[startnum:endnum]:
                    data.append(i.to_dict())
                response["data"] = data
                response["page_num"] = page_num
                response["perpage"] = perpage
                response["record_count"] = queryset.count()
            response["status_code"] = 0
        except Exception as e:
            logger.error(str(e))
            response["status_code"] = 1
            response["status_info"] = str(e)
            response["data"] = []
        return JsonResponse(response)

    def post(self, request, **kwargs):
        """
        同步储存用户访问控制台
        """
        response = {}
        status = kwargs.get("status")
        token = request.COOKIES.get("bk_token")
        bk_user = EsbApi(token).get_user_info()  # 获取当前用户
        username = bk_user.get("username")
        try:
            if status == "getuuid":
                session_uuid = str(uuid.uuid4())
                response["data"] = {"session_uuid": session_uuid, "user_name": username}
            response["status_code"] = 0
        except Exception as e:
            logger.error(str(e))
            response["status_code"] = 1
            response["status_info"] = str(e)
        return JsonResponse(response)


class SshSessionKill(View):
    """
    选中堡垒机主机强制下线
    """
    def post(self, request):

        post_data = json.loads(request.body)
        channel = post_data.get('channel', None)
        session_uuid = post_data.get('session_uuid', None)
        try:
            session_obj = SessionLog.objects.filter(channel=channel, log_name=session_uuid)
            if not session_obj:
                return JsonResponse({'status_code': 1, 'status_info': '会话不存在!'})

            if session_obj[0].is_finished:
                return JsonResponse({'status_code': 0, 'status_info': '会话已关闭!'})
            else:
                session_obj[0].end_time = now()
                session_obj[0].is_finished = True
                session_obj[0].save()

                queue = get_redis_instance()
                queue.publish(channel, json.dumps(['close']))
                return JsonResponse({'status_code': 0, 'status_info': '会话已关闭!'})
        except ObjectDoesNotExist:
            return JsonResponse({'status_code': 1, 'status_info': '会话不存在!'})


class SshReplay(View):
    def get(self, request, **kwargs):
        session_uuid = kwargs.get("session_uuid")
        try:
            if session_uuid:
                session_info = SessionLog.objects.filter(log_name=session_uuid)
                if session_info:
                    log_name = session_info[0].log_name + ".log"
            else:
                log_name = "b4a652f3-6e0e-4116-8705-59ae8503e983.log"
        except Exception as e:
            logger.error(str(e))
        return render(request, 'replay.html', {"log_name": log_name})

    def post(self, request, **kwargs):
        pass


class ReplayFileView(View):
    def get(self, request, **kwargs):
        response = {}
        file_name = kwargs.get("file_name")
        full_path = os.path.join(settings.TERMINAL_PATH, file_name)
        if not os.path.exists(full_path):
            response["status_info"] = 'file does not exist!'
            response["status_code"] = 1
            return JsonResponse(response)
        else:
            with open(full_path, 'rb') as f:
                c = f.read()
            response["data"] = c
            response["status_code"] = 0
            return HttpResponse(c)


class BlockListView(View):
    def get(self, request):
        kwargs = request.GET.dict()
        page = int(kwargs.get("current", 1))
        per_page = int(kwargs.get("pageSize", 10))
        queryset = CommandBlockList.objects.all()
        if kwargs.get("search"):
            queryset = queryset.filter(Q(command__icontains=kwargs.get("search")))
        if kwargs.get("block_type"):
            queryset = queryset.filter(block_type=kwargs.get("block_type"))
        end_query = queryset[(page-1) * per_page: page * per_page]
        dt = {
            "current": page,
            "pageSize": per_page,
            "total": queryset.count(),
            "data": [i.to_dict() for i in end_query]
        }
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, dt))

    def post(self, request):
        data = json.loads(request.body)
        command = data.get("command").strip()
        block_type = data.get("block_type").strip()
        if (not command) or (block_type not in ["cancel", "confirm"]):
            return JsonResponse(error(ErrorStatusCode.PARAMS_ERROR))
        block_info = data.get("block_info")
        while command.find("  ") >= 0:
            command = command.replace("  ", " ")
        try:
            command_obj = CommandBlockList.objects.filter(command=command).first()
        except:
            command_obj = ""
        if not command_obj:
            CommandBlockList.objects.create(command=command, block_type=block_type, block_info=block_info)
            return JsonResponse(success(SuccessStatusCode.MESSAGE_CREATE_SUCCESS))
        return JsonResponse(error(ErrorStatusCode.RECORD_HAS_EXISTED))

    def put(self, request):
        data = json.loads(request.body)
        block_id = data.get("block_id")
        command = data.get("command").strip()
        if not block_id or len(command) == 0:
            return JsonResponse(error(ErrorStatusCode.PARAMS_ERROR))
        block_type = data.get("block_type").strip()
        block_info = data.get("block_info")
        while command.find("  ") >= 0:
            command = command.replace("  ", " ")
        try:
            block_list = CommandBlockList.objects.filter(id=block_id).first()
        except:
            block_list = []
        # 判断是否已经重复
        if block_list:
            if CommandBlockList.objects.filter(command=command).exclude(id=block_id):
                return JsonResponse(error(ErrorStatusCode.RECORD_HAS_EXISTED))
            CommandBlockList.objects.update()
            block_list.command = command
            block_list.block_type = block_type
            block_list.block_info = block_info
            block_list.save()
            return JsonResponse(success(SuccessStatusCode.MESSAGE_UPDATE_SUCCESS))
        return JsonResponse(error(ErrorStatusCode.DATA_NOT_EXISTED))

    def delete(self, request):
        data = json.loads(request.body)
        block_id = data.get("block_id")
        if not block_id:
            return JsonResponse(error(ErrorStatusCode.PARAMS_ERROR))
        block_list = CommandBlockList.objects.filter(id=block_id)
        if block_list:
            block_list.delete()
            return JsonResponse(success(SuccessStatusCode.MESSAGE_DELETE_SUCCESS))
        return JsonResponse(error(ErrorStatusCode.DATA_NOT_EXISTED))


class BlockHistoryView(View):
    def get(self, request):
        data = request.GET.dict()
        page = int(data.get("current", 1))
        per_page = int(data.get("pageSize", 10))
        order_by = data.get("order_by", "-datetime")
        queryset = CommandBlockHistory.objects.filter().order_by(order_by)
        if data.get("search"):
            queryset = queryset.filter(Q(command__icontains=data.get("search")) | Q(hostname__icontains=data.get("search"))).order_by(order_by)
        if data.get("block_type"):
            queryset = queryset.filter(block_type=data.get("block_type")).order_by(order_by)
        end_query = queryset[(page-1) * per_page: page * per_page]
        dt = {
            "current": page,
            "pageSize": per_page,
            "total": queryset.count(),
            "data": [i.to_dict() for i in end_query]
        }
        return JsonResponse(success(SuccessStatusCode.MESSAGE_GET_SUCCESS, dt))


class TerminalHostView(View):
    def get(self, request, **kwargs):
        response = {}
        response['status_code'] = 1
        try:
            server_id = kwargs.get("server_id")
            if not server_id:
                response['status_info'] = "未收到server_id!"
            else:
                # "password", "system_type", "ssh_key_id"))
                host_info = list(AgentAdmin.objects.filter(id=server_id).values("name", "ip", "ssh_port", "username",
                                                                                "system_type", "ssh_key_id"))
                response['data'] = host_info
                response['status_code'] = 0
        except Exception as e:
            response['status_info'] = str(e)
        return JsonResponse(response)

    '''
    创建用于连接的临时主机
    '''
    def post(self, request):
        response = {}
        response['status_code'] = 1
        try:
            data = json.loads(request.body)
            name = data.get("name")
            ip = data.get("ip")
            ssh_port = data.get("ssh_port")
            system_type = data.get("system_type")
            username = data.get("username")
            password = PasswordEncryption().encrypt(data.get("password")) if \
                data.get("password") and data.get("password") != "******" else data.get("password")
            ssh_key_id = data.get("ssh_key_id", "")
            if not (password or ssh_key_id):
                response['status_info'] = "请输入密码或者秘钥!"
            else:
                host_info = AgentAdmin.objects.filter(name=name)
                if host_info:
                    if host_info[0].controller:
                        name = name + "-" + str(uuid.uuid4()).split("-")[2]
                        host_obj = AgentAdmin.objects.create(name=name, ip=ip, username=username, password=password,
                                                             ssh_key_id=ssh_key_id, ssh_port=ssh_port,
                                                             system_type=system_type)
                    else:
                        host_info.update(ip=ip, username=username, password=password, ssh_key_id=ssh_key_id,
                                         ssh_port=ssh_port, system_type=system_type)
                        host_obj = host_info[0]
                else:
                    host_obj = AgentAdmin.objects.create(name=name, ip=ip, username=username, password=password,
                                                         ssh_key_id=ssh_key_id, ssh_port=ssh_port,
                                                         system_type=system_type)
                response['data'] = {"id": host_obj.id}
                response['status_code'] = 0
        except Exception as e:
            response['status_info'] = str(e)
        return JsonResponse(response)


class LinuxFile(View):
    def getFileInfo(self, filepath):
        info = {}
        info['TimeModified'] = datetime.datetime.fromtimestamp(os.path.getatime(filepath)).strftime("%Y-%m-%d %H:%M:%S")
        info['Size'] = os.path.getsize(filepath)
        info['Name'] = os.path.basename(filepath)
        return info

    def get_sftp(self, server_id, bk_token):
        server_obj = AgentAdmin.objects.filter(id=server_id)
        if not server_obj:
            raise Exception("该服务器不存在!")
        server_object = server_obj[0]
        if server_object.ssh_type != "password":
            ssh_key_id = server_object.ssh_key_id
            esb_obj = EsbApi(bk_token)
            res = esb_obj.get_user_ssh_key(str(ssh_key_id))
            pri_key_ = res.get('private_key')
            pri_key = io.StringIO(pri_key_)
            pri_key = paramiko.RSAKey.from_private_key(pri_key)
        else:
            pri_key = None
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
        try:
            password = PasswordEncryption().decrypt(server_object.password)
        except:
            password = ""
        try:
            ssh.connect(server_object.ip, port=server_object.ssh_port, username=server_object.username, password=password, pkey=pri_key, timeout=10)
            stdin, stdout, stderr = ssh.exec_command('pwd')
            home_path = stdout.read().decode().strip('\n')
            sftp = ssh.open_sftp()
        except Exception as e:
            raise Exception("连接linux服务器失败！请检查！")
        return ssh, sftp, home_path

    def get(self, request, **kwargs):
        response = {}
        server_id = str(kwargs.get('server_id'))
        bk_token = request.COOKIES.get("bk_token")
        if kwargs.get("url"):
            path = '/' + kwargs.get("url").strip('/')
        else:
            path = ''
        if re.search('\.\./', path):
            response['status_code'] = 1
            response['status_info'] = "路径错误!"
            return JsonResponse(response)
        try:
            ssh, sftp, home_path = self.get_sftp(server_id, bk_token)
            if not path:
                path = home_path
            response['current_path'] = path
            try:
                folder_list = {"path":[], "file":[]}
                sftp.chdir(path)
                for r in sftp.listdir_attr():
                    if r.filename.startswith("."):
                        continue
                    if r.longname.startswith('d'):
                        folder_list["path"].append(r.filename)
                    else:
                        folder_list["file"].append(r.filename)
                response['status_code'] = 0
                response['data'] = folder_list
                ssh.close()
                return  JsonResponse(response)
            except paramiko.sftp.SFTPError:
                # 下载文件
                tmp_dir = '/tmp/terminal_file/'
                if not os.path.exists(tmp_dir):
                    os.makedirs(tmp_dir)
                filename = path.split('/').pop()
                full_path = tmp_dir + filename
                sftp.get(path, full_path)
                ssh.close()
                with open(full_path, 'rb') as f:
                    c = f.read()
                response = HttpResponse(c)
                response['Content-Type'] = 'application/octet-stream'
                response['Content-Disposition'] = 'attachment;filename=' + os.path.basename(full_path)
                return response
        except Exception as e:
            response['status_code'] = 1
            response['status_info'] = str(e)
            return JsonResponse(response)

    def post(self, request, **kwargs):
        response = {}
        file_obj = request.FILES.get('fileupload', None)
        server_id = str(kwargs.get('server_id'))
        bk_token = request.COOKIES.get("bk_token")
        try:
            ssh, sftp, home_path = self.get_sftp(server_id, bk_token)
            if kwargs.get("url"):
                path = '/' + kwargs.get("url").strip('/')
            else:
                path = home_path
            if re.search('\.\./', path):
                response['status_code'] = 1
                response['status_info'] = "路径错误!"
                return JsonResponse(response)
            tmp_dir = '/tmp/terminal_file/'
            if not os.path.exists(tmp_dir):
                os.makedirs(tmp_dir)
            full_path = tmp_dir + file_obj.name
            with open(full_path, 'wb') as f:
                for line in file_obj.chunks():
                    f.write(line)
            f.close()
            sftp.put(full_path, os.path.join(path,file_obj.name))
            ssh.close()
            response['status_code'] = 0
            response['status_info'] = "上传成功!"
        except Exception as e:
            response['status_code'] = 1
            response['status_info'] = str(e)
        return JsonResponse(response)

    def delete(self, request, **kwargs):
        response = {}
        response['status_code'] = 1
        server_id = str(kwargs.get('server_id'))
        bk_token = request.COOKIES.get("bk_token")
        if kwargs.get("url"):
            path = '/' + kwargs.get("url").strip('/')
        else:
            path = '/root'
        if re.search('\.\./', path):
            response['status_info'] = "路径错误!"
            return JsonResponse(response)
        response['status_code'] = 0
        response['status_info'] = "删除成功!"
        try:
            ssh, sftp, home_path = self.get_sftp(server_id, bk_token)
            if not path:
                path = home_path
            if path == home_path:
                raise Exception("当前用户根目录禁止删除!")
            sftp.remove(path)
        except OSError:
            try:
                sftp.rmdir(path)
            except OSError:
                response['status_code'] = 1
                response['status_info'] = "删除失败!"
        except Exception as e:
            response['status_code'] = 1
            response['status_info'] = str(e)
        finally:
            ssh.close()
        return JsonResponse(response)